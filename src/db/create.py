import sqlite3
from datetime import datetime

def create_database() -> None:
    connection = sqlite3.connect("db.sqlite")
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Customers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier TEXT NOT NULL UNIQUE, 
            registration_date TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)

    # Products
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ean TEXT NOT NULL UNIQUE,
            rrp TEXT NOT NULL CHECK (rrp >= 0),
            cost TEXT NOT NULL CHECK (cost >= 0),
            review_avg TEXT,
            review_count INTEGER NOT NULL DEFAULT 0 CHECK (review_count >= 0)
        );
    """)

   # Offer
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Offer (
            product_id INTEGER PRIMARY KEY,
            stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
            listing_date TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
                ON DELETE CASCADE
        );
    """)
 
    # Orders
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            order_status TEXT NOT NULL DEFAULT 'pending'
                CHECK (order_status IN (
                    'pending',
                    'awaiting_payment',
                    'payment_failed',
                    'processing',
                    'ready_to_ship',
                    'shipped',
                    'delivered_end',
                    'delivery_failed',
                    'return_requested',
                    'return_accepted',
                    'return_rejected',
                    'returned',
                    'refunded_end',
                    'exchanged_end',
                    'on_hold',
                    'cancelled_end',
                    'buyer_canceled_end'
                )),
            order_date TEXT NOT NULL DEFAULT (datetime('now')),
            update_date TEXT NOT NULL DEFAULT (datetime('now')),
            delivery_city TEXT,
            delivery_street TEXT,
            delivery_postal_code TEXT,
            order_total TEXT DEFAULT 0 CHECK (order_total >= 0),
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
                ON DELETE RESTRICT
        );
    """)

    # Order_Details
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Order_Details (
            product_id INTEGER NOT NULL,
            order_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            selling_price TEXT NOT NULL CHECK (selling_price >= 0),
            FOREIGN KEY (order_id) REFERENCES orders (order_id)
                ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products (product_id)
                ON DELETE RESTRICT
        );
    """)
    connection.commit()
    connection.close()

    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Database created successfully.")

if __name__ == "__main__":
    create_database()