import sqlite3
import random
from datetime import datetime, timedelta
from typing import Literal

from faker import Faker

fake = Faker("en_GB")

COUNTRY_LOCALES = {
    "GB": "en_GB",
    "PL": "pl_PL",
    "DE": "de_DE",
    "FR": "fr_FR",
    "NL": "nl_NL",
    "IE": "en_IE",
}
COUNTRY_WEIGHTS = {
    "GB": 70,
    "PL": 8,
    "DE": 8,
    "FR": 6,
    "NL": 5,
    "IE": 3,
}

FAKERS_BY_COUNTRY = {code: Faker(locale) for code, locale in COUNTRY_LOCALES.items()}

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

# Kurierzy dopuszczeni przez CHECK w tabeli Orders, z wagami popularności (PL rynek)
COURIERS = ["InPost", "DHL", "DPD", "GLS", "Pocztex", "UPS", "FedEx", "Orlen Paczka"]
COURIER_WEIGHTS = [30, 20, 15, 10, 10, 5, 5, 5]

# Koszt dostawy zależny (z grubsza) od kuriera; realistyczne widełki PLN
COURIER_COST_RANGES = {
    "InPost": (0, 16),
    "DHL": (10, 25),
    "DPD": (10, 24),
    "GLS": (10, 24),
    "Pocztex": (8, 20),
    "UPS": (15, 40),
    "FedEx": (15, 45),
    "Orlen Paczka": (0, 13),
}


def generate_product_name() -> tuple[str, str]:
    category = random.choice(list(PRODUCT_CATEGORIES.keys()))
    base_name = random.choice(PRODUCT_CATEGORIES[category])

    possible_variants = CATEGORY_VARIANTS.get(category, [])
    if possible_variants and random.random() < 0.5:
        variant = random.choice(possible_variants)
        return f"{base_name} {variant}", category
    return base_name, category


OrderStatus = Literal[
    # A new order has just come in, but it hasn't been fully completed yet.
    "pending",
    # The customer filled out the order form but hasn't paid for it yet.
    "awaiting_payment",
    # The payment failed.
    "payment_failed",
    # The order has been paid for and is ready to be processed.
    "processing",
    # The order has been packed and is ready for shipping.
    "ready_to_ship",
    # The order has been shipped to the customer.
    "shipped",
    # The order has been delivered to the customer - END of the success path.
    "delivered_end",
    # The delivery attempt failed.
    "delivery_failed",
    # The customer has requested a return of the order.
    "return_requested",
    # The seller has accepted the return of the order.
    "return_accepted",
    # The seller has rejected the return of the order - END.
    "return_rejected",
    # The customer has sent the order back to the seller.
    "returned",
    # The seller has processed the return and refunded the customer - END.
    "refunded_end",
    # The seller has exchanged the order for a new one - END.
    "exchanged_end",
    # The seller has put the order on hold due to a payment issue, stock
    # shortage, or other problem.
    "on_hold",
    # The seller has cancelled the order due to a payment issue, stock
    # shortage, or other problem - END.
    "cancelled_end",
    # The customer has cancelled the order - END.
    "buyer_canceled_end",
]

ORDER_STATUSES: list[OrderStatus] = [
    "pending",
    "awaiting_payment",
    "payment_failed",
    "processing",
    "ready_to_ship",
    "shipped",
    "delivered_end",
    "delivery_failed",
    "return_requested",
    "return_accepted",
    "return_rejected",
    "returned",
    "refunded_end",
    "exchanged_end",
    "on_hold",
    "cancelled_end",
    "buyer_canceled_end",
]

STATUS_UPDATE_DAY_RANGES: dict[OrderStatus, tuple[int, int]] = {
    "pending": (0, 1),
    "awaiting_payment": (0, 1),
    "payment_failed": (0, 1),
    "processing": (0, 2),
    "on_hold": (1, 4),
    "ready_to_ship": (1, 3),
    "cancelled_end": (0, 2),
    "buyer_canceled_end": (0, 2),
    "shipped": (2, 5),
    "delivery_failed": (3, 7),
    "delivered_end": (3, 10),
    "return_requested": (10, 14),
    "return_accepted": (12, 16),
    "return_rejected": (12, 16),
    "returned": (14, 20),
    "refunded_end": (16, 24),
    "exchanged_end": (10, 18),
}


