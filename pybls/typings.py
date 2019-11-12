from typing import NewType, TypeVar
from py_ecc.typing import Optimized_Point3D
from py_ecc.fields import optimized_bn128_FQ, optimized_bn128_FQ2


G1Point = Optimized_Point3D[optimized_bn128_FQ]
G2Point = Optimized_Point3D[optimized_bn128_FQ2]

Pubkey = NewType("Pubkey", bytes)
Signature = NewType("Signature", bytes)
PrivateKey = NewType("PrivatKey", int)
Message = NewType("Message", bytes)
MessageHash = TypeVar("MessageHash", G2Point, G1Point)
