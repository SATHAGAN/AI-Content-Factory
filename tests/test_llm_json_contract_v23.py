import pytest
from pydantic import BaseModel

from app.services.llm.json_contract import StructuredOutputError, parse_structured_output


class Example(BaseModel):
    name: str
    count: int


def test_parse_plain_json():
    result=parse_structured_output('{"name":"fox","count":2}',Example)
    assert result.name=="fox"
    assert result.count==2


def test_parse_markdown_json():
    result=parse_structured_output('```json\n{"name":"fox","count":2}\n```',Example)
    assert result.count==2


def test_invalid_json_is_rejected():
    with pytest.raises(StructuredOutputError):
        parse_structured_output("not json",Example)


def test_wrong_schema_is_rejected():
    with pytest.raises(StructuredOutputError):
        parse_structured_output('{"name":"fox","count":"bad"}',Example)
