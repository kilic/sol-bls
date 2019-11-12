from random import randint
from typing import Sequence
from py_ecc.optimized_bn128 import (
    FQ,
    FQ2,
    Z1,
    G2,
    add,
    field_modulus,
    multiply,
    normalize,
)
from pybls.g2pubs.hash import hash_to_g1
from pybls.g2pubs.pairing import pair_check, pair_check_multiple
from pybls.g2pubs.serialize import (
    g2_to_pubkey,
    g1_to_signature,
    pubkey_to_g2,
    signature_to_g1,
)
from pybls.typings import Message, PrivateKey, Pubkey, Signature


def new_priv_key() -> PrivateKey:
    return PrivateKey(randint(1, field_modulus - 1))


def priv_to_pub(priv: PrivateKey) -> Pubkey:
    x, y = normalize(multiply(G2, priv))
    g2 = (x, y, FQ2.one())
    return g2_to_pubkey(g2)


def sign(msg: Message, priv: PrivateKey) -> Signature:
    x, y = normalize(multiply(hash_to_g1(msg), priv))
    g1 = (x, y, FQ.one())
    return g1_to_signature(g1)


def agg_sigs(sigs: Sequence[Signature]) -> Signature:
    aggregated = Z1
    for sig in sigs:
        aggregated = add(aggregated, signature_to_g1(sig))
    return g1_to_signature(aggregated)


def agg_pubs(pubs: Sequence[Pubkey]) -> Pubkey:
    size = len(pubs)
    if size < 1:
        return
    aggregated = pubkey_to_g2(pubs[0])
    for i in range(1, size):
        aggregated = add(aggregated, pubkey_to_g2(pubs[i]))
    return g2_to_pubkey(aggregated)


def verify(sig: Signature, msg: Message, pub: Pubkey) -> bool:
    return pair_check(signature_to_g1(sig), msg, pubkey_to_g2(pub))


def verify_agg_common_msg(sig: Signature, msg: Message, pubs: Sequence[Pubkey]) -> bool:
    aggregated_pub = agg_pubs(pubs)
    return pair_check(signature_to_g1(sig), msg, pubkey_to_g2(aggregated_pub))


def verify_agg(sig: Signature, msgs: Sequence[Message], pubs: Sequence[Pubkey]) -> bool:
    _pubs = []
    for pub in pubs:
        _pubs.append(pubkey_to_g2(pub))
    return pair_check_multiple(signature_to_g1(sig), _pubs, msgs)
