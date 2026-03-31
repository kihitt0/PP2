import psycopg2
from config import load_config


def get_conn():
    return psycopg2.connect(**load_config())


def setup(conn):
    """Create table and load all functions/procedures from procedures.sql."""
    with open('procedures.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print("Database setup complete.")


# --- 1. Search ---
def search_contacts(conn):
    pattern = input("Enter name or phone pattern: ").strip()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM search_contacts(%s);", (pattern,))
        rows = cur.fetchall()
    if rows:
        print(f"\n{'ID':<5} {'Name':<25} {'Phone':<20}")
        print("-" * 52)
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<25} {row[2]:<20}")
    else:
        print("No contacts found.")


# --- 2. Upsert single contact ---
def upsert_contact(conn):
    name  = input("Name: ").strip()
    phone = input("Phone: ").strip()
    with conn.cursor() as cur:
        cur.execute("CALL upsert_contact(%s, %s);", (name, phone))
    conn.commit()
    print("Contact saved.")


# --- 3. Bulk insert ---
def bulk_insert(conn):
    print("Enter contacts (name,phone). Empty line to finish:")
    records = []
    while True:
        line = input("  > ").strip()
        if not line:
            break
        parts = [p.strip() for p in line.split(',', 1)]
        if len(parts) == 2:
            records.append(parts)
        else:
            print("  Format: Name, +phone")

    if not records:
        print("Nothing to insert.")
        return

    # Build 2D array for PostgreSQL: ARRAY[ARRAY['name','phone'], ...]
    data = [[r[0], r[1]] for r in records]
    with conn.cursor() as cur:
        cur.execute("CALL bulk_insert_contacts(%s::TEXT[][]);", (data,))
    conn.commit()
    print(f"Bulk insert done ({len(records)} entries attempted).")


# --- 4. Paginated list ---
def list_paginated(conn):
    try:
        limit  = int(input("Page size (e.g. 5): ").strip())
        offset = int(input("Offset (e.g. 0): ").strip())
    except ValueError:
        print("Invalid number.")
        return
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM get_contacts_paginated(%s, %s);", (limit, offset))
        rows = cur.fetchall()
    if rows:
        print(f"\n{'ID':<5} {'Name':<25} {'Phone':<20}")
        print("-" * 52)
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<25} {row[2]:<20}")
    else:
        print("No contacts on this page.")


# --- 5. Delete ---
def delete_contact(conn):
    print("Delete by: 1 - name, 2 - phone")
    choice = input("Choice: ").strip()
    with conn.cursor() as cur:
        if choice == '1':
            name = input("Name: ").strip()
            cur.execute("CALL delete_contact(p_name => %s);", (name,))
        elif choice == '2':
            phone = input("Phone: ").strip()
            cur.execute("CALL delete_contact(p_phone => %s);", (phone,))
        else:
            print("Invalid choice.")
            return
    conn.commit()
    print("Contact deleted.")


def main():
    conn = get_conn()
    setup(conn)

    menu = {
        '1': ('Search contacts (by name/phone)',  search_contacts),
        '2': ('Upsert contact (insert/update)',   upsert_contact),
        '3': ('Bulk insert contacts',             bulk_insert),
        '4': ('List contacts (paginated)',         list_paginated),
        '5': ('Delete contact',                   delete_contact),
        '0': ('Exit', None),
    }

    while True:
        print("\n=== PhoneBook (Practice 8) ===")
        for key, (label, _) in menu.items():
            print(f"  {key}. {label}")
        choice = input("Select: ").strip()
        if choice == '0':
            break
        elif choice in menu:
            menu[choice][1](conn)
        else:
            print("Invalid option.")

    conn.close()
    print("Goodbye.")


if __name__ == '__main__':
    main()
