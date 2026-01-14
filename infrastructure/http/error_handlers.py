# infrastructure/http/error_handlers.py
from fastapi import Request
from fastapi.responses import JSONResponse

from domain.exceptions.domain_exception import DomainException



def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.code,
            "message": str(exc),
        },
    )
