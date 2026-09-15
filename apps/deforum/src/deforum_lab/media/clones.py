"""Lossless APFS sharing for byte-identical, inactive media files on this Mac."""

import ctypes
import errno
import os
import shutil
import stat
import sys
import uuid
from pathlib import Path

from deforum_lab.media.storage import digest


def copy_media(source, target):
    """Copy new media with APFS sharing where supported, ordinary copying elsewhere.

    Both paths retain independent write semantics. Existing targets are rejected.
    Only filesystem capability failures use ordinary copying; other errors surface.
    """
    source, target = Path(source), Path(target)
    if target.exists() or target.is_symlink():
        raise FileExistsError(target)
    if sys.platform == "darwin":
        libc = ctypes.CDLL(None, use_errno=True)
        clonefile = libc.clonefile
        clonefile.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
        clonefile.restype = ctypes.c_int
        if clonefile(os.fsencode(source), os.fsencode(target), 0) == 0:
            return
        error = ctypes.get_errno()
        if error not in (errno.EXDEV, errno.ENOTSUP, errno.ENOSYS):
            raise OSError(error, os.strerror(error), str(target))
    shutil.copy2(source, target)


def extended_attributes(libc, path):
    listxattr = libc.listxattr
    listxattr.argtypes = [
        ctypes.c_char_p,
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.c_int,
    ]
    listxattr.restype = ctypes.c_ssize_t
    getxattr = libc.getxattr
    getxattr.argtypes = [
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.c_int,
    ]
    getxattr.restype = ctypes.c_ssize_t
    encoded = os.fsencode(path)
    size = listxattr(encoded, None, 0, 0)
    if size < 0:
        raise OSError(ctypes.get_errno(), "Cannot inspect extended attributes")
    names = ctypes.create_string_buffer(max(size, 1))
    if listxattr(encoded, names, size, 0) != size:
        raise ValueError("Extended attributes changed during inspection")
    result = {}
    for name in names.raw[:size].split(b"\0"):
        if not name:
            continue
        length = getxattr(encoded, name, None, 0, 0, 0)
        if length < 0:
            raise OSError(ctypes.get_errno(), "Cannot read extended attribute")
        value = ctypes.create_string_buffer(max(length, 1))
        if getxattr(encoded, name, value, length, 0, 0) != length:
            raise ValueError("Extended attribute changed during inspection")
        result[name] = value.raw[:length]
    return result


def signature(path):
    info = path.lstat()
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def share_duplicate(source, target, expected_sha256):
    """Replace only a verified duplicate with a private copy-on-write clone.

    Existing hardlink groups and files with differing attributes are left alone.
    Call only for completed immutable experiments, while no writer is running.
    There is no ordinary-copy or hardlink fallback on unsupported filesystems.
    """
    if sys.platform != "darwin":
        raise RuntimeError("APFS clone sharing requires macOS")
    source, target = Path(source), Path(target)
    a, b = source.lstat(), target.lstat()
    if not stat.S_ISREG(a.st_mode) or not stat.S_ISREG(b.st_mode):
        raise ValueError("Expected ordinary files, without symlinks")
    if (a.st_dev, a.st_ino) == (b.st_dev, b.st_ino):
        return False
    if b.st_nlink != 1:
        return False
    libc = ctypes.CDLL(None, use_errno=True)
    if extended_attributes(libc, source) != extended_attributes(libc, target):
        return False
    if (a.st_dev, a.st_mode, a.st_uid, a.st_gid) != (
        b.st_dev,
        b.st_mode,
        b.st_uid,
        b.st_gid,
    ):
        return False
    initial = (signature(source), signature(target))
    if (
        a.st_size != b.st_size
        or digest(source) != expected_sha256
        or digest(target) != expected_sha256
    ):
        raise ValueError("Refusing to replace media whose contents differ")
    clonefile = libc.clonefile
    clonefile.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    clonefile.restype = ctypes.c_int
    temporary = target.with_name(f".{target.name}.{uuid.uuid4().hex}.clone")
    try:
        if clonefile(os.fsencode(source), os.fsencode(temporary), 1) != 0:
            error = ctypes.get_errno()
            raise OSError(error, os.strerror(error), str(target))
        shutil.copystat(target, temporary)
        copyfile = libc.copyfile
        copyfile.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_void_p,
            ctypes.c_uint32,
        ]
        copyfile.restype = ctypes.c_int
        # COPYFILE_ACL only: retain the target's access rules, never copy its data.
        if copyfile(os.fsencode(target), os.fsencode(temporary), None, 1) != 0:
            raise OSError(ctypes.get_errno(), "Cannot preserve target ACL")
        if digest(temporary) != expected_sha256:
            raise ValueError("Clone content verification failed")
        if initial != (signature(source), signature(target)):
            raise ValueError("Media changed during clone preparation")
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    return True
