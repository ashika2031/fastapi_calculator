import pytest
from pydantic import ValidationError

from app.calc import compute, get_operation
from app.models import CalcType
from app.schemas import CalculationCreate


def test_basic_operations():
    assert compute(CalcType.Add, 1, 2) == 3
    assert compute(CalcType.Sub, 5, 3) == 2
    assert compute(CalcType.Multiply, 3, 4) == 12
    assert compute(CalcType.Divide, 10, 2) == 5


def test_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError):
        compute(CalcType.Divide, 1, 0)


def test_get_operation_invalid():
    with pytest.raises(ValueError):
        get_operation("NotAType")


def test_calculation_schema_validation():
    # valid
    c = CalculationCreate(a=1.0, b=2.0, type=CalcType.Add)
    assert c.a == 1.0

    # invalid divide by zero
    with pytest.raises(ValidationError):
        CalculationCreate(a=1.0, b=0.0, type=CalcType.Divide)
