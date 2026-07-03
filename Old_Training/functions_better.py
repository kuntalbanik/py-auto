"""
Functions output simple greetings

'->' after function this symbol means return type

"""


# Returns a message with the type of string
def greeter(name: str) -> str:
    """Greet to others"""
    return f"{name}"


def main() -> None:
    friends: list[str] = ["John", "Jane", "Chiko", "Ziko"]
    for friend in friends:
        if greeter(friend) == "John":
            print("He is my best friend. ", greeter(friend))
        else:
            print(greeter(friend))


# Invokes the main function
# Printing current file name

print(__name__)
main()

# print docsting of the function
print(greeter.__doc__)

# print(data)
