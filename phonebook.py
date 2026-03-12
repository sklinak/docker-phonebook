import re
import psycopg2
from psycopg2 import sql, OperationalError, Error

DB_CONFIG = {
    "host": "postgres",
    "port": 5432,
    "database": "phonebook",
    "user": "postgres",
    "password": "postgres"
}


def connect():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except OperationalError as e:
        print(f"Connection error: {e}")
        return None


def validate_full_name(full_name: str):
    full_name = full_name.strip()

    if not full_name:
        return False, "Name cannot be empty."

    if re.search(r"\d", full_name):
        return False, "Name must not contain digits."

    if not re.fullmatch(r"[A-Za-zА-Яа-яЁё' -]+", full_name):
        return False, "Name contains invalid characters."

    return True, ""


def normalize_phone(phone: str) -> str:
    return phone.strip().replace(" ", "")


def validate_phone(phone: str):
    normalized = normalize_phone(phone)

    if not re.fullmatch(r"\+?\d{11}", normalized):
        return False, "Phone must contain 11 digits and may start with '+'. Spaces are allowed."

    return True, ""


def parse_strict_id(raw_id: str):
    raw_id = raw_id.strip()

    if not raw_id:
        return None, "ID cannot be empty."

    if not raw_id.isdigit():
        return None, "ID must contain only digits."

    if raw_id.startswith("0"):
        return None, "ID must not start with 0."

    return int(raw_id), ""


def contact_exists(conn, contact_id: int) -> bool:
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM contacts WHERE id = %s;", (contact_id,))
        return cur.fetchone() is not None


def add_contact(conn, full_name, phone, note):
    ok, msg = validate_full_name(full_name)
    if not ok:
        print(f"Input error: {msg}")
        return

    ok, msg = validate_phone(phone)
    if not ok:
        print(f"Input error: {msg}")
        return

    phone = normalize_phone(phone)

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO contacts (full_name, phone, note)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (full_name.strip(), phone, note.strip() if note else None)
            )
            contact_id = cur.fetchone()[0]
            conn.commit()
            print(f"Contact was added with ID: {contact_id}")
    except Error as e:
        conn.rollback()
        print(f"Database error while adding contact: {e}")


def list_contacts(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, full_name, phone, note FROM contacts ORDER BY id;")
            rows = cur.fetchall()

            if rows:
                print("\nList of contacts:")
                for row in rows:
                    print(f"ID: {row[0]}, full_name: {row[1]}, phone: {row[2]}, note: {row[3]}")
            else:
                print("List is empty.")
    except Error as e:
        conn.rollback()
        print(f"Database error while reading contacts: {e}")


def update_contact(conn, contact_id, full_name=None, phone=None, note=None):
    if not contact_exists(conn, contact_id):
        print(f"Contact ID {contact_id} does not exist.")
        return

    updates = []
    params = []

    if full_name is not None:
        ok, msg = validate_full_name(full_name)
        if not ok:
            print(f"Input error: {msg}")
            return
        updates.append("full_name = %s")
        params.append(full_name.strip())

    if phone is not None:
        ok, msg = validate_phone(phone)
        if not ok:
            print(f"Input error: {msg}")
            return
        updates.append("phone = %s")
        params.append(normalize_phone(phone))

    if note is not None:
        updates.append("note = %s")
        params.append(note.strip())

    if not updates:
        print("No update parameters.")
        return

    params.append(contact_id)
    query = sql.SQL("UPDATE contacts SET {} WHERE id = %s;").format(
        sql.SQL(", ").join(sql.SQL(part) for part in updates)
    )

    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
            print(f"Contact ID {contact_id} was updated.")
    except Error as e:
        conn.rollback()
        print(f"Database error while updating contact: {e}")


def delete_contact(conn, contact_id):
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM contacts WHERE id = %s;", (contact_id,))
            if cur.rowcount == 0:
                print(f"Contact ID {contact_id} does not exist.")
            else:
                conn.commit()
                print(f"Contact ID {contact_id} was deleted.")
    except Error as e:
        conn.rollback()
        print(f"Database error while deleting contact: {e}")


def main_menu():
    conn = connect()
    if not conn:
        return

    try:
        while True:
            print("\n1. Show all contacts")
            print("2. Add contact")
            print("3. Update contact")
            print("4. Delete contact")
            print("5. Exit")

            choice = input("Choose an action: ").strip()

            if choice not in {"1", "2", "3", "4", "5"}:
                print("You can enter only digits 1-5.")
                continue

            choice = int(choice)

            if choice == 1:
                list_contacts(conn)

            elif choice == 2:
                full_name = input("Enter full name: ").strip()
                phone = input("Enter the phone number: ").strip()
                note = input("Enter a note (not necessary): ").strip()
                add_contact(conn, full_name, phone, note)

            elif choice == 3:
                contact_id_raw = input("Enter contact ID for updating: ").strip()
                contact_id, error = parse_strict_id(contact_id_raw)

                if error:
                    print(error)
                    continue

                if not contact_exists(conn, contact_id):
                    print(f"Contact ID {contact_id} does not exist.")
                    continue

                full_name = input("New name (leave empty to keep current): ").strip()
                phone = input("New phone number (leave empty to keep current): ").strip()
                note = input("New note (leave empty to keep current): ").strip()

                update_contact(
                    conn,
                    contact_id,
                    full_name if full_name else None,
                    phone if phone else None,
                    note if note else None
                )

            elif choice == 4:
                contact_id_raw = input("Contact ID for deleting: ").strip()
                contact_id, error = parse_strict_id(contact_id_raw)

                if error:
                    print(error)
                    continue

                delete_contact(conn, contact_id)

            elif choice == 5:
                print("Goodbye.")
                break
    finally:
        conn.close()


if __name__ == "__main__":
    main_menu()