"""Generic class registry."""


class ClassRegistry[T]:
    """Generic registry mapping string keys to values of type T.

    A plain, injectable class with no global state. Callers create an instance and
    register entries explicitly. Duplicate keys are rejected at registration time.

    Typical use: map stable string identifiers to concrete subclasses for
    deserialisation or dynamic dispatch.

    Example::

        registry: ClassRegistry[type[MyBase]] = ClassRegistry()
        registry.register("my_key", MyConcreteClass)
        cls = registry.get("my_key")  # returns MyConcreteClass
    """

    def __init__(self) -> None:
        """Initialise with an empty registry."""
        self._registry: dict[str, T] = {}

    def register(self, key: str, value: T) -> None:
        """Register a value under a key.

        Args:
            key: The stable string identifier.
            value: The value to register.

        Raises:
            TypeError: If the key is already registered.
        """
        if key in self._registry:
            existing = self._registry[key]
            existing_name = (
                existing.__qualname__  # type: ignore[attr-defined]
                if hasattr(existing, "__qualname__")
                else repr(existing)
            )
            raise TypeError(
                f"'{key}' is already registered "
                f"by {existing_name}. "
                f"Each key must be unique."
            )
        self._registry[key] = value

    def get(self, key: str) -> T:
        """Look up a registered value by key.

        Args:
            key: The stable string identifier.

        Returns:
            The value registered under that key.

        Raises:
            KeyError: If no value is registered for the given key.
        """
        return self._registry[key]
