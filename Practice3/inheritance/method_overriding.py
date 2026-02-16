class Animal:
    def speak(self):
        print("Some generic animal sound")

    def __str__(self):
        return "Animal"


class Dog(Animal):
    def speak(self):
        print("Woof! Woof!")

    def __str__(self):
        return "Dog"


class Cat(Animal):
    def speak(self):
        print("Meow!")

    def __str__(self):
        return "Cat"


class Snake(Animal):
    def speak(self):
        print("Hiss!")

    def __str__(self):
        return "Snake"


animals = [Dog(), Cat(), Snake(), Animal()]
for animal in animals:
    print(f"{animal}: ", end="")
    animal.speak()


class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def calculate_bonus(self):
        return self.salary * 0.1

    def __str__(self):
        return f"{self.name} (bonus: {self.calculate_bonus()})"


class Manager(Employee):
    def calculate_bonus(self):
        return self.salary * 0.2


class Director(Employee):
    def calculate_bonus(self):
        return self.salary * 0.3


employees = [
    Employee("Alan", 100000),
    Manager("Marat", 150000),
    Director("Dana", 200000),
]

print()
for emp in employees:
    print(emp)


class PaymentProcessor:
    def process(self, amount):
        raise NotImplementedError("Subclasses must implement process()")


class CreditCardPayment(PaymentProcessor):
    def process(self, amount):
        print(f"Processing credit card payment: ${amount}")


class PayPalPayment(PaymentProcessor):
    def process(self, amount):
        print(f"Processing PayPal payment: ${amount}")


print()
payments = [CreditCardPayment(), PayPalPayment()]
for payment in payments:
    payment.process(99.99)
