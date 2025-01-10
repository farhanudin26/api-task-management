# import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, Form, Request, UploadFile, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
# from config import send_email
from database import get_db
from dtos.auth import AuthLogin, AuthProfilePassword, EmailSchema, ResetPassword
from models.response import AuthResponse, GeneralDataResponse
from models.user import User
from services.auth_service import AuthService
from services.user_service import UserService
from utils.authentication import Authentication
from utils.handling_file import validation_file
from typing import Optional
from config import config
# from utils.rare_limiter import apply_rate_limit
from utils.generate_sensitive import decrypt_value, encrypt_value

router = APIRouter()

@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def auth_login(auth_login: AuthLogin, db: Session = Depends(get_db)):
    """
        Login user dengan rate limiting
    """
    # Logika login tetap
    auth_service = AuthService(db)

    try:
        user = auth_service.auth_login(auth_login)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    user_id = user.get('user_id', None)
    access_token = user.get('access_token', None)
    refresh_token = user.get('refresh_token', None)
    expired_at = user.get('access_token_expired_at', None)
    status_code = status.HTTP_200_OK

    auth_response = AuthResponse(
        code=status_code,
        status="OK",
        data={
            'id': user_id,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expired_at': expired_at
        },
    )
    response = JSONResponse(content=auth_response.model_dump(), status_code=status_code)


    # Set the JWT token in a cookie
    # is_development = config.STAGE == "development"
    # response.set_cookie(
    #     key="access_token", 
    #     value=access_token, 
    #     httponly=False if is_development else True,  # Prevent JavaScript access to the cookie
    #     secure=False if is_development else True,    # Send over HTTPS only
    #     samesite="Lax" if is_development else "None" ,  # Or None if on different domains
    #     max_age=expired_at * 60
    # )

    return response

@router.get("/profile", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def auth_profile(
    request: Request, 
    db: Session = Depends(get_db),  
    payload = Depends(Authentication())):
    """
        Profile user dengan rate limiting
    """
    # # Gunakan username_or_email sebagai kunci untuk rate limiting
    # rate_limit_response = apply_rate_limit(payload.get("uid", ""))  # Gunakan uid dari payload untuk rate limit
    # if rate_limit_response:
    #     return rate_limit_response

    user_service = UserService(db)
    
    user_id = payload.get("uid", None)
    base_url = str(request.base_url) if request else ""

    user = user_service.user_repository.read_user(user_id)

    # if not user_additional:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    
    status_code = status.HTTP_200_OK

    role_data = {
        'id': user.role.id,
        'code': user.role.code,
        'name': user.role.name,
    } if user.role else {}
    
    project_data = {
        'id': user.project_id,
    } if user else {}

    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': role_data,
        'project': project_data,
    }

    auth_response = AuthResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=auth_response.model_dump(), status_code=status_code)
    return response


