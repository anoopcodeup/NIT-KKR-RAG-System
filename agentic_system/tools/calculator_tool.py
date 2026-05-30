"""
Calculator Tool for Agentic RAG System

This tool provides mathematical computation capabilities for fee calculations,
grade computations, and other numerical operations.
"""

import logging
import time
import re
import math
from typing import Dict, Any, Optional, Union
from langchain.tools import tool

logger = logging.getLogger(__name__)


class CalculatorTool:
    """Tool for performing mathematical calculations safely."""
    
    def __init__(self):
        """Initialize Calculator Tool."""
        self.supported_operations = {
            '+': 'addition',
            '-': 'subtraction', 
            '*': 'multiplication',
            '/': 'division',
            '**': 'exponentiation',
            '%': 'percentage'
        }
        logger.info("Calculator Tool initialized successfully")
    
    def calculate(self, expression: str) -> str:
        """
        Perform mathematical calculations and computations.
        
        Use for questions about:
        - Fee calculations and totals
        - Grade computations and GPA calculations
        - Statistical analysis
        - Currency conversions
        - Percentage calculations
        - Date and time calculations
        - Cost comparisons
        - Budget calculations
        
        Args:
            expression: Mathematical expression or calculation request
            
        Returns:
            Computed result with detailed explanation
        """
        start_time = time.time()
        
        try:
            # Parse the calculation request
            parsed_calc = self._parse_calculation_request(expression)
            
            if not parsed_calc:
                return "Unable to parse calculation request. Please provide a clear mathematical expression."
            
            # Perform calculation based on type
            result = self._perform_calculation(parsed_calc)
            
            execution_time = time.time() - start_time
            
            # Format result with explanation
            formatted_result = self._format_calculation_result(
                expression, parsed_calc, result
            )
            
            # Add execution metadata
            metadata = {
                "tool": "calculator",
                "execution_time": execution_time,
                "operation": parsed_calc.get("type", "unknown"),
                "expression": expression
            }
            
            logger.info(f"Calculation completed in {execution_time:.3f}s: {parsed_calc.get('type')}")
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"Error in calculation: {e}")
            return f"Error performing calculation: {str(e)}"
    
    def _parse_calculation_request(self, expression: str) -> Optional[Dict[str, Any]]:
        """
        Parse and understand the calculation request.
        
        Args:
            expression: User's calculation request
            
        Returns:
            Dict with parsed calculation details
        """
        try:
            # Clean and normalize expression
            clean_expr = expression.strip().lower()
            
            # Handle different types of calculations
            if self._is_simple_arithmetic(clean_expr):
                return self._parse_arithmetic(clean_expr)
            
            elif self._is_fee_calculation(clean_expr):
                return self._parse_fee_calculation(clean_expr)
            
            elif self._is_percentage_calculation(clean_expr):
                return self._parse_percentage_calculation(clean_expr)
            
            elif self._is_comparison_calculation(clean_expr):
                return self._parse_comparison_calculation(clean_expr)
            
            else:
                # Try as general arithmetic
                return self._parse_arithmetic(clean_expr)
                
        except Exception as e:
            logger.error(f"Error parsing calculation: {e}")
            return None
    
    def _is_simple_arithmetic(self, expr: str) -> bool:
        """Check if expression is simple arithmetic."""
        # Look for basic arithmetic operators
        arithmetic_pattern = r'^[\d\.\s\+\-\*/\%\(\)\**]+$'
        return bool(re.match(arithmetic_pattern, expr))
    
    def _is_fee_calculation(self, expr: str) -> bool:
        """Check if expression is fee calculation."""
        fee_keywords = ['fee', 'fees', 'cost', 'tuition', 'semester', 'year', 'total']
        return any(keyword in expr for keyword in fee_keywords)
    
    def _is_percentage_calculation(self, expr: str) -> bool:
        """Check if expression is percentage calculation."""
        return '%' in expr or 'percent' in expr
    
    def _is_comparison_calculation(self, expr: str) -> bool:
        """Check if expression is comparison calculation."""
        comparison_keywords = ['compare', 'difference', 'vs', 'versus', 'cheaper', 'expensive']
        return any(keyword in expr for keyword in comparison_keywords)
    
    def _parse_arithmetic(self, expr: str) -> Dict[str, Any]:
        """Parse simple arithmetic expression."""
        try:
            # Safe evaluation using Python's eval with restricted globals
            result = eval(expr, {"__builtins__": {}}, {})
            return {
                "type": "arithmetic",
                "expression": expr,
                "result": result
            }
        except:
            return None
    
    def _parse_fee_calculation(self, expr: str) -> Dict[str, Any]:
        """Parse fee calculation request."""
        # Extract numbers from expression
        numbers = re.findall(r'[\d,]+', expr)
        
        if len(numbers) >= 2:
            try:
                # Remove commas and convert to float
                amounts = [float(num.replace(',', '')) for num in numbers]
                
                return {
                    "type": "fee_calculation",
                    "amounts": amounts,
                    "operation": "sum" if "total" in expr else "individual"
                }
            except ValueError:
                return None
        
        return None
    
    def _parse_percentage_calculation(self, expr: str) -> Dict[str, Any]:
        """Parse percentage calculation."""
        # Extract percentage and base value
        percent_match = re.search(r'(\d+\.?\d*)\s*%?', expr)
        base_match = re.search(r'(\d+\.?\d*)', expr.replace('%', ''))
        
        if percent_match and base_match:
            try:
                percent = float(percent_match.group(1))
                base = float(base_match.group(1))
                
                return {
                    "type": "percentage",
                    "percentage": percent,
                    "base": base
                }
            except ValueError:
                return None
        
        return None
    
    def _parse_comparison_calculation(self, expr: str) -> Dict[str, Any]:
        """Parse comparison calculation."""
        numbers = re.findall(r'[\d,]+', expr)
        
        if len(numbers) >= 2:
            try:
                amounts = [float(num.replace(',', '')) for num in numbers]
                return {
                    "type": "comparison",
                    "amounts": amounts
                }
            except ValueError:
                return None
        
        return None
    
    def _perform_calculation(self, parsed_calc: Dict[str, Any]) -> Any:
        """Perform the actual calculation."""
        calc_type = parsed_calc.get("type")
        
        if calc_type == "arithmetic":
            return parsed_calc.get("result")
        
        elif calc_type == "fee_calculation":
            amounts = parsed_calc.get("amounts", [])
            operation = parsed_calc.get("operation", "sum")
            
            if operation == "sum":
                return sum(amounts)
            else:
                return amounts
        
        elif calc_type == "percentage":
            percent = parsed_calc.get("percentage", 0)
            base = parsed_calc.get("base", 0)
            return (percent / 100) * base
        
        elif calc_type == "comparison":
            amounts = parsed_calc.get("amounts", [])
            if len(amounts) >= 2:
                return {
                    "values": amounts,
                    "difference": amounts[0] - amounts[1] if amounts[0] > amounts[1] else amounts[1] - amounts[0],
                    "higher": max(amounts),
                    "lower": min(amounts)
                }
        
        return None
    
    def _format_calculation_result(self, original_expr: str, parsed_calc: Dict[str, Any], result: Any) -> str:
        """Format calculation result with explanation."""
        calc_type = parsed_calc.get("type")
        
        if calc_type == "arithmetic":
            return f"**Calculation Result:** {result}\n\nExpression: {original_expr}"
        
        elif calc_type == "fee_calculation":
            if isinstance(result, (int, float)):
                return f"**Fee Calculation:** ₹{result:,.2f}\n\nCalculation based on: {original_expr}"
            else:
                return f"**Fee Details:** {result}\n\nQuery: {original_expr}"
        
        elif calc_type == "percentage":
            return f"**Percentage Calculation:** {result:.2f}\n\n{parsed_calc.get('percentage', 0)}% of {parsed_calc.get('base', 0)} = {result}"
        
        elif calc_type == "comparison":
            if isinstance(result, dict):
                higher = result.get("higher", 0)
                lower = result.get("lower", 0)
                diff = result.get("difference", 0)
                
                return f"**Comparison Result:**\n"
                return f"- Higher amount: ₹{higher:,.2f}\n"
                return f"- Lower amount: ₹{lower:,.2f}\n"
                return f"- Difference: ₹{diff:,.2f}\n\n"
                return f"Query: {original_expr}"
        
        return f"**Calculation:** {result}\n\nQuery: {original_expr}"
    
    def get_calculation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about calculator tool.
        
        Returns:
            Dict[str, Any]: Tool statistics
        """
        return {
            "tool": "calculator",
            "status": "initialized",
            "supported_operations": list(self.supported_operations.keys()),
            "supported_types": ["arithmetic", "fee_calculation", "percentage", "comparison"]
        }
    
    def test_connection(self) -> bool:
        """
        Test if calculator tool is working properly.
        
        Returns:
            bool: True if tool is working
        """
        try:
            test_calculations = [
                ("2 + 2", "arithmetic"),
                ("10000 + 15000", "fee_calculation"),
                ("10% of 50000", "percentage")
            ]
            
            for expr, expected_type in test_calculations:
                parsed = self._parse_calculation_request(expr)
                if not parsed or parsed.get("type") != expected_type:
                    logger.error(f"Calculator test failed for: {expr}")
                    return False
            
            logger.info("Calculator tool test: PASSED")
            return True
            
        except Exception as e:
            logger.error(f"Calculator tool test failed: {e}")
            return False


# Factory function
def create_calculator_tool() -> CalculatorTool:
    """
    Factory function to create a Calculator Tool.
    
    Returns:
        CalculatorTool: Configured calculator tool
    """
    return CalculatorTool()


# LangChain tool wrapper function
@tool
def perform_calculation(expression: str) -> str:
    """
    Perform mathematical calculations and computations.
    
    This tool can handle:
    - Basic arithmetic operations (+, -, *, /, **, %)
    - Fee calculations and totals
    - Percentage calculations
    - Cost comparisons
    - Grade and GPA calculations
    - Currency conversions
    - Statistical operations
    
    Perfect for questions about:
    - "Calculate total fees for 4 years"
    - "What is 15% of 50000?"
    - "Compare costs between CSE and ECE"
    - "Add hostel and tuition fees"
    
    Args:
        expression: Mathematical expression or calculation request
        
    Returns:
        Detailed calculation result with explanation
    """
    try:
        # Create tool instance
        tool = create_calculator_tool()
        
        # Execute calculation
        result = tool.calculate(expression)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in calculation: {e}")
        return f"Unable to perform calculation: {str(e)}"


# Test function
def test_calculator_tool():
    """
    Test calculator tool functionality.
    """
    print("Testing Calculator Tool...")
    
    try:
        # Create tool
        tool = create_calculator_tool()
        
        # Test connection
        print("Testing connection...")
        is_connected = tool.test_connection()
        print(f"Connection test: {'PASSED' if is_connected else 'FAILED'}")
        
        if is_connected:
            # Test calculations
            test_calculations = [
                "2 + 2",
                "50000 + 60000 + 70000 + 80000",  # 4 year fees
                "15% of 75000",
                "compare 50000 and 60000"
            ]
            
            for expr in test_calculations:
                print(f"\nExpression: {expr}")
                result = tool.calculate(expr)
                print(f"Result: {result}")
        
        # Get stats
        stats = tool.get_calculation_stats()
        print(f"\nCalculator Stats: {stats}")
        
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    # Run test if executed directly
    test_calculator_tool()
