from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from ds.structures import get_cart

cart_bp = Blueprint('cart', __name__)


@cart_bp.route('/')
def view():
    sid = session.get('sid', '')
    cart = get_cart(sid)
    return render_template('cart.html', items=cart.items(), total=cart.total(), count=cart.size())


@cart_bp.route('/add', methods=['POST'])
def add():
    sid = session.get('sid', '')
    cart = get_cart(sid)
    data = request.get_json() or request.form
    cart.add_item(
        int(data.get('product_id')),
        int(data.get('quantity', 1)),
        float(data.get('price')),
        str(data.get('name'))
    )
    return jsonify({'status': 'ok', 'count': cart.size(), 'total': cart.total()})


@cart_bp.route('/remove', methods=['POST'])
def remove():
    sid = session.get('sid', '')
    cart = get_cart(sid)
    data = request.get_json() or request.form
    cart.remove_item(int(data.get('product_id')))
    return jsonify({'status': 'ok', 'count': cart.size(), 'total': cart.total()})


@cart_bp.route('/clear', methods=['POST'])
def clear():
    sid = session.get('sid', '')
    cart = get_cart(sid)
    cart.clear()
    return redirect(url_for('cart.view'))
