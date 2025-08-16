from __future__ import annotations

from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage
from typing import List
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI

from ..ai_models.openai_model import get_openai_chat_model
from ..utils.schema_builder import build_pydantic_model
from ..utils.context_loader import load_v0_context
from firecrawl import FirecrawlApp


def generate_structured_output(
    system_prompt: str | None,
    user_prompt: str,
    structure: Dict[str, Any],
    model_name: str,
    temperature: float,
) -> Dict[str, Any]:
    """Generate structured output by dynamically building a Pydantic model from a
    provided example dict or JSON Schema, then using LangChain's structured
    outputs helper.

    Reference: LangChain structured outputs docs
    https://python.langchain.com/docs/concepts/structured_outputs/
    """

    # 1) Build Pydantic model dynamically
    output_model = build_pydantic_model(structure)

    # 2) Create chat model
    chat_model: ChatOpenAI = get_openai_chat_model(model_name, temperature)

    # 3) Bind schema using with_structured_output per docs
    structured_model = chat_model.with_structured_output(output_model)

    # 4) Compose messages with optional system prompt
    messages = []
    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))
    messages.append(HumanMessage(content=user_prompt))

    result_obj = structured_model.invoke(messages)

    # 5) Convert returned Pydantic object to dict
    return result_obj.model_dump()


def generate_structured_output_with_images(
    system_prompt: str | None,
    user_prompt: str,
    images: List[dict],
    structure: Dict[str, Any],
    model_name: str,
    temperature: float,
) -> Dict[str, Any]:
    """Same as generate_structured_output, but also accepts images.

    Each image dict should contain:
      - source_type: "base64" or "url"
      - data: base64 string when source_type="base64"
      - url: public URL when source_type="url"
      - mime_type: optional, defaults to image/jpeg
    """

    output_model = build_pydantic_model(structure)
    chat_model: ChatOpenAI = get_openai_chat_model(model_name, temperature)
    structured_model = chat_model.with_structured_output(output_model)

    # Build multimodal content for the user message (OpenAI-compatible)
    content: List[dict] = [{"type": "text", "text": user_prompt}]
    for img in images:
        if img.get("source_type") == "base64" and img.get("data"):
            mime = img.get("mime_type", "image/jpeg")
            data_url = f"data:{mime};base64,{img['data']}"
            content.append({"type": "image_url", "image_url": {"url": data_url}})
        elif img.get("source_type") == "url" and img.get("url"):
            content.append({"type": "image_url", "image_url": {"url": img["url"]}})

    messages = []
    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))
    messages.append(HumanMessage(content=content))

    result_obj = structured_model.invoke(messages)
    return result_obj.model_dump()


def enhance_v0_prompt(user_description: str, model_name: str, temperature: float) -> str:
    """Use the LLM to enhance the user's description into a clear V0 prompt.

    The enhanced prompt is then concatenated with the v0 context so app builders
    have immediate, concrete endpoint instructions.
    """
    chat_model: ChatOpenAI = get_openai_chat_model(model_name, temperature)

    system = SystemMessage(
        content=(
            "You are an expert app-builder prompt engineer. Rewrite the user's description "
            "into a concise, explicit prompt for an app builder (like V0). "
            "The prompt should specify: inputs, UI elements, actions/triggers, API calls to this backend (if relevant), "
            "and expected outputs in structured terms. Keep it brief but unambiguous."
            "Explicitly mention not to use mock data or images in the app."
        )
    )
    human = HumanMessage(content=user_description)
    enhanced = chat_model.invoke([system, human])

    context = load_v0_context()
    composed = enhanced.content.strip() + "\n\n" + context
    return composed


def extract_with_firecrawl(urls: list[str], prompt: str, structure: dict, api_key: str | None) -> dict:
    """Use Firecrawl to extract structured data from web pages according to a
    provided schema (example dict or JSON Schema)."""
    app = FirecrawlApp(api_key=api_key)
    # Build Pydantic model to ensure we provide a JSON schema Firecrawl accepts
    dynamic_model = build_pydantic_model(structure)
    schema = dynamic_model.model_json_schema()
    result = app.extract(urls, prompt=prompt, schema=schema)
    return result


def generate_client_message(
    user_description: str,
    website: str,
    github: str,
    linkedin: str,
    model_name: str,
    temperature: float,
) -> str:
    """Have the LLM tailor a brief client outreach message to the app idea."""
    chat_model: ChatOpenAI = get_openai_chat_model(model_name, temperature)
    system = SystemMessage(
        content=(
            "You are a concise, warm outreach writer. Given an app idea, write a short "
            "message tailored to that idea, including a friendly opener with 2 waving hand emojis, "
            "a sentence mentioning a demo and a loom video, and a polite CTA asking to message back with a hugging face emoji. "
            "End with 'Sincerely, Luka' and include website, github, and LinkedIn as separate lines. Keep under 120 words."
        )
    )
    human = HumanMessage(content=f"App idea: {user_description}\nWebsite: {website}\nGitHub: {github}\nLinkedIn: {linkedin}")
    resp = chat_model.invoke([system, human])
    return resp.content

