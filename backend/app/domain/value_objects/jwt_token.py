"""Value object para token JWT.

Encapsula un token JWT validando que no este vacio
y proporcionando acceso seguro a su valor.
"""


class JwtToken:
    """Token JWT inmutable.

    Attributes:
        value: Cadena del token JWT.
    """

    def __init__(self, value: str) -> None:
        """Inicializa el token JWT.

        Args:
            value: Cadena del token JWT.

        Raises:
            ValueError: Si el token esta vacio.
        """
        if not value:
            raise ValueError("JWT token cannot be empty")
        self._value = value

    @property
    def value(self) -> str:
        """Retorna el valor del token.

        Returns:
            Cadena del token JWT.
        """
        return self._value

    def last_four(self) -> str:
        """Retorna los ultimos 4 caracteres del token para logging seguro.

        Returns:
            Ultimos 4 caracteres del token.
        """
        return self._value[-4:]

    def __eq__(self, other: object) -> bool:
        """Compara igualdad por valor.

        Args:
            other: Objeto a comparar.

        Returns:
            True si ambos tienen el mismo valor.
        """
        if not isinstance(other, JwtToken):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Retorna hash basado en el valor.

        Returns:
            Hash del valor.
        """
        return hash(self._value)

    def __repr__(self) -> str:
        """Representacion segura del objeto (no expone el token completo).

        Returns:
            Representacion en string con solo ultimos 4 caracteres.
        """
        return f"JwtToken(value='...{self.last_four()}')"
