class Animal:
    def __init__(self, name, sound):
        self.name = name
        self.sound = sound

    def speak(self):
        print(f"{self.name} says {self.sound}!")

    def info(self):
        print(f"I am {self.name}")


class Dog(Animal):
    def fetch(self, item):
        print(f"{self.name} fetches the {item}")


class Cat(Animal):
    def purr(self):
        print(f"{self.name} is purring...")


dog = Dog("Rex", "Woof")
dog.speak()
dog.info()
dog.fetch("ball")

cat = Cat("Whiskers", "Meow")
cat.speak()
cat.purr()

print(f"Is dog an Animal? {isinstance(dog, Animal)}")
print(f"Is Dog subclass of Animal? {issubclass(Dog, Animal)}")


class Vehicle:
    def __init__(self, brand, year):
        self.brand = brand
        self.year = year

    def start(self):
        print(f"{self.brand} ({self.year}) started")


class ElectricCar(Vehicle):
    def charge(self):
        print(f"{self.brand} is charging...")

tesla = ElectricCar("Tesla", 2024)
tesla.start()
tesla.charge()
