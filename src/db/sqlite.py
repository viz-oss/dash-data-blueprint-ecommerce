import sqlite3
import random
from datetime import datetime, timedelta

from faker import Faker

fake = Faker("en_GB")

N_CUSTOMERS = 1000
N_PRODUCTS = 80
OFFER_COVERAGE = 0.85       
N_ORDERS = 2000
MAX_ITEMS_PER_ORDER = 4

PRODUCT_CATEGORIES = {
    "Laptop": ["Dell Inspiron", "Lenovo ThinkPad", "HP Pavilion", "Asus VivoBook", "Acer Aspire", "MacBook Air"],
    "Smartphone": ["Samsung Galaxy S23", "iPhone 15", "Xiaomi Redmi Note 13", "Google Pixel 8", "OnePlus 12"],
    "Headphones": ["Sony WH-1000XM5", "JBL Tune 510BT", "Apple AirPods Pro", "Sennheiser HD 450BT", "Bose QuietComfort"],
    "TV": ["Samsung QLED 55\"", "LG OLED 65\"", "Sony Bravia 50\"", "Philips Ambilight 43\""],
    "Jacket": ["The North Face Winter Jacket", "Columbia Rain Jacket", "Reserved Quilted Jacket", "4F Softshell Jacket"],
    "Shoes": ["Nike Air Zoom Running Shoes", "Adidas Superstar Sneakers", "Salomon Trekking Shoes", "CMP Winter Boots"],
    "Coffee Machine": ["DeLonghi Magnifica Coffee Machine", "Philips Series 2200 Coffee Machine", "Krups Essential Coffee Machine"],
    "Vacuum Cleaner": ["Dyson V15 Vacuum Cleaner", "Xiaomi Mi Vacuum", "Bosch Serie 6 Vacuum Cleaner"],
    "Bicycle": ["Kross Level Mountain Bike", "Romet Wagant City Bike", "Ebike City Electric Bike"],
    "Book": ["The Lord of the Rings", "Crime and Punishment", "A Brief History of Time", "Atomic Habits", "The Psychology of Money"],
    "Toy": ["LEGO City Set", "Trefl 1000-piece Puzzle", "Funko Pop Figure", "Settlers of Catan Board Game"],
    "Cosmetic": ["Nivea Moisturising Cream", "Dior Sauvage Perfume", "L'Oreal Elseve Shampoo", "La Roche-Posay Serum"],
}


# Variants matched to product type - to avoid e.g. "T-shirt 128GB"
STORAGE_VARIANTS = ["64GB", "128GB", "256GB", "512GB", "1TB"]
COLOR_VARIANTS = ["Black", "White", "Blue", "Grey", "Red"]
CLOTHING_SIZE_VARIANTS = ["Size S", "Size M", "Size L", "Size XL"]
YEAR_VARIANTS = ["2023", "2024", "2025"]
TIER_VARIANTS = ["Pro", "Plus", "Lite", "Max"]

CATEGORY_VARIANTS = {
    "Laptop": COLOR_VARIANTS + STORAGE_VARIANTS + TIER_VARIANTS,
    "Smartphone": COLOR_VARIANTS + STORAGE_VARIANTS,
    "Headphones": COLOR_VARIANTS,
    "TV": YEAR_VARIANTS,
    "Jacket": CLOTHING_SIZE_VARIANTS + COLOR_VARIANTS,
    "Shoes": CLOTHING_SIZE_VARIANTS,
    "Coffee Machine": COLOR_VARIANTS,
    "Vacuum Cleaner": COLOR_VARIANTS,
    "Bicycle": COLOR_VARIANTS + ["Frame Size S", "Frame Size M", "Frame Size L"],
    "Book": [],        
    "Toy": [],        
    "Cosmetic": [],   
}


CATEGORY_COST_RANGES = {
    "Laptop": (300, 1200),
    "Smartphone": (150, 1000),
    "Headphones": (10, 250),
    "TV": (250, 1600),
    "Jacket": (20, 160),
    "Shoes": (15, 120),
    "Coffee Machine": (30, 600),
    "Vacuum Cleaner": (40, 700),
    "Bicycle": (120, 2400),
    "Book": (3, 16),
    "Toy": (4, 80),
    "Cosmetic": (3, 70),
}


def generate_product_name() -> tuple[str, str]:
    category = random.choice(list(PRODUCT_CATEGORIES.keys()))
    base_name = random.choice(PRODUCT_CATEGORIES[category])

    possible_variants = CATEGORY_VARIANTS.get(category, [])
    if possible_variants and random.random() < 0.5:
        variant = random.choice(possible_variants)
        return f"{base_name} {variant}", category
    return base_name, category


ORDER_STATUSES = [
    "pending",
    "processing",
    "ready_to_ship",
    "shipped",
    "delivered",
    "delivery_failed",
    "return_requested",
    "returned",
    "exchange",
    "on_hold",
    "cancelled",
    "awaiting_payment",
    "payment_failed",
]

STATUS_UPDATE_DAY_RANGES = {
    "pending": (0, 1),
    "awaiting_payment": (0, 1),
    "payment_failed": (0, 1),
    "processing": (0, 2),
    "on_hold": (1, 4),
    "ready_to_ship": (1, 3),
    "cancelled": (0, 2),
    "shipped": (2, 5),
    "delivery_failed": (3, 7),
    "delivered": (3, 10),
    "return_requested": (5, 15),
    "exchange": (5, 18),
    "returned": (5, 21),
}


