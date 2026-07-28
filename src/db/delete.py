import sqlite3

def clear_all_data(db_path: str = "db.sqlite") -> None:
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF;")

    tables = [
        "Order_Details",
        "Orders",
        "Offer",
        "Products",
        "Customers",
    ]

    for table in tables:
        cursor.execute(f'DELETE FROM "{table}";')
        print(f"Wyczyszczono tabele: {table}")

    cursor.execute(
        "DELETE FROM sqlite_sequence WHERE name IN (?, ?, ?, ?);",
        ("Customers", "Products", "Orders", "Order_Details"),
    )

    connection.commit()
    connection.close()
    print("Wszystkie dane wyczyszczone, struktura tabel zachowana.")


if __name__ == "__main__":
    clear_all_data()