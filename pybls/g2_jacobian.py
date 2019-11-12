from py_ecc.optimized_bn128 import FQ2, b2 as B
from py_ecc.typing import Optimized_Field, Optimized_Point3D

inf = (FQ2.zero(), FQ2.one(), FQ2.zero())

def double(
    pt: Optimized_Point3D[Optimized_Field],
) -> Optimized_Point3D[Optimized_Field]:
    x, y, z = pt
    A = x * x
    B = y * y
    C = B * B
    t = x + B
    D = 2 * (t * t - A - C)
    E = 3 * A
    F = E * E
    x3 = F - 2 * D
    y3 = E * (D - x3) - 8 * C
    z3 = 2 * z * y
    return (x3, y3, z3)


def add(
    pt1, pt2: Optimized_Point3D[Optimized_Field]
) -> Optimized_Point3D[Optimized_Field]:
    x1, y1, z1 = pt1
    x2, y2, z2 = pt2
    Z1Z1 = z1 * z1
    Z2Z2 = z2 * z2
    U1 = x1 * Z2Z2
    U2 = x2 * Z1Z1
    S1 = y1 * z2 * Z2Z2
    S2 = y2 * z1 * Z1Z1
    if U1 == U2:
        if S1 == S2:
            return double(pt1)
        return inf
    H = U2 - U1
    i = 2 * H
    I = i * i
    J = H * I
    r = 2 * (S2 - S1)
    V = U1 * I
    x3 = r * r - J - 2 * V
    y3 = r * (V - x3) - 2 * S1 * J
    z = z1 + z2
    z3 = (z * z - Z1Z1 - Z2Z2) * H
    return (x3, y3, z3)


def add_mixed_hmv(
    pt1, pt2: Optimized_Point3D[Optimized_Field]
) -> Optimized_Point3D[Optimized_Field]:
    x1, y1, z1 = pt1
    x2, y2, z2 = pt2
    assert z2 == FQ2.one()
    T1 = z1 * z1
    T2 = T1 * z1
    T1 = T1 * x2
    T2 = T2 * y2
    T1 = T1 - x1
    T2 = T2 - y1
    if T1 == FQ2.zero():
        if T2 == FQ2.zero():
            return double(pt1)
        return inf
    z3 = z1 * T1
    T3 = T1 * T1
    T4 = T3 * T1
    T3 = T3 * x1
    T1 = 2 * T3
    x3 = T2 * T2
    x3 = x3 - T1
    x3 = x3 - T4
    T3 = T3 - x3
    T3 = T3 * T2
    T4 = T4 * y1
    y3 = T3 - T4
    return (x3, y3, z3)


def normalize(
    pt: Optimized_Point3D[Optimized_Field],
) -> Optimized_Point3D[Optimized_Field]:
    x1, y1, z1 = pt
    z = z1.inv()
    z2 = z * z
    x3 = x1 * z2
    y3 = y1 * z2 * z
    return (x3, y3, FQ2.one())


def eq(pt1, pt2: Optimized_Point3D[Optimized_Field]) -> bool:
    x1, y1, z1 = pt1
    x2, y2, z2 = pt2
    return x1 * z2 * z2 == x2 * z1 * z1 and y1 * z2 * z2 * z2 == y2 * z1 * z1 * z1


# Y^2 == X^3 + b Z^6
def is_on_curve(pt: Optimized_Point3D[Optimized_Field]) -> bool:
    x, y, z = pt
    return y * y == x * x * x + B * (z * z * z * z * z * z)


# Taken from py_ecc
def multiply(
    pt: Optimized_Point3D[Optimized_Field], n: int
) -> Optimized_Point3D[Optimized_Field]:
    if n == 0:
        return (pt[0].one(), pt[0].one(), pt[0].zero())
    elif n == 1:
        return pt
    elif not n % 2:
        return multiply(double(pt), n // 2)
    else:
        return add(multiply(double(pt), int(n // 2)), pt)


add_mixed = add_mixed_hmv
