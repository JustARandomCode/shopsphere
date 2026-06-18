from flask import Blueprint, jsonify, request, session
from ds.structures import search_trie, catalog, get_cart, order_queue, deal_heap

api_bp = Blueprint('api', __name__)


@api_bp.route('/search')
def search():
    """
    Search products by name prefix or keyword.
    ---
    tags:
      - API
    parameters:
      - name: q
        in: query
        type: string
        required: true
        description: Search term with at least 2 characters.
        example: phone
    responses:
      200:
        description: A list of matching products.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              name:
                type: string
                example: Wireless Headphones
              description:
                type: string
                example: Noise-cancelling Bluetooth headphones.
              price:
                type: number
                format: float
                example: 129.99
              discount_pct:
                type: integer
                example: 15
              stock:
                type: integer
                example: 24
              category:
                type: string
                example: Electronics
              image_url:
                type: string
                example: https://picsum.photos/seed/1/400/400
    """
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])
    ids = search_trie.search(q, limit=8)
    results = [p for p in catalog.get_all() if p['id'] in ids]
    return jsonify(results[:8])


@api_bp.route('/cart/count')
def cart_count():
    """
    Get the current session cart count and total.
    ---
    tags:
      - API
    responses:
      200:
        description: Cart summary for the current session.
        schema:
          type: object
          properties:
            count:
              type: integer
              example: 3
            total:
              type: number
              format: float
              example: 259.98
    """
    sid = session.get('sid', '')
    cart = get_cart(sid)
    return jsonify({'count': cart.size(), 'total': cart.total()})


@api_bp.route('/ds/status')
def ds_status():
    """
    Get live data-structure status for the dashboard.
    ---
    tags:
      - API
    responses:
      200:
        description: Current in-memory data-structure stats and cart contents.
        schema:
          type: object
          properties:
            array_catalog_size:
              type: integer
              example: 29
            stack_cart_size:
              type: integer
              example: 2
            queue_orders_waiting:
              type: integer
              example: 1
            heap_deals_loaded:
              type: integer
              example: 29
            linked_list_cart_items:
              type: array
              items:
                type: object
                properties:
                  product_id:
                    type: integer
                    example: 1
                  quantity:
                    type: integer
                    example: 2
                  price:
                    type: number
                    format: float
                    example: 129.99
                  name:
                    type: string
                    example: Wireless Headphones
            trie_ready:
              type: boolean
              example: true
            bst_ready:
              type: boolean
              example: true
            graph_ready:
              type: boolean
              example: true
    """
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
