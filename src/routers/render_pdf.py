from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ..api_models.render_pdf_request import RenderPdfRequest
from ..service.pdf_service import render_html_to_pdf_bytes

router = APIRouter()


@router.post("/render-pdf")
def post_render_pdf(body: RenderPdfRequest):
    import io
    try:
        pdf_bytes = render_html_to_pdf_bytes(body.html)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf")

