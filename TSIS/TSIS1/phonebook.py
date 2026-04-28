"""
PhoneBook – TSIS 1
Extended contact management with groups, multiple phones,
email, birthday, sorting, pagination, JSON/CSV import-export,
and new stored procedures.
"""

import psycopg2
import json
import csv
import os
import sys

# ── DB connection ─────────────────────────────────────────────────────────

_CFG = dict(host="localhost", dbname="postgres",
            user="postgres", password="postgres", port=5432)

def get_conn():
    return psycopg2.connect(**_CFG)


def setup_db(conn):
    schema = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema, encoding="utf-8") as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print("Database schema ready.")


# ── Helpers ───────────────────────────────────────────────────────────────

def _print_table(rows, headers):
    if not rows:
        print("  (no results)")
        return
    widths = [max(len(str(r[i])) for r in rows + [headers])
              for i in range(len(headers))]
    sep  = "  ".join("-" * w for w in widths)
    hdr  = "  ".join(str(h).ljust(w) for h, w in zip(headers, widths))
    print(hdr)
    print(sep)
    for row in rows:
        print("  ".join(str(v or "").ljust(w) for v, w in zip(row, widths)))

def _paginate(rows, page_size=5):
    """Yield pages of rows with next/prev navigation."""
    total   = len(rows)
    page    = 0
    pages   = max(1, (total + page_size - 1) // page_size)
    while True:
        start = page * page_size
        chunk = rows[start:start + page_size]
        yield chunk, page + 1, pages
        print(f"\n  Page {page+1}/{pages} – [N]ext [P]rev [Q]uit")
        ch = input("  > ").strip().lower()
        if ch == "n" and page < pages - 1:
            page += 1
        elif ch == "p" and page > 0:
            page -= 1
        elif ch == "q" or ch == "":
            break


# ── 1. Add contact ────────────────────────────────────────────────────────

def add_contact(conn):
    name     = input("Full name: ").strip()
    email    = input("Email (leave blank to skip): ").strip() or None
    birthday = input("Birthday YYYY-MM-DD (blank to skip): ").strip() or None
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO pb_contacts(name,email,birthday) VALUES(%s,%s,%s) RETURNING id",
            (name, email, birthday)
        )
        cid = cur.fetchone()[0]
    conn.commit()
    print(f"  Contact added (id={cid}).")

    # Optionally add phones
    while True:
        ph = input("  Add phone (blank to stop): ").strip()
        if not ph:
            break
        kind = input("  Type [home/work/mobile] (default mobile): ").strip() or "mobile"
        if kind not in ("home", "work", "mobile"):
            kind = "mobile"
        with conn.cursor() as cur:
            cur.execute("SELECT add_phone(%s,%s,%s)", (cid, ph, kind))
        conn.commit()
        print(f"  Phone {ph} ({kind}) added.")

    # Optionally assign group
    grp = input("  Group (blank to skip): ").strip()
    if grp:
        with conn.cursor() as cur:
            cur.execute("SELECT move_to_group(%s,%s)", (cid, grp))
        conn.commit()


# ── 2. Search ─────────────────────────────────────────────────────────────

def search(conn):
    pattern = input("Search (name / email / phone): ").strip()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
        rows = cur.fetchall()
    _print_table(rows, ["ID","Name","Email","Birthday","Group","Phones"])


# ── 3. List with sort + filter + pagination ───────────────────────────────

