# Practice 6: Built-in Functions
# Covers: map(), filter(), reduce(), enumerate(), zip()

from functools import reduce

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
words = ["apple", "banana", "cherry", "date", "elderberry"]


# --- map() ---
# Apply a function to every element and return a map object

squared = list(map(lambda x: x ** 2, numbers))
print("map() - squares:", squared)

uppercased = list(map(str.upper, words))
print("map() - uppercase:", uppercased)


# --- filter() ---
# Keep only elements where the function returns True

evens = list(filter(lambda x: x % 2 == 0, numbers))
print("\nfilter() - evens:", evens)

long_words = list(filter(lambda w: len(w) > 5, words))
print("filter() - words longer than 5 chars:", long_words)


# --- reduce() ---
# Accumulate a single result by applying a function left to right

total = reduce(lambda acc, x: acc + x, numbers)
print("\nreduce() - sum:", total)

product = reduce(lambda acc, x: acc * x, numbers)
print("reduce() - product:", product)

longest = reduce(lambda a, b: a if len(a) >= len(b) else b, words)
print("reduce() - longest word:", longest)


# --- enumerate() ---
# Iterate with both index and value

print("\nenumerate() - words with index:")
for index, word in enumerate(words):
    print(f"  {index}: {word}")

print("\nenumerate(start=1):")
for index, word in enumerate(words, start=1):
    print(f"  {index}. {word}")


# --- zip() ---
# Combine multiple iterables element-by-element

names = ["Alice", "Bob", "Charlie"]
scores = [95, 82, 78]
grades = ["A", "B", "C"]

print("\nzip() - names and scores:")
for name, score in zip(names, scores):
    print(f"  {name}: {score}")

print("\nzip() - three iterables:")
for name, score, grade in zip(names, scores, grades):
    print(f"  {name}: {score} ({grade})")

# zip to create a dict
score_dict = dict(zip(names, scores))
print("\nzip() -> dict:", score_dict)


# --- Combining them ---
# Sum of squares of even numbers using map + filter + reduce

result = reduce(
    lambda acc, x: acc + x,
    map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, numbers))
)
print("\nCombined: sum of squares of even numbers:", result)
