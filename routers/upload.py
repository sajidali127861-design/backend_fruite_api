from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from models.user import User
from utils.dependencies import get_current_admin
import os
import uuid

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_admin: User = Depends(get_current_admin)
):
    allowed_types = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ]
    Max_File_Size=5*1024*1024
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG and WEBP images are allowed"
        )
    contents = await file.read()
    if len(contents) > Max_File_Size:
        return HTTPException(
            status_code="400",
            detail="Imag size must be less than  5 MB"
        )

    file_extension = os.path.splitext(file.filename)[1]

    filename = f"{uuid.uuid4()}{file_extension}"

    file_path = os.path.join(
        UPLOAD_DIR,
        filename
    )

 

    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    return {
        "message": "Image uploaded successfully",
        "image_url": f"/uploads/{filename}"
    }