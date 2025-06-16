import cloudinary
import cloudinary.uploader
import filetype
from fastapi import HTTPException
from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUD_NAME,
    api_key=settings.API_KEY,
    api_secret=settings.API_SECRET
)

def validate_image_file(image_file, max_size_mb=5):
    if not image_file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail=f"File {image_file.filename} không phải ảnh")
    contents = image_file.file.read()
    kind = filetype.guess(contents)
    if not kind or not kind.mime.startswith("image/"):
        raise HTTPException(status_code=400, detail=f"Định dạng ảnh không hợp lệ: {image_file.filename}")
    if len(contents) > max_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Ảnh quá lớn (tối đa {max_size_mb}MB): {image_file.filename}")
    image_file.file.seek(0)  # reset pointer for next read
    return contents

async def validate_image_uploadfile(image, max_size_mb=5):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail=f"File {image.filename} không phải ảnh")
    contents = await image.read()
    kind = filetype.guess(contents)
    if not kind or not kind.mime.startswith("image/"):
        raise HTTPException(status_code=400, detail=f"Định dạng ảnh không hợp lệ: {image.filename}")
    if len(contents) > max_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Ảnh quá lớn (tối đa {max_size_mb}MB): {image.filename}")
    return contents

def upload_image_to_cloudinary(contents, folder="products"):
    try:
        result = cloudinary.uploader.upload(
            contents,
            folder=folder,
            use_filename=True,
            unique_filename=True,
            overwrite=False
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload ảnh thất bại: {str(e)}")

def delete_image_from_cloudinary(public_id):
    try:
        cloudinary.uploader.destroy(public_id)
    except Exception as e:
        pass
