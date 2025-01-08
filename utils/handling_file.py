from fastapi import UploadFile, HTTPException
import uuid
import os
from datetime import datetime
import shutil
from pathlib import Path

async def validation_file(file: UploadFile, allowed_extensions: list = ["image/jpeg", "image/png", "application/pdf", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "text/plain"]):
    # Move the cursor to the end to get the file size
    file.file.seek(0, 2)
    file_size = file.file.tell()

    # Move the cursor back to the beginning
    await file.seek(0)

    # Check the MIME type
    content_type = file.content_type
    if content_type not in allowed_extensions:
        file_formats = ', '.join([mime.split('/')[-1] for mime in allowed_extensions])
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Only files with the following types are allowed: {file_formats}."
        )

    # Set max file size based on content type
    if content_type in ["image/jpeg", "image/png"]:
        limit_file_size_mb = 1  # 1 MB for images
    elif content_type == "application/pdf":
        limit_file_size_mb = 5  # 5 MB for PDFs
    elif content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        limit_file_size_mb = 2  # 2 MB for Excel files
    elif content_type == "text/plain":
        limit_file_size_mb = 1  # 1 MB for text files
    else:
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file type."
        )

    # Check file size
    if file_size > limit_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum allowed size for {content_type.split('/')[-1]} is {limit_file_size_mb} MB."
        )

def upload_file(data: UploadFile, folder: str, name: str = None):
    if data:
        # Ensure the directory exists or create it if it doesn't
        os.makedirs(folder, exist_ok=True)

        # Determine file extension
        file_extension = data.filename.split('.')[-1]

        # Generate a unique filename
        current_date = datetime.now().date()
        if name:
            # Check if file with the same name exists, add a unique suffix if needed
            base_name = name
            new_filename = f"{base_name}.{file_extension}"
            counter = 1
            while os.path.exists(os.path.join(folder, new_filename)):
                new_filename = f"{base_name}_{counter}.{file_extension}"
                counter += 1
        else:
            # Use UUID to ensure filename uniqueness
            new_filename = f"{current_date}-{str(uuid.uuid4())}.{file_extension}"

        # Save the uploaded file to a directory
        file_path = os.path.join(folder, new_filename)
        with open(file_path, "wb") as f_dest:
            shutil.copyfileobj(data.file, f_dest)

        # Return the filename
        return new_filename
    else:
        raise HTTPException(status_code=400, detail="Error uploading file")

def delete_file(file_path: str):
    try:
        # Check if the file exists before attempting to delete
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        else:
            return False  # File not found
    except Exception as e:
        print(e)
        return False  # Error occurred while deleting
