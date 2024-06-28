"""Collection of classes to simulate arbitrary-precision fixed-point arithmetics of complex numbers 

"""

__all__ = [ "ap_complex", "ap_ucomplex" ]

from .ap_complex_base import Base
from .ap_complex import Signed 
from .ap_ucomplex import Unsigned

# Some common aliases
APComplex  = Signed
APUcomplex = Unsigned
