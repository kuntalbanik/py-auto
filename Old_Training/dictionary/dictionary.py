#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

#
# Simple dictionary example
#

# 🔹 Challenge 1: (Basic)
# Create a dictionary with keys "name", "age", and "country" and assign any values to them. Then print the dictionary.

person = {"name": "John", "age": 20, "country": "UAE"}

print(person)
print(person["name"])


# 🔹 Challenge 2: (Basic)
# Access and print the value associated with the "age" key from the following dictionary:
# person = {"name": "Nadia", "age": 25, "city": "Dhaka"}

person = {"name": "Nadia", "age": 25, "city": "Dhaka"}
print(person["age"])


# 🔹 Challenge 3: (Basic)
# Add a new key "email" with any email address to the person dictionary above.

person["email"] = "john@abc.com"
print(person)


# 🔹 Challenge 4: (Medium)
# Write a loop to print all key-value pairs from the following dictionary:
# marks = {"math": 80, "english": 75, "science": 90}

marks = {"math": 80, "english": 75, "science": 90}

for key, val in marks.items():
    print(key, " - ", val)


# 🔹 Challenge 5: (Medium)
# Count how many keys are in this dictionary:
# data = {"a": 1, "b": 2, "c": 3, "d": 4}

data = {"a": 1, "b": 2, "c": 3, "d": 4}
data_count = 0
for d in data.keys():
    data_count += 1
print(data_count)
# Second option

print(len(data))


# 🔹 Challenge 6: (Medium → Advanced)
# You are given a dictionary of prices. Print only the items whose price is more than 100.
products = {"pen": 20, "notebook": 55, "bag": 120, "shoes": 250, "pencil": 10}

products_above_hundred = [pr for pr, val in products.items() if val >= 100]
print(products_above_hundred)


# 🔹 Challenge 7: (Advanced)
# Given a list of names, count how many times each name appears using a dictionary.
# 🔍 Hint: Use a loop + if name not in dict

names = ["rahim", "karim", "rahim", "naim", "karim", "rahim"]

name_counts = {}
for name in names:
    if name not in name_counts:
        name_counts[name] = 1
    else:
        name_counts[name] += 1

print(name_counts)
