from eth_utils import big_endian_to_int
from py_ecc.optimized_bn128 import FQ2, FQ, normalize, is_on_curve, b, b2
from pybls.typings import Signature, Pubkey, G1Point, G2Point


def is_g1_on_curve(p: G1Point):
    return is_on_curve(p, b)


def is_g2_on_curve(p: G2Point):
    return is_on_curve(p, b2)


def signature_to_G2(signature: Signature) -> G2Point:
    g2 = (
        FQ2([big_endian_to_int(signature[:32]), big_endian_to_int(signature[32:64])]),
        FQ2([big_endian_to_int(signature[64:96]), big_endian_to_int(signature[96:])]),
        FQ2.one(),
    )
    assert is_g2_on_curve(g2)
    return g2


def G2_to_signature(point: G2Point) -> Signature:
    x, y = normalize(point)
    return Signature(
        x.coeffs[0].to_bytes(32, "big")
        + x.coeffs[1].to_bytes(32, "big")
        + y.coeffs[0].to_bytes(32, "big")
        + y.coeffs[1].to_bytes(32, "big")
    )


def pubkey_to_G1(pubkey: Pubkey) -> G1Point:
    a1 = big_endian_to_int(pubkey[:32])
    a2 = big_endian_to_int(pubkey[32:])
    g1 = (FQ(a1), FQ(a2), FQ(1))
    assert is_g1_on_curve(g1)
    return g1


def G1_to_pubkey(point: G1Point) -> Pubkey:
    x, y = normalize(point)
    return Pubkey(x.n.to_bytes(32, "big") + y.n.to_bytes(32, "big"))
