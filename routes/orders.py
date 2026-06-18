from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from app import db
from models import Order, OrderItem, Product, CoPurchase
from ds.structures import get_cart, order_queue, rec_graph
import itertools

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/checkout', methods=['POST'])
def checkout():
    sid = session.get('sid', '')
    cart = get_cart(sid)
    if cart.size() == 0:
        return redirect(url_for('cart.view'))

    items = cart.items()          # snapshot before clear
    total_amount = cart.total()   # snapshot before clear

    order = Order(session_id=sid, total=total_amount, status='pending')
    db.session.add(order)
    db.session.flush()            # get order.id without full commit

    product_ids = []
    for item in items:
        db.session.add(OrderItem(
            order_id=order.id,
            product_id=item['product_id'],
            quantity=item['quantity'],
            price=item['price']
        ))
        product_ids.append(item['product_id'])

        p = db.session.get(Product, item['product_id'])
        if p:
            p.stock = max(0, p.stock - item['quantity'])

    # Co-purchase edges: persist + update in-memory graph
    for a, b in itertools.combinations(product_ids, 2):
        rec_graph.add_co_purchase(a, b)
        cp = CoPurchase.query.filter(
            ((CoPurchase.product_a == a) & (CoPurchase.product_b == b)) |
            ((CoPurchase.product_a == b) & (CoPurchase.product_b == a))
        ).first()
        if cp:
            cp.count += 1
        else:
            db.session.add(CoPurchase(product_a=a, product_b=b, count=1))

    db.session.commit()

    order_queue.enqueue({
        'order_id': order.id,
        'session_id': sid,
        'total': float(total_amount),
        'items': items
    })

    cart.clear()
    return redirect(url_for('orders.confirmation', order_id=order.id))


@orders_bp.route('/confirmation/<int:order_id>')
def confirmation(order_id):
    order = db.session.get(Order, order_id)
    if order is None:
        from flask import abort
        abort(404)
    return render_template('confirmation.html', order=order)


@orders_bp.route('/queue')
def queue_status():
    return jsonify({
        'queue_size': order_queue.size(),
        'orders': order_queue.all_orders()[:10]
    })