@router.patch("/profile", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def auth_update_profile(
    username: str = Form(None, min_length=0, max_length=36),
    email: str = Form(None, min_length=0, max_length=36),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    # # Gunakan uid sebagai kunci untuk rate limiting
    # rate_limit_response = apply_rate_limit(payload.get("uid", ""))  # Gunakan uid untuk rate limit
    # if rate_limit_response:
    #     return rate_limit_response

    # Get service
    user_id = payload.get("uid", None)
    user_service = UserService(db)

    # Check if user exists
    exist_user = user_service.user_repository.read_user(user_id)
    if not exist_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    

    try:

        # Update the user model
        role_id = exist_user.role_id
        is_active = exist_user.is_active

        user_model = User(
            id=user_id,
            role_id=role_id,
            username=username,
            email=email,
            is_active=is_active,
        )

        # Update user profile
        data = user_service.update_user(
            exist_user,
            user_model,
        )

    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    # Prepare response data
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


@router.put("/profile/password", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def auth_update_profile(
    auth_profile_password: AuthProfilePassword,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    # # Gunakan uid sebagai kunci untuk rate limiting
    # rate_limit_response = apply_rate_limit(payload.get("uid", ""))  # Gunakan uid untuk rate limit
    # if rate_limit_response:
    #     return rate_limit_response

    # get service
    user_id = payload.get("uid", None)
    user_service = UserService(db)
    
    exist_user = user_service.user_repository.read_user(user_id)
    if not exist_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    is_password_valid = user_service.verify_password(auth_profile_password.old_password, exist_user.password)
    if not is_password_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is not valid")
    
    if auth_profile_password.confirm_new_password != auth_profile_password.new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password and confirm new password are not the same")
    
    new_password = user_service.get_password_hash(auth_profile_password.new_password)
    
    user_model = User(
        id=user_id,
        password=new_password,
    )
    try:
        data = user_service.update_user_password(
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

@router.post("/register", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def register(
    role_id: str = Form(...),
    username: str = Form(..., min_length=1, max_length=36),
    name: str = Form(..., min_length=1, max_length=225),
    email: str = Form(..., min_length=1, max_length=225),
    password: str = Form(..., min_length=1, max_length=512),
    db: Session = Depends(get_db), 
):  
    """
        Create User

        - should login

        - create this user to subordinate if user that login has subordinate access
        - only admin and leader
    """
    # service
    # role_service = RoleService(db)
    user_service = UserService(db)

    # cek role user
    # user_id_active = payload.get("uid", None)
    # user_active = user_service.user_repository.read_user(user_id_active)
    # if not user_active or user_active.role.code not in ['ADM', 'CLN']:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Anda Tidak Memiliki Hak Akses"
    #     )
    
    # validation
    # exist_role_id = role_service.role_repository.read_role(role_id)
    # if not exist_role_id:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    exist_username = user_service.user_repository.get_user_by_username(username)
    if exist_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exist")
    
    exist_email = user_service.user_repository.get_user_by_email(email)
    if exist_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exist")
    
    try:

        user_model = User(
            role_id=role_id,
            username=username,
            name=name,
            email=email,
            password=user_service.get_password_hash(password),

        )

        data = user_service.create_user(
            user_model,
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

# @router.get("/check_confirmation_user", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
# def check_confirmation_user(
#     db: Session = Depends(get_db),  
#     payload = Depends(Authentication())
# ):
#     """
#         Check user confirmation based on category_employee
#     """
#     # # Gunakan uid sebagai kunci untuk rate limiting
#     # rate_limit_response = apply_rate_limit(payload.get("uid", ""))  # Gunakan uid untuk rate limit
#     # if rate_limit_response:
#     #     return rate_limit_response

#     user_service = UserService(db)
#     user_additional_service = UserAdditionalService(db)

#     # Get logged in user's ID
#     user_id = payload.get("uid", None)
    
#     # Retrieve user information
#     user = user_service.user_repository.read_user(user_id)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

#     # Check category_employee
#     category_employee = user.category_employee
#     if category_employee in ["Magang S1/S2", "PKL SMK"]:
#         data_response = GeneralDataResponse(
#             code=status.HTTP_200_OK,
#             status="valid_confirmation",
#             data={}
#         )
#         return JSONResponse(content=data_response.model_dump(), status_code=status.HTTP_200_OK)

#     # Retrieve user additional information
#     additional_info = user_additional_service.user_additional_repository.read_user_additional_by_user_id(user_id)
    
#     required_fields = ['menikah', 'bpjs_kes', 'bpjs_tk', 'total_children', 'wp_gabung']
#     for field in required_fields:
#         value = getattr(additional_info, field, None)
        
#         # Cek apakah field null (None)
#         if value is None:
#             data_response = GeneralDataResponse(
#                 code=status.HTTP_400_BAD_REQUEST,
#                 status="need_more_register",
#                 data={}
#             )
#             return JSONResponse(content=data_response.model_dump(), status_code=status.HTTP_400_BAD_REQUEST)

#     # If all required fields are filled
#     data_response = GeneralDataResponse(
#         code=status.HTTP_200_OK,
#         status="valid_confirmation",
#         data={}
#     )
# return JSONResponse(content=data_response.model_dump(), status_code=status.HTTP_200_OK)


# @router.post("/forgot-password", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
# async def auth_forgot_password(data: EmailSchema, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
#     """
#     Auth forgot password
#     """
#     user_service = UserService(db)
#     auth_service = AuthService(db)
    
#     user = user_service.user_repository.get_user_by_email(data.email)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
#     reset_code = str(uuid.uuid1())
#     auth_service.auth_repository.create_reset_password_token(data.email, reset_code, db)
    
#     subject = "Reset Password Request"
#     recipient = [data.email]
#     message = f"""
#     <p>Hi,</p>
#     <p>You received this email, because you request to reset your password.</p>
#     <p>This is your token code adalah: <strong>{reset_code}</strong></p>
#     <p>Use this token code to regenerate new password. This code will expired in 10 minutes.</p>
#     <p>If you not request to forgot password, ignore this email.</p>
#     <p>Thanks,</p>
#     <p></p>
#     """

#     background_tasks.add_task(
#         send_email, 
#         subject=subject, 
#         recipient=recipient, 
#         message=message
#     )

#     status_code = status.HTTP_200_OK
#     data = {
#         'message':  "Your token will be send to email",
#     }

#     data_response = GeneralDataResponse(
#         code=status_code,
#         status="OK",
#         data=data,
#     )
#     response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
#     return response

# @router.patch('/reset-password', response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
# async def auth_reset_password(request: ResetPassword, db: Session = Depends(get_db)):
#     """
#         Auth Reset Password
#     """
#     auth_service = AuthService(db)
#     user_service = UserService(db)
    
#     reset_token = auth_service.auth_repository.reset_password_token(request.reset_password_token)
#     if not reset_token:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset password not found or already expired, send new request to reset password")
    
#     if request.new_password != request.confirm_new_password:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password not match")
    
#     new_hashed_password = user_service.get_password_hash(request.new_password)

#     user = user_service.user_repository.get_user_by_email(reset_token.email)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

#     user.password = new_hashed_password
#     db.commit()
    
#     auth_service.auth_repository.delete_user_token(request.reset_password_token, reset_token.email)

#     status_code = status.HTTP_200_OK
#     data = {
#         'message':  "Password reset successful",
#     }

#     data_response = GeneralDataResponse(
#         code=status_code,
#         status="OK",
#         data=data,
#     )
#     response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
#     return response

# @router.post("/refresh-token", response_model=AuthResponse, status_code=status.HTTP_200_OK)
# def auth_refresh_token(db: Session = Depends(get_db)):
#     """
#         Refresh token user

#         COMING SOON
#     """
#     pass

# @router.post("/logout", response_model=AuthResponse, status_code=status.HTTP_200_OK)
# def auth_logout(db: Session = Depends(get_db)):
#     """
#         Logout user

#         COMING SOON
#         - refer with saving refresh token
#     """
#     pass


