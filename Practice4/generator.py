
# TASK1
def squares(a):
    for i in range(1, a + 1):
        yield i ** 2

a = int(input())
for i in squares(a):
    print(i)


# TASK2
def even_numbers(n):
    for i in range(0, n + 1, 2):
        yield i

n = int(input())
print(",".join(str(i) for i in even_numbers(n)))


# TASK3
def divisible_by_3_and_4(n):
    for i in range(0, n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

n = int(input())
for i in divisible_by_3_and_4(n):
    print(i)


# TASK4
def squares_range(a, b):
    for i in range(a, b + 1):
        yield i ** 2

a = int(input())
b = int(input())
for val in squares_range(a, b):
    print(val)


# TASK5
def countdown(n):
    while n >= 0:
        yield n
        n -= 1

n = int(input())
for val in countdown(n):
    print(val)
