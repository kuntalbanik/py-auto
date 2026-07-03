#!/usr/bin/python3

#
# Simple number guessing game. User input their numbers and checked by the system.
# If lower then return 'Too Low' and if higher then return 'Too High'.
#
# Project reference link : https://www.geeksforgeeks.org/python/python-projects-beginner-to-advanced/
#


import random

generatedNumber: int = random.randint(1, 10)
print(generatedNumber)

print(f"Welcome to number guessing game.\nPlease enter number within 1-10.")
counter = 0

while True:

    enteredNumber: int = int(input("> "))
    if enteredNumber == generatedNumber:
        print(f"You won! with {counter} try")
        break
    elif enteredNumber > generatedNumber:
        print("Too High")
    elif enteredNumber < generatedNumber:
        print("Too Low")
    counter += 1
    # if counter > 4:
    #     print("You Loose")
    #     break