def list_contacts(conn):
    print("\nSort by: [1] Name  [2] Birthday  [3] Date added")
    sort_choice = input("Choice (default 1): ").strip() or "1"
    sort_map = {"1": "c.name", "2": "c.birthday NULLS LAST", "3": "c.created_at"}
    order_by = sort_map.get(sort_choice, "c.name")

    grp_filter = input("Filter by group (blank = all): ").strip() or None

    page_size = 5
    try:
        page_size = int(input(f"Page size (default {page_size}): ").strip() or page_size)
    except ValueError:
        pass

    with conn.cursor() as cur:
        if grp_filter:
            cur.execute(f"""
                SELECT c.id, c.name, c.email, c.birthday, g.name AS grp,
                       STRING_AGG(p.phone||' ('||p.kind||')', ', ' ORDER BY p.kind) AS phones,
                       c.created_at::DATE
                FROM pb_contacts c
                LEFT JOIN pb_groups g ON g.id = c.group_id
                LEFT JOIN pb_phones p ON p.contact_id = c.id
                WHERE g.name ILIKE %s
                GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
                ORDER BY {order_by}
            """, (f"%{grp_filter}%",))
        else:
            cur.execute(f"""
                SELECT c.id, c.name, c.email, c.birthday, g.name AS grp,
                       STRING_AGG(p.phone||' ('||p.kind||')', ', ' ORDER BY p.kind) AS phones,
                       c.created_at::DATE
                FROM pb_contacts c
                LEFT JOIN pb_groups g ON g.id = c.group_id
                LEFT JOIN pb_phones p ON p.contact_id = c.id
                GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
                ORDER BY {order_by}
            """)
        rows = cur.fetchall()

    headers = ["ID","Name","Email","Birthday","Group","Phones","Added"]
    for chunk, page, pages in _paginate(rows, page_size):
        print(f"\n--- Page {page}/{pages} ---")
        _print_table(chunk, headers)


# ── 4. Add phone to existing contact ─────────────────────────────────────

def add_phone_menu(conn):
    cid  = input("Contact ID: ").strip()
    ph   = input("Phone number: ").strip()
    kind = input("Type [home/work/mobile] (default mobile): ").strip() or "mobile"
    if kind not in ("home", "work", "mobile"):
        kind = "mobile"
    with conn.cursor() as cur:
        cur.execute("SELECT add_phone(%s,%s,%s)", (cid, ph, kind))
    conn.commit()
    print("Phone added.")


# ── 5. Move to group ──────────────────────────────────────────────────────

def move_group_menu(conn):
    cid  = input("Contact ID: ").strip()
    grp  = input("Group name: ").strip()
    with conn.cursor() as cur:
        cur.execute("SELECT move_to_group(%s,%s)", (cid, grp))
    conn.commit()
    print(f"Contact {cid} moved to group '{grp}'.")


# ── 6. Delete contact ─────────────────────────────────────────────────────

def delete_contact(conn):
    cid = input("Contact ID to delete: ").strip()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM pb_contacts WHERE id=%s RETURNING name", (cid,))
        row = cur.fetchone()
    conn.commit()
    if row:
        print(f"Deleted: {row[0]}")
    else:
        print("Contact not found.")


# ── 7. Export to JSON ─────────────────────────────────────────────────────

