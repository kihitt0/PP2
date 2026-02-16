numbers = [-5, 3, -1, 7, -8, 2]
by_abs = sorted(numbers, key=lambda x: abs(x))
print(f"By absolute value: {by_abs}")


words = ["Python", "I", "lambda", "hi", "programming"]
by_length = sorted(words, key=lambda w: len(w))
print(f"By length: {by_length}")


students = [("Alan", 85), ("Marat", 92), ("Dana", 78), ("Aigerim", 95)]
by_grade = sorted(students, key=lambda s: s[1], reverse=True)
print(f"By grade (desc): {by_grade}")


products = [
    {"name": "Laptop", "price": 450000},
    {"name": "Phone", "price": 250000},
    {"name": "Headphones", "price": 35000},
    {"name": "Tablet", "price": 180000},
]
by_price = sorted(products, key=lambda p: p["price"])
for p in by_price:
    print(f"  {p['name']}: {p['price']}")


employees = [
    {"name": "Alan", "dept": "IT", "salary": 500000},
    {"name": "Marat", "dept": "HR", "salary": 400000},
    {"name": "Dana", "dept": "IT", "salary": 450000},
    {"name": "Asem", "dept": "HR", "salary": 420000},
]
by_dept_salary = sorted(employees, key=lambda e: (e["dept"], -e["salary"]))
print("\nBy department and salary:")
for e in by_dept_salary:
    print(f"  {e['dept']} - {e['name']}: {e['salary']}")


youngest = min(students, key=lambda s: s[1])
oldest = max(students, key=lambda s: s[1])
print(f"\nLowest grade: {youngest}")
print(f"Highest grade: {oldest}")
