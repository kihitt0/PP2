import math

# TASK1 - Convert degree to radian
degree = float(input("Enter degree: "))
radian = math.radians(degree)
print(round(radian, 6))


# TASK2 - Calculate the area of a trapezoid
height = float(input("Enter height: "))
base1 = float(input("Enter base1: "))
base2 = float(input("Enter base2: "))
area = (base1 + base2) / 2 * height
print(area)


# TASK3 - Calculate the area of a regular polygon
n = int(input("Enter number of sides: "))
side = float(input("Enter side length: "))
area = (n * side ** 2) / (4 * math.tan(math.pi / n))
print(round(area, 2))


# TASK4 - Calculate the area of a parallelogram
base = float(input("Enter base: "))
height = float(input("Enter height: "))
area = base * height
print(float(area))
