from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from ..api_models.client_message_request import ClientMessageRequest
from ..service.structured_service import generate_client_message

router = APIRouter()


@router.post("/generate-client-message")
def post_generate_client_message(body: ClientMessageRequest) -> JSONResponse:
    try:
        msg = generate_client_message(
            user_description=body.user_description,
            website=body.website,
            github=body.github,
            linkedin=body.linkedin,
            model_name=body.model,
            temperature=body.temperature,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return JSONResponse({"message": msg})


