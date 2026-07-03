# syntax
# variable_name: data_type = value

name: str = "John"
age: int = 30
height: float = 5.9
is_student: bool = True

numbers: list[int] = [1, 2, 3, 4, 5]
user_info: dict[str, str] = {"name": "John", "age": "30"}
demo_set: set[int] = {1, 2, 3, 4, 5}
demo_none: None = None


# Function arguments and return types
#
# syntax
# def function_name(parameter: data_type) -> return_type:
#     return value


def add_numbers(a: int, b: int) -> int:
    return a + b


result: int = add_numbers(1, 2)
print(result)


# complete example
# ১. ভ্যারিয়েবল অ্যানোটেশন
hotel_name: str = "Grand Bengal"


# ২. ফাংশন আর্গুমেন্ট এবং রিটার্ন টাইপ অ্যানোটেশন
def calculate_bill(room_rent: float, days: int, discount: float = 0.0) -> float:
    total: float = room_rent * days
    net_payable: float = total - (total * discount)
    return net_payable


# ফাংশন কল করা
final_bill: float = calculate_bill(room_rent=3500.50, days=3, discount=0.10)

# আউটপুট প্রিন্ট
print(f"Hotel: {hotel_name}")
print(f"Total Bill: {final_bill} BDT")
