from typing import Sequence
from py_ecc.optimized_bn128 import G1, final_exponentiate, neg, pairing, FQ12
from pybls.typings import Message, G1Point, G2Point
from pybls.g1pubs.hash import hash_to_g2

TARGET = FQ12.one()


def pair_check(sig: G2Point, msg: Message, pub: G1Point) -> bool:
    f = pairing(sig, neg(G1), final_exponentiate=False) * pairing(
        hash_to_g2(msg), pub, final_exponentiate=False
    )
    return final_exponentiate(f) == TARGET


def pair_check_multiple(
    sig: G2Point, pubs: Sequence[G1Point], msgs: Sequence[Message]
) -> bool:
    size = len(pubs)
    if size == 0:
        raise Exception("empty pubkey vector")
    if len(msgs) == 0:
        raise Exception("empty message vector")
    if size != len(msgs):
        raise Exception("size of public keys and messages should be equal")
    f = pairing(sig, neg(G1), final_exponentiate=False)
    for i in range(size):
        f *= pairing(hash_to_g2(msgs[i]), pubs[i], final_exponentiate=False)
    return final_exponentiate(f) == TARGET
