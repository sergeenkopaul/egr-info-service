from fastapi import FastAPI

from routers.subject_info import subject_info_router
from auth.routers import auth_router
from auth import models
from db.database import engine
from constants import BASE_URL_PREFIX
from logger import logger

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(subject_info_router, prefix=BASE_URL_PREFIX)
app.include_router(auth_router, prefix=BASE_URL_PREFIX)