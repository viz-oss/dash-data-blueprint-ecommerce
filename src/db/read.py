import sqlite3
from contextlib import contextmanager


class DatabaseReader:
    def __init__(self, db_path: str = "db.sqlite") -> None:
        self.db_path = db_path

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.db_path)
        try:
            yield connection
        finally:
            connection.close()

    def get_customers(self) -> list[dict]:
        with self.connect() as db:
            cur = db.execute(
                "SELECT customer_id, identifier, registration_date FROM Customers"
            )
            rows = cur.fetchall()
            return [
                {
                    "customer_id": row[0],
                    "identifier": row[1],
                    "registration_date": row[2],
                }
                for row in rows
            ]

    def get_products(self) -> list[dict]:
        with self.connect() as db:
            cur = db.execute(
                """
                SELECT product_id, name, rrp, cost, review_avg, review_count
                FROM Products
                """
            )
            rows = cur.fetchall()
            return [
                {
                    "product_id": row[0],
                    "name": row[1],
                    "rrp": row[2],
                    "cost": row[3],
                    "review_avg": row[4],
                    "review_count": row[5],
                }
                for row in rows
            ]

    def get_offers(self) -> list[dict]:
        with self.connect() as db:
            cur = db.execute(
                "SELECT product_id, stock_quantity, listing_date FROM Offer"
            )
            rows = cur.fetchall()
            return [
                {
                    "product_id": row[0],
                    "stock_quantity": row[1],
                    "listing_date": row[2],
                }
                for row in rows
            ]

    def get_orders(self) -> list[dict]:
        with self.connect() as db:
            cur = db.execute(
                """
                SELECT order_id, customer_id, order_status, order_date, update_date,
                       delivery_city, delivery_street, delivery_postal_code, order_total
                FROM Orders
                """
            )
            rows = cur.fetchall()
            return [
                {
                    "order_id": row[0],
                    "customer_id": row[1],
                    "order_status": row[2],
                    "order_date": row[3],
                    "update_date": row[4],
                    "delivery_city": row[5],
                    "delivery_street": row[6],
                    "delivery_postal_code": row[7],
                    "order_total": row[8],
                }
                for row in rows
            ]


if __name__ == "__main__":
    reader = DatabaseReader()
    print(f"Customers: {len(reader.get_customers())}")
    print(f"Products: {len(reader.get_products())}")
    print(f"Offers: {len(reader.get_offers())}")
    print(f"Orders: {len(reader.get_orders())}")