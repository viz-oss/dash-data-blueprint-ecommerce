import sqlite3, json
from contextlib import contextmanager
from datetime import datetime, timedelta

class DatabaseReader:
    EXCLUDED_SALE_STATUSES = (
        "pending",
        "processing",
        "shipped",
        "awaiting_payment",
        "payment_failed",
        "on_hold",
        "cancelled_end",
        "buyer_canceled_end",
        "returned",
        "refunded_end",
        "return_accepted",
        "return_requested",
        "delivery_failed",
    )

    RETURN_STATUSES = (
        "returned",
        "return_accepted",
        "return_requested",
        "refunded_end",
    )

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
                SELECT product_id, ean, name, rrp, cost, review_avg, review_count
                FROM Products
                """
            )
            rows = cur.fetchall()
            return [
                {
                    "product_id": row[0],
                    "ean": row[1],
                    "name": row[2],
                    "rrp": row[3],
                    "cost": row[4],
                    "review_avg": row[5],
                    "review_count": row[6],
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
                       invoice, delivery_first_name, delivery_last_name, delivery_phone,
                       delivery_country_code, delivery_city, delivery_street,
                       delivery_postal_code, courier, delivery_cost, order_total
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
                "invoice": row[5],
                "delivery_first_name": row[6],
                "delivery_last_name": row[7],
                "delivery_phone": row[8],
                "delivery_country_code": row[9],
                "delivery_city": row[10],
                "delivery_street": row[11],
                "delivery_postal_code": row[12],
                "courier": row[13],
                "delivery_cost": row[14],
                "order_total": row[15],
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

    def get_product_sales_stats(
        self,
        from_: str | None = None,
        to: str | None = None,
    ) -> list[dict]:
        excluded = self.EXCLUDED_SALE_STATUSES
        placeholders = ",".join("?" * len(excluded))

        query = f"""
            SELECT
                od.product_id,
                p.name,
                SUM(od.quantity) AS total_quantity,
                SUM(od.quantity * od.selling_price) AS total_revenue,
                SUM(od.quantity * (od.selling_price - p.cost)) AS total_margin
            FROM Order_Details od
            JOIN Orders o ON o.order_id = od.order_id
            JOIN Products p ON p.product_id = od.product_id
            WHERE o.order_status NOT IN ({placeholders})
        """
        params: list = list(excluded)

        if from_:
            query += " AND date(o.order_date) >= date(?)"
            params.append(from_)
        if to:
            query += " AND date(o.order_date) <= date(?)"
            params.append(to)

        query += " GROUP BY od.product_id, p.name"

        with self.connect() as db:
            cur = db.execute(query, params)
            rows = cur.fetchall()

        return [
            {
                "product_id": row[0],
                "name": row[1],
                "total_quantity": row[2] or 0,
                "total_revenue": row[3] or 0.0,
                "total_margin": row[4] or 0.0,
            }
            for row in rows
        ]

    def get_product_growth_stats(
        self,
        recent_days: int = 30,
        from_: str | None = None,
        to: str | None = None,
    ) -> list[dict]:
        if to:
            d_to = datetime.strptime(to, "%Y-%m-%d")
        else:
            d_to = datetime.now()

        if from_:
            d_from = datetime.strptime(from_, "%Y-%m-%d")
        elif to:
            d_from = d_to - timedelta(days=recent_days)
        else:
            d_from = d_to - timedelta(days=recent_days)

        recent_start = d_from.strftime("%Y-%m-%d")
        recent_end = d_to.strftime("%Y-%m-%d")

        window_days = max((d_to - d_from).days, 1)
        previous_start = (d_from - timedelta(days=window_days)).strftime("%Y-%m-%d")
        previous_end = recent_start

        excluded = self.EXCLUDED_SALE_STATUSES
        placeholders = ",".join("?" * len(excluded))
        query = f"""
            SELECT
                od.product_id,
                p.name,
                SUM(CASE WHEN date(o.order_date) >= date(?) AND date(o.order_date) <= date(?)
                         THEN od.quantity ELSE 0 END) AS recent_quantity,
                SUM(CASE WHEN date(o.order_date) >= date(?) AND date(o.order_date) < date(?)
                         THEN od.quantity ELSE 0 END) AS previous_quantity
            FROM Order_Details od
            JOIN Orders o ON o.order_id = od.order_id
            JOIN Products p ON p.product_id = od.product_id
            WHERE o.order_status NOT IN ({placeholders})
              AND date(o.order_date) >= date(?)
              AND date(o.order_date) <= date(?)
            GROUP BY od.product_id, p.name
        """
        params = [
            recent_start, recent_end,
            previous_start, recent_start,
            *excluded,
            previous_start, recent_end,
        ]

        with self.connect() as db:
            cur = db.execute(query, params)
            rows = cur.fetchall()

        result = []
        for product_id, name, recent_qty, previous_qty in rows:
            recent_qty = recent_qty or 0
            previous_qty = previous_qty or 0
            if previous_qty > 0:
                growth_rate = round(recent_qty / previous_qty, 4)
            else:
                growth_rate = None
            result.append(
                {
                    "product_id": product_id,
                    "name": name,
                    "recent_quantity": recent_qty,
                    "previous_quantity": previous_qty,
                    "growth_rate": growth_rate,
                }
            )
        return result

    def get_product_listing_date(self, product_id: int) -> str | None:
        with self.connect() as db:
            cur = db.execute(
                """
                SELECT MIN(listing_date)
                FROM Offer
                WHERE product_id = ? AND stock_quantity > 0
                """,
                (product_id,),
            )
            row = cur.fetchone()
        return row[0] if row and row[0] is not None else None

    def get_product_rating_stats(self, min_votes: int = 10) -> list[dict]:
        with self.connect() as db:
            cur = db.execute(
                "SELECT product_id, name, review_avg, review_count FROM Products WHERE review_count > 0"
            )
            rows = cur.fetchall()

        if not rows:
            return []

        parsed_rows = [
            (product_id, name, float(review_avg), int(review_count))
            for product_id, name, review_avg, review_count in rows
        ]

        global_avg = sum(review_avg for _, _, review_avg, _ in parsed_rows) / len(parsed_rows)

        result = []
        for product_id, name, review_avg, review_count in parsed_rows:
            weighted = (review_count * review_avg + min_votes * global_avg) / (review_count + min_votes)
            result.append(
                {
                    "product_id": product_id,
                    "name": name,
                    "review_avg": review_avg,
                    "review_count": review_count,
                    "weighted_rating": round(weighted, 3),
                }
            )
        return result

    def get_product_by_id(self, product_id: int) -> dict | None:
        with self.connect() as db:
            cur = db.execute(
                """
                SELECT product_id, ean, name, rrp, cost, review_avg, review_count
                FROM Products
                WHERE product_id = ?
                """,
                (product_id,),
            )
            row = cur.fetchone()
        if row is None:
            return None
        return {
            "product_id": row[0],
            "ean": row[1],
            "name": row[2],
            "rrp": float(row[3]) if row[3] is not None else 0.0,
            "cost": float(row[4]) if row[4] is not None else 0.0,
            "review_avg": float(row[5]) if row[5] is not None else 0.0,
            "review_count": int(row[6]) if row[6] is not None else 0,
        }

    def get_product_stock(self, product_id: int) -> int:
        with self.connect() as db:
            cur = db.execute(
                "SELECT SUM(stock_quantity) FROM Offer WHERE product_id = ?",
                (product_id,),
            )
            total = cur.fetchone()[0]
        return total or 0

    def get_product_return_rate(self, product_id: int) -> float:
        with self.connect() as db:
            cur = db.execute(
                """
                SELECT COUNT(*)
                FROM Order_Details od
                WHERE od.product_id = ?
                """,
                (product_id,),
            )
            total = cur.fetchone()[0] or 0
            if total == 0:
                return 0.0

            placeholders = ",".join("?" * len(self.RETURN_STATUSES))
            cur = db.execute(
                f"""
                SELECT COUNT(*)
                FROM Order_Details od
                JOIN Orders o ON o.order_id = od.order_id
                WHERE od.product_id = ? AND o.order_status IN ({placeholders})
                """,
                (product_id, *self.RETURN_STATUSES),
            )
            returned = cur.fetchone()[0] or 0

        return round(returned / total, 4)


if __name__ == "__main__":
    reader = DatabaseReader()
    print(f"Customers({len(reader.get_customers())}): {json.dumps(reader.get_customers(), indent=2)}")
    print(f"Products({len(reader.get_products())}): {json.dumps(reader.get_products(), indent=2)}")
    print(f"Offers({len(reader.get_offers())}): {json.dumps(reader.get_offers(), indent=2)}")
    print(f"Orders({len(reader.get_orders())}): {json.dumps(reader.get_orders(), indent=2)}")