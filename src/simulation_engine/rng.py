"""Seeded random number generator for deterministic simulations."""

import random
from typing import List, TypeVar

T = TypeVar("T")


class SeededRNG:
    """
    Deterministic random number generator with seed control.

    Provides reproducible random number generation for simulation scenarios.
    Same seed always produces same sequence of random values.
    """

    def __init__(self, seed: int) -> None:
        """
        Initialize RNG with specific seed.

        Args:
            seed: Integer seed for reproducibility
        """
        self.seed = seed
        self._rng = random.Random(seed)

    def reset(self) -> None:
        """Reset RNG to initial seed state."""
        self._rng.seed(self.seed)

    def uniform(self, a: float, b: float) -> float:
        """
        Generate random float from uniform distribution [a, b].

        Args:
            a: Lower bound (inclusive)
            b: Upper bound (inclusive)

        Returns:
            Random float in range [a, b]
        """
        return self._rng.uniform(a, b)

    def normal(self, mu: float, sigma: float) -> float:
        """
        Generate random float from normal (Gaussian) distribution.

        Args:
            mu: Mean of distribution
            sigma: Standard deviation

        Returns:
            Random float from normal distribution
        """
        return self._rng.normalvariate(mu, sigma)

    def exponential(self, lambd: float) -> float:
        """
        Generate random float from exponential distribution.

        Args:
            lambd: Rate parameter (1/mean)

        Returns:
            Random float from exponential distribution
        """
        return self._rng.expovariate(lambd)

    def choice(self, seq: List[T]) -> T:
        """
        Select random element from sequence.

        Args:
            seq: List of options to choose from

        Returns:
            Randomly selected element
        """
        return self._rng.choice(seq)
