# ShopSphere — Smart E-Commerce Platform

Full-stack Python e-commerce application where **every data structure is a live, functional component** — not a demo.

## Stack

- **Backend**: Python 3.11 + Flask
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Frontend**: Jinja2 templates · Claymorphism × Parallax × Kinetic Typography
- **DS Layer**: Pure Python, zero external libraries for DS implementations

---

## Data Structure → Feature Map

| Data Structure | Location | Real-World Role | Complexity |
|---|---|---|---|
| **Array / List** | `ds/structures.py: ProductCatalog` | Product catalog with O(1) index pagination | `O(1)` page slice |
| **Linked List** | `ds/structures.py: ShoppingCart` | Each cart item is a node; insert at head | `O(1)` insert, `O(n)` total |
| **Stack** | `ds/structures.py: BrowsingHistory` | Back-navigation between product pages | `O(1)` push/pop |
| **Queue** | `ds/structures.py: OrderQueue` | FIFO order processing pipeline, thread-safe | `O(1)` enqueue/dequeue |
| **Hash Map** | `ds/structures.py: SessionStore` | Custom hash map with separate chaining for sessions | `O(1)` avg get/set |
| **Min-Heap** | `ds/structures.py: DealHeap` | Flash deal ranking by discount % | `O(k log n)` top-k |
| **BST** | `ds/structures.py: PriceBST` | Price range filter — range query in O(k + log n) | `O(log n)` insert |
| **Graph** | `ds/structures.py: RecommendationGraph` | Co-purchase weighted graph, BFS for "also bought" | `O(V + E)` BFS |
| **Trie** | `ds/structures.py: SearchTrie` | Search bar autocomplete, O(m) prefix lookup | `O(m)` search |
| **Deque** | `ds/structures.py: RecentlyViewed` | Double-ended queue, cap-bounded recently viewed | `O(1)` both ends |

---

## Setup

### 1. PostgreSQL

```bash
psql -U postgres
CREATE DATABASE shopsphere;
\q
```

### 2. Environment

```bash
cp .env.example .env
# Edit DATABASE_URL with your credentials
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Seed database

```bash
python seed.py
```

This creates 29 products across 6 categories, with co-purchase pairs to seed the recommendation graph.

### 5. Run

```bash
python run.py
```

Visit `http://localhost:5000`

---

## Project Structure

```
shopsphere/
├── run.py              # Entry point
├── app.py              # Flask factory + extensions
├── seed.py             # DB seeder
├── requirements.txt
├── .env.example
│
├── ds/
│   └── structures.py   # ALL 10 data structures — pure Python
│
├── models/
│   └── __init__.py     # SQLAlchemy models (User, Product, Order, etc.)
│
├── routes/
│   ├── main.py         # Homepage
│   ├── products.py     # Catalog + Detail
│   ├── cart.py         # Cart CRUD
│   ├── orders.py       # Checkout + Queue
│   ├── auth.py         # Login/Register
│   └── api.py          # JSON API (search, cart count, DS status)
│
└── templates/
    ├── base.html        # Design system + nav + parallax JS
    ├── index.html       # Homepage with kinetic hero + deals
    ├── products.html    # Catalog with BST price filter sidebar
    ├── product_detail.html  # Detail with parallax + graph recs
    ├── cart.html        # Cart with linked list visualization
    ├── confirmation.html
    └── auth.html
```

---

## API Endpoints

| Endpoint | Method | DS Used | Description |
|---|---|---|---|
| `/api/search?q=term` | GET | Trie | Autocomplete, returns matching products |
| `/api/cart/count` | GET | Linked List | Cart item count + total |
| `/api/ds/status` | GET | All | Live DS stats dump |
| `/orders/queue` | GET | Queue | Raw order queue state (JSON) |
| `/cart/add` | POST | Linked List | Insert node into cart |
| `/cart/remove` | POST | Linked List | Delete node from cart |

---

## DS Design Decisions

**Why a custom Hash Map instead of Python `dict`?**
To demonstrate separate chaining collision resolution. Python's dict is a hash map but the implementation is opaque.

**Why Linked List for cart instead of dict?**
Cart operations are dominated by: (1) insert item — O(1) head insert, (2) total traversal — O(n), (3) remove — O(n). A linked list models the actual access pattern. The traversal visualization on the cart page shows each node explicitly.

**Why BST for price filter instead of SQL WHERE?**
To demonstrate in-memory range queries. The BST is loaded from DB on first request and queried in-memory — faster for repeated filters, explicit O(log n) + O(k) complexity.

**Why Trie for search instead of ILIKE?**
Trie prefix queries are O(m) where m = query length, regardless of catalog size. SQL ILIKE is O(n) without a GIN index. The Trie also powers the autocomplete without a DB round-trip per keystroke.

---

## Frontend

**Design system**: Claymorphism × Dark mode × Parallax × Kinetic Typography

- Color: Deep indigo/violet base (`#0d0d1a`) with violet/pink/cyan accents
- Type: Syne (display, 900 weight) + Cabinet Grotesk (body) + JetBrains Mono (data/labels)
- Clay cards: multi-layer box-shadow with glow, subtle border, hover lift with spring easing
- Parallax: scroll-triggered Y translation on hero orbs and product images
- Kinetic type: word-split hover skew on `.kinetic` class
- DS ticker: scrolling marquee showing every DS → feature mapping
- Linked list visualization: visual node-chain on cart page
