def total(*args):
    print(f"Arguments: {args}")
    return sum(args)

print(f"Sum: {total(1, 2, 3)}")
print(f"Sum: {total(10, 20, 30, 40)}")


def average(*grades):
    if not grades:
        return 0
    return sum(grades) / len(grades)

print(f"Average grade: {average(85, 90, 78, 92)}")


def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"  {key}: {value}")

print("Student info:")
print_info(name="Alan", age=20, university="SDU")


def make_order(customer, *items, **details):
    print(f"\nCustomer: {customer}")
    print(f"Items: {', '.join(items)}")
    for key, value in details.items():
        print(f"  {key}: {value}")

make_order("Alan", "Pizza", "Cola", "Salad",
           delivery="courier", address="10 Abay St")


def add(a, b, c):
    return a + b + c

numbers = [1, 2, 3]
print(f"\nUnpacking list: {add(*numbers)}")

params = {"a": 10, "b": 20, "c": 30}
print(f"Unpacking dict: {add(**params)}")


def wrapper(*args, **kwargs):
    print(f"args: {args}")
    print(f"kwargs: {kwargs}")

wrapper(1, 2, 3, name="Alan", age=20)
