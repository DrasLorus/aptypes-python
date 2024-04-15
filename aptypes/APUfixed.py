from .APFixedBase import APFixedBase

class APUfixed(APFixedBase):
    """APFixedBase unsigned implementation 

    """

    @classmethod
    def _signed(cls) -> bool:
        return False
    
    def __neg__(self) -> None:
        """__neg__ method is blocked, as APUfixed cannot be negated

        Raises:
            NotImplementedError: APUfixed class cannot be negated
        """
        raise NotImplementedError(f'{self.__class__.__name__} class cannot be negated')