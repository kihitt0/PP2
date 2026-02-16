class Employee:
    company = "TechCorp"
    employee_count = 0

    def __init__(self, name, position):
        self.name = name
        self.position = position
        Employee.employee_count += 1

e1 = Employee("Alan", "Developer")
e2 = Employee("Marat", "Designer")
e3 = Employee("Dana", "Manager")

print(f"Company: {Employee.company}")
print(f"Total employees: {Employee.employee_count}")
print(f"e1 company: {e1.company}")


class Counter:
    count = 0

    def __init__(self):
        Counter.count += 1
        self.id = Counter.count

c1 = Counter()
c2 = Counter()
c3 = Counter()
print(f"c1 id: {c1.id}, c2 id: {c2.id}, c3 id: {c3.id}")
print(f"Total: {Counter.count}")


class Config:
    debug = False
    version = "1.0"
    max_retries = 3

print(f"Debug: {Config.debug}")
Config.debug = True
print(f"Debug: {Config.debug}")


class Student:
    school = "SDU"
    all_students = []

    def __init__(self, name, gpa):
        self.name = name
        self.gpa = gpa
        Student.all_students.append(self)

    @classmethod
    def average_gpa(cls):
        if not cls.all_students:
            return 0
        return sum(s.gpa for s in cls.all_students) / len(cls.all_students)

Student("Alan", 3.8)
Student("Marat", 3.5)
Student("Dana", 3.9)

print(f"School: {Student.school}")
print(f"Average GPA: {Student.average_gpa():.2f}")
