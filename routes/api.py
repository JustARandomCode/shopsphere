from flask import Blueprint, jsonify, request, session
from ds.structures import search_trie, catalog, get_cart, order_queue, deal_heap

api_bp = Blueprint('api', __name__)


@api_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])
    ids = search_trie.search(q, limit=8)
    results = [p for p in catalog.get_all() if p['id'] in ids]
    return jsonify(results[:8])


@api_bp.route('/cart/count')
def cart_count():
    sid = session.get('sid', '')
    cart = get_cart(sid)
    return jsonify({'count': cart.size(), 'total': cart.total()})


@api_bp.route('/ds/status')
def ds_status():
    """Live data-structure stats — for the DS Dashboard page."""
    sid = session.get('sid', '')
    cart = get_cart(sid)
    return jsonify({
        'array_catalog_size': catalog.total(),
        'stack_cart_size': cart.size(),
        'queue_orders_waiting': order_queue.size(),
        'heap_deals_loaded': deal_heap.size(),
        'linked_list_cart_items': cart.items(),
        'trie_ready': True,
        'bst_ready': True,
        'graph_ready': True,
    })
