import pytest
from pydantic import ValidationError

from app.cost import cost_usd
from app.schemas import StructuredAnswer, Usage


def test_cost_formula():

    usage = Usage(
        input_tokens=1000,
        output_tokens=500
    )

    assert cost_usd(
        usage,
        0.5,
        1.5
    ) == pytest.approx(0.00125)


def test_structured_output_validation():

    ok = StructuredAnswer.model_validate_json(
        '{"answer": "42", '
        '"confidence": 0.9, '
        '"sources": ["p.3"]}'
    )

    assert ok.confidence == 0.9

    with pytest.raises(ValidationError):

        StructuredAnswer.model_validate_json(
            '{"answer": "42", "confidence": 7}'
        )