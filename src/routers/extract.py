from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from ..api_models.extract_request import ExtractRequest
from ..api_models.screenshot_request import ScreenshotRequest
from ..service.structured_service import extract_with_firecrawl


router = APIRouter()


@router.post("/extract")
def post_extract(body: ExtractRequest):

    try:
        data = extract_with_firecrawl(
            urls=body.urls,
            prompt=body.prompt,
            structure=body.structure,
            api_key=body.api_key,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return jsonable_encoder(data)


@router.post("/screenshot")
def post_screenshot(body: ScreenshotRequest):
    from ..service.structured_service import screenshot_with_firecrawl

    try:
        result = screenshot_with_firecrawl(url=body.url, options={"options": body.options})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return jsonable_encoder(result)

