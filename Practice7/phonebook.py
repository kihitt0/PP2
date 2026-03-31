import csv
import psycopg2
from config import load_config


def create_table(conn):
    sql = """
    CREATE TABLE IF NOT EXISTS phonebook (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        phone VARCHAR(20) NOT NULL UNIQUE
    );
    """
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print("Table 'phonebook' is ready.")


def insert_from_csv(conn, filename='contacts.csv'):
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [(row['name'].strip(), row['phone'].strip()) for row in reader]

    sql = """
    INSERT INTO phonebook (name, phone)
    VALUES (%s, %s)
    ON CONFLICT (phone) DO NOTHING;
    """
    with conn.cursor() as cur:
        cur.executemany(sql, rows)
    conn.commit()
    print(f"Imported {len(rows)} records from {filename}.")


def insert_from_console(conn):
    name = input("Enter name: ").strip()
    phone = input("Enter phone: ").strip()
    sql = """
    INSERT INTO phonebook (name, phone)
    VALUES (%s, %s)
    ON CONFLICT (phone) DO UPDATE SET name = EXCLUDED.name;
    """
    with conn.cursor() as cur:
        cur.execute(sql, (name, phone))
    conn.commit()
    print(f"Contact '{name}' saved.")


def update_contact(conn):
    print("Update: 1 - name, 2 - phone")
    choice = input("Choice: ").strip()
    phone = input("Enter existing phone to identify contact: ").strip()
    if choice == '1':
        new_name = input("New name: ").strip()
        sql = "UPDATE phonebook SET name = %s WHERE phone = %s;"
        with conn.cursor() as cur:
            cur.execute(sql, (new_name, phone))
    elif choice == '2':
        new_phone = input("New phone: ").strip()
        sql = "UPDATE phonebook SET phone = %s WHERE phone = %s;"
        with conn.cursor() as cur:
            cur.execute(sql, (new_phone, phone))
    else:
        print("Invalid choice.")
        return
    conn.commit()
    print("Contact updated.")


def query_contacts(conn):
    print("Search: 1 - by name, 2 - by phone prefix, 3 - all")
    choice = input("Choice: ").strip()
    with conn.cursor() as cur:
        if choice == '1':
            name = input("Enter name (or part): ").strip()
            cur.execute("SELECT id, name, phone FROM phonebook WHERE name ILIKE %s ORDER BY name;", (f'%{name}%',))
        elif choice == '2':
            prefix = input("Enter phone prefix: ").strip()
            cur.execute("SELECT id, name, phone FROM phonebook WHERE phone LIKE %s ORDER BY phone;", (f'{prefix}%',))
        else:
            cur.execute("SELECT id, name, phone FROM phonebook ORDER BY name;")
        rows = cur.fetchall()
    if rows:
        print(f"\n{'ID':<5} {'Name':<25} {'Phone':<20}")
        print("-" * 52)
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<25} {row[2]:<20}")
    else:
        print("No contacts found.")


def delete_contact(conn):
    print("Delete by: 1 - name, 2 - phone")
    choice = input("Choice: ").strip()
    with conn.cursor() as cur:
        if choice == '1':
            name = input("Enter name: ").strip()
            cur.execute("DELETE FROM phonebook WHERE name ILIKE %s;", (name,))
        elif choice == '2':
            phone = input("Enter phone: ").strip()
            cur.execute("DELETE FROM phonebook WHERE phone = %s;", (phone,))
        else:
            print("Invalid choice.")
            return
        deleted = cur.rowcount
    conn.commit()
    print(f"Deleted {deleted} contact(s).")


def main():
    config = load_config()
    conn = psycopg2.connect(**config)
    create_table(conn)

    menu = {
        '1': ('Import from CSV',          insert_from_csv),
        '2': ('Add contact (console)',     insert_from_console),
        '3': ('Update contact',            update_contact),
        '4': ('Search / list contacts',    query_contacts),
        '5': ('Delete contact',            delete_contact),
        '0': ('Exit',                      None),
    }

    while True:
        print("\n=== PhoneBook ===")
        for key, (label, _) in menu.items():
            print(f"  {key}. {label}")
        choice = input("Select: ").strip()
        if choice == '0':
            break
        elif choice in menu:
            _, func = menu[choice]
            if choice == '1':
                func(conn)
            else:
                func(conn)
        else:
            print("Invalid option.")

    conn.close()
    print("Goodbye.")


if __name__ == '__main__':
    main()
