from __future__ import annotations
import abc
import numpy

class Base(abc.ABC):
    """Core interface to handle fixed-point arbitrary-precision numbers

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
    def bit_width(self) -> int:
        """Bit width

        Returns:
            int: arbitrary length in bits
        """
        return self.__bit_width

    @property
    def bit_int(self) -> int:
        """Integer bits

        Returns:
            int: arbitrary number of bits above the fixed point
        """
        return self.__bit_int

    @property
    def bit_quote(self) -> int:
        """Quotient bits

        Returns:
            int: arbitrary number of bits below the fixed point
        """
        return self.__bit_quote

    @property
    def raw(self) -> int:
        """Internal raw value

        Returns:
            int: internal raw value, as a pur python integer
        """
        return self.__v

    @raw.setter
    def raw(self, value: int):
        if not isinstance(value, int):
            raise ValueError("Only int type is supported")
        self._validate_value(value, self.bit_width, self.signed)
        self.__v = value

    @property
    def bin(self) -> str:
        """Internal binary value

        Returns:
            str: internal binary value, as a python string
        """
        isneg  = self.raw < 0
        value  = abs(self.raw) - 1 if isneg else self.raw
        common = ('{0:0%db}' % self.bit_width).format(value)
        binrep = common.replace('1','X').replace('0','1').replace('X', '0') if isneg else common
        return binrep

    @staticmethod
    def bin_complement(binrep: str) -> str:
        """perform the two-complement of a python binary-represented integer

        Args:
            binrep (str): binary representation of an arbitrary-precision python integer

        Returns:
            str: the two-complement of binrep
        """
        return '-' + binrep.replace('1','X').replace('0','1').replace('X', '0')

    @bin.setter
    def bin(self, binrep: str):
        if len(binrep) != self.__bit_width:
            raise ValueError(f'Binary word length must be {self.__bit_width}')
        ispos    = binrep[0] == '0'
        self.raw = int(binrep, 2) if ispos else int(self.bin_complement(binrep), 2)
    @classmethod
    def _max_raw_value(cls, bit_width: int) -> int:
        """Compute the maximum raw value achievable by this class for bit_width bits

        Args:
            bit_width (int): targetted bit width

        Returns:
            int: maximum raw value achievable
        """
        return 2**(bit_width - int(cls._signed())) - 1

    @property
    def max_raw_value(self) -> int:
        """Maximum raw value achievable

        Returns:
            int: Maximum raw value achievable for the current object
        """
        return type(self)._max_raw_value(self.bit_width)

    @classmethod
    def _min_raw_value(cls, bit_width) -> int:
        """Compute the minimum raw value achievable by this class for bit_width bits

        Args:
            bit_width (int): targetted bit width

        Returns:
            int: minimum raw value achievable
        """
        svalue = int(cls._signed())
        return  -2**(bit_width - svalue) * svalue

    @property
    def min_raw_value(self) -> int:
        """Minimum raw value achievable

        Returns:
            int: Minimum raw value achievable for the current object
        """
        return type(self)._min_raw_value(self.bit_width)

    @property
    def precision(self) -> float:
        """Fixed-point precison quantum

        Returns:
            int: the fixed-point precison quantum, the smallest value that
                can be represented accuratly
        """
        return 2.**(-self.bit_quote)

    @property
    def value(self) -> float:
        """Floating-point value

        Returns:
            int: the equivalent floating-point value, based on the fixed point
                position and assuming a linear binary conversion
        """
        return self.raw * 2.**(-self.bit_quote)

    @value.setter
    def value(self, value: float) -> None:
        if not isinstance(value, (float, numpy.floating)):
            raise ValueError("require a floating point value")
        self.raw = int(value * 2**(self.bit_quote))

    @property
    def max_value(self) -> float:
        """Maximum floating point value achievable

        Returns:
            float: maximum floating point value achievable
        """
        return self.max_raw_value * 2.**(-self.bit_quote)

    @property
    def min_value(self) -> float:
        """Minimum floating point value achievable

        Returns:
            float: minimum floating point value achievable
        """
        return self.min_raw_value * 2.**(-self.bit_quote)

    @property
    def scaling(self) -> str:
        """Scaling method in use

        Returns:
            str: Scaling method in use
        """
        return self.__scaling_method

    @staticmethod
    def _estimate_int_width(signed: bool, value: float | int) -> int:
        """Estimation of the necessary number of integer bits

        Args:
            signed (bool): whether the object is signed
            value (float | int): the value to approximate

        Returns:
            int: an estimation of the minimum bit_int required to
                store the integer part of the value
        """
        return int(numpy.log2(abs(value) + value.__class__(not value))) + 1 + int(signed)

    @staticmethod
    def _estimate_width(bit_int: int, bit_quote: int) -> int:
        """Estimation of the bit length

        Args:
            bit_int (int): Integer bits
            bit_quote (int): Quotient bits

        Returns:
            int: an estimation of the bit length
        """
        return bit_int + bit_quote

    @staticmethod
    def _estimate_quote_width(bit_int: int, bit_width: int | None) -> int:
        """Estimation of the number of quotient bit

        Args:
            bit_int (int): Integer bits
            bit_width (int | None): Bit length, or max(32, bit_int+16) when None 

        Returns:
            int: an estimation of the number of quotient bit
        """
        if bit_width is None:
            bit_width = max(32, bit_int + 16)
        return bit_width - bit_int

    @staticmethod
    def _validate_value(value: int, bit_width: int, signed: bool) -> bool:
        """INTERNAL USE ONLY: Validate a raw value

        Args:
            value (int): raw value to validate
            bit_width (int): targetted bit width
            signed (bool): whether the object is signed

        Raises:
            ValueError: value in not an int
            ValueError: bit_width is too small for value

        Returns:
            bool: True if the triplet is correct, otherwise False.
        """
        if not isinstance(value, int):
            raise ValueError("Value must be an int")
        if value > 2**(bit_width - signed) - 1 or value < (-2**(bit_width - signed) * signed):
            str_sign = ' signed' if signed else 'n unsigned'
            raise ValueError(f"A{str_sign} of {bit_width} bits cannot hold the value {value}")

    def __init__(self, value: float | str | int | Base,
                 bit_width: int = None, bit_int: int = None,
                 **kwargs):
        """Base constructor

        Args:
            - value (any): The initial value. If its type is:
                - `float` or `numpy.floating`:
                  it is interpreted as a floating-point value to approximate.
                  When bit_width or bit_int are None, they are estimated using the dedicated method.
                - `str`:
                  it is interpreted as a binary value to be set as-is.
                  If bit_width is None, it is set to the length of value.
                  bit_int is required.
                - `int` or `numpy.integer`:
                  it is interpreted as a raw value to be set as-is.
                  If bit_width is None, it is estimated using the dedicated method.
                  bit_int is required.
                - `Base` or subclasses:
                  its raw value is copied.
                  When bit_width or bit_int are None, their value is also copied.
                - any other type: a `NotImplementedError` is raised.
            - bit_width (int, optional): requested bit length, see value for details.
                Defaults to None.
            - bit_int (int, optional): requested number of integer bits, see value for details.
                Defaults to None.

        Raises:
            ValueError: bit_int argument missing while required
            NotImplementedError: value type not supported
        """
        if 'scaling' in kwargs:
            self.__scaling_method = kwargs['scaling']
        else:
            self.__scaling_method = 'internal'
        if isinstance(value, (float, numpy.floating)):
            if bit_int is None:
                bit_int = self._estimate_int_width(self.signed, value)
            bit_quote = self._estimate_quote_width(bit_int, bit_width)
            if bit_width is None:
                bit_width = self._estimate_width(bit_int, bit_quote)
            value = int(value * 2**bit_quote)
        elif isinstance(value, str):
            if bit_int is None:
                raise ValueError('bit_int must be provided when using binary representation')
            if bit_width is None:
                bit_width = len(value)
            bit_quote  = self._estimate_quote_width(bit_int, bit_width)
            ispos     = value[0] == '0'
            neg_value = int(value[1:], 2) - int('1' + '0'*(bit_width - 1), 2)
            pos_value = int(value, 2)
            value = pos_value if (ispos or not self.signed) else neg_value
        elif issubclass(value.__class__, Base):
            if bit_width is None:
                bit_width = value.bit_width
            if bit_int is None:
                bit_int = value.bit_int
            bit_quote = self._estimate_quote_width(bit_int, bit_width)
            value     = value.raw
        elif isinstance(value, (int, numpy.integer)):
            if bit_int is None:
                raise ValueError('bit_int must be provided when using raw representation')
            bit_quote = self._estimate_quote_width(bit_int, bit_width)
            if bit_width is None:
                bit_width = self._estimate_width(bit_int, bit_quote)
            value = int(value)
        else:
            supported_types = ', '.join(['float',
                                         'numpy.floating',
                                         'int',
                                         'numpy.integer',
                                         'str',
                                         'Base'])
            raise NotImplementedError(f'Currently supported type: {supported_types}')
        self._validate_value(value, bit_width, int(self.signed))
        self.__v         = value
        self.__bit_width = bit_width
        self.__bit_int   = bit_int
        self.__bit_quote = bit_quote

    def __add__(self, value: float | str | int | Base,
                bit_width: int = None, bit_int: int = None) -> Base:
        if isinstance(value, Base):
            local = value
        else:
            local = self.__class__(value, bit_width, bit_int)
        local_int = max(self.bit_int, local.bit_int) + 1 if bit_int is None else bit_int
        if bit_width is None:
            local_quote = max(self.bit_quote, local.bit_quote)
            local_width = local_int + local_quote
        else:
            local_width = bit_width
            local_quote = local_width - local_int
        if self.scaling == 'internal':
            scales      = [2**(local_quote - self.bit_quote), 2**(local_quote - local.bit_quote)]
            local_value = int(self.raw * scales[0]) + int(local.raw * scales[1])
        else:
            local_value = self.raw + local.raw
        return self.__class__(local_value, local_width, local_int)

    def bitstrained_add(self, value: float | str | int | Base,
                       bit_width: int , bit_int: int = None) -> Base:
        """perform an addition but enforcing a specific bit-size

        Args:
            value (float | str | int | Base): the value to add
            bit_width (int): the bit width targeted
            bit_int (int, optional): the int part width targeted. Defaults to None.

        Returns:
            Base: the result of the addition on bit_width bits.
        """
        # pylint: disable-next=unnecessary-dunder-call
        return self.__add__(value, bit_width, bit_int)

    def __sub__(self, value: float | str | int | Base,
                bit_width: int = None, bit_int: int = None) -> Base:
        if isinstance(value, Base):
            local = value
        else:
            local = self.__class__(value, bit_width, bit_int)
        local_int = max(self.bit_int, local.bit_int) + 1 if bit_int is None else bit_int
        if bit_width is None:
            local_quote = max(self.bit_quote, local.bit_quote)
            local_width = local_int + local_quote
        else:
            local_width = bit_width
            local_quote = local_width - local_int
        if self.scaling == 'internal':
            scales = [2**(local_quote - self.bit_quote), 2**(local_quote - local.bit_quote)]
            local_value = int(self.raw * scales[0]) - int(local.raw * scales[1])
        else:
            local_value = self.raw - local.raw
        return self.__class__(local_value, local_width, local_int)

    def bitstrained_sub(self, value: float | str | int | Base,
                       bit_width: int, bit_int: int = None) -> Base:
        """perform a substraction but enforcing a specific bit-size

        Args:
            value (float | str | int | Base): the value to substract
            bit_width (int): the bit width targeted
            bit_int (int, optional): the int part width targeted. Defaults to None.

        Returns:
            Base: the result of the substraction on bit_width bits.
        """
        # pylint: disable-next=unnecessary-dunder-call
        return self.__sub__(value, bit_width, bit_int)

    def __mul__(self, value: float | str | int | Base,
                bit_width: int = None, bit_int: int = None) -> Base:
        if isinstance(value, Base):
            local = value
        else:
            local = self.__class__(value, bit_width, bit_int)
        local_int = self.bit_int + local.bit_int if bit_int is None else bit_int
        if bit_width is None:
            local_quote = self.bit_quote + local.bit_quote
            local_width = local_int + local_quote
        else:
            local_width = bit_width
            local_quote = local_width - local_int
        local_value = self.raw * local.raw
        return self.__class__(value=local_value, bit_width=local_width, bit_int=local_int)

    def bitstrained_mul(self, value: float | str | int | Base,
                       bit_width: int, bit_int: int = None) -> Base:
        """perform a multiplication but enforcing a specific bit-size

        Args:
            value (float | str | int | Base): the value to multiply
            bit_width (int): the bit width targeted
            bit_int (int, optional): the int part width targeted. Defaults to None.

        Returns:
            Base: the result of the multiplication on bit_width bits.
        """
        # pylint: disable-next=unnecessary-dunder-call
        return self.__mul__(value, bit_width, bit_int)

    def __neg__(self) -> Base:
        return self.__class__(-self.raw, self.__bit_width + 1, self.bit_int + 1)

    def __lt__(self, value: Base, bit_width: int = None, bit_int: int = None) -> bool:
        if isinstance(value, Base):
            local = value
        else:
            local = self.__class__(value, bit_width, bit_int)
        scale = 2**(self.bit_quote - local.bit_quote) if self.scaling == 'internal' else 1
        return self.raw < local.raw * scale

    def __gt__(self, value: Base, bit_width: int = None, bit_int: int = None) -> bool:
        if isinstance(value, Base):
            local = value
        else:
            local = self.__class__(value, bit_width, bit_int)
        scale = 2**(self.bit_quote - local.bit_quote) if self.scaling == 'internal' else 1
        return self.raw > local.raw * scale

    def __eq__(self, value: Base) -> bool:
        if isinstance(value, Base):
            local = value
        else:
            local = self.__class__(value)
        scale = 2.**(self.bit_quote - local.bit_quote) if self.scaling == 'internal' else 1
        return self.raw == local.raw * scale

    def truncate(self, bits: int, lsb: bool = True) -> Base:
        """Truncate arbitrary number of MSBs or LSBs 

        Args:
            bits (int): number of bits to truncate
            lsb (bool, optional): truncate least-significant (right-most in binary rep.) bits.
                Defaults to True.

        Raises:
            ValueError: bits is negative, and negative truncation are not defined.

        Returns:
            Base: A new Base with bits truncated and values adjusted accordingly
        """
        if bits < 0:
            raise ValueError('Negative truncation are not defined.')
        if lsb:
            return self.__class__(self.bin[:-bits],
                self.bit_width - bits,
                self.bit_int)
        return self.__class__(self.bin[bits:],
            self.bit_width - bits,
            self.bit_int - bits)


    def pad(self, bits: int, lsb: bool = True) -> Base:
        """Pad arbitrary bits without affecting the value

        Args:
            bits (int): number of padded bits.
            lsb (bool, optional): pad least-significant (right-most in binary rep.) bits.
                Defaults to True.

        Returns:
            Base: depending of the sign and of lsb, a zero- or one-padded version of the object
        """
        if lsb:
            return self.__class__(
                self.bin + '0' * bits,
                self.__bit_width + bits,
                self.bit_int)
        sign_str = self.bin[0] if self.signed else '0'
        return self.__class__(
            sign_str * bits + self.bin,
            self.__bit_width + bits,
            self.bit_int + bits)

    @classmethod
    def _saturate_high(cls, value, bit_width) -> int:
        return int(min(value, cls._max_raw_value(bit_width)))

    @classmethod
    def _saturate_low(cls, value, bit_width) -> int:
        return int(max(value, cls._min_raw_value(bit_width)))

    def saturate(self, bits: int) -> Base:
        """Truncate most-significant bits while saturating the value  

        Args:
            bits (int): MSB to be truncated

        Returns:
            Base: a trucated version of the object, saturated if the value exceeded
                the one achievable after truncation.
        """
        local_width = self.bit_width - bits
        local_int = self.bit_int - bits
        if self.raw >= 0:
            return self.__class__(
                self._saturate_high(self.raw, local_width),
                local_width,
                local_int)
        return self.__class__(
            self._saturate_low(self.raw, local_width),
            local_width,
            local_int)

    def __repr__(self):
        class_str  = f'{self.__class__.__name__}'
        param_strs = [f'value={self.raw}',
                      f'bit_width={self.bit_width}',
                      f'bit_int={self.bit_int}']
        return class_str + '(' + ','.join(param_strs) + ')'

    def __str__(self):
        return f'{self.value} {self.bit_width}[{"S" if self.signed else "U"}{self.bit_int}]'

    def __float__(self):
        return self.value

    def __int__(self):
        return self.raw
