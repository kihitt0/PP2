class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

calc = Calculator()
print(f"5 + 3 = {calc.add(5, 3)}")
print(f"10 - 4 = {calc.subtract(10, 4)}")
print(f"6 * 7 = {calc.multiply(6, 7)}")


class Pizza:
    def __init__(self, size):
        self.size = size
        self.toppings = []

    def add_topping(self, topping):
        self.toppings.append(topping)
        return self

    def show(self):
        print(f"{self.size} pizza with {', '.join(self.toppings)}")

pizza = Pizza("Large")
pizza.add_topping("cheese").add_topping("mushrooms").add_topping("pepperoni")
pizza.show()


class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def to_fahrenheit(self):
        return self.celsius * 9/5 + 32

    def to_kelvin(self):
        return self.celsius + 273.15

    @classmethod
    def from_fahrenheit(cls, f):
        return cls((f - 32) * 5/9)

    @staticmethod
    def is_freezing(celsius):
        return celsius <= 0

t = Temperature(100)
print(f"100C = {t.to_fahrenheit()}F = {t.to_kelvin()}K")

t2 = Temperature.from_fahrenheit(212)
print(f"212F = {t2.celsius}C")

print(f"Is 0C freezing? {Temperature.is_freezing(0)}")
print(f"Is 25C freezing? {Temperature.is_freezing(25)}")
