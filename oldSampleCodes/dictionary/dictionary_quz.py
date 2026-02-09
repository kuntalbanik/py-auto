#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

# =================================================================
# 🔥 Python Challenges: List of Dictionaries Edition
# (All questions in English, as you requested)
# -------------------------------------------------

students = [
    {"name": "Rahim", "age": 18},
    {"name": "Karim", "age": 20},
    {"name": "Nusrat", "age": 19},
]

# 🔹 Challenge 1: (Basic)
# Print the name of each student from the list.

for student in students:
    print(student["name"])


# 🔹 Challenge 2: (Basic)
# Print the name and age of the student whose age is exactly 20.

print("Challenge 2: (Basic)")
for student in students:
    if student["age"] == 20:
        print(student["name"])


# 🔹 Challenge 3: (Medium)
# Create a list of names of students who are 19 or older.

print("Challenge 3: (Medium)")
student_names = []
for student in students:
    if student["age"] >= 19:
        student_names.append(student["name"])

print(student_names)


# 🔹 Challenge 4: (Medium)
# Add a new key   "passed": True   to each student dictionary.

print("Challenge 4: (Medium)")
for student in students:
    student["passed"] = True

print(students)


# 🔹 Challenge 5: (Advanced)
# Count how many students are older than 18.

print("Challenge 5: (Advanced)")
student_counter = 0
for student in students:
    if student["age"] > 18:
        student_counter += 1

print(student_counter)


# 🧠 Bonus Challenge: (Expert)
# From a list of employee dictionaries, find the person with the highest salary.

print("Bonus Challenge: (Expert)")
employees = [
    {"name": "Asha", "salary": 50000},
    {"name": "Bashir", "salary": 75000},
    {"name": "Chumki", "salary": 68000},
]
emp_max = []
for emp in employees:
    emp_max.append(emp["salary"])

print(max(emp_max))
