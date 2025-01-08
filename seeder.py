from sqlalchemy import create_engine, text
from dotenv import dotenv_values
import bcrypt
import pandas as pd
from sqlalchemy.orm import sessionmaker, declarative_base
from passlib.context import CryptContext
from models.role import Role
from models.ticket_status import TicketStatus
from models.ticket_type import TicketType
from models.ticket import Ticket
from models.user import User
from services.user_service import UserService

config_env = dotenv_values()

engine = create_engine(config_env['DB'])
connection = engine.connect()

Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def fill_na_dataframe(df):
    # Fill NaN values with appropriate types using .loc
    for column in df.columns:
        if df[column].dtype == 'object':  # For string/object columns
            df.loc[df[column].isna(), column] = ''  # Fill NaN with empty string
        elif df[column].dtype in ['float64', 'int64']:  # For numeric columns
            df.loc[df[column].isna(), column] = 0  # Fill NaN with 0
    return df

def ticket_status_seeder(url):
    df = pd.read_excel(url, dtype={'id': str}, engine='openpyxl', sheet_name='ticket_status')
    # Fill NaN values with appropriate types using .loc
    df = fill_na_dataframe(df)
    for index, row in df.iterrows():
        try:
            data_id = str(row['id'])
            title = str(row['title'])
            description = str(row['description'])
            is_active = row['is_active']

            # check data
            exist_data = session.query(TicketStatus).filter_by(id=data_id).first()
            if not exist_data: # create
                new_data = TicketStatus(
                    id=data_id,
                    title=title,
                    description=description,
                    is_active=is_active,
                )
                session.add(new_data)
                print(f"created {data_id} ")
            else: # update
                exist_data.title = title
                exist_data.description = description
                exist_data.is_active = is_active
                print(f"updated {data_id} ")
            session.commit()
        except Exception as e:
           print(f"Error processing data: {str(e)}")

def ticket_type_seeder(url):
    df = pd.read_excel(url, dtype={'id': str}, engine='openpyxl', sheet_name='ticket_type')
    # Fill NaN values with appropriate types using .loc
    df = fill_na_dataframe(df)
    for index, row in df.iterrows():
        try:
            data_id = str(row['id'])
            title = str(row['title'])
            description = str(row['description'])
            is_active = row['is_active']

            # check data
            exist_data = session.query(TicketType).filter_by(id=data_id).first()
            if not exist_data: # create
                new_data = TicketType(
                    id=data_id,
                    title=title,
                    is_active=is_active,
                    description=description,
                )
                session.add(new_data)
                print(f"created {data_id} ")
            else: # update
                exist_data.title = title
                exist_data.description = description
                exist_data.is_active = is_active
                print(f"updated {data_id} ")
            session.commit()
        except Exception as e:
           print(f"Error processing data: {str(e)}")
           
def role_seeder(url):
    df = pd.read_excel(url, dtype={'id': str}, engine='openpyxl', sheet_name='role')
    # Fill NaN values with appropriate types using .loc
    df = fill_na_dataframe(df)
    for index, row in df.iterrows():
        try:
            data_id = str(row['id'])
            code = str(row['code'])
            level = int(row['level'])
            name = str(row['name'])
            is_active = row['is_active']
            description = str(row['description'])

            # check data
            exist_data = session.query(Role).filter_by(id=data_id).first()
            if not exist_data: # create
                new_data = Role(
                    id=data_id,
                    code=code,
                    level=level,
                    name=name,
                    description=description,
                    is_active=is_active,
                )
                session.add(new_data)
                print(f"created {data_id} ")
            else: # update
                exist_data.code = code
                exist_data.level = level
                exist_data.name = name
                exist_data.is_active = is_active
                exist_data.description = description
                print(f"updated {data_id} ")
            session.commit()
        except Exception as e:
           print(f"Error processing data: {str(e)}")
           
def user_seeder(url):
    df = pd.read_excel(url, dtype={'id': str}, engine='openpyxl', sheet_name='user')
    # Fill NaN values with appropriate types using .loc
    df = fill_na_dataframe(df)
    for index, row in df.iterrows():
        try:
            user_id = str(row['id'])
            username = str(row['username'])
            email = str(row['email'])
            is_active = row['is_active']
            role_id = str(row['role_id'])
            password = str(row['password'])
            project_id = str(row['project_id'])

            user_service = UserService(session)

            # check data
            exist_data = session.query(User).filter_by(id=user_id).first()
            if not exist_data: # create
                new_data = User(
                    id=user_id,
                    username=username,
                    email=email,
                    is_active=is_active,
                    role_id=role_id,
                    project_id=project_id,
                    password=user_service.get_password_hash(password),
                )
                session.add(new_data)
                print(f"created {user_id} ")
            else: # update
                exist_data.username = username
                exist_data.email = email
                exist_data.is_active = is_active
                exist_data.role_id = role_id
                exist_data.project_id = project_id
                exist_data.password = user_service.get_password_hash(password)
                print(f"updated {user_id} ")
            session.commit()
        except Exception as e:
           print(f"Error processing data: {str(e)}")
           
url = 'seed_data.xlsx'
# customize dummy
print("MASTER DATA :")

print("ROLE")
role_seeder(url)
print("USER")
user_seeder(url)
print("ticket_status")
ticket_status_seeder(url)
print("ticket_type")
ticket_type_seeder(url)
