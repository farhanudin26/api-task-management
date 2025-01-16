from fastapi import APIRouter

from api.endpoints import auth,user,role,task_management

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Auth"])

router.include_router(role.router, prefix="/role", tags=["Role"])
router.include_router(task_management.router, prefix="/task_management", tags=["Task Management"])
router.include_router(user.router, prefix="/user", tags=["User"])






