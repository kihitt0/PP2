def square(x):
    return x ** 2

square_lambda = lambda x: x ** 2

print(f"Function: {square(5)}")
print(f"Lambda:   {square_lambda(5)}")


add = lambda a, b: a + b
print(f"3 + 7 = {add(3, 7)}")

full_name = lambda first, last: f"{first} {last}"
print(f"Name: {full_name('Alan', 'Kasymov')}")


greet = lambda: "Hello, World!"
print(greet())


check_age = lambda age: "Adult" if age >= 18 else "Minor"
print(f"Age 20: {check_age(20)}")
print(f"Age 15: {check_age(15)}")


result = (lambda x, y: x * y)(6, 7)
print(f"6 * 7 = {result}")


def multiplier(n):
    return lambda x: x * n

double = multiplier(2)
triple = multiplier(3)
print(f"double(5) = {double(5)}")
print(f"triple(5) = {triple(5)}")
