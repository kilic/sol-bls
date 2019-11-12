import hashlib
from typing import TypeVar
from eth_utils import big_endian_to_int
from py_ecc.optimized_bn128 import (
    FQ,
    FQ2,
    b2,
    curve_order,
    field_modulus,
    is_on_curve,
    multiply,
)
from py_ecc.utils import prime_field_inv as inv
from pybls.typings import G2Point, MessageHash
from pybls.utils import sqrt

FQT = TypeVar("FQT", FQ, FQ2)

P = field_modulus
P_MINUS3_OVER4 = ((P - 3) * inv(4, P)) % P
P_MINUS1_OVER2 = ((P - 1) * inv(2, P)) % P
P_PLUS1_OVER4 = ((P + 1) * inv(4, P)) % P
COFACTOR_G2 = 2 * P - curve_order


def _hash(msg: bytes, additional: bytes) -> bytes:
    data = msg + additional
    return hashlib.sha256(data).digest()


def hash_ORBLS(msg: bytes) -> FQ2:
    x_re = big_endian_to_int(_hash(msg, b"\x01"))
    x_im = big_endian_to_int(_hash(msg, b"\x02"))
    return FQ2([x_re, x_im])


def map_to_g2(raw_hash: FQ2) -> G2Point:
    one = FQ2.one()
    x = raw_hash
    while True:
        y = x * x * x + b2
        y = sqrt(y)
        if y is not None:
            break
        x += one
    h = multiply((x, y, one), COFACTOR_G2)
    assert is_on_curve(h, b2)
    return h


def hash_to_g2(msg: bytes) -> MessageHash:
    raw_hash = hash_ORBLS(msg)
    return map_to_g2(raw_hash)
