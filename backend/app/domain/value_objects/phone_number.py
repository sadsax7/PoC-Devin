"""Value object para numero de telefono en formato E.164.

Valida que el numero de telefono cumpla con el formato internacional
E.164: +[codigo_pais][numero].
"""

import re


class PhoneNumber:
    """Numero de telefono inmutable en formato E.164.

    Attributes:
        value: Numero de telefono validado.
    """

    _E164_PATTERN: re.Pattern[str] = re.compile(r"^\+[1-9]\d{6,14}$")

    def __init__(self, value: str) -> None:
        """Inicializa el numero de telefono tras validar formato E.164.

        Args:
            value: Numero de telefono a validar.

        Raises:
            ValueError: Si el formato no es E.164 valido.
        """
        if not self._E164_PATTERN.match(value):
            raise ValueError(
                f"Phone number '{value}' does not match E.164 format (+[country_code][number])"
            )
        self._value = value

    @property
    def value(self) -> str:
        """Retorna el valor del numero de telefono.

        Returns:
            Numero de telefono en formato E.164.
        """
        return self._value

    def ends_with(self, suffix: str) -> bool:
        """Verifica si el numero termina con un sufijo dado.

        Args:
            suffix: Sufijo a verificar.

        Returns:
            True si el numero termina con el sufijo.
        """
        return self._value.endswith(suffix)

    def __eq__(self, other: object) -> bool:
        """Compara igualdad por valor.

        Args:
            other: Objeto a comparar.

        Returns:
            True si ambos tienen el mismo valor.
        """
        if not isinstance(other, PhoneNumber):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Retorna hash basado en el valor.

        Returns:
            Hash del valor del numero.
        """
        return hash(self._value)

    def __repr__(self) -> str:
        """Representacion del objeto.

        Returns:
            Representacion en string.
        """
        return f"PhoneNumber(value='{self._value}')"
