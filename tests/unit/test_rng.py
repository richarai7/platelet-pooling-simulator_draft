"""Tests for SeededRNG module."""
import pytest
from simulation_engine.rng import SeededRNG


class TestSeededRNG:
    """Test deterministic random number generation."""

    def test_same_seed_produces_same_sequence(self) -> None:
        """Verify identical seeds produce identical random sequences."""
        rng1 = SeededRNG(seed=42)
        rng2 = SeededRNG(seed=42)

        sequence1 = [rng1.uniform(0, 100) for _ in range(10)]
        sequence2 = [rng2.uniform(0, 100) for _ in range(10)]

        assert sequence1 == sequence2

    def test_different_seeds_produce_different_sequences(self) -> None:
        """Verify different seeds produce different random sequences."""
        rng1 = SeededRNG(seed=42)
        rng2 = SeededRNG(seed=99)

        sequence1 = [rng1.uniform(0, 100) for _ in range(10)]
        sequence2 = [rng2.uniform(0, 100) for _ in range(10)]

        assert sequence1 != sequence2

    def test_uniform_distribution(self) -> None:
        """Test uniform random distribution within range."""
        rng = SeededRNG(seed=42)
        values = [rng.uniform(10.0, 20.0) for _ in range(100)]

        assert all(10.0 <= v <= 20.0 for v in values)
        assert min(values) < 12.0  # Should explore lower range
        assert max(values) > 18.0  # Should explore upper range

    def test_normal_distribution(self) -> None:
        """Test normal (Gaussian) distribution."""
        rng = SeededRNG(seed=42)
        values = [rng.normal(mu=50.0, sigma=10.0) for _ in range(1000)]

        mean = sum(values) / len(values)
        assert 45.0 < mean < 55.0  # Mean should be ~50 with tolerance

    def test_exponential_distribution(self) -> None:
        """Test exponential distribution."""
        rng = SeededRNG(seed=42)
        lambd = 0.5
        values = [rng.exponential(lambd) for _ in range(1000)]

        # All values should be positive
        assert all(v >= 0 for v in values)
        # Mean should be approximately 1/lambda
        mean = sum(values) / len(values)
        expected_mean = 1 / lambd
        assert 0.8 * expected_mean < mean < 1.2 * expected_mean

    def test_choice_from_list(self) -> None:
        """Test random choice from list."""
        rng = SeededRNG(seed=42)
        options = ["A", "B", "C", "D"]
        choices = [rng.choice(options) for _ in range(100)]

        # All choices should be from options
        assert all(c in options for c in choices)
        # Should have selected multiple different options
        assert len(set(choices)) >= 3

    def test_seed_reset(self) -> None:
        """Test resetting RNG to initial seed state."""
        rng = SeededRNG(seed=42)
        
        sequence1 = [rng.uniform(0, 100) for _ in range(5)]
        rng.reset()
        sequence2 = [rng.uniform(0, 100) for _ in range(5)]

        assert sequence1 == sequence2
