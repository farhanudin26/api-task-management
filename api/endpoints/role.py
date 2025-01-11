from fastapi import APIRouter, Depends, Form, Query, Request, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from dtos.role.role import CreateRole, EditRole
from models.response import GeneralDataPaginateResponse, GeneralDataResponse
from models.role import Role
from services.role_service import RoleService
# from services.user.user_service import UserService
# from utils.authentication import Authentication
from services.user_service import UserService
from utils.authentication import Authentication
from utils.manual import get_total_pages

router = APIRouter()

def check_admin(user_service: UserService, user_id: str):
    user = user_service.user_repository.read_user(user_id)
    # if not user or user.role.code != 'ADM':
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can perform this action")

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: CreateRole,
    db: Session = Depends(get_db), 
    # payload = Depends(Authentication())
):
    """
        Create Role

        - should login
        - only admin
    """
    # user_id = payload.get("uid", None)

    # service
    user_service = UserService(db)
    role_service = RoleService(db)
    
    # check_admin(user_service)
    
    exist_code = role_service.role_repository.get_role_by_code(data.code)
    if exist_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code already exist")
    
    exist_name = role_service.role_repository.get_role_by_name(data.name)
    if exist_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name already exist")
    
    exist_id = role_service.role_repository.read_role(data.role_id)
    if exist_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Id already exist")
    
    try:
        role_model = Role(
            id=data.role_id,
            code=data.code,
            level=data.level,
            name=data.name,
            description=data.description,
        )

        data = role_service.role_repository.create_role(role_model)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    
    status_code = status.HTTP_201_CREATED
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

@router.get("", response_model=GeneralDataPaginateResponse, status_code=status.HTTP_200_OK)
def read_roles(
    offset: int = Query(None, ge=1), 
    size: int = Query(None, ge=1),
    is_active: bool = Query(None),
    level: int = Query(None),
    sort_by: str = Query(None),
    sort_order: str = Query(None),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read All Role

        - should login
        - filter role by level that user login
    """
    user_id = payload.get('uid', None)
    user_service = UserService(db)
    role_service = RoleService(db)
    check_admin(user_service, user_id)


    user = user_service.user_repository.read_user(user_id)
    level = user.role.level if user.role else None
    
    roles = role_service.role_repository.read_roles(
        offset=offset, 
        size=size,
        is_active=is_active,
        level=level,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    if not roles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    count = role_service.role_repository.count_roles(
        is_active=is_active, 
        level=level,
    )
    total_pages = get_total_pages(size, count)
    

    datas = []
    for role in roles:
        datas.append({
            'id': role.id,
            'code': role.code,
            'level': role.level,
            'name': role.name,
            'description': role.description,
            'is_active': role.is_active,
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

@router.get("/{role_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def read_role(
    role_id: str,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read Role

        - should login
    """
    
    user_id = payload.get('uid', None)

    role_service = RoleService(db)
    user_service = UserService(db)
    role = role_service.role_repository.read_role(role_id)
    check_admin(user_service, user_id)


    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data={
            'id': role.id,
            'code': role.code,
            'level': role.level,
            'name': role.name,
            'description': role.description,
            'is_active': role.is_active,
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

# @router.patch("/{role_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
# async def update_role(
#     role_id: str,
#     data: EditRole,
#     db: Session = Depends(get_db), 
#     payload = Depends(Authentication())
# ):
#     """
#         Update Role

#         - should login
#         - only admin
#     """
#     user_id = payload.get("uid", None)

#     # service
#     user_service = UserService(db)
#     role_service = RoleService(db)

#     check_admin(user_service, user_id)
    
#     # validation
#     exist_role = role_service.role_repository.read_role(role_id)
#     if not exist_role:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
#     try:
#         role_model = Role(
#             id=role_id,
#             code=data.code,
#             name=data.name,
#             level=data.level,
#             description=data.description,
#             is_active=data.is_active,
#         )

#         data = role_service.update_role(
#             exist_role,
#             role_model
#         )
#     except ValueError as error:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

#     status_code = status.HTTP_200_OK
#     data = {
#         'id': data.id,
#     }

#     data_response = GeneralDataResponse(
#         code=status_code,
#         status="OK",
#         data=data,
#     )
#     response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
#     return response

# @router.delete("/{role_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
# async def delete_role(
#     role_id: str,
#     db: Session = Depends(get_db), 
#     payload = Depends(Authentication())
# ):
#     """
#         Delete Role
        
#         If user still have using this role, throw bad request that should clear user with the selected role
#         - should login
#         - only admin
#     """
#     user_id = payload.get("uid", None)

#     # service
#     user_service = UserService(db)
#     role_service = RoleService(db)

#     check_admin(user_service, user_id)
    
#     # try:
#         # ganti jadi read data by user_id yang diambil hanya data pertama/first bukan semua
#     #     count_user = user_service.user_repository.count_users(role_id=role_id)
#     #     if count_user > 0:
#     #         raise ValueError("Clear user with this role before deleting this role")
#     #     role_service.delete_role(role_id)
#     # except ValueError as error:
#     #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    
#     existing_user = user_service.user_repository.read_user_by_role_id(role_id)
#     if existing_user:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete. User is in use user.")

#     status_code = status.HTTP_200_OK
#     data = {
#         'id': role_id,
#     }

#     data_response = GeneralDataResponse(
#         code=status_code,
#         status="OK",
#         data=data,
#     )
#     response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
#     return response
