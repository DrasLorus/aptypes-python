from .APComplexBase import Base

class Signed(Base):
    """Base signed implementation 

    """

    @classmethod
    def _signed(cls) -> bool:
        return True