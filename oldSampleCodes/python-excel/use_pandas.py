import pandas as pd


FILE_NAME = "ORDER_BOOKING_2025-26.xlsx"
# df = pd.read_excel(FILE_NAME)  # default: first sheet
df = pd.read_excel(
    FILE_NAME, usecols=["CUSTOMER NAME", "SO NO."]
)  # default: first sheet

# print(df)

for data in df:
    print(data)
