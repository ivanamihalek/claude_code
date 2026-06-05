# Test file for the pi calculation function

import sys
from main import calculate_pi

def test_pi_calculation():
    """Test the pi calculation function"""
    
    print("Testing pi calculation function...")
    print("-" * 50)
    
    # Test 1: Calculate pi to 5 decimal places
    pi_5 = calculate_pi(5)
    expected_5 = 3.14159
    print(f"Test 1: Pi to 5 decimal places")
    print(f"  Result:   {pi_5}")
    print(f"  Expected: {expected_5}")
    assert abs(pi_5 - expected_5) < 0.00001, f"Failed: {pi_5} != {expected_5}"
    print("  ✓ PASSED\n")
    
    # Test 2: Calculate pi to 10 decimal places
    pi_10 = calculate_pi(10)
    expected_10 = 3.1415926536
    print(f"Test 2: Pi to 10 decimal places")
    print(f"  Result:   {pi_10}")
    print(f"  Expected: {expected_10}")
    # Allow small floating point errors
    assert abs(pi_10 - expected_10) < 0.0000000001, f"Failed: {pi_10} != {expected_10}"
    print("  ✓ PASSED\n")
    
    # Test 3: Calculate pi to 3 decimal places
    pi_3 = calculate_pi(3)
    expected_3 = 3.142
    print(f"Test 3: Pi to 3 decimal places")
    print(f"  Result:   {pi_3}")
    print(f"  Expected: {expected_3}")
    assert abs(pi_3 - expected_3) < 0.001, f"Failed: {pi_3} != {expected_3}"
    print("  ✓ PASSED\n")
    
    # Test 4: Calculate pi with default precision (5)
    pi_default = calculate_pi()
    print(f"Test 4: Pi with default precision")
    print(f"  Result: {pi_default}")
    assert 3.14159 <= pi_default <= 3.14160, f"Failed: Result out of range"
    print("  ✓ PASSED\n")
    
    print("-" * 50)
    print("All tests passed! ✓")

if __name__ == "__main__":
    try:
        test_pi_calculation()
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        sys.exit(1)
