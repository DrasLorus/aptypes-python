"""Collection of classes to simulate arbitrary-precision fixed-point arithmetics, for real numbers 

"""

__all__ = [ "ap_fixed", "ap_ufixed" ]


from .ap_fixed_base import Base
from .ap_fixed import Signed
from .ap_ufixed import Unsigned

# Some aliases
APFixed = Signed
APUfixed = Unsigned
