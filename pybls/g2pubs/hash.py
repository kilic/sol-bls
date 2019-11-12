import hashlib

from py_ecc.optimized_bn128 import FQ, b, is_on_curve
from pybls.typings import G1Point, MessageHash
from pybls.utils import sqrt


def _hash(msg: bytes, additional: bytes) -> bytes:
    data = msg + additional
    return hashlib.sha256(data).digest()


def hash_ORBLS(msg: bytes) -> FQ:
    _msg = _hash(msg, b"")
    return FQ(int.from_bytes(_msg, "big"))


def map_to_g1(raw_hash: FQ) -> G1Point:
    one = FQ.one()
    x = raw_hash
    while True:
        y = x * x * x + b
        y = sqrt(y)
        if y is not None:
            break
        x += one
    h = (x, y, FQ.one())
    assert is_on_curve(h, b)
    return h


def hash_to_g1(msg: bytes) -> MessageHash:
    raw_hash = hash_ORBLS(msg)
    return map_to_g1(raw_hash)
