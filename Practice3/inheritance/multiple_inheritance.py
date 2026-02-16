class Flyable:
    def fly(self):
        print(f"{self.name} is flying")


class Swimmable:
    def swim(self):
        print(f"{self.name} is swimming")


class Walkable:
    def walk(self):
        print(f"{self.name} is walking")


class Duck(Flyable, Swimmable, Walkable):
    def __init__(self, name):
        self.name = name

duck = Duck("Donald")
duck.fly()
duck.swim()
duck.walk()


class Engine:
    def start_engine(self):
        print("Engine started")

class Electric:
    def charge(self):
        print("Charging battery")

class HybridCar(Engine, Electric):
    def __init__(self, brand):
        self.brand = brand

    def info(self):
        print(f"{self.brand} Hybrid")

car = HybridCar("Toyota")
car.info()
car.start_engine()
car.charge()


class A:
    def greet(self):
        print("Hello from A")

class B(A):
    def greet(self):
        print("Hello from B")

class C(A):
    def greet(self):
        print("Hello from C")

class D(B, C):
    pass

d = D()
d.greet()
print(f"\nMRO: {[cls.__name__ for cls in D.__mro__]}")


class JSONMixin:
    def to_json(self):
        import json
        return json.dumps(self.__dict__)

class CSVMixin:
    def to_csv(self):
        return ",".join(str(v) for v in self.__dict__.values())

class User(JSONMixin, CSVMixin):
    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email

user = User("Alan", 20, "alan@example.com")
print(f"\nJSON: {user.to_json()}")
print(f"CSV: {user.to_csv()}")