def random_datetime_between(start: datetime, end: datetime) -> str:
    """Returns a random timestamp (as a string) between start and end in SQLite format."""
    delta = end - start
    random_seconds = random.randint(0, max(int(delta.total_seconds()), 0))
    return (start + timedelta(seconds=random_seconds)).strftime("%Y-%m-%d %H:%M:%S")


def seed_customers(cursor, n: int) -> list[int]:
    ids = []
    used_identifiers = set()
    for _ in range(n):
        identifier = fake.unique.email()
        used_identifiers.add(identifier)
        registration_date = random_datetime_between(
            datetime.now() - timedelta(days=730), datetime.now()
        )
        cursor.execute(
            """
            INSERT INTO Customers (identifier, registration_date)
            VALUES (?, ?)
            """,
            (identifier, registration_date),
        )
        ids.append(cursor.lastrowid)
    return ids


def seed_products(cursor, n: int) -> list[int]:
    ids = []
    for _ in range(n):
        name, category = generate_product_name()
        min_cost, max_cost = CATEGORY_COST_RANGES[category]
        cost = round(random.uniform(min_cost, max_cost), 2)
        # RRP is always >= cost, typical margin 15-60%
        rrp = round(cost * random.uniform(1.15, 1.6), 2)

        review_count = random.randint(0, 500)
        review_avg = round(random.uniform(1.0, 5.0), 2) if review_count > 0 else None

        cursor.execute(
            """
            INSERT INTO Products (name, rrp, cost, review_avg, review_count)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, str(rrp), str(cost), review_avg, review_count),
        )
        ids.append(cursor.lastrowid)
    return ids


def seed_offer(cursor, product_ids: list[int], coverage: float) -> list[int]:
    """Not every product has to be currently on offer - we sample a subset."""
    offered_ids = random.sample(
        product_ids, k=int(len(product_ids) * coverage)
    )
    for product_id in offered_ids:
        stock_quantity = random.randint(0, 1000)
        listing_date = random_datetime_between(
            datetime.now() - timedelta(days=365), datetime.now()
        )
        cursor.execute(
            """
            INSERT INTO Offer (product_id, stock_quantity, listing_date)
            VALUES (?, ?, ?)
            """,
            (product_id, stock_quantity, listing_date),
        )
    return offered_ids


def seed_orders_with_details(
    cursor,
    customer_ids: list[int],
    product_ids: list[int],
    products_rrp_map: dict[int, float],
    n_orders: int,
    max_items: int,
) -> None:
    now = datetime.now()

    for _ in range(n_orders):
        customer_id = random.choice(customer_ids)
        status = random.choice(ORDER_STATUSES)
        min_days, max_days = STATUS_UPDATE_DAY_RANGES[status]

        oldest_possible = 365
        days_ago = random.randint(min_days, max(min_days, oldest_possible))
        order_date_dt = now - timedelta(
            days=days_ago, seconds=random.randint(0, 86400)
        )
        order_date = order_date_dt.strftime("%Y-%m-%d %H:%M:%S")
        update_earliest = order_date_dt + timedelta(days=min_days)
        update_latest = min(order_date_dt + timedelta(days=max_days), now)
        if update_earliest > update_latest:
            update_earliest = update_latest
        update_date = random_datetime_between(update_earliest, update_latest)

        address = fake.address() if hasattr(fake, "address") else None
        delivery_city = fake.city()
        delivery_street = fake.street_address()
        delivery_postal_code = fake.postcode()

        cursor.execute(
            """
            INSERT INTO Orders (
                customer_id, order_status, order_date, update_date,
                delivery_city, delivery_street, delivery_postal_code, order_total
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                customer_id,
                status,
                order_date,
                update_date,
                delivery_city,
                delivery_street,
                delivery_postal_code,
                "0", 
            ),
        )
        order_id = cursor.lastrowid

        n_items = random.randint(1, max_items)
        chosen_products = random.sample(
            product_ids, k=min(n_items, len(product_ids))
        )

        order_total = 0.0
        for product_id in chosen_products:
            quantity = random.randint(1, 5)
            rrp = products_rrp_map[product_id]
            selling_price = round(rrp * random.uniform(0.85, 1.0), 2)

            cursor.execute(
                """
                INSERT INTO Order_Details (product_id, order_id, quantity, selling_price)
                VALUES (?, ?, ?, ?)
                """,
                (product_id, order_id, quantity, str(selling_price)),
            )
            order_total += selling_price * quantity

        cursor.execute(
            "UPDATE Orders SET order_total = ? WHERE order_id = ?",
            (str(round(order_total, 2)), order_id),
        )


def main() -> None:
    connection = sqlite3.connect("db.sqlite")
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    customer_ids = seed_customers(cursor, N_CUSTOMERS)
    product_ids = seed_products(cursor, N_PRODUCTS)
    cursor.execute("SELECT product_id, rrp FROM Products")
    products_rrp_map = {row[0]: float(row[1]) for row in cursor.fetchall()}

    seed_offer(cursor, product_ids, OFFER_COVERAGE)
    seed_orders_with_details(
        cursor, customer_ids, product_ids, products_rrp_map, N_ORDERS, MAX_ITEMS_PER_ORDER
    )

    connection.commit()
    connection.close()

    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Database populated with test data.")


if __name__ == "__main__":
    main()