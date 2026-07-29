import sqlite3, json
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

    def get_order_status_counts(self) -> dict[str, int]:
        with self.connect() as db:
            cur = db.execute(
                "SELECT order_status, COUNT(*) FROM Orders GROUP BY order_status"
            )
            return {status: count for status, count in cur.fetchall()}

    def get_order_count_by_status(
        self,
        status: str,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> int:
        query = "SELECT COUNT(*) FROM Orders WHERE order_status = ?"
        params: list = [status]

        if date_from:
            query += " AND date(order_date) >= ?"
            params.append(date_from)
        if date_to:
            query += " AND date(order_date) <= ?"
            params.append(date_to)

        with self.connect() as db:
            cur = db.execute(query, params)
            return cur.fetchone()[0]

    def get_order_by_id(self, order_id: int) -> dict | None:
        with self.connect() as db:
            cur = db.execute(
                """
                SELECT order_id, customer_id, order_status, order_date, update_date,
                       delivery_city, delivery_street, delivery_postal_code, order_total
                FROM Orders
                WHERE order_id = ?
                """,
                (order_id,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            return {
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

    def get_order_items(self, order_id: int) -> list[dict]:
        with self.connect() as db:
            cur = db.execute(
                """
                SELECT od.product_id, p.name, od.quantity, od.selling_price
                FROM Order_Details od
                JOIN Products p ON p.product_id = od.product_id
                WHERE od.order_id = ?
                """,
                (order_id,),
            )
            rows = cur.fetchall()
            return [
                {
                    "product_id": row[0],
                    "name": row[1],
                    "quantity": row[2],
                    "selling_price": row[3],
                }
                for row in rows
            ]

    def get_orders_by_status(
        self,
        status: str,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[dict]:
        query = "SELECT order_id, order_status, order_date, order_total FROM Orders WHERE order_status = ?"
        params: list = [status]

        if date_from:
            query += " AND date(order_date) >= ?"
            params.append(date_from)
        if date_to:
            query += " AND date(order_date) <= ?"
            params.append(date_to)

        query += " ORDER BY order_date DESC"

        with self.connect() as db:
            cur = db.execute(query, params)
            rows = cur.fetchall()
            return [
                {
                    "order_id": row[0],
                    "order_status": row[1],
                    "order_date": row[2],
                    "order_total": row[3],
                }
                for row in rows
            ]


if __name__ == "__main__":
    reader = DatabaseReader()
    print(f"Customers({len(reader.get_customers())}): {json.dumps(reader.get_customers(), indent=2)}")
    print(f"Products({len(reader.get_products())}): {json.dumps(reader.get_products(), indent=2)}")
    print(f"Offers({len(reader.get_offers())}): {json.dumps(reader.get_offers(), indent=2)}")
    print(f"Orders({len(reader.get_orders())}): {json.dumps(reader.get_orders(), indent=2)}")