"""
Seed PostgreSQL with sample products and co-purchases.
Run once: python seed.py
The running Flask process loads its own DS from DB via before_request.
"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Product, CoPurchase

PRODUCTS = [
    # Electronics
    {"name": "Wireless Noise-Cancelling Headphones", "category": "Electronics", "price": 8999, "discount_pct": 20, "stock": 50,
     "description": "Premium ANC headphones with 30-hour battery life and foldable design."},
    {"name": "Mechanical Keyboard RGB TKL", "category": "Electronics", "price": 5499, "discount_pct": 15, "stock": 30,
     "description": "Compact tenkeyless mechanical keyboard with hot-swap switches and per-key RGB."},
    {"name": "USB-C Hub 7-in-1", "category": "Electronics", "price": 2499, "discount_pct": 10, "stock": 80,
     "description": "7-port hub: 4K HDMI, 3x USB-A, SD card, PD charging."},
    {"name": "27-inch 4K Monitor", "category": "Electronics", "price": 24999, "discount_pct": 8, "stock": 20,
     "description": "IPS panel, 144Hz, HDR400, factory-calibrated colour accuracy."},
    {"name": "Portable SSD 1TB", "category": "Electronics", "price": 7999, "discount_pct": 25, "stock": 45,
     "description": "NVMe speeds in a palm-sized chassis. 1050 MB/s read."},
    {"name": "Wireless Ergonomic Mouse", "category": "Electronics", "price": 3299, "discount_pct": 12, "stock": 60,
     "description": "Sculpted for long hours. Silent clicks, 70-day battery life."},
    {"name": "Smart LED Desk Lamp", "category": "Electronics", "price": 1899, "discount_pct": 5, "stock": 100,
     "description": "Touch dimming, colour temperature control, USB-A charging port."},
    {"name": "Bluetooth Speaker Waterproof", "category": "Electronics", "price": 4499, "discount_pct": 18, "stock": 35,
     "description": "IPX7 waterproof, 360 degree sound, 24-hour playtime."},
    # Clothing
    {"name": "Oversized Streetwear Hoodie", "category": "Clothing", "price": 1799, "discount_pct": 30, "stock": 120,
     "description": "400 GSM heavyweight fleece, dropped shoulders, kangaroo pocket."},
    {"name": "Slim-Fit Chino Trousers", "category": "Clothing", "price": 1299, "discount_pct": 10, "stock": 90,
     "description": "Stretch-cotton blend. Available in 6 earth tones."},
    {"name": "Technical Running Jacket", "category": "Clothing", "price": 3499, "discount_pct": 20, "stock": 40,
     "description": "Lightweight wind and water resistant. Reflective details."},
    {"name": "Graphic Print Tee Brutalist", "category": "Clothing", "price": 899, "discount_pct": 0, "stock": 200,
     "description": "100% combed cotton. Screen-printed brutalist architecture graphic."},
    {"name": "Merino Wool Beanie", "category": "Clothing", "price": 699, "discount_pct": 5, "stock": 150,
     "description": "Fine-grade merino. Anti-itch, breathable, temperature regulating."},
    {"name": "Cargo Shorts Tech Fabric", "category": "Clothing", "price": 1599, "discount_pct": 15, "stock": 70,
     "description": "8-pocket design in ripstop nylon. Quick-dry, stretch."},
    # Home & Kitchen
    {"name": "Pour Over Coffee Set", "category": "Home & Kitchen", "price": 2199, "discount_pct": 8, "stock": 55,
     "description": "Gooseneck kettle, Chemex-style carafe, hand grinder."},
    {"name": "Cast Iron Skillet 10-inch", "category": "Home & Kitchen", "price": 2899, "discount_pct": 0, "stock": 40,
     "description": "Pre-seasoned. Works on induction, gas, oven, campfire."},
    {"name": "Bamboo Cutting Board Set", "category": "Home & Kitchen", "price": 1099, "discount_pct": 20, "stock": 75,
     "description": "3-piece set: large, medium, small. Anti-bacterial bamboo."},
    {"name": "Sous Vide Precision Cooker", "category": "Home & Kitchen", "price": 6499, "discount_pct": 12, "stock": 25,
     "description": "1200W, Wi-Fi enabled, 0.1 degree C precision, quiet motor."},
    {"name": "Insulated Water Bottle 1L", "category": "Home & Kitchen", "price": 999, "discount_pct": 0, "stock": 200,
     "description": "Triple-wall vacuum insulation. Keeps cold 24h, hot 12h."},
    # Books
    {"name": "The Algorithm Design Manual Skiena", "category": "Books", "price": 1499, "discount_pct": 0, "stock": 30,
     "description": "The definitive guide to algorithm design. Used in top CS programs globally."},
    {"name": "Designing Data-Intensive Applications", "category": "Books", "price": 1799, "discount_pct": 5, "stock": 25,
     "description": "Kleppmann on distributed systems and data engineering."},
    {"name": "Clean Code Robert C Martin", "category": "Books", "price": 1199, "discount_pct": 0, "stock": 40,
     "description": "Principles, patterns, and practices of writing clean code."},
    {"name": "System Design Interview Vol 2", "category": "Books", "price": 1399, "discount_pct": 10, "stock": 35,
     "description": "An insider guide to scalable system design for SWE interviews."},
    # Sports
    {"name": "Adjustable Dumbbell Set 2-24kg", "category": "Sports", "price": 8999, "discount_pct": 15, "stock": 20,
     "description": "Space-saving dial-select dumbbell. Replaces 15 pairs."},
    {"name": "Yoga Mat 6mm Premium Cork", "category": "Sports", "price": 1899, "discount_pct": 10, "stock": 60,
     "description": "Natural cork top layer. Non-slip, antimicrobial, biodegradable."},
    {"name": "Resistance Band Set 5-piece", "category": "Sports", "price": 799, "discount_pct": 20, "stock": 120,
     "description": "5 resistance levels, fabric-covered, non-roll design."},
    # Accessories
    {"name": "Minimalist Leather Wallet", "category": "Accessories", "price": 1299, "discount_pct": 0, "stock": 80,
     "description": "Full-grain vegetable-tanned leather. Holds 8 cards, RFID block."},
    {"name": "Canvas Backpack 25L", "category": "Accessories", "price": 2499, "discount_pct": 12, "stock": 45,
     "description": "Waxed canvas, brass hardware, padded 15 inch laptop sleeve."},
    {"name": "Mechanical Wristwatch", "category": "Accessories", "price": 12999, "discount_pct": 0, "stock": 15,
     "description": "38mm case, exhibition caseback, 42-hour power reserve."},
]

CO_PURCHASE_PAIRS = [
    (0, 1), (0, 5), (1, 5), (0, 2), (3, 0), (3, 2),
    (1, 2), (4, 1), (4, 0), (7, 0), (6, 0),
    (8, 9), (8, 12), (9, 13), (10, 9), (11, 8),
    (14, 15), (14, 17), (15, 16), (17, 18),
    (19, 20), (19, 21), (20, 22), (21, 22),
    (23, 24), (24, 25), (23, 25),
    (26, 27), (27, 28),
]


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        CoPurchase.query.delete()
        Product.query.delete()
        db.session.commit()

        for i, p in enumerate(PRODUCTS):
            db.session.add(Product(
                name=p['name'],
                category=p['category'],
                price=p['price'],
                discount_pct=p['discount_pct'],
                stock=p['stock'],
                description=p['description'],
                image_url=f'https://picsum.photos/seed/{i + 1}/400/400'
            ))
        db.session.commit()
        print(f'Seeded {len(PRODUCTS)} products')

        ids = [p.id for p in Product.query.order_by(Product.id).all()]
        for a_idx, b_idx in CO_PURCHASE_PAIRS:
            if a_idx < len(ids) and b_idx < len(ids):
                db.session.add(CoPurchase(
                    product_a=ids[a_idx],
                    product_b=ids[b_idx],
                    count=1
                ))
        db.session.commit()
        print(f'Seeded {len(CO_PURCHASE_PAIRS)} co-purchase pairs')
        print('Done. Run: python run.py')


if __name__ == '__main__':
    seed()
