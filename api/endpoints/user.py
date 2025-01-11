from datetime import date
import uuid
from fastapi import APIRouter, Depends, Form, Query, Request, UploadFile, status, HTTPException, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from constant import UserGender
from database import get_db
from models.response import GeneralDataPaginateResponse, GeneralDataResponse
from models.user import User
from services.role_service import RoleService
from services.user_service import UserService
# from utils.authentication import Authentication
# from utils.generate_sensitive import encrypt_value
from utils.authentication import Authentication
from utils.handling_file import validation_file
from utils.manual import get_total_pages

router = APIRouter()

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    role_id: str = Form(...),
    username: str = Form(..., min_length=1, max_length=36),
    email: str = Form(..., min_length=1, max_length=225),
    password: str = Form(..., min_length=1, max_length=512),
    name: str = Form(..., min_length=1, max_length=225),
    gender: UserGender = Form(...),    
    image: UploadFile = None,
    db: Session = Depends(get_db), 
    # payload = Depends(Authentication())
):  
    """
        Create User

        - should login

        - create this user to subordinate if user that login has subordinate access
        - only admin and leader
    """
    # service
    role_service = RoleService(db)
    user_service = UserService(db)

    # cek role user
    # user_id_active = payload.get("uid", None)
    # user_active = user_service.user_repository.read_user(user_id_active)
    # if not user_active or user_active.role.code not in ['ADM', 'USER']:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Anda Tidak Memiliki Hak Akses"
    #     )
    
    # validation
    exist_role_id = role_service.role_repository.read_role(role_id)
    if not exist_role_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    exist_username = user_service.user_repository.get_user_by_username(username)
    if exist_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exist")
    
    exist_email = user_service.user_repository.get_user_by_email(email)
    if exist_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exist")
    
    try:
        if (image):
            await validation_file(file=image)

        content_type = image.content_type if image else ""
        file_extension = content_type.split('/')[1] if image else ""
        
        user_model = User(
            role_id=role_id,
            username=username,
            email=email,
            password=user_service.get_password_hash(password),
            name=name,
            gender=gender.value,            
        )

        data = user_service.create_user(
            user_model,
            image,
            file_extension,            
        )

    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))         
    
    status_code = status.HTTP_201_CREATED
    result = {
        'id': data.id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=result,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.get("", response_model=GeneralDataPaginateResponse, status_code=status.HTTP_200_OK)
def read_users(
    request: Request,
    role_ids: str = Query(None),
    role_id: str = Query(None),
    sort_by: str = Query(None),
    sort_order: str = Query(None),
    filter_by_column: str = Query(None),
    filter_value: str = Query(None),
    is_role_level: bool = Query(None),
    is_active: bool = Query(None),
    project_id: str = Query(None), 
    user_id: str = Query(None), 
    offset: int = Query(None, ge=1), 
    size: int = Query(None, ge=1),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read All User

        - need login
        - has leveling that show only user with range level
        - has subordinate that show only user on his subordinate if has subordinate is active

        - if has access to view it show all user
        - if has access to view and has subodirnate it show user on this subodirnate
        - if no has access to view it only show his user itself

        - only admin and leader
    """

    #cek role user
    user_id_active = payload.get("uid", None)
    user_service = UserService(db)
    user_active = user_service.user_repository.read_user(user_id_active)
    if not user_active or user_active.role.code not in ['ADM', 'USER',]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Anda Tidak Memiliki Hak Akses")

    base_url = str(request.base_url) if request else ""
    custom_filters = {filter_by_column: filter_value} if filter_by_column and filter_value else None
    
    if user_id:
        custom_filters = custom_filters or {}
        custom_filters['id'] = user_id

    users = user_service.user_repository.read_users(
        role_ids=role_ids,
        role_id=role_id, 
        offset=offset, 
        size=size, 
        sort_by=sort_by, 
        sort_order=sort_order, 
        custom_filters=custom_filters,
        # role_level=role_level,
        is_role_level=is_role_level,
        user_id=user_id,
        is_active=is_active,
        project_id=project_id,
    )

    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    count = user_service.user_repository.count_users(
        role_id=role_id, 
        custom_filters=custom_filters,
        # role_level=role_level,
        is_role_level=is_role_level,
        user_id=user_id,
        is_active=is_active,
        project_id=project_id,
    )
    total_pages = get_total_pages(size, count)
    

    datas = []
    for user in users:
        role = {
            'id': user.role.id,
            'name': user.role.name,
        } if user.role else {}
        datas.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'project_id': user.project_id,
            'is_active': user.is_active,
            'role': role,
            'project_id': user.project_id,
            'created_at': str(user.created_at),
            'updated_at': str(user.updated_at),
        })

    status_code = status.HTTP_200_OK
    data_response = GeneralDataPaginateResponse(
        code=status_code,
        status="OK",
        data=datas,
        meta={
            "size": size,
            "total": count,
            "total_pages": total_pages,
            "offset": offset
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.get("/{user_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def read_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read User

        - should login
        - only admin and leader
    """

    #cek role user
    user_id_active = payload.get("uid", None)
    user_service = UserService(db)
    user = user_service.user_repository.read_user(user_id_active)
    # if not user or user.role.code not in ['ADM', 'USER',]:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Anda Tidak Memiliki Hak Akses")

    user_service = UserService(db)
    base_url = str(request.base_url) if request else ""
    user = user_service.user_repository.read_user(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    role = {
        'id': user.role.id,
        'name': user.role.name,
        'is_active': user.role.is_active,
    } if user.role else {}

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data={
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': role,
            'is_active': user.is_active,
            'created_at': str(user.created_at),
            'updated_at': str(user.updated_at),
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.patch("/{user_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: str,
    role_id: str = Form(...),
    password: str = Form(None, min_length=8, max_length=50),
    username: str = Form(None, min_length=0, max_length=36),
    project_id: str = Form(None, min_length=0, max_length=36),
    email: str = Form(None, min_length=0, max_length=225),
    is_active: bool = Form(default=True),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Update User
        
        - should login
        - only admin and leader
        - leader just can edit/delete subordinate
    """

    # service
    # role_service = RoleService(db)
    user_service = UserService(db)

    user_id_active = payload.get("uid", None)
    user = user_service.user_repository.read_user(user_id_active)
    if not user or user.role.code not in ['ADM', 'CLN',]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Anda Tidak Memiliki Hak Akses")
    
    # validation
    # exist_role_id = role_service.role_repository.read_role(role_id)
    # if not exist_role_id:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    exist_user = user_service.user_repository.read_user(user_id)
    if not exist_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # Validasi tambahan untuk role CLN
    if user.role.code == 'CLN' and exist_user.project_id != user.project_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Anda Tidak Memiliki Hak Akses untuk edit user di proyek lain")
    
    try:

        if password:
            hashed_password = user_service.get_password_hash(password)
        else:
            hashed_password = exist_user.password 

        user_model = User(
            id=user_id,
            role_id=role_id,
            username=username,
            project_id=project_id,
            email=email,
            is_active=is_active,
            password=hashed_password,
        )


        data = user_service.update_user(
            exist_user,
            user_model,
        )

    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'id': data.id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.delete("/{user_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
): 
    """
        Delete User
        
        - should login
        - only admin and leader
    """
    # service
    user_service = UserService(db)    

    #cek role user
    user_id_active = payload.get("uid", None)
    user_service = UserService(db)
    user = user_service.user_repository.read_user(user_id_active)
    if not user or user.role.code not in ['ADM','CLN']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Anda Tidak Memiliki Hak Akses")
    
    exist_user = user_service.user_repository.read_user(user_id)
    if not exist_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Validasi tambahan untuk role CLN
    if user.role.code == 'CLN' and exist_user.project_id != user.project_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Anda Tidak Memiliki Hak Akses untuk menghapus user di proyek lain"
        )    
    
    try:
        user_service.delete_user(user_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'id': user_id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response