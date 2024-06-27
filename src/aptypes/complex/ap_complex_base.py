from __future__ import annotations
import abc
import numpy

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

    @property
    def signed(self) -> bool:
        """Signed type indicator

        Returns:
            bool: whether the class is signed or not
        """
        return type(self)._signed()

    @property
    def bit_width(self) -> int:
        """Bit width of real and imaginary part

        Returns:
            int: arbitrary length in bits
        """
        return self.__re.bit_width

    @property
    def bit_int(self) -> int:
        """Integer bits of real and imaginary part

        Returns:
            int: arbitrary number of bits above the fixed point
        """
        return self.__re.bit_int

    @property
    def bit_quote(self) -> int:
        """Quotient bits of real and imaginary part

        Returns:
            int: arbitrary number of bits below the fixed point
        """
        return self.__re.bit_quote

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
        """the conceptual value hold by the number 

        Returns:
            complex: a floating-point value of the complex-number
        """
        return self.real.value + 1j * self.imag.value

    @property
    def root_class(self) -> type:
        """Type of real and imaginary parts

        Returns:
            type: the underlying type of the real and imaginary parts
        """
        return self.real.__class__

    def __neg__(self) -> Base:
        return self.__class__(value = (-self.real, -self.imag),
                              bit_width = self.bit_width + 1,
                              bit_int = self.bit_int + 1)

    def __add__(self, value, bit_width = None, bit_int = None) -> Base:
        if isinstance(value, real.Base) or (numpy.isrealobj(value) and numpy.isscalar(value)):
            local      = self.root_class(value = value, bit_width = bit_width, bit_int = bit_int)
            local_v_re = self.real + local
            local_v_im = self.imag
        else:
            if isinstance(value, Base):
                local = value
            else:
                local = self.__class__(value=value, bit_width=bit_width, bit_int=bit_int)
            local_v_re = self.real + local.real
            local_v_im = self.imag + local.imag
        return self.__class__((local_v_re, local_v_im), bit_width=bit_width, bit_int=bit_int)

    def __sub__(self, value) -> Base:
        if isinstance(value, real.Base) or (numpy.isrealobj(value) and numpy.isscalar(value)):
            local      = self.root_class(value = value, bit_width = None, bit_int = None)
            local_v_re = self.__re - local
            local_v_im = self.__im
        else:
            if isinstance(value, Base):
                local = value
            else:
                local = self.__class__(value = value, bit_width = None, bit_int = None)
            # pylint: disable=protected-access
            local_v_re = self.__re - local.__re
            local_v_im = self.__im - local.__im
        return self.__class__(value = (local_v_re, local_v_im), bit_width = None, bit_int = None)

    def __mul__(self, value) -> Base:
        if isinstance(value, real.Base) or (numpy.isrealobj(value) and numpy.isscalar(value)):
            local    = self.root_class(value)
            local_v_re = self.__re * local
            local_v_im = self.__im * local
        else:
            if isinstance(value, Base):
                local = value
            else:
                local = self.__class__(value = value, bit_width = None, bit_int = None)
            # pylint: disable=protected-access
            local_v_re = self.__re * local.__re - self.__im * local.__im
            local_v_im = self.__re * local.__im + self.__im * local.__re
        return self.__class__(value = (local_v_re, local_v_im), bit_width = None, bit_int = None)

    def __eq__(self, value: real.Base) -> bool:
        if isinstance(value, Base):
            local = value
        else:
            local = self.__class__(value)
        return self.real == local.real and self.imag == local.imag

    def __repr__(self):
        class_str = f'{self.__class__.__name__}'
        val_str   = f'value=({self.real.raw}, {self.imag.raw})'
        bitw_str  = f'bit_width={self.bit_width}'
        biti_str  = f'bit_int={self.bit_int}'
        return class_str + '(' + val_str + ',' + bitw_str + ',' + biti_str + ')'

    def __str__(self):
        return f"{self.value} {self.bit_width}[{'S' if self.signed else 'U'}{self.bit_int}]"

    def __complex__(self):
        return complex(self.value)

    def __abs__(self):
        return abs(complex(self))

    def __init__(self, value: any, bit_width: int = None, bit_int: int = None):
        """Base constructor

        Args:
            - value (any): The initial value. If its type is:
                - `complex`, `numpy.couple` or `Base` and derivatives: real and imaginary parts
                    are extracted and converted to `real.Base`.
                - `tuple`, `list` or `numpy.ndarray`:
                    - if length is 1, real part is the first value and imaginary part is null,
                    - if length is 2, real part is the first value and imaginary part is the
                        second value,
                    - otherwise, a `ValueError` is raised.
                - `float` or `numpy.floating`: it is interpreted as a floating-point real value
                    to approximate, imaginary part is set to 0.
                - `int` or `numpy.integer`: it is interpreted as a real raw value to be set as-is,
                    imaginary part is set to 0.
                - a `real.Base` derivative: its raw value is copied to the real part,
                    imaginary part is set to 0.
                - any other type: a `NotImplementedError` is raised.

            - bit_width (`int`, optional): requested bit length. 
                See `real.Base.__init__` documentation for details. Defaults to None.
            - bit_int (`int`, optional): requested number of integer bits.
                See `real.Base.__init__` documentation for details. Defaults to None.

        Raises:
            ValueError: the type for value is not supported
        """
        re, im = 0.0, 0.0
        argument_error = ValueError(
            "value can either be a complex value, a real value or a (real, imag) couple"
        )
        if isinstance(value, (Base, complex, numpy.complexfloating)):
            re, im = value.real, value.imag
        elif isinstance(value, (tuple, list, numpy.ndarray)):
            lenval = len(value)
            conditions = (any(numpy.iscomplex(value)),
                          any([isinstance(x, Base) for x in value]),
                          (lenval not in (1, 2)))
            if any(conditions):
                raise argument_error
            re, im = value if lenval > 1 else (value[0], 0)
        elif isinstance(value, real.Base) or numpy.isreal(value):
            re = value
        else:
            raise argument_error
        root_class = real.Signed if type(self)._signed() else real.Unsigned
        apre = root_class(re, bit_width, bit_int)
        apim = root_class(im, bit_width, bit_int)
        local_q = max(apre.bit_quote, apim.bit_quote)
        local_i = max(apre.bit_int, apim.bit_int)
        local_w = local_i + local_q
        self.__re = root_class(re, local_w, local_i)
        self.__im = root_class(im, local_w, local_i)

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
            lsb (bool, optional): truncate least-significant (right-most in binary rep.)
                                  bits. Defaults to True.

        Returns:
            Base: A new Base with bits truncated and values adjusted accordingly
        """
        return self.__class__((self.real.truncate(bits, lsb), self.imag.truncate(bits, lsb)),
                              bit_width = None, bit_int = None)

    def pad(self, bits: int, lsb: bool = True):
        """Pad both the real and imaginary parts

        Args:
            bits (int): number of padded bits.
            lsb (bool, optional): pad least-significant (right-most in binary rep.) bits.
                                  Defaults to True.

        Returns:
            Base: depending of the sign and of lsb, a zero- or one-padded version of the object
        """
        return self.__class__((self.real.pad(bits, lsb), self.imag.pad(bits, lsb)),
                              bit_width = None, bit_int = None)

    def saturate(self, bits: int):
        """Truncate most-significant bits while saturating the value of both the real
        and imaginary parts 

        Args:
            bits (int): MSB to be truncated

        Returns:
            Base: a trucated version of the object, saturated if the value exceeded
                  the one achievable after truncation.
        """
        return self.__class__(value = (self.real.saturate(bits), self.imag.saturate(bits)),
                              bit_width = None, bit_int = None)
    