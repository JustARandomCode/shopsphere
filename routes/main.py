from flask import Blueprint, render_template, session
from ds.structures import catalog, deal_heap, get_recently_viewed

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    # DS boot fires via app.before_request — catalog is guaranteed loaded here.
    sid = session.get('sid', '')
    rv_ids = get_recently_viewed(sid).get()

    top_deals = deal_heap.top_deals(6)
    featured = catalog.paginate(1, 8)
    rv_products = [p for p in catalog.get_all() if p['id'] in rv_ids[:5]] if rv_ids else []
    categories = sorted({p['category'] for p in catalog.get_all() if p.get('category')})

    return render_template(
        'index.html',
        top_deals=top_deals,
        featured=featured,
        recently_viewed=rv_products,
        categories=categories
    )
