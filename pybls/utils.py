from typing import TypeVar
from py_ecc.optimized_bn128 import b, b2, is_on_curve, FQ, FQ2, field_modulus
from py_ecc.utils import prime_field_inv as inv
from pybls.typings import G1Point, G2Point


def is_valid_g1_point(p: G1Point) -> bool:
    return is_on_curve(p, b)


def is_valid_g2_point(p: G2Point) -> bool:
    return is_on_curve(p, b2)


FQT = TypeVar("FQT", FQ, FQ2)

P = field_modulus
P_MINUS3_OVER4 = ((P - 3) * inv(4, P)) % P
P_MINUS1_OVER2 = ((P - 1) * inv(2, P)) % P
P_PLUS1_OVER4 = ((P + 1) * inv(4, P)) % P


def sqrt(a: FQT):
    """
    https://eprint.iacr.org/2012/685.pdf
    algoritm 2 for fq
    algoritm 9 and fq2
    """

    def _try_sqrt_in_fp2(a: FQ2) -> FQ2:
        a1 = a ** P_MINUS3_OVER4
        alpha = a1 * a1 * a
        x0 = a1 * a
        if alpha == FQ2([-1, 0]):
            return FQ2((x0.coeffs[1], x0.coeffs[0]))
        alpha = alpha + FQ2.one()
        alpha = alpha ** P_MINUS1_OVER2
        return alpha * x0

    def _try_sqrt_in_fp(a: FQ) -> FQ:
        return a ** P_PLUS1_OVER4

    x = 0
    if isinstance(a, FQ):
        x = _try_sqrt_in_fp(a)
    elif isinstance(a, FQ2):
        x = _try_sqrt_in_fp2(a)
    return x if x * x == a else None
