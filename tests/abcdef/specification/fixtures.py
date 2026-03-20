"""Test fixtures for specification module."""

from abcdef.specification.specification import Specification


class Person:
    """Simple domain object for specification testing."""

    def __init__(self, age: int, email: str) -> None:
        """Initialize a Person with age and email.

        Args:
            age: The person's age.
            email: The person's email address.
        """
        self.age = age
        self.email = email


class IsAdult(Specification[Person]):
    """Specification: adult candidates are 18 or older."""

    def is_satisfied_by(self, candidate: Person) -> bool:
        """Return True if the candidate is 18 or older.

        Args:
            candidate: The person to evaluate.

        Returns:
            True if age >= 18, False otherwise.
        """
        return candidate.age >= 18


class HasValidEmail(Specification[Person]):
    """Specification: valid emails contain '@'."""

    def is_satisfied_by(self, candidate: Person) -> bool:
        """Return True if the candidate's email contains '@'.

        Args:
            candidate: The person to evaluate.

        Returns:
            True if email contains '@', False otherwise.
        """
        return "@" in candidate.email
