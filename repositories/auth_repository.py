import sqlalchemy as sa
from sqlalchemy.orm import Session
from models.user import User
# from models.user.user_tokens import UserToken
from utils.generate_access_token import generate_access_token
from utils.generate_refresh_token import generate_refresh_token

class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def auth_login(self, user: User, is_password_valid: bool):
        if is_password_valid:
            # add payload
            payload = {
                'uid': user.id,
                'username': user.username,
                # 'role_code': user.role.code if user.role else "",
            }
            # generate refresh_token
            refresh_token = generate_refresh_token(payload)
            # generate access token and access token expired
            access_token, access_token_expired_at = generate_access_token(payload)

            # saving data of refresh token
            ## COMING SOON

            return {
                'user_id': user.id,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'access_token_expired_at': access_token_expired_at,
            }

        else:
            raise ValueError("Password invalid")
        
    # def create_reset_password_token(self, email: str, reset_code: str, session: Session):
    #     try:
    #         # Check if there's an existing active reset token for this email
    #         existing_token = session.query(UserToken).filter(
    #             UserToken.email == email,
    #             UserToken.status == '1'
    #         ).first()

    #         if existing_token:
    #             # Update the existing token
    #             existing_token.reset_code = reset_code
    #             existing_token.expired_in = sa.func.date_add(sa.func.now(), sa.text("INTERVAL 10 MINUTE"))
    #             existing_token.created_at = sa.func.now()
    #             logging.info("Reset token updated successfully")
    #         else:
    #             # Create a new reset token
    #             new_user_token = UserToken(
    #                 email=email, 
    #                 reset_code=reset_code, 
    #                 status='1', 
    #                 expired_in=sa.func.date_add(sa.func.now(), sa.text("INTERVAL 10 MINUTE")),
    #                 created_at=sa.func.now()
    #             )
    #             session.add(new_user_token)
    #             logging.info("New reset token created successfully")
            
    #         session.commit()
    #         return existing_token if existing_token else new_user_token
    #     except Exception as e:
    #         session.rollback()
    #         logging.error("Error in creating/updating reset token: %s", e)
    #         raise e
        
    # def reset_password_token(self, reset_password_token: str):
    #     user_token = self.db.query(UserToken).filter(
    #         UserToken.status == '1',
    #         UserToken.reset_code == reset_password_token,
    #         UserToken.expired_in >= sa.func.now()
    #     ).first()
    #     return user_token

    # def delete_user_token(self, reset_password_token: str, email: str):
    #     try:
    #         user_token = self.db.query(UserToken).filter(
    #             UserToken.status == '1',
    #             UserToken.reset_code == reset_password_token,
    #             UserToken.email == email
    #         ).first()
    #         if user_token:
    #             self.db.delete(user_token)
    #             self.db.commit()
    #     except Exception as e:
    #         self.db.rollback()
    #         logging.error("Error disabling reset user token: %s", e)
    #         raise e

