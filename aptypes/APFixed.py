from .APFixedBase import APFixedBase

class APFixed(APFixedBase):
    """APFixedBase signed implementation 

    """

    @classmethod
    def _signed(cls) -> bool:
        return True