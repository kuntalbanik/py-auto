#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

#
# Simple list example
#
#

my_list = [1, 2, 3, 4, 5, 6]
print(my_list)


#
# List comprehension
#
# Rules
# new_list = [যা_রাখবো for উপাদান in উৎস if শর্ত]
# [expression for item in iterable if condition]
#
# 🎯 চ্যালেঞ্জ: নিচের কাজগুলো করো List Comprehension দিয়ে:


# ১ থেকে ১০ পর্যন্ত সংখ্যার বর্গের তালিকা তৈরি করো
number_list = [x * x for x in range(1, 11)]
print(number_list)


# একটি স্ট্রিং লিস্ট থেকে শুধু যেগুলোতে ‘a’ আছে, সেগুলো বের করো
string_list = ["amit", "korolo", "kimka", "motton", "chicken", "john", "rock", "chika"]
newstring_list = [str_lst for str_lst in string_list if "a" in str_lst]
print(newstring_list)


# একটি লিস্ট থেকে ডুপ্লিকেট বাদ দিয়ে নতুন লিস্ট বানাও
dup_list = ["John", "Jane", "John", "Kula", "Mapi", "Hana", "Jana", "Mapi"]
dup_list_new = list(set(dup_list))
print(dup_list_new)


# ===============================================================
# Challenge 3: (Medium)
# From a list of numbers, create a new list that contains only the square of odd numbers.

# numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
new_numbers = [num * num for num in numbers if num % 2 == 0]
print(new_numbers)


# Challenge 4: (Medium → Advanced)
# Given a list of names, create a new list that contains only those names that are 5 or more characters long.
# names = ["Rafi", "Karim", "Nusrat", "Zara", "Nayeem", "Tanvir"]

names = ["Rafi", "Karim", "Nusrat", "Zara", "Nayeem", "Tanvir"]
new_names = [name for name in names if len(name) >= 5]
print(new_names)


# Challenge 5: (Advanced)
# Given the following list of strings, create a new list containing only those that start and end with the same letter.
# words = ["radar", "level", "python", "noon", "apple", "civic"]

words = ["radar", "level", "python", "noon", "apple", "civic"]
new_words = [word for word in words if word[0] == word[-1]]
print(new_words)
