"""
ShopSphere — Data Structures as Real-World E-Commerce Implementations
Every DS here is wired into actual app functionality, not demo code.
"""

from collections import deque
import heapq
import threading
import time
from typing import Any, Optional


# ─────────────────────────────────────────────
# 1. ARRAY/LIST  →  Product Catalog Pagination
# ─────────────────────────────────────────────
class ProductCatalog:
    """
    Array-backed catalog.
    Supports O(1) index access for pagination slicing.
    """
    def __init__(self):
        self._items: list = []

    def add(self, product: dict):
        self._items.append(product)

    def paginate(self, page: int, size: int = 12) -> list:
        start = (page - 1) * size
        return self._items[start:start + size]

    def total(self) -> int:
        return len(self._items)

    def get_all(self) -> list:
        return self._items

    def filter_by_category(self, category: str) -> list:
        return [p for p in self._items if p.get('category') == category]


# ─────────────────────────────────────────────
# 2. STACK  →  Browsing History (Back navigation)
# ─────────────────────────────────────────────
class BrowsingHistory:
    """
    LIFO Stack — user navigates product pages.
    Back button = pop(). Exactly how browser history works.
    """
    def __init__(self):
        self._stack: list = []

    def visit(self, product_id: int):
        if self._stack and self._stack[-1] == product_id:
            return
        self._stack.append(product_id)

    def back(self) -> Optional[int]:
        if len(self._stack) > 1:
            self._stack.pop()
            return self._stack[-1]
        return None

    def current(self) -> Optional[int]:
        return self._stack[-1] if self._stack else None

    def history(self) -> list:
        return list(reversed(self._stack))


# ─────────────────────────────────────────────
# 3. QUEUE  →  Order Processing Pipeline
# ─────────────────────────────────────────────
class OrderQueue:
    """
    FIFO Queue — orders enter and are processed in arrival order.
    Thread-safe with deque for O(1) enqueue/dequeue.
    """
    def __init__(self):
        self._queue: deque = deque()
        self._lock = threading.Lock()

    def enqueue(self, order: dict):
        with self._lock:
            order['queued_at'] = time.time()
            order['status'] = 'queued'
            self._queue.append(order)

    def dequeue(self) -> Optional[dict]:
        with self._lock:
            if self._queue:
                return self._queue.popleft()
            return None

    def peek(self) -> Optional[dict]:
        return self._queue[0] if self._queue else None

    def size(self) -> int:
        return len(self._queue)

    def all_orders(self) -> list:
        return list(self._queue)


# ─────────────────────────────────────────────
# 4. LINKED LIST  →  Shopping Cart
# ─────────────────────────────────────────────
class CartNode:
    def __init__(self, product_id: int, quantity: int, price: float, name: str):
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
        self.name = name
        self.next: Optional['CartNode'] = None


class ShoppingCart:
    """
    Singly Linked List — each cart item is a node.
    Allows O(1) insertion, O(n) traversal for total.
    Models real cart: add, remove, update quantities.
    """
    def __init__(self):
        self.head: Optional[CartNode] = None
        self._size = 0

    def add_item(self, product_id: int, quantity: int, price: float, name: str):
        # Check if exists — update quantity
        node = self.head
        while node:
            if node.product_id == product_id:
                node.quantity += quantity
                return
            node = node.next
        # Insert at head O(1)
        new_node = CartNode(product_id, quantity, price, name)
        new_node.next = self.head
        self.head = new_node
        self._size += 1

    def remove_item(self, product_id: int):
        if not self.head:
            return
        if self.head.product_id == product_id:
            self.head = self.head.next
            self._size -= 1
            return
        node = self.head
        while node.next:
            if node.next.product_id == product_id:
                node.next = node.next.next
                self._size -= 1
                return
            node = node.next

    def total(self) -> float:
        total = 0.0
        node = self.head
        while node:
            total += node.price * node.quantity
            node = node.next
        return round(total, 2)

    def items(self) -> list:
        result = []
        node = self.head
        while node:
            result.append({
                'product_id': node.product_id,
                'name': node.name,
                'quantity': node.quantity,
                'price': node.price,
                'subtotal': round(node.price * node.quantity, 2)
            })
            node = node.next
        return result

    def size(self) -> int:
        return self._size

    def clear(self):
        self.head = None
        self._size = 0


# ─────────────────────────────────────────────
# 5. HASH MAP  →  Session Store & Product Cache
# ─────────────────────────────────────────────
class SessionStore:
    """
    Custom hash map with separate chaining.
    Stores user session data: cart, prefs, tokens.
    O(1) average get/set.
    """
    def __init__(self, capacity: int = 128):
        self.capacity = capacity
        self._buckets: list = [[] for _ in range(capacity)]
        self._size = 0

    def _hash(self, key: str) -> int:
        h = 0
        for ch in key:
            h = (h * 31 + ord(ch)) % self.capacity
        return h

    def set(self, key: str, value: Any):
        idx = self._hash(key)
        bucket = self._buckets[idx]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self._size += 1

    def get(self, key: str) -> Any:
        idx = self._hash(key)
        for k, v in self._buckets[idx]:
            if k == key:
                return v
        return None

    def delete(self, key: str):
        idx = self._hash(key)
        self._buckets[idx] = [(k, v) for k, v in self._buckets[idx] if k != key]

    def keys(self) -> list:
        return [k for bucket in self._buckets for k, _ in bucket]


