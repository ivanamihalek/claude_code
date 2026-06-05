# Python program to calculate pi to the 5th digit

from decimal import Decimal, getcontext

def calculate_pi(precision=5):
    """
    Calculate pi to the specified decimal precision using the Machin formula.
    
    The Machin formula: pi = 16*arctan(1/5) - 4*arctan(1/239)
    
    Args:
        precision: Number of decimal places to calculate (default: 5)
    
    Returns:
        float: Pi rounded to the specified precision
    """
    # Set precision higher than needed to avoid rounding errors
    getcontext().prec = precision + 10
    
    def arctan(x, num_terms):
        """Calculate arctan using Taylor series"""
        getcontext().prec = precision + 10
        x = Decimal(x)
        power = x
        result = power
        
        for n in range(1, num_terms):
            power *= -x * x
            result += power / (2 * n + 1)
        
        return result
    
    # Use Machin's formula: pi = 16*arctan(1/5) - 4*arctan(1/239)
    num_terms = precision + 10
    pi = 4 * (4 * arctan(Decimal(1) / Decimal(5), num_terms) - 
              arctan(Decimal(1) / Decimal(239), num_terms))
    
    # Convert to float and round to specified precision
    return float(round(pi, precision))


# Defining main function
def main():
    pi_value = calculate_pi(5)
    print(f"Pi to 5 decimal places: {pi_value}")


# Using the special variable
# __name__
if __name__=="__main__":
    main()