#!/usr/bin/env python3

#
# Type Hinting - Optional Static type Checking in python
#

food: str = "Milk"
pizza_base: str = "Thin"
topping: str = "Olives"
pizza_size: int = 12
price: float = 8.99


print(f"Louis is going to drink {food}")

food = False
# This error only occurred when mypy type checker installed on vscode

print(f"Pizza size {pizza_size} inches, Base {pizza_base}, Topping {topping}")
order_details: str = (
    """Pizza size {pizza_size} inches, Base {pizza_base}, Topping {topping}"""
)
print(order_details)
