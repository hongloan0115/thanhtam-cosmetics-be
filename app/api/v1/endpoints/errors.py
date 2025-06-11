from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    for error in exc.errors():
        if (
            error.get("type") == "int_parsing"
            and error.get("loc", [None, None])[-1] == "category_id"
        ):
            return JSONResponse(
                status_code=422,
                content={
                    "detail": "ID danh mục không hợp lệ. Vui lòng nhập số nguyên.",
                    "errors": exc.errors()
                }
            )
        if error.get("type") == "missing":
            locs = [str(loc) for loc in error.get("loc", []) if loc != "body"]
            return JSONResponse(
                status_code=422,
                content={
                    "detail": "Thiếu trường bắt buộc " + " ".join(locs),
                    "errors": exc.errors()
                }
            )

    return JSONResponse(
        status_code=422,
        content={"detail": "Dữ liệu không hợp lệ", "errors": exc.errors()}
    )
