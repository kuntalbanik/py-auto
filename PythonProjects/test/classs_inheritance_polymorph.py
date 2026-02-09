"""
Example of class, inheritance & polymorphism

"""

class Animal:
    def __init__(self, name: str, age: int, num_legs: int) -> None:
        # Create & initialize instance variables
        self.name = name
        self.age = age
        self.num_legs = num_legs

    def __str__(self) -> str:
        return f"Name : {self.name}"
    
    def talk(self) -> None:
        print(f"{self.name} not talk yet...")
    
# 
# 
class Dog(Animal):
    # inherit from Animal class
    def __init__(self, name: str, age: int, num_legs: int, breed: str) -> None:
        super().__init__(name, age, num_legs)
        self.breed = breed
        self.type = "Dog" # Add extra variable type="Dog"

    def __str__(self) -> str:
        return f"{self.type} : {self.name}, 'Breed' : {self.breed}"
    
    def talk(self) -> None:
        print(f"{self.name} says wog...")

    def sniff(self, item: str) -> None:
        print(f"{self.name} is sniffing {item}")


# Create animal object
a1 = Animal("Rob",8,4)
print(a1)

# Create dog object
d1 = Dog("Why",7,4,"Spenial")
print(d1)
d1.talk()
