import os
import uuid
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
from flasgger import Swagger
load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    swagger = Swagger(app)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'shopsphere-dev-key-change-in-prod')

    db_url = os.environ.get('DATABASE_URL', '')
    if not db_url:
        raise RuntimeError('DATABASE_URL not set. Copy .env.example to .env and fill in your Supabase URI.')

    # Supabase transaction pooler (port 6543) requires sslmode=require.
    # Supabase session pooler (port 5432) also works — same rule.
    if '?' not in db_url:
        db_url += '?sslmode=require'
    elif 'sslmode' not in db_url:
        db_url += '&sslmode=require'

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Transaction pooler doesn't support persistent connections — disable pooling on SQLAlchemy side.
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from models import User, Product, Order, OrderItem, CoPurchase  # noqa

    @app.before_request
    def ensure_session_id():
        if 'sid' not in session:
            session['sid'] = str(uuid.uuid4())

    @app.before_request
    def boot_ds_once():
        from ds.structures import catalog, deal_heap, price_bst, rec_graph, search_trie
        if catalog.total() > 0:
            return
        from models import Product, CoPurchase
        for p in Product.query.all():
            d = p.to_dict()
            catalog.add(d)
            deal_heap.push(d)
            price_bst.insert(d)
            rec_graph.add_product(p.id)
            search_trie.insert(p.name, p.id)
            for word in p.name.lower().split():
                search_trie.insert(word, p.id)
        for cp in CoPurchase.query.all():
            for _ in range(cp.count):
                rec_graph.add_co_purchase(cp.product_a, cp.product_b)

    from routes.main import main_bp
    from routes.products import products_bp
    from routes.cart import cart_bp
    from routes.orders import orders_bp
    from routes.auth import auth_bp
    from routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
