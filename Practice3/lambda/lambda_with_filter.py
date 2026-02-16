numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(f"Even: {evens}")


values = [-5, 3, -1, 7, -8, 2, 0]
positives = list(filter(lambda x: x > 0, values))
print(f"Positives: {positives}")


words = ["hi", "hello", "I", "Python", "ok", "programming"]
long_words = list(filter(lambda w: len(w) > 3, words))
print(f"Long words: {long_words}")


people = [
    {"name": "Alan", "age": 20},
    {"name": "Dana", "age": 16},
    {"name": "Marat", "age": 25},
    {"name": "Asem", "age": 17},
]
adults = list(filter(lambda p: p["age"] >= 18, people))
print(f"Adults: {[p['name'] for p in adults]}")


data = ["hello", "", "world", "", "", "python"]
cleaned = list(filter(lambda s: s != "", data))
print(f"Without empty: {cleaned}")

cleaned2 = list(filter(None, data))
print(f"filter(None): {cleaned2}")


numbers = range(1, 21)
result = list(map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, numbers)))
print(f"Squares of even 1-20: {result}")
