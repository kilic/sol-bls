from eth_utils import big_endian_to_int
from py_ecc.optimized_bn128 import FQ2, FQ, normalize
from pybls.typings import Signature, Pubkey, G1Point, G2Point
from pybls.utils import is_valid_g2_point, is_valid_g1_point


def pubkey_to_g2(pub: Pubkey) -> G2Point:
    g2 = (
        FQ2([big_endian_to_int(pub[:32]), big_endian_to_int(pub[32:64])]),
        FQ2([big_endian_to_int(pub[64:96]), big_endian_to_int(pub[96:])]),
        FQ2.one(),
    )
    assert is_valid_g2_point(g2)
    return g2


def g2_to_pubkey(point: G2Point) -> Signature:
    x, y = normalize(point)
    return Pubkey(
        x.coeffs[0].to_bytes(32, "big")
        + x.coeffs[1].to_bytes(32, "big")
        + y.coeffs[0].to_bytes(32, "big")
        + y.coeffs[1].to_bytes(32, "big")
    )


def signature_to_g1(sig: Signature) -> G1Point:
    a1 = big_endian_to_int(sig[:32])
    a2 = big_endian_to_int(sig[32:])
    g1 = (FQ(a1), FQ(a2), FQ(1))
    assert is_valid_g1_point(g1)
    return g1


def g1_to_signature(point: G1Point) -> Signature:
    x, y = normalize(point)
    return Pubkey(x.n.to_bytes(32, "big") + y.n.to_bytes(32, "big"))
