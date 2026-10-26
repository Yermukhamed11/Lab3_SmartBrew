"""SmartBrew AI: a dependency-free, simulated coffee-machine prototype.

Run with Python 3.11+: python3 app.py. Hardware, payments and weather are
explicit local simulations; no real money or physical devices are controlled.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import hmac
import io
import json
import math
import mimetypes
import os
from pathlib import Path
import secrets
import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent
BREW_SECONDS = 12
MAX_BODY = 65_536


def now() -> str:
    """Get a timestamp for persisted events.

    Inputs: None.
    Returns: str: current timezone-aware UTC ISO 8601 timestamp.
    """
    return datetime.now(timezone.utc).isoformat()


class APIError(Exception):
    """Carry a safe HTTP error message and status from validation to the handler."""

    def __init__(self, status: int, message: str):
        """Initialize an API validation or authorization failure.

        Inputs: status: integer HTTP error status. message: safe, user-visible explanation.
        Returns: None; stores status and exception message.
        """
        super().__init__(message)
        self.status = status


def number(value, name: str, minimum: float, maximum: float, integer=False):
    """Validate finite numeric input and inclusive limits.

    Inputs: value: int/float, excluding bool. name: field label. minimum/maximum: inclusive bounds. integer: whether a whole number is required.
    Returns: int when integer=True, otherwise float. Raises APIError(400) for invalid input.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise APIError(400, f'{name} must be a number.')
    if not math.isfinite(value) or not minimum <= value <= maximum:
        raise APIError(400, f'{name} must be between {minimum} and {maximum}.')
    if integer and int(value) != value:
        raise APIError(400, f'{name} must be a whole number.')
    return int(value) if integer else float(value)


def text_field(value, name: str, maximum=100, allow_empty=False) -> str:
    """Validate and trim a text field.

    Inputs: value: string. name: field label. maximum: maximum trimmed length. allow_empty: whether an empty trimmed value is accepted.
    Returns: str: trimmed text. Raises APIError(400) for invalid type or length.
    """
    if not isinstance(value, str) or len(value.strip()) > maximum or (not value.strip() and not allow_empty):
        raise APIError(400, f'{name} must be {1 if not allow_empty else 0}–{maximum} characters.')
    return value.strip()


