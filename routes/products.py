from flask import Blueprint, render_template, request, session
from models import Product, db
from ds.structures import (
    catalog, price_bst, rec_graph,
    get_recently_viewed, get_history
)

products_bp = Blueprint('products', __name__)


@products_bp.route('/')
def listing():
    page = int(request.args.get('page', 1))
    category = request.args.get('category', '').strip()
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')

    has_price_filter = min_price != '' or max_price != ''
    low = float(min_price) if min_price else 0.0
    high = float(max_price) if max_price else 999_999.0

    if has_price_filter:
        items = price_bst.range_query(low, high)
        if category:
            items = [i for i in items if i.get('category') == category]
    elif category:
        items = catalog.filter_by_category(category)
    else:
        items = catalog.get_all()

    total = len(items)
    size = 12
    start = (page - 1) * size
    paginated = items[start:start + size]

    categories = sorted({p['category'] for p in catalog.get_all() if p.get('category')})

    return render_template(
        'products.html',
        products=paginated,
        page=page,
        total=total,
        categories=categories,
        current_category=category,
        min_price=min_price,
        max_price=max_price,
    )


@products_bp.route('/<int:pid>')
def detail(pid):
    sid = session.get('sid', '')

    product = db.session.get(Product, pid)
    if product is None:
        from flask import abort
        abort(404)

    p_dict = product.to_dict()

    # Stack: record visit (do this BEFORE calling back() so history is accurate)
    hist = get_history(sid)
    back_id = hist.current()       # peek without mutating
    hist.visit(pid)                # push current page

    # Deque: recently viewed
    get_recently_viewed(sid).view(pid)

    # Graph: recommendations via BFS
    rec_ids = rec_graph.recommend(pid, depth=2, top_k=4)
    recs = [p for p in catalog.get_all() if p['id'] in rec_ids]

    return render_template(
        'product_detail.html',
        product=p_dict,
        recommendations=recs,
        back_id=back_id if back_id != pid else None
    )
