import sys
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from dojo import hash256 
import importlib.util
from pathlib import Path
from elliptic_curves import Point

def _load_field_element():
    """Use YOUR Week 1 FieldElement if it works; otherwise the reference one."""
    week1 = Path(__file__).resolve().parents[2] / "week-01"
    for label, path in (("your Week 1", week1 / "exercises" / "finite_fields.py"),
                        ("the Week 1 reference solution", week1 / "solutions" / "finite_fields.py")):
        try:
            spec = importlib.util.spec_from_file_location(f"ff_{path.parent.name}", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            FE = mod.FieldElement
            if FE(3, 7) + FE(5, 7) == FE(1, 7) and FE(2, 7) / FE(4, 7) == FE(4, 7):
                print(f"(using FieldElement from {label})")
                return FE
        except Exception:
            continue
    raise SystemExit("No working FieldElement found - finish week-01/exercises/finite_fields.py first.")

P = 2 ** 256 - 2 **32 - 977
A = 0
B = 7
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

class SECP256Field(_load_field_element()):

    def __init__(self, num, prime=None):
        super().__init__(num=num,prime=P)

    def __repr__(self):
        return "{:x}".format(self.num).zfill(64)

class SECP256Point(Point):

    def __init(self, x, y, a=None,b=None):
        a = SECP256Field(A)
        b = SECP256Field(B)
        if type(x) == int:
            super().__init__(x=SECP256Field(x), y=SECP256Field(y), a=a, b=b)
        else:
            super().__init__(x=x, y=y, a=a, b=b)

    def __rmul__(self, coeff):
        coef = coeff % N
        return super().__rmul__(coef)

print(SECP256Field(3))