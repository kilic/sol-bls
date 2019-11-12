from random import randint
from py_ecc.optimized_bn128 import add, G2, normalize, eq, FQ2, multiply, curve_order
from pybls.g2_jacobian import (
    multiply as multiply_jacobian,
    add_mixed as add_mixed_jacobian,
    normalize as normalize_jacobian,
)


def rand_int():
    return randint(1, curve_order - 1)


def _normalize(p1):
    x, y = normalize(p1)
    return (x, y, FQ2.one())


def test_jacobian_equations():
    k = rand_int()
    a = multiply_jacobian(G2, k)
    _a = multiply(G2, k)
    assert eq(normalize_jacobian(a), _normalize(_a))

    b = add_mixed_jacobian(a, G2)
    _b = add(_a, G2)
    assert eq(normalize_jacobian(b), _normalize(_b))

