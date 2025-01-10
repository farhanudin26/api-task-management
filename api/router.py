from fastapi import APIRouter

from api.endpoints import auth,user,role

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Auth"])

router.include_router(role.router, prefix="/role", tags=["Role"])
router.include_router(user.router, prefix="/user", tags=["User"])






