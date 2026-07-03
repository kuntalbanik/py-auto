#
# This is very good data structure for creating choices or varieties
#

# import library
from enum import Enum, auto


class PizzaSize(Enum):
    """Sizes of pizza"""

    SMALL = 8
    MEDIUM = 10
    LARGE = 12


print(f"Pizza size is {PizzaSize.MEDIUM.value}")
