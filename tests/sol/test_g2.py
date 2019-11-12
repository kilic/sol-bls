import pytest
from random import randint
from py_ecc.typing import Optimized_Field, Optimized_Point3D
from py_ecc.optimized_bn128 import (
    G2,
    normalize,
    FQ2,
    multiply,
    curve_order,
    field_modulus,
    eq,
    double,
)
from pybls.g2_jacobian import (
    multiply as multiply_jacobian,
    add as add_jacobian,
    add_mixed as add_mixed_jacobian,
    double as double_jacobian,
    eq as eq_jacobian,
    normalize as normalize_jacobian,
    is_on_curve as is_on_curve_jacobian,
)

COFACTOR_G2 = 2 * field_modulus - curve_order


def rand_int():
    return randint(1, curve_order - 1)


def _normalize(p1) -> Optimized_Point3D[Optimized_Field]:
    x, y = normalize(p1)
    return (x, y, FQ2.one())


def rand_g2():
    return normalize(multiply(G2, rand_int()))


def rand_g2_jacobian() -> Optimized_Point3D[Optimized_Field]:
    p = multiply_jacobian(G2, rand_int())
    p = multiply_jacobian(p, COFACTOR_G2)
    assert is_on_curve_jacobian(p)
    return p


def sol_to_fq(a):
    return FQ2([a[0], a[1]])


def g2_to_sol(a):
    def fq2_to_sol(a):
        return [a.coeffs[0], a.coeffs[1]]

    return [
        fq2_to_sol(a[0]),
        fq2_to_sol(a[1]),
        fq2_to_sol(a[2]),
    ]


def sol_to_g2(a):
    return [
        FQ2(a[0]),
        FQ2(a[1]),
        FQ2(a[2]),
    ]


@pytest.fixture(scope="module", autouse=True)
def G2LIB(accounts, TESTG2):
    deployed = accounts[0].deploy(TESTG2)
    yield deployed


@pytest.mark.g2lib
def test_g2_normalize(G2LIB):
    a = rand_g2_jacobian()
    normalized = G2LIB.normalize(g2_to_sol(a))
    assert eq(sol_to_g2(normalized), normalize_jacobian(a))


@pytest.mark.g2lib
def test_g2_add(G2LIB):
    a, b = rand_g2_jacobian(), rand_g2_jacobian()
    assert eq_jacobian(a, b) is False

    c = add_jacobian(a, b)
    c2 = sol_to_g2(G2LIB.add(g2_to_sol(a), g2_to_sol(b)))
    assert eq_jacobian(c, c2)

    c2 = sol_to_g2(G2LIB.add(g2_to_sol(G2), g2_to_sol(G2)))
    assert eq(normalize_jacobian(c2), double(G2))


@pytest.mark.g2lib
def test_g2_add_mixed(G2LIB):
    a, b = rand_g2_jacobian(), rand_g2_jacobian()
    assert eq_jacobian(a, b) is False

    b = normalize_jacobian(b)
    c = add_mixed_jacobian(a, b)
    b = g2_to_sol(b)
    c2 = sol_to_g2(G2LIB.addMixed(g2_to_sol(a), [b[0], b[1]]))
    assert eq_jacobian(c, c2)

    b = g2_to_sol(G2)
    c2 = sol_to_g2(G2LIB.addMixed(b, [b[0], b[1]]))
    assert eq(normalize_jacobian(c2), double(G2))


@pytest.mark.g2lib
def test_g2_double(G2LIB):
    a = rand_g2_jacobian()
    c = double_jacobian(a)
    c2 = sol_to_g2(G2LIB.double(g2_to_sol(a)))
    assert eq_jacobian(c, c2)


@pytest.mark.gas
def test_g2_normalize_bench(G2LIB):
    a = double_jacobian(G2)
    tx = G2LIB.normalizeBench(g2_to_sol(a))
    print("Gas Usage, G2 Normalize ", tx.events["Debug"]["gasUsed"], "\n")


@pytest.mark.gas
def test_g2_add_bench(G2LIB):
    b = double_jacobian(G2)
    a = double_jacobian(b)
    tx = G2LIB.addBench(g2_to_sol(a), g2_to_sol(b))
    print("Gas Usage, G2 Addition ", tx.events["Debug"]["gasUsed"], "\n")


@pytest.mark.gas
def test_g2_add_mixed_bench(G2LIB):
    a = double_jacobian(G2)
    g2 = g2_to_sol(G2)
    tx = G2LIB.addMixedBench(g2_to_sol(a), [g2[0], g2[1]])
    print("Gas Usage, G2 Mixed Addition ", tx.events["Debug"]["gasUsed"], "\n")


@pytest.mark.gas
def test_g2_double_bench(G2LIB):
    tx = G2LIB.doubleBench(g2_to_sol(G2))
    print("Gas Usage, G2 Doubling ", tx.events["Debug"]["gasUsed"], "\n")
