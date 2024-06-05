import asyncio
from typing import Annotated

from fastapi import APIRouter, Path, HTTPException, Depends
from fastapi.responses import JSONResponse
from selenium.webdriver.support.wait import TimeoutException

from auth.dependencies import get_current_active_user
from auth.models import User
from info_getters.egr_info_getter import *
from info_getters.license_info_getter import LicenseInfoGetter
from logger import logger

subject_info_router = APIRouter()

@subject_info_router.get('/find_subject_by_vat_number/{vat_number}/')
async def find_subject_by_vat_number(
        user : Annotated[User, Depends(get_current_active_user)],
        vat_number : int = Path(ge=100000000, le=999999999)
    ):
    data = await asyncio.create_task(find_vat(vat_number))
    return JSONResponse({'data' : data})

@subject_info_router.get('/find_subjects_by_name/{name}')
async def find_subjects_by_name(
        user : Annotated[User, Depends(get_current_active_user)],
        name : str
    ):
    data = await asyncio.create_task(find_vat_by_name(name))
    return JSONResponse({'data' : data})

@subject_info_router.get('/get_full_info/{vat_number}/')
async def get_full_info(
        user : Annotated[User, Depends(get_current_active_user)],
        vat_number : int = Path(ge=100000000, le=999999999),
    ):
    data = await asyncio.create_task(get_full_info_about_subject(vat_number))
    return JSONResponse({'data' : data})

@subject_info_router.get('/get_base_info/{vat_number}/')
async def get_base_info(
    user : Annotated[User, Depends(get_current_active_user)],
    vat_number : int = Path(ge=100000000, le=999999999)
):
    data = await asyncio.create_task(get_base_info_about_subject(vat_number))
    return JSONResponse({'data' : data})    

@subject_info_router.get('/license_info/{vat_number}/')
async def get_license_info(
    user : Annotated[User, Depends(get_current_active_user)],
    vat_number : int = Path(ge=100000000, le=999999999)
):
    try:
        data = LicenseInfoGetter.get_info_about_license(vat_number)
        return data
    except TimeoutException:
        raise HTTPException(status_code=404, detail="Subject has no licenses.")
    except Exception as e:
        logger.exception(f"Information about license can't be retrieved: {e}", exc_info=True)   
        raise HTTPException(status_code=500, detail="Information about license can't be retrieved.")
    