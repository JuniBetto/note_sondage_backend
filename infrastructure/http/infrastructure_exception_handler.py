from fastapi.responses import JSONResponse

from domain.exceptions.infrastructure_exception import InfrastructureException


def infrastructure_exception_handler(request, exc: InfrastructureException):
    return JSONResponse(
        status_code=500,
        content={
            "error": exc.code,
            "message": str(exc),
        }
    )
