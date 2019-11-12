from random import randint
from typing import Sequence
from py_ecc.optimized_bn128 import (
    FQ,
    FQ2,
    G1,
    Z1,
    Z2,
    add,
    field_modulus,
    multiply,
    normalize,
)
from pybls.g1pubs.hash import hash_to_g2
from pybls.g1pubs.pairing import pair_check, pair_check_multiple
from pybls.g1pubs.serialize import (
    G1_to_pubkey,
    G2_to_signature,
    pubkey_to_G1,
    signature_to_G2,
)
from pybls.typings import Message, PrivateKey, Pubkey, Signature


def new_priv_key() -> PrivateKey:
    return PrivateKey(randint(1, field_modulus - 1))


def priv_to_pub(priv: PrivateKey) -> Pubkey:
    x, y = normalize(multiply(G1, priv))
    g1 = (x, y, FQ.one())
    return G1_to_pubkey(g1)


def sign(msg: Message, priv: PrivateKey) -> Signature:
    x, y = normalize(multiply(hash_to_g2(msg), priv))
    g2 = (x, y, FQ2.one())
    return G2_to_signature(g2)


def agg_sigs(sigs: Sequence[Signature]) -> Signature:
    aggregated = Z2
    for sig in sigs:
        aggregated = add(aggregated, signature_to_G2(sig))
    return G2_to_signature(aggregated)


def agg_pubs(pubs: Sequence[Pubkey]) -> Signature:
    aggregated = Z2
    for pub in pubs:
        aggregated = add(aggregated, pubkey_to_G1(pub))
    return G1_to_pubkey(aggregated)


def verify(sig: Signature, msg: Message, pub: Pubkey) -> bool:
    return pair_check(signature_to_G2(sig), msg, pubkey_to_G1(pub))


def verify_agg_common_msg(sig: Signature, msg: Message, pubs: Sequence[Pubkey]) -> bool:
    aggregated_pub = Z1
    for pub in pubs:
        aggregated_pub = add(aggregated_pub, pubkey_to_G1(pub))
    return pair_check(signature_to_G2(sig), msg, aggregated_pub)


def verify_agg(sig: Signature, msgs: Sequence[Message], pubs: Sequence[Pubkey]) -> bool:
    _pubs = []
    for pub in pubs:
        _pubs.append(pubkey_to_G1(pub))
    return pair_check_multiple(signature_to_G2(sig), _pubs, msgs)
