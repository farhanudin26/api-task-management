import uuid
from sqlalchemy import Integer, asc, desc, func, or_
from sqlalchemy.orm import Session, aliased
# from models.role import Role
from models.user import User
# from constant import CategoryEmployee, ProjectStatus

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_name_by_id(self, user_id: str) -> str:
        # Query untuk mendapatkan user berdasarkan user_id
        user = self.db.query(User).filter(User.id == user_id).first()
        return user.username

    def read_all_users(self, is_active: bool = None, user_id_filter=None, offset: int = None, size: int = None):
        query = self.db.query(User).order_by(asc(User.username))
        
        if user_id_filter:
            query = query.filter(User.id.in_(user_id_filter))

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        # Apply pagination
        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        users = query.all()

        return users

    def read_user_by_role_id(self, role_id: str):
        return self.db.query(User).filter(User.role_id == role_id).first()

    def create_user(self, user: User):
        if user.is_active is None:
            user.is_active = True
        user.id = str(uuid.uuid4())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_username(self, username: str) -> User:
        return self.db.query(User).filter(User.username == username).first()
   
    def get_user_by_credential(self, username_or_email: str) -> User:
        return self.db.query(User).filter(or_(User.username.ilike(username_or_email), User.email.ilike(username_or_email))).first()

    def get_user_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()
    
    def read_users(
        self,
        role_ids: str = None,  
        role_id: str = None, 
        sort_by: str = None, 
        sort_order: str = 'asc', 
        custom_filters: dict = None,
        offset: int = None, 
        size: int = None,
        is_role_level: bool = False,
        role_level: int = None,
        user_id: str = None,
        is_active: bool = None,
    ) -> list[User]:
        query = self.db.query(User)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(User, sort_by):
                query = query.order_by(asc(getattr(User, sort_by)))
            elif sort_order == 'desc' and hasattr(User, sort_by):
                query = query.order_by(desc(getattr(User, sort_by)))

        if role_ids is not None:
            if isinstance(role_ids, str):
                # Pecah string berdasarkan koma dan hapus spasi ekstra
                role_ids = [role.strip() for role in role_ids.split(',')]
            query = query.filter(User.role_id.in_(role_ids))  # Pastikan role_id sesuai dengan kolom pada model

        if role_id is not None:
            query = query.filter(User.role_id == role_id)

        # if is_role_level and role_level is not None:
        #     query = query.filter(User.role.has(Role.level >= role_level))
        
        if user_id is not None:
            query = query.filter(User.id == user_id)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(User, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(User, column) == value)

        # Pagination
        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all()
    
    def update_user(self, user: User):
        self.db.commit()
        return user
    
    def count_users(
        self, 
        role_ids: str = None, 
        role_id: str = None, 
        custom_filters: dict = None,
        is_role_level: bool = False,
        role_level: int = None,
        is_active: bool = None,
        user_id: str = None,
    ) -> int:
        query = self.db.query(User)
        
        if role_id is not None:
            query = query.filter(User.role_id == role_id)
            
            
        # Filter berdasarkan role_ids jika ada
        if role_ids:
            query = query.filter(User.role_id.in_(role_ids.split(',')))

        # if is_role_level and role_level is not None:
        #     query = query.filter(User.role.has(Role.level >= role_level))

        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        if user_id is not None:
            query = query.filter(User.id == user_id)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(User, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(User, column) == value)

        return query.count()

    def read_user(self, id: str) -> User:
        user = self.db.query(User).filter(User.id == id).first()
        return user

    def delete_user(self, user: User) -> str:
        user_id = user.id
        self.db.delete(user)
        self.db.commit()
        return user_id
    
    def gender_validation(self, gender: str) -> bool:
        valid_gender = ['male', 'female', None] 
        return gender in valid_gender
