"""Collection of classes to simulate arbitrary-fixed-precision fixed-point arithmetics 

"""

__all__ = [ "APFixed", "APUfixed", "APComplex", "APUcomplex", "real", "complex" ]

from .real import APFixed, APUfixed
from .complex import APComplex, APUcomplex

