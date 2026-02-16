class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def info(self):
        print(f"Name: {self.name}, Age: {self.age}")


class Student(Person):
    def __init__(self, name, age, university):
        super().__init__(name, age)
        self.university = university

    def info(self):
        super().info()
        print(f"University: {self.university}")


s = Student("Alan", 20, "SDU")
s.info()


class Shape:
    def __init__(self, color):
        self.color = color

    def describe(self):
        print(f"Shape color: {self.color}")


class Rectangle(Shape):
    def __init__(self, color, width, height):
        super().__init__(color)
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def describe(self):
        super().describe()
        print(f"Rectangle {self.width}x{self.height}, area={self.area()}")


class Square(Rectangle):
    def __init__(self, color, side):
        super().__init__(color, side, side)


r = Rectangle("blue", 5, 3)
r.describe()

print()

sq = Square("red", 4)
sq.describe()


class Logger:
    def __init__(self):
        self.logs = []

    def log(self, message):
        self.logs.append(message)

class TimestampLogger(Logger):
    def __init__(self):
        super().__init__()
        self.count = 0

    def log(self, message):
        self.count += 1
        super().log(f"[{self.count}] {message}")

logger = TimestampLogger()
logger.log("Started")
logger.log("Processing")
logger.log("Done")
print(f"Logs: {logger.logs}")
