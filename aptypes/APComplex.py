from .APComplexBase import APComplexBase

class APComplex(APComplexBase):
    """APComplexBase signed implementation 

    """

    @classmethod
    def _signed(cls) -> bool:
        return True