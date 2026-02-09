# import tkinter as tk
# from tkinter import ttk, messagebox
from openpyxl import Workbook, load_workbook
import os


FILE_NAME = "ORDER_BOOKING_2025-26.xlsx"

# Open the spreadsheet
workbook = load_workbook(FILE_NAME)


# Get the first sheet
sheet = workbook.worksheets[0]

# Create a list to store the values
names = []

# Iterate over the rows in the sheet
for row in sheet:
    # Get the value of the first cell
    # in the row (the "Name" cell)
    name = row[0].value

    # pass
    # Add the value to the list
    names.append(name)
    print(name)
    if name == None:
        break

# Print the list of names
# print(names)
