from datetime import date, datetime
from fastapi import APIRouter, Depends, Form, Query, status, HTTPException, Response, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import insert
from database import get_db
from models.response import GeneralDataPaginateResponse, GeneralDataResponse
# from services.user.user_group_service import UserGroupService
from models.task_management import TaskManagement
from repositories.task_management_repository import TaskManagementRepository
from services.task_management_service import TaskManagementRepository, TaskManagementService
from services.user_service import UserService
from utils.authentication import Authentication
from utils.manual import get_total_pages
import os
from typing import Optional, List
# from models.project import Project
# from models.user.user_group import UserGroup
from io import BytesIO
from openpyxl.utils import get_column_letter
# from openpyxl import load_workbook
# from openpyxl.styles import Font, PatternFill, Alignment
import pandas as pd
import math
router = APIRouter()

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
def create_task_management(
    task_management: str = Form(..., min_length=1, max_length=256),
    description: Optional[str] = Form(None, min_length=0, max_length=512),
    date: str = Form(...),
    db: Session = Depends(get_db),
    payload=Depends(Authentication())
):
    """
    Membuat Tugas harian
    """

    user_id_active = payload.get("uid", None)

    user_service = UserService(db)
    task_management_service = TaskManagementService(db)  # Buat instance dengan db
    user_active = user_service.user_repository.read_user(user_id_active)

    try:
        # Buat instance TaskManagement
        task_management_model = TaskManagement(
            user_id=user_active.id,  # Pastikan ini adalah ID, bukan objek
            task_management=task_management,
            description=description,
            date=date,
            priority=False,
        )
        # Panggil method pada instance task_management_service
        task_management = task_management_service.create_task_management(task_management=task_management_model)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    result = {
        'id': task_management.id,
    }
    data_response = GeneralDataResponse(
        code=status.HTTP_201_CREATED,
        status="OK",
        data=result,
    )
    return data_response

# @router.get("", response_model=GeneralDataPaginateResponse, status_code=status.HTTP_200_OK)
# def read_tasks(
#     assign_at: Optional[date] = Query(None),
#     sort_by: Optional[str] = Query(None),
#     sort_order: Optional[str] = Query(None),
#     filter_by_column: Optional[str] = Query(None),
#     filter_value: Optional[str] = Query(None),
#     project_id: Optional[str] = Query(None),
#     user_id: Optional[str] = Query(None),
#     year: Optional[int] = Query(None),
#     month: Optional[int] = Query(None),
#     day: Optional[int] = Query(None),
#     offset: Optional[int] = Query(None, ge=1), 
#     size: Optional[int] = Query(None, ge=1),
#     include_subordinates: bool = Query(False),
#     db: Session = Depends(get_db), 
#     payload = Depends(Authentication())
# ):
#     """
#     Read All Tasks or Task by Date

#     - need login
#     """
#     user_id_active = payload.get("uid", None)
#     user_role = payload.get("role", None)

#     # Services
#     task_service = TaskManagementService(db)
#     user_service = UserService(db)

#     custom_filters = {filter_by_column: filter_value} if filter_by_column and filter_value else {}
#     user_active = user_service.user_repository.read_user(user_id_active)

#     if user_active.role.code == 'EMPLOYEE':
#         custom_filters['user_id'] = user_id_active
#     elif user_active.role.code == 'LEAD':
#         subordinate_ids = user_service.get_subordinates(user_id_active)
#         if include_subordinates:
#             custom_filters['user_id'] = {'$in': [user_id_active] + subordinate_ids}
#         else:
#             custom_filters['user_id'] = user_id_active
#     elif user_active.role.code == 'ADM':
#         if include_subordinates:
#             custom_filters.pop('user_id', None)  # Admin can see all tasks
#         else:
#             custom_filters['user_id'] = user_id_active
#     else:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to view data")
    
