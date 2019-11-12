from pybls.utils import sqrt, FQ2, FQ


def test_sqrt_fq2():
    one = sqrt(FQ2.one())
    assert one == FQ2.one()

    # should_be_none = sqrt(FQ2([-1, -1]))
    # assert should_be_none is None

    a = FQ2([17, 100])
    aa = a * a
    c = sqrt(aa)
    assert c * c == aa


def test_sqrt_fq():

    one = sqrt(FQ.one())
    assert one == FQ.one()

    should_be_none = sqrt(FQ(-1))
    assert should_be_none is None

    a = FQ(17)
    aa = a * a
    c = sqrt(aa)
    assert c * c == aa
