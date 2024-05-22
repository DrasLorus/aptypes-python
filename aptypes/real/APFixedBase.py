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
    def bitW(self) -> int:
        """Bit width

        Returns:
            int: arbitrary length in bits
        """
        return self.__bitW

    @property
    def bitI(self) -> int:
        """Integer bits

        Returns:
            int: arbitrary number of bits above the fixed point
        """
        return self.__bitI

    @property
    def bitQ(self) -> int:
        """Quotient bits

        Returns:
            int: arbitrary number of bits below the fixed point
        """
        return self.__bitQ

    @property
    def raw(self) -> int:
        """Internal raw value

        Returns:
            int: internal raw value, as a pur python integer
        """
        return self.__V

    @raw.setter
    def raw(self, val: int):
        if not isinstance(val, int):
            raise ValueError("Only int type is supported")
        self._validateValue(val, self.bitW, self.signed)
        self.__V = val

    @property
    def bin(self) -> str:
        """Internal binary value

        Returns:
            str: internal binary value, as a python string
        """
        isneg  = self.raw < 0
        value  = abs(self.raw) - 1 if isneg else self.raw
        common = ('{0:0%db}' % self.bitW).format(value)
        binrep = common.replace('1','X').replace('0','1').replace('X', '0') if isneg else common
        return binrep

    @bin.setter
    def bin(self, binrep: str):
        if len(binrep) != self.__bitW:
            raise ValueError(f'Binary word length must be {self.__bitW}')
        ispos    = binrep[0] == '0'
        self.raw = int(binrep, 2) if ispos else int('-'+binrep.replace('1','X').replace('0','1').replace('X', '0'), 2) - 1

    @classmethod
    def _maxRawValue(cls, bitW: int) -> int:
        """Compute the maximum raw value achievable by this class for bitW bits

        Args:
            bitW (int): targetted bit width

        Returns:
            int: maximum raw value achievable
        """
        return 2**(bitW - int(cls._signed())) - 1

    @property
    def maxRawValue(self) -> int:
        """Maximum raw value achievable

        Returns:
            int: Maximum raw value achievable for the current object
        """
        return type(self)._maxRawValue(self.bitW)

    @classmethod
    def _minRawValue(cls, bitW) -> int:
        """Compute the minimum raw value achievable by this class for bitW bits

        Args:
            bitW (int): targetted bit width

        Returns:
            int: minimum raw value achievable
        """
        svalue = int(cls._signed())
        return  -2**(bitW - svalue) * svalue
    
    @property
    def minRawValue(self) -> int:
        """Minimum raw value achievable

        Returns:
            int: Minimum raw value achievable for the current object
        """
        return type(self)._minRawValue(self.bitW)

    @property
    def precision(self) -> float:
        """Fixed-point precison quantum

        Returns:
            int: the fixed-point precison quantum, the smallest value that can be represented accuratly
        """
        return 2.**(-self.bitQ)

    @property
    def value(self) -> float:
        """Floating-point value

        Returns:
            int: the equivalent floating-point value, based on the fixed point position and assuming a linear binary conversion
        """
        return self.raw * 2.**(-self.bitQ)

    @value.setter
    def value(self, val: float) -> None:
        if not isinstance(val, (float, numpy.floating)):
            raise ValueError("require a floating point value") 
        self.raw = int(val * 2**(self.bitQ))

    @property
    def maxValue(self) -> float:
        """Maximum floating point value achievable

        Returns:
            float: maximum floating point value achievable
        """
        return self.maxRawValue * 2.**(-self.bitQ)

    @property
    def minValue(self) -> float:
        """Minimum floating point value achievable

        Returns:
            float: minimum floating point value achievable
        """
        return self.minRawValue * 2.**(-self.bitQ)

    @property
    def scaling(self) -> str:
        """Scaling method in use

        Returns:
            str: Scaling method in use
        """
        return self.__scalingMethod
  
    @staticmethod
    def _estimateIWidth(signed: bool, val: float | int) -> int:
        """Estimation of the necessary number of integer bits

        Args:
            signed (bool): whether the object is signed
            val (float | int): the value to approximate

        Returns:
            int: an estimation of the minimum bitI required to store the integer part of the value
        """
        return int(numpy.log2(abs(val) + val.__class__(not val))) + 1 + int(signed)

    @staticmethod
    def _estimateWidth(bitI: int, bitQ: int) -> int:
        """Estimation of the bit length

        Args:
            bitI (int): Integer bits
            bitQ (int): Quotient bits

        Returns:
            int: an estimation of the bit length
        """
        return bitI + bitQ

    @staticmethod
    def _estimateQWidth(bitI: int, bitW: int | None) -> int:
        """Estimation of the number of quotient bit

        Args:
            bitI (int): Integer bits
            bitW (int | None): Bit length, or max(32, bitI+16) when None 

        Returns:
            int: an estimation of the number of quotient bit
        """
        if bitW is None:
            bitW = max(32, bitI + 16)
        return bitW - bitI

    @staticmethod
    def _validateValue(V: int, bitW: int, signed: bool) -> bool:
        """INTERNAL USE ONLY: Validate a raw value

        Args:
            V (int): raw value to validate
            bitW (int): targetted bit width
            signed (bool): whether the object is signed

        Raises:
            ValueError: V in not an int
            ValueError: bitW is too small for V

        Returns:
            bool: True if the triplet is correct, otherwise False.
        """
        if not isinstance(V, int):
            raise ValueError("Value must be an int")
        if V > 2**(bitW - signed) - 1 or V < (-2**(bitW - signed) * signed):
            str_sign = ' signed' if signed else 'n unsigned'
            raise ValueError(f"A{str_sign} of {bitW} bits cannot hold the value {V}")

    def __init__(self, val: float | str | int | Base, 
                 bitW: int = None, bitI: int = None,
                 **kwargs):
        """Base constructor

        Args:
            val (any): The initial value. If its type is:
                - float or numpy.floating, it is interpreted as a floating-point value to approximate. When bitW or bitI are None, they are estimated using the dedicated method.
                - str, it is interpreted as a binary value to be set as-is. If bitW is None, it is set to the length of val. bitI is required.
                - int or numpy.integer, it is interpreted as a raw value to be set as-is. If bitW is None, it is estimated using the dedicated method. bitI is required.
                - Base or subclasses, its raw value is copied. When bitW or bitI are None, their value is also copied.
                - any other type, a NotImplementedError is raised.
            bitW (int, optional): requested bit length, see val for details. Defaults to None.
            bitI (int, optional): requested number of integer bits, see val for details. Defaults to None.

        Raises:
            ValueError: bitI argument missing while required
            NotImplementedError: val type not supported
        """
        if 'scaling' in kwargs.keys():
            self.__scalingMethod = kwargs['scaling']
        else:
            self.__scalingMethod = 'internal'
        if isinstance(val, (float, numpy.floating)):
            if bitI is None:
                bitI = self._estimateIWidth(self.signed, val)
            bitQ = self._estimateQWidth(bitI, bitW)
            if bitW is None:
                bitW = self._estimateWidth(bitI, bitQ)
            V   = int(val * 2**bitQ)
        elif isinstance(val, str):
            if bitI is None:
                raise ValueError('bitI must be provided when using binary representation')
            if bitW is None:
                bitW = len(val)
            bitQ   = self._estimateQWidth(bitI, bitW)
            ispos = val[0] == '0'
            V     = int(val, 2) if (ispos or not self.signed) else int(val[1:], 2) - int('1' + '0'*(bitW - 1), 2)
        elif issubclass(val.__class__, Base):
            if bitW is None:
                bitW = val.bitW
            if bitI is None:
                bitI = val.bitI
            bitQ = self._estimateQWidth(bitI, bitW)
            V   = val.raw
        elif isinstance(val, (int, numpy.integer)):
            if bitI is None:
                raise ValueError('bitI must be provided when using raw representation')
            bitQ = self._estimateQWidth(bitI, bitW)
            if bitW is None:
                bitW = self._estimateWidth(bitI, bitQ)
            V   = int(val)
        else:
            raise NotImplementedError('Currently supported type: float, numpy.floating, int, str and Base')
        self._validateValue(V, bitW, int(self.signed))
        self.__V   = V
        self.__bitW = bitW
        self.__bitI = bitI
        self.__bitQ = bitQ

    def __add__(self, val: float | str | int | Base, 
                bitW: int = None, bitI: int = None) -> Base:
        if isinstance(val, Base):
            local = val
        else:
            local = self.__class__(val, bitW, bitI)
        localI = max(self.bitI, local.bitI) + 1 if bitI is None else bitI
        if bitW is None:
            localQ = max(self.bitQ, local.bitQ)
            localW = localI + localQ
        else:
            localW = bitW
            localQ = localW - localI
        if self.scaling == 'internal':
            scales = [2**(localQ - self.bitQ), 2**(localQ - local.bitQ)]
            localV = int(self.raw * scales[0]) + int(local.raw * scales[1])
        else:
            localV = self.raw + local.raw 
        return self.__class__(localV, localW, localI)
    
    def bitstrainedAdd(self, val: float | str | int | Base, 
                       bitW: int , bitI: int = None):
        return self.__add__(val, bitW, bitI)

    def __sub__(self, val: float | str | int | Base, 
                bitW: int = None, bitI: int = None) -> Base:
        if isinstance(val, Base):
            local = val
        else:
            local = self.__class__(val, bitW, bitI)
        localI = max(self.bitI, local.bitI) + 1 if bitI is None else bitI
        if bitW is None:
            localQ = max(self.bitQ, local.bitQ)
            localW = localI + localQ
        else:
            localW = bitW
            localQ = localW - localI
        if self.scaling == 'internal':
            scales = [2**(localQ - self.bitQ), 2**(localQ - local.bitQ)]
            localV = int(self.raw * scales[0]) - int(local.raw * scales[1])
        else:
            localV = self.raw - local.raw 
        return self.__class__(localV, localW, localI)

    def bitstrainedSub(self, val: float | str | int | Base, 
                       bitW: int, bitI: int = None):
        return self.__sub__(val, bitW, bitI)

    def __mul__(self, val: float | str | int | Base,
                bitW: int = None, bitI: int = None) -> Base:
        if isinstance(val, Base):
            local = val
        else:
            local = self.__class__(val, bitW, bitI)
        localI = self.bitI + local.bitI if bitI is None else bitI
        if bitW is None:
            localQ = self.bitQ + local.bitQ
            localW = localI + localQ
        else:
            localW = bitW
            localQ = localW - localI
        localV = self.raw * local.raw
        return self.__class__(val=localV, bitW=localW, bitI=localI)

    def bitstrainedMul(self, val: float | str | int | Base,
                       bitW: int, bitI: int = None):
        return self.__mul__(val, bitW, bitI)

    def __neg__(self) -> Base:
        return self.__class__(-self.raw, self.__bitW + 1, self.bitI + 1)

    def __lt__(self, val: Base, bitW: int = None, bitI: int = None) -> bool:
        if isinstance(val, Base):
            local = val
        else:
            local = self.__class__(val, bitW, bitI)
        scale = 2**(self.bitQ - local.bitQ) if self.scaling == 'internal' else 1
        return self.raw < local.raw * scale
    
    def __gt__(self, val: Base, bitW: int = None, bitI: int = None) -> bool:
        if isinstance(val, Base):
            local = val
        else:
            local = self.__class__(val, bitW, bitI)
        scale = 2**(self.bitQ - local.bitQ) if self.scaling == 'internal' else 1
        return self.raw > local.raw * scale

    def __eq__(self, val: Base) -> bool:
        if isinstance(val, Base):
            local = val
        else:
            local = self.__class__(val)
        scale = 2.**(self.bitQ - local.bitQ) if self.scaling == 'internal' else 1
        return self.raw == local.raw * scale

    def truncate(self, bits: int, lsb: bool = True) -> Base:
        """Truncate arbitrary number of MSBs or LSBs 

        Args:
            bits (int): number of bits to truncate
            lsb (bool, optional): truncate least-significant (right-most in binary rep.) bits. Defaults to True.

        Raises:
            ValueError: bits is negative, and negative truncation are not defined.

        Returns:
            Base: A new Base with bits truncated and values adjusted accordingly
        """
        if bits < 0:
            raise ValueError('Negative truncation are not defined.')
        if lsb:
            return self.__class__(self.bin[:-bits],
                self.bitW - bits,
                self.bitI)
        else:
            return self.__class__(self.bin[bits:],
                self.bitW - bits,
                self.bitI - bits)


    def pad(self, bits: int, lsb: bool = True) -> Base:
        """Pad arbitrary bits without affecting the value

        Args:
            bits (int): number of padded bits.
            lsb (bool, optional): pad least-significant (right-most in binary rep.) bits. Defaults to True.

        Returns:
            Base: depending of the sign and of lsb, a zero- or one-padded version of the object
        """
        if lsb:
            return self.__class__(
                self.bin + '0' * bits,
                self.__bitW + bits, 
                self.bitI)
        else:
            sign_str = self.bin[0] if self.signed else '0'
            return self.__class__(
                sign_str * bits + self.bin,
                self.__bitW + bits,
                self.bitI + bits)

    @classmethod
    def _saturateHigh(cls, val, bitW) -> int:
        return int(min(val, cls._maxRawValue(bitW)))

    @classmethod
    def _saturateLow(cls, val, bitW) -> int:
        return int(max(val, cls._minRawValue(bitW)))

    def saturate(self, bits: int) -> Base:
        """Truncate most-significant bits while saturating the value  

        Args:
            bits (int): MSB to be truncated

        Returns:
            Base: a trucated version of the object, saturated if the value exceeded the one achievable after truncation.
        """
        localW = self.bitW - bits
        localI = self.bitI - bits
        if self.raw >= 0:
            return self.__class__(
                self._saturateHigh(self.raw, localW),
                localW,
                localI)
        else:
            return self.__class__(
                self._saturateLow(self.raw, localW),
                localW,
                localI)
    
    def __repr__(self):
        return f'{self.__class__.__name__}(val={self.raw}, bitW={self.bitW}, bitI={self.bitI})'
    
    def __str__(self):
        return f'{self.value} {self.bitW}[{"S" if self.signed else "U"}{self.bitI}]'

    def __float__(self):
        return self.value

    def __int__(self):
        return self.raw

