from typing import Protocol
from app.models import CalcType


class Operation(Protocol):
    def compute(self, a: float, b: float) -> float:
        ...


class AddOp:
    def compute(self, a: float, b: float) -> float:
        return a + b


class SubOp:
    def compute(self, a: float, b: float) -> float:
        return a - b


class MultiplyOp:
    def compute(self, a: float, b: float) -> float:
        return a * b


class DivideOp:
    def compute(self, a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("division by zero")
        return a / b


_FACTORY_MAP = {
    CalcType.Add: AddOp,
    CalcType.Sub: SubOp,
    CalcType.Multiply: MultiplyOp,
    CalcType.Divide: DivideOp,
}


def get_operation(calc_type: CalcType) -> Operation:
    cls = _FACTORY_MAP.get(calc_type)
    if cls is None:
        raise ValueError(f"Unsupported calculation type: {calc_type}")
    return cls()


def compute(calc_type: CalcType, a: float, b: float) -> float:
    op = get_operation(calc_type)
    return op.compute(a, b)
