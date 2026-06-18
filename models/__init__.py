# models/__init__.py
# Import db from extensions, NOT from app — breaks circular import.
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# db is injected via app.py's db.init_app(app).
# We import it from app only at runtime (inside functions) when needed outside models.
# At module level, we grab it from the app module which is safe because
# app.py defines db at module scope before create_app() is called.
from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='user', lazy=True)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_pct = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(80))
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'discount_pct': self.discount_pct,
            'stock': self.stock,
            'category': self.category,
            'image_url': self.image_url or f'https://picsum.photos/seed/{self.id}/400/400',
        }


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(36))
    status = db.Column(db.String(30), default='pending')
    total = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    product = db.relationship('Product')


class CoPurchase(db.Model):
    """Tracks co-purchased product pairs — feeds RecommendationGraph on boot."""
    __tablename__ = 'co_purchases'
    id = db.Column(db.Integer, primary_key=True)
    product_a = db.Column(db.Integer, db.ForeignKey('products.id'))
    product_b = db.Column(db.Integer, db.ForeignKey('products.id'))
    count = db.Column(db.Integer, default=1)