#     # Fetch tasks based on the filters and date
#     tasks = task_service.read_tasks(
#         sort_by=sort_by,
#         sort_order=sort_order,
#         custom_filters=custom_filters,
#         offset=offset,
#         size=size,
#         project_id=project_id,
#         user_id=user_id,
#         year=year,
#         month=month,
#         day=day,
#     )  

#     if not tasks:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

#     # Prepare data for the response
#     datas = []
#     for task in tasks:
#         user = {
#             'id': task.user.id,
#             'name': task.user.name,
#         } if task.user else {}
#         project = {
#             'id': task.project.id,
#             'title': task.project.title,
#             'category': task.project.category,
#         } if task.project else {}
#         datas.append({
#             'id': task.id,
#             'user': user,
#             'project': project,
#             'title': task.title,
#             'description': task.description,
#             'total_hour': round(task.total_hour, 2),
#             'assign_at': str(task.assign_at),
#             'created_at': str(task.created_at),
#             'updated_at': str(task.updated_at),
#         })

#     # Prepare metadata
#     meta = {}
    
#     count = task_service.task_repository.count_tasks(
#         custom_filters=custom_filters,
#         project_id=project_id,
#         user_id=user_id,
#         year=year,
#         month=month,
#         day=day,
#     )

#     total_pages = get_total_pages(size, count)
#     meta = {
#         "size": size,
#         "total": count,
#         "total_pages": total_pages,
#         "offset": offset,
#         "start_date": '',
#         "end_date": '',
#     }

#     # Add start and end date to meta if year and month are provided
#     if year and month:
#         period = task_service.task_repository.get_period_by_year_and_month(year, month)
#         if period:
#             meta["start_date"] = str(period.start_at)
#             meta["end_date"] = str(period.end_at)

#     # Prepare response
#     status_code = status.HTTP_200_OK
#     data_response = GeneralDataPaginateResponse(
#         code=status_code,
#         status="OK",
#         data=datas,
#         meta=meta,
#     )
#     response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
#     return response

# @router.get("/{task_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
# def read_task(
#     task_id: int,
#     db: Session = Depends(get_db), 
#     payload = Depends(Authentication())
# ):
#     """
#         Read Task

#         - should login

#     """
#     user_id_active = payload.get("uid", None)

#     # service
#     user_service = UserService(db)
#     task_service = TaskService(db)
    
#     user_active = user_service.user_repository.read_user(user_id_active)

#     task = task_service.task_repository.read_task(task_id)

#     if not task:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    
#     user = {
#         'id': task.user.id,
#         'name': task.user.name,
#     } if task.user else {}
#     project = {
#         'id': task.project.id,
#         'title': task.project.title,
#         'category': task.project.category,
#     } if task.project else {}

#     status_code = status.HTTP_200_OK
#     data_response = GeneralDataResponse(
#         code=status_code,
#         status="OK",
#         data={
#             'id': task.id,
#             'user': user,
#             'project': project,
#             'title': task.title,
#             'description': task.description,
#             'total_hour': task.total_hour,
#             'assign_at': str(task.assign_at),
#             'created_at': str(task.created_at),
#             'updated_at': str(task.updated_at),
#         },
#     )
#     response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
#     return response

# @router.patch("/{task_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
# async def update_task(
#     task_id: int,
#     project_id: str = Form(None, min_length=1, max_length=36),
#     title: str = Form(..., min_length=1, max_length=256),
#     assign_at: date = Form(...),
#     total_hour: float = Form(...),
#     description: str = Form(None, min_length=0, max_length=512),
#     db: Session = Depends(get_db), 
#     payload = Depends(Authentication())
# ):
#     """
#     Update Task

#     - should login
#     """
#     user_id_active = payload.get("uid", None)

#     user_service = UserService(db)
#     project_service = ProjectService(db)
#     task_service = TaskService(db)
#     permission_service = PermissionService(db)
#     paid_leave_service = PaidLeaveService(db)
    
#     user_active = user_service.user_repository.read_user(user_id_active)

