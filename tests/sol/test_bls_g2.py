import pytest
from py_ecc.optimized_bn128 import field_modulus, FQ2, FQ
from pybls.g2pubs import (
    new_priv_key,
    priv_to_pub,
    verify,
    sign,
    hash_to_g1,
    agg_pubs,
    agg_sigs,
    verify_agg_common_msg,
    verify_agg,
)
from pybls.g2pubs.serialize import pubkey_to_g2, signature_to_g1


def rand_pubkey():
    sk = new_priv_key()
    return priv_to_pub(sk)


def pubkey_to_sol(pk):
    g2 = pubkey_to_g2(pk)
    return [[g2[0].coeffs[0], g2[0].coeffs[1]], [g2[1].coeffs[0], g2[1].coeffs[1]]]


def msg_to_sol(msg):
    return [msg[0].n, msg[1].n]


def signature_to_sol(sig):
    g1 = signature_to_g1(sig)
    return [g1[0].n, g1[1].n]


@pytest.fixture(scope="module", autouse=True)
def BLSG2(accounts, TESTBLSG2):
    deployed = accounts[0].deploy(TESTBLSG2)
    yield deployed


@pytest.mark.bls_g2
def test_aggregate_pubkeys(BLSG2):
    pk1, pk2, pk3 = rand_pubkey(), rand_pubkey(), rand_pubkey()
    _agg = pubkey_to_g2(agg_pubs([pk1, pk2, pk3]))
    agg = BLSG2.aggregatePubkeys(
        [pubkey_to_sol(pk1), pubkey_to_sol(pk2), pubkey_to_sol(pk3),]
    )
    assert FQ2(agg[0]) == _agg[0]
    assert FQ2(agg[1]) == _agg[1]


@pytest.mark.bls_g2
def test_sqrt(BLSG2):
    def rand_fq() -> FQ:
        from random import randint

        return FQ(randint(1, field_modulus - 1))

    aa = FQ(-1)
    _, ok = BLSG2.sqrt(aa)
    assert ok is False

    a = rand_fq()
    aa = a * a
    a, ok = BLSG2.sqrt(aa)
    assert ok is True
    _a = FQ(a)
    assert _a * _a == aa


@pytest.mark.bls_g2
def test_hash_to_point(BLSG2):
    msg = b"\x00\x00\x00\x01"
    _h = hash_to_g1(msg)
    h = BLSG2.hashToPoint(msg)
    assert FQ(h[0]) == _h[0]
    assert FQ(h[1]) == _h[1]

    import os

    msg = os.urandom(256)
    _h = hash_to_g1(msg)
    h = BLSG2.hashToPoint(msg)
    assert FQ(h[0]) == _h[0]
    assert FQ(h[1]) == _h[1]


@pytest.mark.bls_g2
def test_verify_single(BLSG2):

    msg = b"\x00\x00\x00\x01"
    priv = new_priv_key()
    pub = priv_to_pub(priv)
    sig = sign(msg, priv)
    assert verify(sig, msg, pub)

    _msg = hash_to_g1(msg)

    tx = BLSG2.verifySingle(
        signature_to_sol(sig), pubkey_to_sol(pub), msg_to_sol(_msg),
    )

    assert tx.events["DebugVerification"]["verified"]


@pytest.mark.bls_g2
def test_verify_multi_common(BLSG2):
    msg = b"\x00\x00\x00\x01"
    #
    priv1 = new_priv_key()
    pub1, sig1 = priv_to_pub(priv1), sign(msg, priv1)
    priv2 = new_priv_key()
    pub2, sig2 = priv_to_pub(priv2), sign(msg, priv2)
    priv3 = new_priv_key()
    pub3, sig3 = priv_to_pub(priv3), sign(msg, priv3)
    sig = agg_sigs([sig1, sig2, sig3])
    assert verify_agg_common_msg(sig, msg, [pub1, pub2, pub3])

    _msg = hash_to_g1(msg)
    pubs = []
    for pub in [pub1, pub2, pub3]:
        pubs.append(pubkey_to_sol(pub))

    tx = BLSG2.verifyMultipleCommonMessage(
        signature_to_sol(sig), pubs, msg_to_sol(_msg),
    )

    assert tx.events["DebugVerification"]["verified"]


@pytest.mark.bls_g2
def test_verify_multi(BLSG2):
    msg1, msg2, msg3 = b"\x00\x00\x00\x01", b"\x00\x00\x00\x02", b"\x00\x00\x00\x04"
    #
    priv1 = new_priv_key()
    pub1, sig1 = priv_to_pub(priv1), sign(msg1, priv1)
    priv2 = new_priv_key()
    pub2, sig2 = priv_to_pub(priv2), sign(msg2, priv2)
    priv3 = new_priv_key()
    pub3, sig3 = priv_to_pub(priv3), sign(msg3, priv3)
    sig = agg_sigs([sig1, sig2, sig3])
    assert verify_agg(sig, [msg1, msg2, msg3], [pub1, pub2, pub3])

    pubs = []
    for pub in [pub1, pub2, pub3]:
        pubs.append(pubkey_to_sol(pub))

    msgs = []
    for msg in [msg1, msg2, msg3]:
        msgs.append(msg_to_sol(hash_to_g1(msg)))

    tx = BLSG2.verifyMultiple(signature_to_sol(sig), pubs, msgs, {"gas_limit": 1000000})

    assert tx.events["DebugVerification"]["verified"]

@pytest.mark.bls_g2
@pytest.mark.parametrize(
    "size", [3, 10, 25]
)
def test_verify_multi_raw(BLSG2, size):
    msgx = b"\x00\x00\x00\x01"  #  pretend like messages are different
    msgs = [msgx] * size
    pubs, sigs = [], []
    for i in range(0, size):
        sk = new_priv_key()
        pub, sig = priv_to_pub(sk), sign(msgx, sk)
        pubs.append(pub)
        sigs.append(sig)

    sig = agg_sigs(sigs)
    # assert verify_agg(sig, msgs, pubs)

    _pubs = []
    for pub in pubs:
        _pubs.append(pubkey_to_sol(pub))

    tx = BLSG2.verifyMultipleRawMessages(
        signature_to_sol(sig), _pubs, msgs, {"gas_limit": 9995000}
    )

    assert tx.events["DebugVerification"]["verified"]


@pytest.mark.gas
def test_aggregate_pubkeys_bench(BLSG2):
    size = 100
    pubs = []
    for i in range(0, size):
        pubs.append(pubkey_to_sol(rand_pubkey()))
    tx = BLSG2.aggregatePubkeysBench(pubs)
    print("Gas Usage, Aggregate Pubkey", tx.events["Debug"]["gasUsed"], "\n")


@pytest.mark.gas
def test_hash_to_point_bench(BLSG2):
    msg = b"\x00\x00\x00\x01"
    tx = BLSG2.hashToPointBench(msg)
    print("Gas Usage, Hash To Point", tx.events["Debug"]["gasUsed"], "\n")


@pytest.mark.gas
def test_sqrt_bench(BLSG2):
    msg = b"\x00\x00\x00\x01"
    tx = BLSG2.sqrtBench(25)
    print("Gas Usage, Square Root", tx.events["Debug"]["gasUsed"], "\n")
