#!/usr/bin/env python3
"""
Problem Statement Implementation

Generates output matching the problem statement:
1: 4-3-2-1
2: 4
3: 3
4: 3

This could represent:
- A countdown sequence
- State transitions
- Test case numbering
- Configuration values
"""


def generate_output():
    """Generate the exact output from problem statement."""
    print("1: 4-3-2-1")
    print("2: 4")
    print("3: 3")
    print("4: 3")


def generate_as_dict():
    """Return problem statement data as dictionary."""
    return {
        1: "4-3-2-1",
        2: 4,
        3: 3,
        4: 3
    }


def generate_as_list():
    """Return problem statement data as list of tuples."""
    return [
        (1, "4-3-2-1"),
        (2, 4),
        (3, 3),
        (4, 3)
    ]


if __name__ == "__main__":
    print("Problem Statement Output:")
    print("=" * 40)
    generate_output()
    print("\nAs Dictionary:")
    print(generate_as_dict())
    print("\nAs List:")
    print(generate_as_list())
