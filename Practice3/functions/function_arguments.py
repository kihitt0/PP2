def describe_pet(animal, name):
    print(f"I have a {animal} named {name}")

describe_pet("cat", "Barsik")
describe_pet("dog", "Rex")

describe_pet(name="Murka", animal="cat")


def make_coffee(size="medium", sugar=1):
    print(f"Coffee: size={size}, sugar={sugar} spoons")

make_coffee()
make_coffee("large")
make_coffee(sugar=0)
make_coffee("small", 3)


def create_profile(name, age, city="Not specified"):
    print(f"Name: {name}, Age: {age}, City: {city}")

create_profile("Alan", 20)
create_profile("Marat", 22, "Almaty")


def average(numbers):
    return sum(numbers) / len(numbers)

scores = [85, 90, 78, 92, 88]
print(f"Average score: {average(scores)}")


def connect(host="localhost", port=5432, db="main"):
    print(f"Connecting to {db} at {host}:{port}")

connect()
connect("192.168.1.1", 3306, "users")
connect(db="orders")
