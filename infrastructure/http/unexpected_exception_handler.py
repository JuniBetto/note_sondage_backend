from fastapi.responses import JSONResponse


def unexpected_exception_handler(request, exc: Exception):
    # log.error("Unexpected error", exc_info=exc)

    return JSONResponse(
        status_code=500,
        content={
            "error": "UNEXPECTED_ERROR",
            "message": "Internal server error"
        }
    )
