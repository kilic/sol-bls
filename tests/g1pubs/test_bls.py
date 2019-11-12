from py_ecc.optimized_bn128 import G1, G2
from pybls.g1pubs import (
    agg_sigs,
    new_priv_key,
    priv_to_pub,
    sign,
    verify,
    verify_agg_common_msg,
    verify_agg,
)
from pybls.g1pubs.hash import hash_to_g2
from pybls.g1pubs.serialize import (
    pubkey_to_G1,
    G1_to_pubkey,
    signature_to_G2,
    G2_to_signature,
)


def test_hash_to_g2():
    msg = b"\x00\x00\x00\x01"
    point = hash_to_g2(msg)
    _ = point


def test_serializing_g1():
    P = G1
    b = G1_to_pubkey(P)
    assert P == pubkey_to_G1(b)


def test_serializing_g2():
    P = G2
    b = G2_to_signature(P)
    assert P == signature_to_G2(b)


def test_verify_single():
    msg = b"\x00\x00\x00\x01"
    #
    priv = new_priv_key()
    pub = priv_to_pub(priv)
    sig = sign(msg, priv)
    #
    assert verify(sig, msg, pub)


def test_common_message_verify():
    msg = b"\x00\x00\x00\x01"
    #
    priv1 = new_priv_key()
    pub1 = priv_to_pub(priv1)
    sig1 = sign(msg, priv1)
    #
    priv2 = new_priv_key()
    pub2 = priv_to_pub(priv2)
    sig2 = sign(msg, priv2)
    #
    priv3 = new_priv_key()
    pub3 = priv_to_pub(priv3)
    sig3 = sign(msg, priv3)
    #
    sig = agg_sigs([sig1, sig2, sig3])
    assert verify_agg_common_msg(sig, msg, [pub1, pub2, pub3])


def test_distinct_messages_verify():
    msg1 = b"\x00\x00\x00\x01"
    msg2 = b"\x00\x00\x00\x02"
    msg3 = b"\x00\x00\x00\x04"
    #
    priv1 = new_priv_key()
    pub1 = priv_to_pub(priv1)
    sig1 = sign(msg1, priv1)
    #
    priv2 = new_priv_key()
    pub2 = priv_to_pub(priv2)
    sig2 = sign(msg2, priv2)
    #
    priv3 = new_priv_key()
    pub3 = priv_to_pub(priv3)
    sig3 = sign(msg3, priv3)
    #
    sig = agg_sigs([sig1, sig2, sig3])
    assert verify_agg(sig, [msg1, msg2, msg3], [pub1, pub2, pub3])
