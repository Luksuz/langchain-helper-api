from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..api_models.ocr_request import OCRRequest
from ..service.ocr_service import extract_text_rich
from ..api_models.extract_text_request import ExtractTextRequest
from ..service.text_extraction_service import extract_text

router = APIRouter()


@router.post("/ocr")
def post_ocr(body: OCRRequest) -> JSONResponse:

    try:
        result = extract_text_rich(
            image_base64=body.image_base64,
            mime_type=body.mime_type,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return JSONResponse(result)


@router.post("/extract-text")
def post_extract_text(body: ExtractTextRequest) -> JSONResponse:
    try:
        text, method = extract_text(
            file_base64=body.file_base64,
            filename=body.filename,
            use_langchain=True,
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return JSONResponse({"text": text, "method": method})

