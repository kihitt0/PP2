numbers = [1, 2, 3, 4, 5]
squares = list(map(lambda x: x ** 2, numbers))
print(f"Squares: {squares}")


celsius = [0, 20, 37, 100]
fahrenheit = list(map(lambda c: c * 9/5 + 32, celsius))
print(f"Celsius:    {celsius}")
print(f"Fahrenheit: {fahrenheit}")


names = ["alan", "marat", "aigerim"]
capitalized = list(map(lambda name: name.capitalize(), names))
print(f"Capitalized: {capitalized}")


words = ["Python", "lambda", "function", "map"]
lengths = list(map(lambda w: len(w), words))
print(f"Words:   {words}")
print(f"Lengths: {lengths}")


a = [1, 2, 3]
b = [10, 20, 30]
sums = list(map(lambda x, y: x + y, a, b))
print(f"{a} + {b} = {sums}")


students = [
    {"name": "Alan", "grade": 85},
    {"name": "Marat", "grade": 92},
    {"name": "Aigerim", "grade": 78},
]
names_grades = list(map(lambda s: f"{s['name']}: {s['grade']}", students))
print(f"Students: {names_grades}")
