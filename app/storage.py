import os
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

ALLOWED_PHOTO_TYPES = {
    ".png": "image/png",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}
MAX_PHOTO_BYTES = 5 * 1024 * 1024


def upload_root() -> Path:
    return Path(os.getenv("UPLOAD_DIR", "/data/uploads"))


def save_tank_photo(tank_id: int, upload: UploadFile) -> str:
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in ALLOWED_PHOTO_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")
    payload = upload.file.read(MAX_PHOTO_BYTES + 1)
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
    if len(payload) > MAX_PHOTO_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is too large")

    directory = upload_root() / "tanks"
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / f"{tank_id}{suffix}"
    for existing in directory.glob(f"{tank_id}.*"):
        if existing != destination:
            existing.unlink(missing_ok=True)
    destination.write_bytes(payload)
    return str(destination)


def photo_media_type(path: str) -> str:
    media_type = ALLOWED_PHOTO_TYPES.get(Path(path).suffix.lower())
    if media_type is None or not Path(path).is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return media_type
