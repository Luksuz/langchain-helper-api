from fastapi import APIRouter, HTTPException
from ..api_models.structured_request import StructuredGenRequest
from ..api_models.structured_response import StructuredGenResponse
from ..api_models.structured_vision_request import StructuredGenVisionRequest
from ..service.structured_service import (
    generate_structured_output,
    generate_structured_output_with_images,
)

router = APIRouter()


@router.post("/generate", response_model=StructuredGenResponse)
def post_generate(request: StructuredGenRequest) -> StructuredGenResponse:
    try:
        result = generate_structured_output(
            system_prompt=request.system_prompt,
            user_prompt=request.user_prompt,
            structure=request.structure,
            model_name=request.model,
            temperature=request.temperature,
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return StructuredGenResponse(data=result, model_name=request.model)


@router.post("/generate-vision", response_model=StructuredGenResponse)
def post_generate_vision(request: StructuredGenVisionRequest) -> StructuredGenResponse:
    try:
        result = generate_structured_output_with_images(
            system_prompt=request.system_prompt,
            user_prompt=request.user_prompt,
            images=[img.model_dump() for img in request.images],
            structure=request.structure,
            model_name=request.model,
            temperature=request.temperature,
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return StructuredGenResponse(data=result, model_name=request.model)

