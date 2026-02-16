class Dog:
    pass

my_dog = Dog()
print(type(my_dog))


class Cat:
    def meow(self):
        print("Meow!")

cat = Cat()
cat.meow()


class Person:
    def say_hello(self):
        print("Hello, I am a person")

    def say_goodbye(self):
        print("Goodbye!")

p = Person()
p.say_hello()
p.say_goodbye()


class Car:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

    def info(self):
        print(f"{self.brand} {self.model}")

car1 = Car("Toyota", "Camry")
car2 = Car("BMW", "X5")
car1.info()
car2.info()


class Circle:
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14159 * self.radius ** 2

    def perimeter(self):
        return 2 * 3.14159 * self.radius

c = Circle(5)
print(f"Area: {c.area()}")
print(f"Perimeter: {c.perimeter()}")
