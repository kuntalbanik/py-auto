#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

#
# Concept of sets
#
# set কী?
# Python এ set হলো একটি unordered collection যেখানে প্রতিটি উপাদান ইউনিক (অর্থাৎ, কোনো ডুপ্লিকেট থাকতে পারে না)।
# ✅ মূল বৈশিষ্ট্য:
# প্রতিটি মান একবারই থাকতে পারে।
# set এ index নেই → তাই আমরা ordered access (যেমন myset[0]) করতে পারি না।
# ডুপ্লিকেট নিজে থেকেই সরিয়ে ফেলে।
#
#

number_set = {1, 2, 3, 3, 4, 4, 5, 5}
print(number_set)


# Challenge 2: (Basic)
# Add the number 6 to the following set and print the updated set.
# my_set = {1, 2, 3, 4, 5}

my_set = {1, 2, 3, 4, 5}
output = 0
for data in my_set:
    output += data

print(output)


# 🔹 Challenge 3: (Basic)
# Remove the element 3 from the set without using del.

my_set = {1, 2, 3, 4, 5}
my_set.remove(3)  # Remove value based on key
print(my_set)


# 🔹 Challenge 4: (Medium)
# Check if the number 4 exists in the following set:
# nums = {1, 3, 5, 7, 4, 9}
# If yes, print "Found", otherwise print "Not Found".

nums = {1, 3, 5, 7, 4, 9}

if 4 in nums:
    print("Found")
else:
    print("Not Found")


# 🔹 Challenge 5: (Medium)
# Convert this list to a set to remove duplicates:
# data = [1, 2, 2, 3, 4, 4, 5, 1]
# Then convert it back to a list and print it.

data = [1, 2, 2, 3, 4, 4, 5, 1]
data = list(set(data))
print(data)


# 🔹 Challenge 6: (Medium → Advanced)
# Find the common elements between two sets:
# a = {1, 2, 3, 4}
# b = {3, 4, 5, 6}
# Use a set operation to find the intersection.

a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

print(a.intersection(b))


# 🔹 Challenge 7: (Advanced)
# You are given two sets. Print the elements that are in the first set but not in the second.
# a = {10, 20, 30, 40}
# b = {30, 40, 50, 60}

a = {10, 20, 30, 40}
b = {30, 40, 50, 60}

print(a.difference(b))


# 🔹 Challenge 8: (Advanced)
# You are given a sentence as a string. Print all the unique letters used in that sentence.
# sentence = "Python programming is fun"
# (Hint: Use set() with the string.)

sentence = "Python programming is fun"
print(set(sentence))


# 🏁 Bonus Challenge (Expert-level):
# Given a list of words, print the words that have all unique letters (no repeated characters).
# words = ["python", "apple", "mango", "kite", "bubble"]

words = ["python", "apple", "mango", "kite", "bubble"]

for word in words:
    if len(word) == len(set(word)):
        print(word)
