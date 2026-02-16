class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

s = Student("Alan", 20)
print(f"{s.name}, {s.age}")


class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        print(f"Deposited {amount}. Balance: {self.balance}")

    def withdraw(self, amount):
        if amount > self.balance:
            print("Insufficient funds!")
        else:
            self.balance -= amount
            print(f"Withdrew {amount}. Balance: {self.balance}")

acc = BankAccount("Alan", 1000)
acc.deposit(500)
acc.withdraw(200)
acc.withdraw(2000)


class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def distance_to(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

p1 = Point(0, 0)
p2 = Point(3, 4)
print(f"Distance: {p1.distance_to(p2)}")


class Book:
    def __init__(self, title, author, pages):
        self.title = title
        self.author = author
        self.pages = pages
        self.current_page = 0

    def read(self, pages):
        self.current_page = min(self.current_page + pages, self.pages)
        print(f"Reading '{self.title}' - page {self.current_page}/{self.pages}")

book = Book("Python Crash Course", "Eric Matthes", 544)
book.read(50)
book.read(100)
