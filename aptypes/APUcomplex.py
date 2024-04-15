from .APComplexBase import APComplexBase

class APUcomplex(APComplexBase):
    """APComplexBase unsigned implementation 

    """

    @classmethod
    def _signed(cls):
        return False