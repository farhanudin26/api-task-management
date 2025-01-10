from sqlalchemy.orm import Session

from models.role import Role
from repositories.role_repository import RoleRepository

class RoleService:
    def __init__(self, db: Session):
        self.db = db
        self.role_repository = RoleRepository(db)

    def validation_unique_based_other_role(self, exist_role: Role, role: Role):
        if role.code:
            exist_code = self.role_repository.get_role_by_code(role.code)
            if exist_code and (exist_role.id != exist_code.id):
                raise ValueError('Code already used in other account')
            exist_role.code = role.code
        
        if role.name:
            exist_name = self.role_repository.get_role_by_name(role.name)
            if exist_name and (exist_role.id != exist_name.id):
                raise ValueError('Name already used in other account')
            exist_role.name = role.name
    
    def update_role(self, exist_role: Role, role: Role):
        self.validation_unique_based_other_role(exist_role, role)
        
        exist_role.level = role.level
        exist_role.description = role.description
        exist_role.is_active = role.is_active

        return self.role_repository.update_role(exist_role)
    
    def delete_role(self, role_id: str):
        role = self.role_repository.read_role(role_id)
        if not role:
            raise ValueError("Role not found")

        return self.role_repository.delete_role(role)