s = "hello world"
num_str = "123"
mix = "Hello\tWorld"
lines = "one\ntwo\nthree"

# 1
print(s.capitalize())

# 2
print(s.casefold())

# 3
print(s.center(20, "-"))

# 4
print(s.count("l"))

# 5
print(s.encode())

# 6
print(s.endswith("world"))

# 7
print(mix.expandtabs(4))

# 8
print(s.find("world"))

# 9
print("My name is {}".format("Boss"))

# 10
print("My name is {name}".format_map({"name": "Boss"}))

# 11
print(s.index("world"))

# 12
print(s.isalnum())

# 13
print("Hello".isalpha())

# 14
print("Hello".isascii())

# 15
print("123".isdecimal())

# 16
print(num_str.isdigit())

# 17
print("variable_name".isidentifier())

# 18
print(s.islower())

# 19
print("123".isnumeric())

# 20
print(s.isprintable())

# 21
print("   ".isspace())

# 22
print("Hello World".istitle())

# 23
print("HELLO".isupper())

# 24
print(", ".join(["one", "two", "three"]))

# 25
print(s.ljust(20, "-"))

# 26
print(s.lower())

# 27
print("   hello".lstrip())

# 28
table = str.maketrans("h", "H")
print(s.translate(table))

# 29
print(s.partition(" "))

# 30
print(s.replace("world", "boss"))

# 31
print(s.rfind("l"))

# 32
print(s.rindex("l"))

# 33
print(s.rjust(20, "-"))

# 34
print(s.rpartition(" "))

# 35
print(s.rsplit(" "))

# 36
print("hello   ".rstrip())

# 37
print(s.split(" "))

# 38
print(lines.splitlines())

# 39
print(s.startswith("hello"))

# 40
print("   hello   ".strip())

# 41
print("HeLLo".swapcase())

# 42
print("hello world".title())

# 43
table = str.maketrans("eo", "30")
print(s.translate(table))

# 44
print(s.upper())

# 45
print("42".zfill(5))