#     exist_task = task_service.task_repository.read_task(task_id)
#     if not exist_task:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
#     exist_project = project_service.project_repository.read_project(project_id)
#     if not exist_project:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
#     user_task_owner = user_service.user_repository.read_user(exist_task.user_id)

#     if user_active.role.code == 'EMPLOYEE' and user_active.id != exist_task.user_id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update others' task")
    
#     if user_active.role.code == 'LEAD':
#         if user_active.id != exist_task.user_id and not user_service.is_subordinate(exist_task.user_id, user_active.id):
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update this task")
    
#     if user_active.role.code != 'ADM' and user_task_owner.role.code == 'ADM':
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update admin's task")
    
#     if total_hour <= 0:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Total jam harus lebih dari 0"
#         )

#     # Menghitung total jam pada tanggal yang sama (tidak termasuk task saat ini)
#     total_hours_on_date = task_service.task_repository.sum_total_hour_tasks(
#         user_id=exist_task.user_id,
#         assign_at=assign_at
#     ) - exist_task.total_hour + total_hour

#     if total_hours_on_date > 24:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Total jam pada tanggal yang sama melebihi 24 jam"
#         )

#     # Validasi Paid Leave yang tumpang tindih
#     overlapping_paid_leaves = paid_leave_service.paid_leave_repository.read_paid_leaves_between(
#         user_id=exist_task.user_id,
#         start_at=assign_at,
#         end_at=assign_at,
#         status=[PaidLeaveStatus.pending.value, PaidLeaveStatus.approved.value]
#     )
#     if overlapping_paid_leaves:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Tidak dapat membuat tugas pada tanggal ini karena terdapat Paid Leave yang masih pending atau sudah disetujui"
#         )

#     # Validasi Permission yang tumpang tindih
#     overlapping_permissions = permission_service.permission_repository.read_permissions_between(
#         user_id=exist_task.user_id,
#         start_at=assign_at,
#         end_at=assign_at,
#         status=[PermissionStatus.pending.value, PermissionStatus.approved.value]
#     )
#     if overlapping_permissions:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Tidak dapat membuat tugas pada tanggal ini karena terdapat Permission yang masih pending atau sudah disetujui"
#         )
        
#     try:
#         # Update task data
#         updated_task = Task(
#             project_id=project_id,
#             title=title,
#             assign_at=assign_at,
#             total_hour=total_hour,
#             description=description
#         )
#         data = task_service.update_task(
#             exist_task=exist_task,
#             task=updated_task
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

# @router.delete("/{task_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
# async def delete_task(
#     task_id: int,
#     db: Session = Depends(get_db), 
#     payload = Depends(Authentication())
# ):
#     """
#         Delete Task
        
#         - harus login
#     """
#     user_id_active = payload.get("uid", None)

#     user_service = UserService(db)
#     task_service = TaskService(db)
    
#     user_active = user_service.user_repository.read_user(user_id_active)
#     exist_task = task_service.task_repository.read_task(task_id)

#     if not exist_task:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task tidak ditemukan")
    
#     user_task_owner = user_service.user_repository.read_user(exist_task.user_id)

#     if user_active.role.code == 'EMPLOYEE' and user_active.id != exist_task.user_id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tidak diizinkan untuk menghapus task orang lain")
    
#     if user_active.role.code == 'LEAD':
#         if user_active.id != exist_task.user_id and not user_service.is_subordinate(exist_task.user_id, user_active.id):
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tidak diizinkan untuk menghapus task ini")
    
#     if user_active.role.code != 'ADM' and user_task_owner.role.code == 'ADM':
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tidak diizinkan untuk menghapus task admin")
    
#     try:
#         task_service.task_repository.delete_task(exist_task)
#         db.commit()
#     except Exception as error:
#         db.rollback()
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

#     status_code = status.HTTP_200_OK
#     data = {
#         'id': task_id,
#     }

#     data_response = GeneralDataResponse(
#         code=status_code,
#         status="OK",
#         data=data,
#     )
#     response = JSONResponse(content=data_response.dict(), status_code=status_code)
#     return response
