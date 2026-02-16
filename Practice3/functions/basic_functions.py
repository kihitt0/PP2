def greet():
    print("Hello, World!")

greet()


def greet_user(name):
    print(f"Hello, {name}!")

greet_user("Alan")


def add(a, b):
    print(f"{a} + {b} = {a + b}")

add(3, 5)


def multiply(a, b):
    return a * b

result = multiply(4, 7)
print(f"4 * 7 = {result}")


def square(n):
    return n ** 2

print(f"Square of 6 = {square(6)}")


def double(x):
    return x * 2

def add_one(x):
    return x + 1

print(f"double(add_one(3)) = {double(add_one(3))}")
