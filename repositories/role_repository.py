from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from models.role import Role
from models.user import User 

class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_role(self, role: Role):
        role.is_active = 0
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def get_role_by_code(self, code: str) -> Role:
        return self.db.query(Role).filter(Role.code == code).first()

    def get_role_by_name(self, name: str) -> Role:
        return self.db.query(Role).filter(Role.name == name).first()

    def read_roles(
        self, 
        offset: int = None, 
        size: int = None,
        is_active: bool = None,
        level: int = None,
        sort_by: str = None, 
        sort_order: str = 'asc', 
    ) -> list[Role]:
        query = self.db.query(Role)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(Role, sort_by):
                query = query.order_by(asc(getattr(Role, sort_by)))
            elif sort_order == 'desc' and hasattr(Role, sort_by):
                query = query.order_by(desc(getattr(Role, sort_by)))

        if is_active is not None:
            query = query.filter(Role.is_active == is_active)

        if level is not None:
            query = query.filter(Role.level >= level)

        # Pagination
        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all()
    
    def count_roles(
        self, 
        is_active: bool = None,
        level: int = None,
    ) -> int:
        query = self.db.query(Role)

        if is_active is not None:
            query = query.filter(Role.is_active == is_active)

        if level is not None:
            query = query.filter(Role.level >= level)

        return query.count()

    def update_role(self, role: Role):
        self.db.commit()
        return role

    def read_role(self, id: str) -> Role:
        role = self.db.query(Role).filter(Role.id == id).first()
        return role

    def delete_role(self, role: Role) -> int:
        role_id = role.id
        self.db.delete(role)
        self.db.commit()
        return role_id