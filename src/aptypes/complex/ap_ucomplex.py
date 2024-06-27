from .ap_complex_base import Base

class Unsigned(Base):
    """Base unsigned implementation 

    """

    @classmethod
    def _signed(cls):
        return False
