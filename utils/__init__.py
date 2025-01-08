# import pandas as pd
from fastapi import HTTPException, status


async def validate_file_content_type(content_type: str, allowed_content_types: tuple):
    if content_type.lower() not in allowed_content_types:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid file content type. Only {', '.join(allowed_content_types)} files are allowed.")

# async def validation_sheet_name_multiple(file_content, expected_sheet_name):
#     # validation sheet name
#     try:
#         df = pd.read_excel(file_content, engine='openpyxl', sheet_name=expected_sheet_name, keep_default_na=False, na_filter=False)
#         return df
#     except ValueError as e:
#         print(e)
#         # Handle sheet name validation error
#         error_message = f"Sheet name should be: {expected_sheet_name}"
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)
