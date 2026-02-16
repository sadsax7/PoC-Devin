"""Value object para contrasena hasheada.

Encapsula el hash de una contrasena, asegurando que nunca
se almacena en texto plano.
"""


class HashedPassword:
    """Contrasena hasheada inmutable.

    Attributes:
        value: Hash de la contrasena.
    """

    def __init__(self, value: str) -> None:
        """Inicializa la contrasena hasheada.

        Args:
            value: Hash de la contrasena.

        Raises:
            ValueError: Si el hash esta vacio.
        """
        if not value:
            raise ValueError("Password hash cannot be empty")
        self._value = value

    @property
    def value(self) -> str:
        """Retorna el valor del hash.

        Returns:
            Hash de la contrasena.
        """
        return self._value

    def __eq__(self, other: object) -> bool:
        """Compara igualdad por valor.

        Args:
            other: Objeto a comparar.

        Returns:
            True si ambos tienen el mismo hash.
        """
        if not isinstance(other, HashedPassword):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Retorna hash basado en el valor.

        Returns:
            Hash del valor.
        """
        return hash(self._value)

    def __repr__(self) -> str:
        """Representacion segura del objeto (no expone el hash).

        Returns:
            Representacion en string sin exponer el hash.
        """
        return "HashedPassword(value='***')"
