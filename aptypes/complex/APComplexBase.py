from __future__ import annotations

from .. import real

class Base:
    """Core interface to handle complex fixed-point arbitrary-precision numbers

    """

    @classmethod
    @abc.abstractmethod
    def _signed(cls) -> bool:
        """Internal use only

        Returns:
            bool: use as a specialization mechanism
        """
        pass

    @property
    def signed(self) -> bool:
        """Signed type indicator

        Returns:
            bool: whether the class is signed or not
        """
        return type(self)._signed()

    @property
    def bitW(self) -> int:
        """Bit width of real and imaginary part

        Returns:
            int: arbitrary length in bits
        """
        return self.__re.bitW

    @property
    def bitI(self) -> int:
        """Integer bits of real and imaginary part

        Returns:
            int: arbitrary number of bits above the fixed point
        """
        return self.__re.bitI
    
    @property
    def bitQ(self) -> int:
        """Quotient bits of real and imaginary part

        Returns:
            int: arbitrary number of bits below the fixed point
        """
        return self.__re.bitQ
    
    @property
    def real(self) -> real.Base:
        """The real part

        Returns:
            real.Base: the fixed-point real part
        """
        return self.__re

    @property
    def imag(self) -> real.Base:
        """The imaginary part

        Returns:
            real.Base: the fixed-point imaginary part
        """
        return self.__im

    @property
    def value(self) -> complex:
        return self.real.value + 1j * self.imag.value

    @property
    def rootClass(self) -> type:
        """Type of real and imaginary parts

        Returns:
            type: the underlying type of the real and imaginary parts
        """
        return self.real.__class__

    def __neg__(self) -> Base:
        return self.__class__((-self.real, -self.imag), self.__bitW + 1, self.bitI + 1, True)

    def __add__(self, val, bitW=None, bitI=None) -> Base:
        if isinstance(val, real.Base) or (numpy.isrealobj(val) and numpy.isscalar(val)):
            local    = self.rootClass(val=val, bitW=bitW, bitI=bitI)
            localVRe = self.real + local
            localVIm = self.imag
        else:
            if isinstance(val, Base):
                local = val
            else:
                local = self.__class__(val=val, bitW=bitW, bitI=bitI)
            localVRe = self.real + local.real
            localVIm = self.imag + local.imag
        return self.__class__((localVRe, localVIm), bitW=bitW, bitI=bitI)
    
    def __sub__(self, val) -> Base:
        if isinstance(val, real.Base) or (numpy.isrealobj(val) and numpy.isscalar(val)):
            local    = self.rootClass(val=val, bitW=None, bitI=None)
            localVRe = self.__re - local
            localVIm = self.__im
        else:
            if isinstance(val, Base):
                local = val
            else:
                local = self.__class__(val=val, bitW=None, bitI=None)
            localVRe = self.__re - local.__re
            localVIm = self.__im - local.__im
        return self.__class__((localVRe, localVIm), bitW=None, bitI=None)
    
    def __mul__(self, val) -> Base:
        if isinstance(val, real.Base) or (numpy.isrealobj(val) and numpy.isscalar(val)):
            local    = self.rootClass(val)
            localVRe = self.__re * local
            localVIm = self.__im * local
        else:
            if isinstance(val, Base):
                local = val
            else:
                local = self.__class__(val=val, bitW=None, bitI=None)
            localVRe = self.__re * local.__re - self.__im * local.__im
            localVIm = self.__re * local.__im + self.__im * local.__re
        return self.__class__((localVRe, localVIm), bitW=None, bitI=None)

    def __eq__(self, val: real.Base) -> bool:
        if isinstance(val, Base):
            local = val
        else:
            local = self.__class__(val)
        return self.real == local.real and self.imag == local.imag
    
    def __repr__(self):
        return f'{self.__class__.__name__}(val=({self.real.raw}, {self.imag.raw}), bitW={self.bitW}, bitI={self.bitI})'

    def __str__(self):
        return "(%r+%rj) %d[%c%d]" % (self.real.value, self.imag.value, self.bitW, 'S' if self.signed else 'U', self.bitI)

    def __complex__(self):
        return complex(self.value)

    def __abs__(self):
        return abs(complex(self))

    def __init__(self, val: any, bitW: int = None, bitI: int = None):
        """Base constructor

        Args:
            val (any): The initial value. If its type is:
                - complex, numpy.couple or Base and derivatives, real and imaginary parts are extracted and converted to real.Base.
                - tuple, list or numpy.ndarray:
                    - if length is 1, real part is the first value and imaginary part is null,
                    - if length is 2, real part is the first value and imaginary part is the second value,
                    - otherwise, a ValueError is raised.
                - float or numpy.floating, it is interpreted as a floating-point real value to approximate, imaginary part is set to 0.
                - int or numpy.integer, it is interpreted as a real raw value to be set as-is, imaginary part is set to 0.
                - an real.Base derivative, its raw value is copied to the real part, imaginary part is set to 0.
                - any other type, a NotImplementedError is raised.
            bitW (int, optional): requested bit length. See real.Base.__init__ documentation for details. Defaults to None.
            bitI (int, optional): requested number of integer bits. See real.Base.__init__ documentation for details. Defaults to None.

        Raises:
            ValueError: the type for value is not supported
        """
        real, imag = 0.0, 0.0
        argumentError = ValueError("val can either be a complex value, a real value or a (real, imag) couple")
        if isinstance(val, (Base, complex, numpy.complexfloating)):
            real, imag = val.real, val.imag
        elif isinstance(val, (tuple, list, numpy.ndarray)):
            lenval = len(val)
            if any(numpy.iscomplex(val)) or any([isinstance(x, Base) for x in val]) or (lenval not in (1, 2)):
                raise argumentError
            if lenval == 1:
                real = val[0]
            else: # lenval == 2
                (real, imag) = val
        elif isinstance(val, real.Base) or numpy.isreal(val):
            real =  val
        else:
            raise argumentError
        rootClass = real.Signed if type(self)._signed() else real.Unsigned
        re = rootClass(real, bitW, bitI)
        im = rootClass(imag, bitW, bitI)
        localQ = max(re.bitQ, im.bitQ)
        localI = max(re.bitI, im.bitI)
        localW = localI + localQ
        self.__re = rootClass(re, localW, localI)
        self.__im = rootClass(im, localW, localI)

    def magn(self):
        """Return the unsigned fixed-point magnitude of the complex

        Returns:
            real.Unsigned: The magnitude of the complex, i.e., Re**2 + Im**2.
        """
        value = self.real * self.real + self.imag * self.imag
        return real.Unsigned(value).truncate(1, False)

    def truncate(self, bits: int, lsb: bool = True):
        """Truncate both the real and the imaginary parts

        Args:
            bits (int): number of bits to truncate
            lsb (bool, optional): truncate least-significant (right-most in binary rep.) bits. Defaults to True.

        Returns:
            Base: A new Base with bits truncated and values adjusted accordingly
        """
        return self.__class__((self.real.truncate(bits, lsb), self.imag.truncate(bits, lsb)), 
                              bitW=None, bitI=None)

    def pad(self, bits: int, lsb: bool = True):
        """Pad both the real and imaginary parts

        Args:
            bits (int): number of padded bits.
            lsb (bool, optional): pad least-significant (right-most in binary rep.) bits. Defaults to True.

        Returns:
            Base: depending of the sign and of lsb, a zero- or one-padded version of the object
        """
        return self.__class__((self.real.pad(bits, lsb), self.imag.pad(bits, lsb)), 
                              bitW=None, bitI=None)

    def saturate(self, bits: int):
        """Truncate most-significant bits while saturating the value of both the real and imaginary parts 

        Args:
            bits (int): MSB to be truncated

        Returns:
            Base: a trucated version of the object, saturated if the value exceeded the one achievable after truncation.
        """
        return self.__class__((self.real.saturate(bits), self.imag.saturate(bits)), 
                              bitW=None, bitI=None)
    