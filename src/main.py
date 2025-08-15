from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .api_models.structured_request import StructuredGenRequest
from .api_models.structured_response import StructuredGenResponse
from .service.structured_service import generate_structured_output, generate_structured_output_with_images
from .api_models.structured_vision_request import StructuredGenVisionRequest

app = FastAPI(title="Handy Structured Output API", version="0.1.0")

# Allow local dev cross-origin by default
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/generate", response_model=StructuredGenResponse)
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


# Convenience: `uvicorn src.main:app --reload`


@app.post("/generate-vision", response_model=StructuredGenResponse)
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

