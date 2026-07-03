#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

#
# Compound interest calculation using while loop
#

# import my custom fuction
from function.functions import area

# import sys


principal: float = 1000
rate: float = 0.05
years = 5
year = 1

while year <= years:
    principal = principal * (1 + rate)
    print(year, principal)
    year += 1


print(area(25))

# string
new_string = "Hello World!"
print(new_string[::-1])
print(new_string.split(" "))

# First class object
#
items = {"number": 42, "text": "Hello"}

print(items["number"])
