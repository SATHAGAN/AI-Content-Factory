from __future__ import annotations

import json
from typing import Any, Type

from pydantic import BaseModel


class StructuredOutputError(ValueError):
    pass


def parse_structured_output(raw: str | dict[str, Any], schema: Type[BaseModel]) -> BaseModel:
    if isinstance(raw, dict):
        data=raw
    else:
        text=raw.strip()
        if text.startswith("```"):
            lines=text.splitlines()
            lines=lines[1:-1] if len(lines)>=2 else lines
            text="\n".join(lines)
            if text.lower().startswith("json"):
                text=text[4:].lstrip()
        try:
            data=json.loads(text)
        except json.JSONDecodeError as exc:
            raise StructuredOutputError("LLM returned invalid JSON") from exc
    try:
        return schema.model_validate(data)
    except Exception as exc:
        raise StructuredOutputError("LLM JSON did not match the required schema") from exc
