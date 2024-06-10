from fastapi import Request
from fastapi.responses import JSONResponse

from routers.exceptions import NoNameFoundException, NoVATNumberFoundException


async def NoVATNumberFoundException_handler(request: Request, exc: NoVATNumberFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Subject with VAT '{exc.vat_number}' was not found."},
    )

async def NoNameFoundException_handler(request: Request, exc: NoNameFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Subjects with name '{exc.name}' were not found."},
    )
