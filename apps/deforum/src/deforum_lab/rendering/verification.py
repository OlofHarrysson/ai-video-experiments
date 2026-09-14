"""Validate saved one-painting ComfyUI execution and lineage."""

import copy

from deforum_lab.records import require


def validate_execution(
    requested,
    executed,
    upload,
    history,
    response,
    submission,
    parent_hash,
    initialization_hash,
):
    """Adapt continuity_controls_review checks for a warped upload, keeping both hashes."""
    expected = copy.deepcopy(requested)
    require(
        upload.get("type") == "input" and bool(upload.get("name")),
        "Missing input upload",
    )
    expected["20"]["inputs"]["image"] = "/".join(
        filter(None, [upload.get("subfolder"), upload["name"]])
    )
    require(
        executed == expected, "Executed graph differs from uploaded requested graph"
    )
    if "sha256" in upload:
        require(
            upload["sha256"] == initialization_hash,
            "Upload checksum differs from warped initialization",
        )
    require(
        submission.get("parent_sha256") == parent_hash,
        "Submission parent checksum differs",
    )
    if "initialization_sha256" in submission:
        require(
            submission["initialization_sha256"] == initialization_hash,
            "Submission initialization differs",
        )
    prompt_id = response.get("prompt_id")
    require(
        bool(prompt_id) and not response.get("node_errors"),
        "Submission rejected or missing prompt id",
    )
    require(
        submission.get("prompt_id") == prompt_id
        and submission.get("frames") == 1
        and bool(submission.get("collected_at")),
        "Submission not collected or prompt id differs",
    )
    status = history["status"]
    require(
        status.get("completed") is True and status.get("status_str") == "success",
        "Unsuccessful history",
    )
    require(
        history["prompt"][1] == prompt_id and history["prompt"][2] == executed,
        "History graph or prompt id differs",
    )
    require("11" in history["prompt"][4], "SaveImage missing from executed outputs")
    for event, payload in status.get("messages", []):
        require(
            event not in ("execution_error", "execution_interrupted"),
            "History contains execution failure",
        )
        if "prompt_id" in payload:
            require(
                payload["prompt_id"] == prompt_id, "History event prompt id differs"
            )
    images = history["outputs"]["11"]["images"]
    require(
        len(images) == 1
        and images[0].get("type") == "output"
        and images[0]["filename"].endswith(".png"),
        "Unexpected SaveImage output",
    )
    return prompt_id, images[0]
