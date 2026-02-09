#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

#
# Simple tuples with examples
#

numbers = (10, 20, 30, 40)
print(numbers)


# 🔹 Challenge 2: (Basic)
# Access and print the second item from the following tuple:

colors = ("red", "green", "blue", "yellow")
print(colors[1])


# 🔹 Challenge 4: (Medium)
# Check if the value "blue" exists in the tuple colors and print "Found" if it does.

if "blue" in colors:
    print("Found")


# 🔹 Challenge 5: (Medium)
# Write a loop to print each item in the tuple:

numbers = (1, 2, 3, 4, 5)
index = 0

while index < len(numbers):
    print(numbers[index])
    index += 1
