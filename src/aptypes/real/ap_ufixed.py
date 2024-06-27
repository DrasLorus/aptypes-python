from .ap_fixed_base import Base

class Unsigned(Base):
    """Base unsigned implementation 

    """

    @classmethod
    def _signed(cls) -> bool:
        return False

    def __neg__(self) -> None:
        """__neg__ method is blocked, as Unsigned cannot be negated

        Raises:
            NotImplementedError: Unsigned class cannot be negated
        """
        raise NotImplementedError(f'{self.__class__.__name__} class cannot be negated')
