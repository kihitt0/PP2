def square(n):
    return n ** 2

print(f"square(5) = {square(5)}")


def min_max(numbers):
    return min(numbers), max(numbers)

lo, hi = min_max([4, 1, 7, 3, 9])
print(f"Min: {lo}, Max: {hi}")


def even_numbers(n):
    return [i for i in range(1, n + 1) if i % 2 == 0]

print(f"Even numbers up to 10: {even_numbers(10)}")


def build_person(name, age, city):
    return {
        "name": name,
        "age": age,
        "city": city
    }

person = build_person("Alan", 20, "Astana")
print(f"Person: {person}")


def divide(a, b):
    if b == 0:
        return "Division by zero!"
    return a / b

print(f"10 / 3 = {divide(10, 3)}")
print(f"10 / 0 = {divide(10, 0)}")


def say_hello(name):
    print(f"Hello, {name}")

result = say_hello("World")
print(f"Result: {result}")


def is_adult(age):
    return age >= 18

print(f"Age 20 - adult? {is_adult(20)}")
print(f"Age 15 - adult? {is_adult(15)}")