class Store:
    """Persist menu, inventory, orders, service state and audit events in SQLite."""

    def __init__(self, path: str):
        """Initialize persistent storage and insert missing seed records.

        Inputs: path: SQLite database file path; parent directories are created if needed.
        Returns: None; creates tables and default records without overwriting existing data.
        """
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.sessions = {}
        self.session_lock = threading.Lock()
        with self.db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL,
                    category TEXT NOT NULL, price_cents INTEGER NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1, default_milk_percent INTEGER NOT NULL,
                    recipe TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS ingredients (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, unit TEXT NOT NULL,
                    stock REAL NOT NULL CHECK(stock>=0), capacity REAL NOT NULL CHECK(capacity>0));
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY, product_id TEXT NOT NULL, product_name TEXT NOT NULL,
                    milk_percent INTEGER NOT NULL, sugar_grams INTEGER NOT NULL,
                    total_cents INTEGER NOT NULL, payment_method TEXT NOT NULL,
                    status TEXT NOT NULL, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, severity TEXT NOT NULL,
                    event TEXT NOT NULL, message TEXT NOT NULL, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            ''')
            db.execute("INSERT OR IGNORE INTO settings VALUES ('mode','normal')")
            db.executemany('INSERT OR IGNORE INTO ingredients VALUES (?,?,?,?,?)', [
                ('beans', 'Coffee beans', 'g', 700, 1000),
                ('water', 'Water', 'ml', 3500, 5000),
                ('milk', 'Milk', 'ml', 2400, 3000),
                ('sugar', 'Sugar', 'g', 600, 1000),
                ('matcha', 'Matcha powder', 'g', 300, 500),
            ])
            products = [
                ('espresso', 'Espresso', 'A bold, rich shot with a golden crema.', 'hot', 250, 0, {'beans':18,'water':60}),
                ('cappuccino', 'Cappuccino', 'Balanced espresso, silky milk and a soft foam finish.', 'hot', 350, 40, {'beans':18,'water':90}),
                ('latte', 'Caffè Latte', 'Smooth espresso with a generous pour of creamy milk.', 'hot', 400, 70, {'beans':18,'water':120}),
                ('iced-latte', 'Iced Latte', 'Chilled espresso and milk for a refreshing coffee break.', 'iced', 420, 60, {'beans':18,'water':180}),
                ('matcha', 'Matcha Latte', 'Earthy green tea with a mellow, velvety finish.', 'hot', 450, 70, {'matcha':8,'water':120}),
            ]
            for pid, name, description, category, price, milk, recipe in products:
                db.execute('INSERT OR IGNORE INTO products VALUES (?,?,?,?,?,1,?,?)',
                           (pid, name, description, category, price, milk, json.dumps(recipe)))

    @contextmanager
    def db(self):
        """Manage an atomic database transaction and connection lifetime.

        Inputs: None; uses this Store instance database path.
        Returns: Context manager yielding sqlite3.Connection with named rows; commits on success, rolls back on an exception and always closes.
        """
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        try:
            connection.execute('BEGIN IMMEDIATE')
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def log(db, severity: str, event: str, message: str):
        """Append a non-secret audit event within the caller transaction.

        Inputs: db: open SQLite connection. severity: log level. event: event code. message: safe event details.
        Returns: None; inserts one timestamped log row.
        """
        db.execute('INSERT INTO logs(severity,event,message,created_at) VALUES(?,?,?,?)',
                   (severity, event, message, now()))

    @staticmethod
    def mode(db) -> str:
        """Read the persisted operating mode.

        Inputs: db: open SQLite connection containing the settings table.
        Returns: str: 'normal' or 'service'.
        """
        return db.execute("SELECT value FROM settings WHERE key='mode'").fetchone()[0]

    @staticmethod
    def inventory(db) -> dict:
        """Compute ingredient levels and strict below-15% alerts.

        Inputs: db: open SQLite connection containing ingredient quantities/capacities.
        Returns: dict: ingredients list with percentage/low fields and alerts list of low ingredients.
        """
        ingredients = []
        for row in db.execute('SELECT * FROM ingredients ORDER BY name'):
            item = dict(row)
            item['percentage'] = round(item['stock'] / item['capacity'] * 100, 2)
            item['low'] = item['stock'] < item['capacity'] * .15
            ingredients.append(item)
        return {'ingredients': ingredients, 'alerts': [item for item in ingredients if item['low']]}

    @staticmethod
    def recipe(product, milk: int, sugar: int) -> dict:
        """Construct ingredient quantities for a customized drink.

        Inputs: product: product row with a JSON base recipe. milk: integer 0–100 percent of a 200 ml allowance. sugar: integer 0–20 grams.
        Returns: dict mapping ingredient IDs to required grams or millilitres; does not deduct stock.
        """
        recipe = json.loads(product['recipe'])
        recipe['milk'] = milk * 2  # 100% slider means a 200 ml milk allowance.
        recipe['sugar'] = sugar
        return recipe

    def menu(self, include_inactive=False) -> dict:
        """Read menu products and default-recipe availability.

        Inputs: include_inactive: boolean; include hidden products when True.
        Returns: dict with products list and machine_mode. Each product includes integer price_cents and available/active booleans.
        """
        with self.db() as db:
            stock = {row['id']: row['stock'] for row in db.execute('SELECT * FROM ingredients')}
            products = []
            for row in db.execute('SELECT * FROM products ORDER BY rowid'):
                if not row['active'] and not include_inactive:
                    continue
                item = dict(row)
                item.pop('recipe')
                item['active'] = bool(item['active'])
                item['available'] = all(stock[key] >= amount for key, amount in self.recipe(row, row['default_milk_percent'], 0).items())
                products.append(item)
            return {'products': products, 'machine_mode': self.mode(db)}

    @staticmethod
    def order(db, order_id: str) -> dict:
        """Read an order and advance its elapsed-time brewing state.

        Inputs: db: open SQLite transaction. order_id: opaque SB-prefixed order identifier.
        Returns: dict of order details including status and progress 0–100. Raises APIError(404) if absent; may persist ready status.
        """
        row = db.execute('SELECT * FROM orders WHERE id=?', (order_id,)).fetchone()
        if row is None:
            raise APIError(404, 'Order not found.')
        item = dict(row)
        elapsed = max(0, (datetime.now(timezone.utc) - datetime.fromisoformat(item['created_at'])).total_seconds())
        if item['status'] == 'brewing' and elapsed >= BREW_SECONDS:
            db.execute("UPDATE orders SET status='ready' WHERE id=?", (order_id,))
            item['status'] = 'ready'
            Store.log(db, 'info', 'brew_ready', f'Order {order_id} is ready for collection.')
        item['progress'] = min(99, int(elapsed / BREW_SECONDS * 100)) if item['status'] == 'brewing' else 100
        return item

    def purchase(self, body: dict) -> dict:
        """Create a simulated paid order with atomic inventory deduction.

        Inputs: body: dict with product_id, integer milk_percent(0–100), sugar_grams(0–20), payment_method('card'/'phone'), payment_result('approved'/'declined').
        Returns: dict of the new brewing order. Raises APIError for invalid input, declined payment, missing product, service/busy machine or insufficient stock; failed purchases do not deduct stock.
        """
        product_id = text_field(body.get('product_id'), 'product_id')
        milk = number(body.get('milk_percent'), 'milk_percent', 0, 100, True)
        sugar = number(body.get('sugar_grams'), 'sugar_grams', 0, 20, True)
        method = body.get('payment_method')
        result = body.get('payment_result')
        if method not in ('card', 'phone') or result not in ('approved', 'declined'):
            raise APIError(400, 'Choose card/phone and approved/declined simulation.')
        # Payment declines are audit events, never paid orders or stock mutations.
        if result == 'declined':
            with self.db() as db:
                self.log(db, 'warning', 'payment_declined', 'Simulated contactless payment declined; no charge.')
            raise APIError(402, 'Simulated payment declined. No charge or ingredients consumed.')
        with self.db() as db:
            if self.mode(db) == 'service':
                raise APIError(409, 'Machine is in service mode. Ask a technician to return it to normal mode.')
            if db.execute("SELECT 1 FROM orders WHERE status IN ('brewing','ready')").fetchone():
                raise APIError(409, 'Machine is busy. Collect the current drink before ordering again.')
            product = db.execute('SELECT * FROM products WHERE id=? AND active=1', (product_id,)).fetchone()
            if product is None:
                raise APIError(404, 'Drink is not available on the menu.')
            recipe = self.recipe(product, milk, sugar)
            for key, amount in recipe.items():
                row = db.execute('SELECT stock,name FROM ingredients WHERE id=?', (key,)).fetchone()
                if row['stock'] < amount:
                    raise APIError(409, f"Not enough {row['name'].lower()} for this recipe.")
            for key, amount in recipe.items():
                db.execute('UPDATE ingredients SET stock=stock-? WHERE id=?', (amount, key))
            order_id = 'SB-' + secrets.token_hex(8).upper()
            db.execute('INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?)',
                       (order_id, product_id, product['name'], milk, sugar, product['price_cents'], method, 'brewing', now()))
            self.log(db, 'info', 'payment_approved', f'Simulated payment approved; order {order_id} started.')
            for ingredient in self.inventory(db)['alerts']:
                self.log(db, 'warning', 'low_inventory', f"{ingredient['name']} below 15% capacity.")
            return self.order(db, order_id)

    def edit_menu(self, body: dict, product_id=None) -> dict:
        """Add or partially update a validated menu entry.

        Inputs: body: dict of name, description, category(hot/iced), price_cents, default_milk_percent and optional active. product_id: existing ID for edits, None for creation.
        Returns: dict of the saved product. Raises APIError for unsupported/invalid fields or missing edit target; persists changes and audit event.
        """
        allowed = {'name', 'description', 'category', 'price_cents', 'default_milk_percent', 'active'}
        if not body or set(body) - allowed:
            raise APIError(400, 'Supply only supported menu fields.')
        with self.db() as db:
            existing = db.execute('SELECT * FROM products WHERE id=?', (product_id,)).fetchone() if product_id else None
            if product_id and existing is None:
                raise APIError(404, 'Drink not found.')
            values = dict(existing) if existing else {'active': True}
            values.update(body)
            name = text_field(values.get('name'), 'name', 60)
            description = text_field(values.get('description', ''), 'description', 300, True)
            category = values.get('category')
            if category not in ('hot', 'iced'):
                raise APIError(400, 'category must be hot or iced.')
            price = number(values.get('price_cents'), 'price_cents', 1, 10000, True)
            milk = number(values.get('default_milk_percent', 0), 'default_milk_percent', 0, 100, True)
            if not isinstance(values['active'], (bool, int)) or values['active'] not in (0, 1):
                raise APIError(400, 'active must be a boolean.')
            product_id = product_id or 'drink-' + secrets.token_hex(5)
            db.execute('''INSERT INTO products VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                       name=excluded.name,description=excluded.description,category=excluded.category,
                       price_cents=excluded.price_cents,active=excluded.active,default_milk_percent=excluded.default_milk_percent''',
                       (product_id, name, description, category, price, int(values['active']), milk,
                        values.get('recipe', json.dumps({'beans':18,'water':120}))))
            self.log(db, 'info', 'menu_updated', f'Menu entry {product_id} updated.')
        return next(item for item in self.menu(True)['products'] if item['id'] == product_id)

    def weather(self, scenario: str, hour) -> dict:
        """Produce explicit simulated weather/time context.

        Inputs: scenario: 'hot', 'cold', 'mild' or 'offline'. hour: integer or integer string 0–23, interpreted as UTC.
        Returns: dict with source, online, temperature_c, condition, hour and message. Offline context logs a warning; invalid inputs raise APIError(400).
        """
        if scenario not in ('hot', 'cold', 'mild', 'offline'):
            raise APIError(400, 'Unknown weather scenario.')
        if isinstance(hour, str):
            try:
                hour = int(hour)
            except ValueError:
                raise APIError(400, 'hour must be between 0 and 23.') from None
        hour = number(hour, 'hour', 0, 23, True)
        temperatures = {'hot':30, 'cold':4, 'mild':18, 'offline':None}
        online = scenario != 'offline'
        if not online:
            with self.db() as db:
                self.log(db, 'warning', 'weather_offline', 'Simulated weather source unavailable; using time-only fallback.')
        return {'source':'simulated', 'online':online, 'temperature_c':temperatures[scenario],
                'condition':{'hot':'sunny','cold':'cloudy','mild':'clear','offline':'unavailable'}[scenario],
                'hour':hour, 'message':'Local simulation; no external weather API.' if online else 'Offline simulation: time-only fallback.'}

    def recommend(self, body: dict) -> dict:
        """Choose an available drink with transparent weather/time rules.

        Inputs: body: dict with optional scenario (default mild) and hour (default current UTC hour).
        Returns: dict with product_id, product_name, reason, weather and engine. Raises APIError(409) if no drink is available.
        """
        weather = self.weather(body.get('scenario', 'mild'), body.get('hour', datetime.now(timezone.utc).hour))
        products = [item for item in self.menu()['products'] if item['available']]
        if not products:
            raise APIError(409, 'No available drinks to recommend.')
        if weather['online'] and weather['temperature_c'] >= 25:
            preferred = 'iced-latte'
            reason = 'It is warm (25°C or above): try a refreshing iced coffee.'
        elif weather['online'] and weather['temperature_c'] <= 10:
            preferred = 'latte'
            reason = 'It is cold (10°C or below): a warm latte is a comfortable choice.'
        elif weather['hour'] < 12:
            preferred = 'espresso'
            reason = 'Before noon: a bold espresso for your morning.'
        else:
            preferred = 'cappuccino'
            reason = 'After noon: a balanced cappuccino for your break.'
        selected = next((item for item in products if item['id'] == preferred), products[0])
        if selected['id'] != preferred:
            reason += ' The first available drink replaces an unavailable recommendation.'
        if not weather['online']:
            reason = 'Weather unavailable; time-only fallback. ' + reason
        return {'product_id':selected['id'], 'product_name':selected['name'], 'reason':reason,
                'weather':weather, 'engine':'deterministic rules, not a live AI model'}


class Handler(BaseHTTPRequestHandler):
    """Serve static UI and same-origin JSON API with role-protected administration."""

    def log_message(self, format, *args):
        """Suppress routine request logging to avoid echoing user URLs.

        Inputs: format: BaseHTTPRequestHandler log format string. args: formatting values, deliberately unused.
        Returns: None; emits no log output.
        """

    def send_data(self, status: int, value, content_type='application/json; charset=utf-8', headers=None):
        """Send a JSON or byte HTTP response with security headers.

        Inputs: status: HTTP status integer. value: JSON-serializable data or bytes. content_type: MIME header. headers: optional additional header dict.
        Returns: None; writes headers and response bytes to the client socket.
        """
        payload = json.dumps(value, ensure_ascii=False).encode() if not isinstance(value, bytes) else value
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'same-origin')
        self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(payload)

    def body(self) -> dict:
        """Parse a bounded JSON request object.

        Inputs: None explicitly; reads Content-Length and bytes from the current HTTP request.
        Returns: dict: parsed JSON object, or empty dict for no body. Raises APIError(400/413) for malformed, non-object or oversized input.
        """
        try:
            size = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            raise APIError(400, 'Invalid Content-Length.') from None
        if size < 0 or size > MAX_BODY:
            raise APIError(413, 'Request body is too large.')
        try:
            value = json.loads(self.rfile.read(size)) if size else {}
        except (ValueError, UnicodeDecodeError):
            raise APIError(400, 'Request body must contain valid JSON.') from None
        if not isinstance(value, dict):
            raise APIError(400, 'Request body must be a JSON object.')
        return value

    def role(self):
        """Resolve the current browser session without exposing its token.

        Inputs: None explicitly; reads the request Cookie header and server in-memory sessions.
        Returns: str: 'admin'/'technician' for a valid unexpired session, otherwise None.
        """
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get('Cookie', ''))
        except Exception:
            return None
        token = cookie.get('smartbrew_session')
        with self.server.store.session_lock:
            entry = self.server.store.sessions.get(token.value) if token else None
            if entry and entry[1] > time.time():
                return entry[0]
        return None

    def require(self, role: str):
        """Enforce exact role authorization for a protected route.

        Inputs: role: required session role, 'admin' or 'technician'.
        Returns: None on success. Raises APIError(403) for an absent, expired or wrong-role session.
        """
        if self.role() != role:
            raise APIError(403, f'{role.capitalize()} sign-in required.')

    def route(self, method: str):
        """Dispatch a request to the API or static-file handler.

        Inputs: method: 'GET', 'POST' or 'PATCH'; path, headers and body are read from the current HTTP request.
        Returns: None; sends one response and may update storage/session state. Raises APIError for expected route, validation or authorization errors.
        """
        parsed = urlsplit(self.path)
        path = parsed.path
        store = self.server.store
        body = self.body() if method in ('POST', 'PATCH') else {}
        # Browsers must submit mutations from this origin; CLI requests may omit Origin.
        origin = self.headers.get('Origin')
        if method != 'GET' and origin and urlsplit(origin).netloc != self.headers.get('Host'):
            raise APIError(403, 'Cross-origin changes are not allowed.')
        if method == 'GET' and not path.startswith('/api/'):
            filename = 'index.html' if path == '/' else path.lstrip('/')
            file = (ROOT / 'static' / filename).resolve()
            if not file.is_relative_to(ROOT / 'static') or not file.is_file():
                raise APIError(404, 'File not found.')
            self.send_data(200, file.read_bytes(), mimetypes.guess_type(file)[0] or 'application/octet-stream')
            return
        if method == 'GET' and path == '/api/menu':
            self.send_data(200, store.menu())
            return
        if method == 'GET' and path == '/api/session':
            with store.db() as db:
                self.send_data(200, {'role':self.role(), 'machine_mode':store.mode(db)})
            return
        if method == 'POST' and path == '/api/auth/login':
            role = body.get('role')
            if role not in ('admin', 'technician'):
                raise APIError(400, 'Choose admin or technician.')
            expected = os.environ.get('SMARTBREW_ADMIN_PASSWORD', 'smartbrew-admin') if role == 'admin' else os.environ.get('SMARTBREW_TECH_PIN', '2468')
            supplied = body.get('credential')
            if not isinstance(supplied, str) or not hmac.compare_digest(hashlib.sha256(supplied.encode()).digest(), hashlib.sha256(expected.encode()).digest()):
                raise APIError(401, 'Incorrect credentials.')
            token = secrets.token_urlsafe(32)
            with store.session_lock:
                # Replace a previous browser session and discard expired entries.
                cookie = SimpleCookie(self.headers.get('Cookie', ''))
                old = cookie.get('smartbrew_session')
                if old:
                    store.sessions.pop(old.value, None)
                store.sessions = {key:value for key,value in store.sessions.items() if value[1] > time.time()}
                store.sessions[token] = (role, time.time()+3600)
            with store.db() as db:
                self.send_data(200, {'role':role,'machine_mode':store.mode(db)}, headers={'Set-Cookie':f'smartbrew_session={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age=3600'})
            return
        if method == 'POST' and path == '/api/auth/logout':
            cookie = SimpleCookie(self.headers.get('Cookie', ''))
            old = cookie.get('smartbrew_session')
            with store.session_lock:
                if old:
                    store.sessions.pop(old.value, None)
            with store.db() as db:
                self.send_data(200, {'role':None,'machine_mode':store.mode(db)}, headers={'Set-Cookie':'smartbrew_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0'})
            return
        if method == 'GET' and path == '/api/weather':
            query = parse_qs(parsed.query)
            self.send_data(200, store.weather(query.get('scenario', ['mild'])[0], query.get('hour', [datetime.now(timezone.utc).hour])[0]))
            return
        if method == 'POST' and path == '/api/recommendation':
            self.send_data(200, store.recommend(body))
            return
        if method == 'POST' and path == '/api/orders':
            self.send_data(201, store.purchase(body))
            return
        parts = path.strip('/').split('/')
        if len(parts) in (3, 4) and parts[:2] == ['api','orders']:
            with store.db() as db:
                order = store.order(db, parts[2])
                if len(parts) == 4 and parts[3] == 'collect' and method == 'POST':
                    if order['status'] != 'ready':
                        raise APIError(409, 'Only a ready drink can be collected.')
                    db.execute("UPDATE orders SET status='completed' WHERE id=?", (parts[2],))
                    store.log(db, 'info', 'drink_collected', f'Order {parts[2]} collected.')
                    order = store.order(db, parts[2])
                elif not (method == 'GET' and len(parts) == 3):
                    raise APIError(404, 'Route not found.')
                self.send_data(200, order)
            return
        if path.startswith('/api/admin/menu'):
            self.require('admin')
            if path == '/api/admin/menu' and method == 'GET':
                self.send_data(200, store.menu(True))
            elif path == '/api/admin/menu' and method == 'POST':
                self.send_data(201, store.edit_menu(body))
            elif len(parts) == 4 and method == 'PATCH':
                self.send_data(200, store.edit_menu(body, parts[3]))
            else:
                raise APIError(404, 'Route not found.')
            return
        if path.startswith('/api/inventory'):
            self.require('admin')
            with store.db() as db:
                if len(parts) == 3 and method == 'POST':
                    row = db.execute('SELECT * FROM ingredients WHERE id=?', (parts[2],)).fetchone()
                    if row is None:
                        raise APIError(404, 'Ingredient not found.')
                    stock = number(body.get('stock'), 'stock', 0, row['capacity'])
                    db.execute('UPDATE ingredients SET stock=? WHERE id=?', (stock, parts[2]))
                    store.log(db, 'warning' if stock < .15*row['capacity'] else 'info', 'sensor_override', f"Simulated {row['name']} sensor set to {stock} {row['unit']}.")
                elif not (method == 'GET' and len(parts) == 2):
                    raise APIError(404, 'Route not found.')
                self.send_data(200, store.inventory(db))
            return
        if path.startswith('/api/service/'):
            self.require('technician')
            with store.db() as db:
                if path == '/api/service/mode' and method == 'POST':
                    enabled = body.get('enabled')
                    if not isinstance(enabled, bool):
                        raise APIError(400, 'enabled must be a boolean.')
                    if enabled and db.execute("SELECT 1 FROM orders WHERE status IN ('brewing','ready')").fetchone():
                        raise APIError(409, 'Collect the active drink before entering service mode.')
                    mode = 'service' if enabled else 'normal'
                    db.execute("UPDATE settings SET value=? WHERE key='mode'", (mode,))
                    store.log(db, 'info', 'service_mode', f'Machine switched to {mode} mode.')
                    self.send_data(200, {'machine_mode':mode})
                elif path == '/api/service/diagnostics' and method == 'POST':
                    if store.mode(db) != 'service':
                        raise APIError(409, 'Enable service mode before running diagnostics.')
                    component = body.get('component')
                    fault = body.get('simulate_fault', False)
                    if component not in ('milk_pump','water_pump','heater') or not isinstance(fault, bool):
                        raise APIError(400, 'Choose a known component and boolean simulate_fault.')
                    result = {'id':secrets.token_hex(6),'component':component,'passed':not fault,'duration_seconds':2,
                              'reading':(20 if fault else 92) if component == 'heater' else (0 if fault else 40),
                              'unit':'°C' if component == 'heater' else 'ml / 2 s', 'simulated':True,'created_at':now()}
                    store.log(db, 'error' if fault else 'info', 'diagnostic', f"SIMULATED {component}: {'FAIL' if fault else 'PASS'}; nominal 2 s fixture, no hardware activated.")
                    self.send_data(200, result)
                elif path in ('/api/service/logs','/api/service/logs.csv') and method == 'GET':
                    logs = [dict(row) for row in db.execute('SELECT * FROM logs ORDER BY id DESC LIMIT 1000')]
                    if path.endswith('.csv'):
                        output = io.StringIO(newline='')
                        writer = csv.DictWriter(output, fieldnames=['id','severity','event','message','created_at'])
                        writer.writeheader()
                        writer.writerows(logs)
                        self.send_data(200, output.getvalue().encode('utf-8-sig'), 'text/csv; charset=utf-8', {'Content-Disposition':'attachment; filename="smartbrew-logs.csv"'})
                    else:
                        self.send_data(200, {'logs':logs})
                else:
                    raise APIError(404, 'Route not found.')
            return
        if path == '/api/dashboard' and method == 'GET':
            self.require('admin')
            with store.db() as db:
                date = now()[:10]
                counts = db.execute("SELECT count(*),sum(CASE WHEN status='completed' THEN 1 ELSE 0 END),coalesce(sum(CASE WHEN status='completed' THEN total_cents ELSE 0 END),0) FROM orders WHERE substr(created_at,1,10)=?", (date,)).fetchone()
                popular = [dict(row) for row in db.execute("SELECT product_name AS name,count(*) AS quantity FROM orders WHERE status='completed' AND substr(created_at,1,10)=? GROUP BY product_name ORDER BY quantity DESC,name", (date,))]
                self.send_data(200, {'date':date,'total_orders':counts[0],'completed_orders':counts[1] or 0,
                    'revenue_cents':counts[2],'average_order_cents':round(counts[2]/counts[1]) if counts[1] else 0,
                    'popular_products':popular,'low_stock':store.inventory(db)['alerts']})
            return
        raise APIError(404, 'Route not found.')

    def dispatch(self, method: str):
        """Translate route failures into safe HTTP responses.

        Inputs: method: 'GET', 'POST' or 'PATCH'.
        Returns: None; sends a normal response, a safe API error, or a generic 500 error; ignores disconnected clients.
        """
        try:
            self.route(method)
        except APIError as error:
            self.send_data(error.status, {'error':str(error)})
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception:
            self.send_data(500, {'error':'Internal server error. Check the local database and restart if needed.'})

    def do_GET(self):
        """Handle the standard-library GET callback.

        Inputs: None explicitly; the server populates request attributes on self.
        Returns: None; dispatches and writes the HTTP response.
        """
        self.dispatch('GET')

    def do_POST(self):
        """Handle the standard-library POST callback.

        Inputs: None explicitly; the server populates request attributes on self.
        Returns: None; dispatches and writes the HTTP response.
        """
        self.dispatch('POST')

    def do_PATCH(self):
        """Handle the standard-library PATCH callback.

        Inputs: None explicitly; the server populates request attributes on self.
        Returns: None; dispatches and writes the HTTP response.
        """
        self.dispatch('PATCH')


def create_server(host='127.0.0.1', port=8000, db_path=None):
    """Create a configured HTTP server without starting its serve loop.

    Inputs: host: bind address (default loopback). port: integer TCP port, 0 chooses a free port. db_path: optional SQLite path; otherwise SMARTBREW_DB or data/smartbrew.db.
    Returns: ThreadingHTTPServer with initialized Store; caller must serve and close it.
    """
    store = Store(db_path or os.environ.get('SMARTBREW_DB', str(ROOT / 'data' / 'smartbrew.db')))
    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    server.store = store
    return server


def main():
    """Start the command-line application and close it after interruption.

    Inputs: None explicitly; CLI accepts --host, --port and --db.
    Returns: None; serves until KeyboardInterrupt and closes the listening socket.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=8000, type=int)
    parser.add_argument('--db', default=None)
    args = parser.parse_args()
    server = create_server(args.host, args.port, args.db)
    print(f'SmartBrew AI running on {args.host}:{server.server_port}. All devices/payments/weather are simulated.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
