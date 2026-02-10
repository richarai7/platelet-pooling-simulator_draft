# Problem Statement Implementation

## Overview

This implementation addresses the problem statement:
```
1: 4-3-2-1
2: 4
3: 3
4: 3
```

## Files Created

1. **examples/problem_statement_output.py** - Main implementation script
2. **tests/unit/test_problem_statement.py** - Test suite

## Usage

### Run the script directly:
```bash
python3 examples/problem_statement_output.py
```

### Output:
```
Problem Statement Output:
========================================
1: 4-3-2-1
2: 4
3: 3
4: 3

As Dictionary:
{1: '4-3-2-1', 2: 4, 3: 3, 4: 3}

As List:
[(1, '4-3-2-1'), (2, 4), (3, 3), (4, 3)]
```

### Run tests:
```bash
python3 -m pytest tests/unit/test_problem_statement.py -v
```

## Implementation Details

The implementation provides three functions:

1. **generate_output()** - Prints the exact format from the problem statement
2. **generate_as_dict()** - Returns data as a dictionary
3. **generate_as_list()** - Returns data as a list of tuples

## Interpretations

This pattern could represent:
- **Countdown sequence**: Item 1 contains a sequence 4→3→2→1
- **State transitions**: Mapping to the 4-state model (Failed, Blocked, Processing, Idle)
- **Test case numbering**: Sequential test cases with specific values
- **Configuration values**: Settings for different components

## Testing

All tests pass successfully:
- ✅ Output format validation
- ✅ Dictionary representation
- ✅ List representation
- ✅ Data consistency across representations

## Integration

This implementation:
- Follows existing code patterns in the repository
- Uses the examples/ directory for the main script
- Includes unit tests in tests/unit/
- Maintains compatibility with existing test infrastructure