def export_json(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.name, c.email,
                   c.birthday::TEXT, g.name AS grp,
                   COALESCE(
                       JSON_AGG(
                           JSON_BUILD_OBJECT('phone', p.phone, 'kind', p.kind)
                       ) FILTER (WHERE p.id IS NOT NULL), '[]'
                   ) AS phones
            FROM pb_contacts c
            LEFT JOIN pb_groups g ON g.id = c.group_id
            LEFT JOIN pb_phones p ON p.contact_id = c.id
            GROUP BY c.id, c.name, c.email, c.birthday, g.name
            ORDER BY c.name
        """)
        rows = cur.fetchall()

    contacts = [
        {"id": r[0], "name": r[1], "email": r[2], "birthday": r[3],
         "group": r[4], "phones": r[5]}
        for r in rows
    ]
    fn = input("Output filename (default: contacts.json): ").strip() or "contacts.json"
    with open(fn, "w", encoding="utf-8") as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2, default=str)
    print(f"Exported {len(contacts)} contacts to {fn}.")


# ── 8. Import from JSON ───────────────────────────────────────────────────

def import_json(conn):
    fn = input("JSON filename: ").strip()
    if not os.path.exists(fn):
        fn = os.path.join(os.path.dirname(__file__), fn)
    if not os.path.exists(fn):
        print("File not found.")
        return
    with open(fn, encoding="utf-8") as f:
        contacts = json.load(f)

    added = skipped = 0
    for c in contacts:
        with conn.cursor() as cur:
            # Duplicate check by name (case-insensitive)
            cur.execute("SELECT id FROM pb_contacts WHERE LOWER(name)=LOWER(%s)",
                        (c.get("name",""),))
            if cur.fetchone():
                skipped += 1
                continue
            cur.execute(
                "INSERT INTO pb_contacts(name,email,birthday) VALUES(%s,%s,%s) RETURNING id",
                (c.get("name"), c.get("email"), c.get("birthday"))
            )
            cid = cur.fetchone()[0]
            for ph in c.get("phones", []):
                cur.execute("SELECT add_phone(%s,%s,%s)",
                            (cid, ph.get("phone",""), ph.get("kind","mobile")))
            if c.get("group"):
                cur.execute("SELECT move_to_group(%s,%s)", (cid, c["group"]))
        conn.commit()
        added += 1

    print(f"Imported: {added} added, {skipped} skipped (duplicates).")


# ── 9. Import from CSV ────────────────────────────────────────────────────

def import_csv(conn):
    fn = input("CSV filename (columns: name,phone,kind,email,birthday,group): ").strip()
    if not os.path.exists(fn):
        fn = os.path.join(os.path.dirname(__file__), fn)
    if not os.path.exists(fn):
        print("File not found.")
        return
    added = skipped = 0
    with open(fn, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("name","").strip()
            if not name:
                continue
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM pb_contacts WHERE LOWER(name)=LOWER(%s)", (name,))
                existing = cur.fetchone()
                if existing:
                    cid = existing[0]
                    # Append phone to existing contact
                    ph   = row.get("phone","").strip()
                    kind = row.get("kind","mobile").strip() or "mobile"
                    if ph:
                        cur.execute("SELECT add_phone(%s,%s,%s)", (cid, ph, kind))
                    skipped += 1
                else:
                    email    = row.get("email","").strip() or None
                    birthday = row.get("birthday","").strip() or None
                    cur.execute(
                        "INSERT INTO pb_contacts(name,email,birthday) VALUES(%s,%s,%s) RETURNING id",
                        (name, email, birthday)
                    )
                    cid = cur.fetchone()[0]
                    ph   = row.get("phone","").strip()
                    kind = row.get("kind","mobile").strip() or "mobile"
                    if ph:
                        cur.execute("SELECT add_phone(%s,%s,%s)", (cid, ph, kind))
                    grp = row.get("group","").strip()
                    if grp:
                        cur.execute("SELECT move_to_group(%s,%s)", (cid, grp))
                    added += 1
            conn.commit()
    print(f"CSV import: {added} added, {skipped} merged (phone appended).")


# ── Menu ──────────────────────────────────────────────────────────────────

MENU = [
    ("Add contact",          add_contact),
    ("Search contacts",      search),
    ("List / sort / filter", list_contacts),
    ("Add phone to contact", add_phone_menu),
    ("Move contact to group",move_group_menu),
    ("Delete contact",       delete_contact),
    ("Export to JSON",       export_json),
    ("Import from JSON",     import_json),
    ("Import from CSV",      import_csv),
    ("Exit",                 None),
]

def main():
    try:
        conn = get_conn()
    except Exception as e:
        print(f"Cannot connect to database: {e}")
        sys.exit(1)

    setup_db(conn)
    print("\n=== PhoneBook – TSIS 1 ===")

    while True:
        print()
        for i, (label, _) in enumerate(MENU, 1):
            print(f"  {i}. {label}")
        choice = input("\nChoice: ").strip()
        if not choice.isdigit():
            continue
        idx = int(choice) - 1
        if idx < 0 or idx >= len(MENU):
            continue
        label, fn = MENU[idx]
        if fn is None:
            print("Bye!")
            conn.close()
            break
        try:
            fn(conn)
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
