"""Small matched-image contact sheets."""

from PIL import Image, ImageDraw, ImageFont


def sheet(rows, target, size=(640, 426)):
    board = Image.new("RGB", (size[0] * 2, (size[1] + 28) * len(rows)), "#181818")
    draw = ImageDraw.Draw(board)
    font = ImageFont.load_default(size=17)
    for row, pair in enumerate(rows):
        for col, (im, label) in enumerate(pair):
            im = im.copy()
            im.thumbnail(size)
            x, y = col * size[0], row * (size[1] + 28)
            board.paste(im, (x, y + 28))
            draw.text((x + 8, y + 5), label, font=font, fill="white")
    target.parent.mkdir(parents=True, exist_ok=True)
    board.save(target)
