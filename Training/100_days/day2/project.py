# Tip Calculator
print("Welcome to the tip calculator!")
total_bill = float(input("What was the total bill? "))
tip = float(input("How much tip percentage would you like to give: \
                  10, 12, or 15? "))
people = float(input("How many people to split the bill? "))
person_to_pay = (tip / 100 * total_bill + total_bill) / people
print("Each person should pay : ", person_to_pay)