# ─────────────────────────────────────────────
# 6. MIN-HEAP  →  Flash Sale / Deal Ranking
# ─────────────────────────────────────────────
class DealHeap:
    """
    Min-Heap by discount percentage (inverted → max discount first).
    Surfaces best deals to homepage in O(k log n).
    """
    def __init__(self):
        self._heap: list = []

    def push(self, product: dict):
        # Negate discount so max-discount is "smallest" in min-heap
        discount = product.get('discount_pct', 0)
        heapq.heappush(self._heap, (-discount, product['id'], product))

    def top_deals(self, k: int = 5) -> list:
        return [item[2] for item in heapq.nsmallest(k, self._heap)]

    def pop_best(self) -> Optional[dict]:
        if self._heap:
            return heapq.heappop(self._heap)[2]
        return None

    def size(self) -> int:
        return len(self._heap)


# ─────────────────────────────────────────────
# 7. BINARY SEARCH TREE  →  Price Range Filter
# ─────────────────────────────────────────────
class BSTNode:
    def __init__(self, price: float, product: dict):
        self.price = price
        self.product = product
        self.left: Optional['BSTNode'] = None
        self.right: Optional['BSTNode'] = None


class PriceBST:
    """
    BST keyed by price.
    Range queries: find all products between min_price and max_price.
    O(log n) average insertion, O(k + log n) range query.
    """
    def __init__(self):
        self.root: Optional[BSTNode] = None

    def insert(self, product: dict):
        price = product.get('price', 0)
        self.root = self._insert(self.root, price, product)

    def _insert(self, node, price, product):
        if not node:
            return BSTNode(price, product)
        if price <= node.price:
            node.left = self._insert(node.left, price, product)
        else:
            node.right = self._insert(node.right, price, product)
        return node

    def range_query(self, low: float, high: float) -> list:
        result = []
        self._range(self.root, low, high, result)
        return result

    def _range(self, node, low, high, result):
        if not node:
            return
        if low < node.price:
            self._range(node.left, low, high, result)
        if low <= node.price <= high:
            result.append(node.product)
        if node.price < high:
            self._range(node.right, low, high, result)


# ─────────────────────────────────────────────
# 8. GRAPH  →  Product Recommendation Engine
# ─────────────────────────────────────────────
class RecommendationGraph:
    """
    Undirected weighted graph.
    Edge weight = co-purchase frequency.
    BFS from a product → surfaces "customers also bought".
    """
    def __init__(self):
        self._adj: dict = {}  # product_id -> {neighbor_id: weight}

    def add_product(self, product_id: int):
        if product_id not in self._adj:
            self._adj[product_id] = {}

    def add_co_purchase(self, a: int, b: int):
        self.add_product(a)
        self.add_product(b)
        self._adj[a][b] = self._adj[a].get(b, 0) + 1
        self._adj[b][a] = self._adj[b].get(a, 0) + 1

    def recommend(self, product_id: int, depth: int = 2, top_k: int = 5) -> list:
        if product_id not in self._adj:
            return []
        visited = {product_id}
        scores: dict = {}
        queue = deque([(product_id, 1.0)])
        for _ in range(depth):
            next_queue = deque()
            while queue:
                pid, factor = queue.popleft()
                for neighbor, weight in self._adj.get(pid, {}).items():
                    if neighbor not in visited:
                        scores[neighbor] = scores.get(neighbor, 0) + weight * factor
                        next_queue.append((neighbor, factor * 0.5))
                        visited.add(neighbor)
            queue = next_queue
        ranked = sorted(scores.items(), key=lambda x: -x[1])
        return [pid for pid, _ in ranked[:top_k]]


# ─────────────────────────────────────────────
# 9. TRIE  →  Product Search Autocomplete
# ─────────────────────────────────────────────
class TrieNode:
    def __init__(self):
        self.children: dict = {}
        self.is_end = False
        self.product_ids: list = []


class SearchTrie:
    """
    Trie for O(m) prefix lookups — m = query length.
    Powers the search bar autocomplete.
    """
    def __init__(self):
        self.root = TrieNode()

    def insert(self, term: str, product_id: int):
        term = term.lower()
        node = self.root
        for ch in term:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
            if product_id not in node.product_ids:
                node.product_ids.append(product_id)
        node.is_end = True

    def search(self, prefix: str, limit: int = 8) -> list:
        prefix = prefix.lower()
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]
        return node.product_ids[:limit]


# ─────────────────────────────────────────────
# 10. DEQUE  →  Recently Viewed Products
# ─────────────────────────────────────────────
class RecentlyViewed:
    """
    Double-ended queue with max capacity.
    New views pushed to front, oldest dropped from back.
    """
    def __init__(self, max_size: int = 10):
        self._dq: deque = deque(maxlen=max_size)

    def view(self, product_id: int):
        if product_id in self._dq:
            self._dq.remove(product_id)
        self._dq.appendleft(product_id)

    def get(self) -> list:
        return list(self._dq)


# ─────────────────────────────────────────────
# GLOBAL IN-MEMORY INSTANCES (per-process)
# ─────────────────────────────────────────────
catalog = ProductCatalog()
order_queue = OrderQueue()
deal_heap = DealHeap()
price_bst = PriceBST()
rec_graph = RecommendationGraph()
search_trie = SearchTrie()

# Per-user instances stored in session (keyed by session_id)
session_store = SessionStore()


def get_cart(session_id: str) -> ShoppingCart:
    cart = session_store.get(f"cart:{session_id}")
    if cart is None:
        cart = ShoppingCart()
        session_store.set(f"cart:{session_id}", cart)
    return cart


def get_history(session_id: str) -> BrowsingHistory:
    h = session_store.get(f"history:{session_id}")
    if h is None:
        h = BrowsingHistory()
        session_store.set(f"history:{session_id}", h)
    return h


def get_recently_viewed(session_id: str) -> RecentlyViewed:
    rv = session_store.get(f"rv:{session_id}")
    if rv is None:
        rv = RecentlyViewed()
        session_store.set(f"rv:{session_id}", rv)
    return rv