def get_status_emoji(status: OrderStatus) -> str:
    emoji = '❓'
    if status in ['pending', 'awaiting_payment']:
        emoji = '⏳'
    elif status == 'processing':
        emoji = '❗'
    elif status == 'ready_to_ship':
        emoji = '⚡'
    elif status == 'shipped':
        emoji = '🚚'
    elif status == 'delivered_end':
        emoji = '🆗'
    elif status == 'return_accepted':
        emoji = '📦'
    elif status in ['refunded_end', 'exchanged_end']:
        emoji = '↩️'
    elif status in ['payment_failed', 'delivery_failed', 'return_requested', 'returned', 'on_hold']:
        emoji = '‼️'
    elif status in ['cancelled_end', 'return_rejected', 'buyer_canceled_end']:
        emoji = '❌'
    return emoji


def random_datetime_between(start: datetime, end: datetime) -> str:
    """Returns a random timestamp (as a string) between start and end in SQLite format."""
    delta = end - start
    random_seconds = random.randint(0, max(int(delta.total_seconds()), 0))
    return (start + timedelta(seconds=random_seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def generate_ean13() -> str:
    """Generates a random, valid EAN-13 barcode (with correct check digit)."""
    digits = [random.randint(0, 9) for _ in range(12)]
    checksum = sum(d * (3 if i % 2 else 1) for i, d in enumerate(digits))
    check_digit = (10 - checksum % 10) % 10
    digits.append(check_digit)
    return "".join(map(str, digits))


def generate_nip() -> str:
    """Generuje losowy, poprawny (z sumą kontrolną) polski NIP."""
    weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    digits = [random.randint(0, 9) for _ in range(9)]
    checksum = sum(w * d for w, d in zip(weights, digits)) % 11
    if checksum == 10:
        return generate_nip()
    digits.append(checksum)
    return "".join(map(str, digits))


def seed_products(cursor, n: int) -> list[int]:
    ids = []
    used_eans = set()
    for _ in range(n):
        name, category = generate_product_name()
        min_cost, max_cost = CATEGORY_COST_RANGES[category]
        cost = round(random.uniform(min_cost, max_cost), 2)
        rrp = round(cost * random.uniform(1.15, 1.6), 2)

        review_count = random.randint(0, 500)
        review_avg = round(random.uniform(1.0, 5.0), 2) if review_count > 0 else None

        ean = generate_ean13()
        while ean in used_eans:
            ean = generate_ean13()
        used_eans.add(ean)

        cursor.execute(
            """
            INSERT INTO Products (name, ean, rrp, cost, review_avg, review_count)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, ean, str(rrp), str(cost), review_avg, review_count),
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
        order_date = order_date_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        update_earliest = order_date_dt + timedelta(days=min_days)
        update_latest = min(order_date_dt + timedelta(days=max_days), now)
        if update_earliest > update_latest:
            update_earliest = update_latest
        update_date = random_datetime_between(update_earliest, update_latest)

        # Kraj dostawy, a za nim spójny lokalnie faker (adres/telefon/imię
        # muszą pasować do kraju, nie mogą zostać "brytyjskie" dla PL/DE itd.)
        delivery_country_code = random.choices(
            list(COUNTRY_WEIGHTS.keys()), weights=list(COUNTRY_WEIGHTS.values()), k=1
        )[0]
        local_fake = FAKERS_BY_COUNTRY[delivery_country_code]

        delivery_city = local_fake.city()
        delivery_street = local_fake.street_address()
        delivery_postal_code = local_fake.postcode()
        delivery_phone = local_fake.phone_number()

        courier = random.choices(COURIERS, weights=COURIER_WEIGHTS, k=1)[0]
        min_cost, max_cost = COURIER_COST_RANGES[courier]
        delivery_cost = round(random.uniform(min_cost, max_cost), 2)
        # przesyłki zagraniczne są droższe
        if delivery_country_code != "PL":
            delivery_cost = round(delivery_cost + random.uniform(15, 40), 2)

        # ok. 35% zamówień z fakturą
        invoice = 1 if random.random() < 0.35 else 0

        # invoice = 1 (faktura na firmę): first_name = nazwa firmy, last_name = NIP
        # invoice = 0 (paragon / os. prywatna): zwykłe imię i nazwisko odbiorcy
        if invoice:
            delivery_first_name = local_fake.company()
            delivery_last_name = generate_nip()
        else:
            delivery_first_name = local_fake.first_name()
            delivery_last_name = local_fake.last_name()

        cursor.execute(
            """
            INSERT INTO Orders (
                customer_id, order_status, order_date, update_date, invoice,
                delivery_first_name, delivery_last_name, delivery_phone, delivery_country_code,
                delivery_city, delivery_street, delivery_postal_code,
                courier, delivery_cost, order_total
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                customer_id,
                status,
                order_date,
                update_date,
                invoice,
                delivery_first_name,
                delivery_last_name,
                delivery_phone,
                delivery_country_code,
                delivery_city,
                delivery_street,
                delivery_postal_code,
                courier,
                str(delivery_cost),
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