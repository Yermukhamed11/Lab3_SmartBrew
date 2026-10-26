"""HTTP integration tests for SmartBrew's ten assignment features.

Every case owns a temporary SQLite database and an HTTP server on a random
loopback port. No browser, physical machine, Internet, or external package is
required. One test waits for the real simulated brewing timer.
"""

import csv
import http.cookiejar
import io
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request

import app


class SmartBrewHTTPTests(unittest.TestCase):
    """Exercise public, administrator, and technician workflows over HTTP."""

    def setUp(self):
        """Create an isolated database/server; input: none; return: None."""
        self.tempdir = tempfile.TemporaryDirectory(prefix="smartbrew-tests-")
        self.db_path = str(Path(self.tempdir.name) / "test.db")
        self.start_server()
        self.customer = self.client()
        self.admin = self.client()
        self.technician = self.client()

    def tearDown(self):
        """Stop this case's server and remove its data; return: None.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        self.stop_server()
        self.tempdir.cleanup()

    def start_server(self):
        """Bind an HTTP server using self.db_path; return: None.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        self.server = app.create_server(
            host="127.0.0.1", port=0, db_path=self.db_path
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = "http://127.0.0.1:%d" % self.server.server_address[1]

    def stop_server(self):
        """Release the current server/socket and wait for its thread; return: None.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    @staticmethod
    def client():
        """Create an independent cookie-aware HTTP client; return: OpenerDirector.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        return urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
        )

    def request(self, method, path, data=None, client=None, raw=None):
        """Send an HTTP request through an isolated test client.

        Inputs: method and path strings; optional data is JSON-serializable and
        overrides raw bytes; client is an optional OpenerDirector (default:
        customer); raw supplies optional request bytes for malformed-JSON tests.
        Returns: (integer HTTP status, decoded JSON dict or response text,
        HTTP headers), including non-success responses for assertions.
        """
        opener = client or self.customer
        headers = {}
        body = raw
        if data is not None:
            body = json.dumps(data).encode("utf-8")
        if body is not None:
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(
            self.base_url + path, data=body, method=method, headers=headers
        )
        try:
            response = opener.open(req, timeout=5)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            payload = response.read()
            if "application/json" in response.headers.get("Content-Type", ""):
                payload = json.loads(payload)
            else:
                payload = payload.decode("utf-8")
            return response.status, payload, response.headers

    def login_admin(self):
        """Authenticate the administrator test client; input: none; return: None."""
        status, payload, _ = self.request(
            "POST", "/api/auth/login",
            {"role": "admin", "credential": "smartbrew-admin"}, self.admin,
        )
        self.assertEqual(status, 200, payload)
        self.assertEqual(payload["role"], "admin")

    def login_technician(self):
        """Authenticate the technician test client; input: none; return: None."""
        status, payload, _ = self.request(
            "POST", "/api/auth/login",
            {"role": "technician", "credential": "2468"}, self.technician,
        )
        self.assertEqual(status, 200, payload)
        self.assertEqual(payload["role"], "technician")

    def products(self):
        """Fetch the public menu; input: none; return: list of product dictionaries."""
        status, payload, _ = self.request("GET", "/api/menu")
        self.assertEqual(status, 200, payload)
        return payload["products"]

    def order_body(self, **overrides):
        """Construct a valid order. Inputs: keyword field overrides. Returns: order dict."""
        product = self.products()[0]
        body = {
            "product_id": product["id"], "milk_percent": 20, "sugar_grams": 5,
            "payment_method": "card", "payment_result": "approved",
        }
        body.update(overrides)
        return body

    def inventory(self):
        """Fetch inventory as an authenticated administrator; return: response dict.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        status, payload, _ = self.request("GET", "/api/inventory", client=self.admin)
        self.assertEqual(status, 200, payload)
        return payload

    def test_menu_displays_prices_and_availability(self):
        """SB-01: public menu contains usable priced choices; input: none; return: None."""
        products = self.products()
        self.assertGreaterEqual(len(products), 3)
        for product in products:
            self.assertIsInstance(product["price_cents"], int)
            self.assertGreater(product["price_cents"], 0)
            self.assertIsInstance(product["available"], bool)
            self.assertTrue(product["name"])

    def test_customization_and_payment_reserve_inventory(self):
        """SB-01/02: customized approved purchase consumes stock; return: None.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        self.login_admin()
        before = {row["id"]: row["stock"] for row in self.inventory()["ingredients"]}
        status, order, _ = self.request("POST", "/api/orders", self.order_body())
        self.assertEqual(status, 201, order)
        self.assertEqual(order["milk_percent"], 20)
        self.assertEqual(order["sugar_grams"], 5)
        self.assertEqual(order["status"], "brewing")
        self.assertEqual(order["payment_method"], "card")
        self.assertGreater(order["total_cents"], 0)
        after = {row["id"]: row["stock"] for row in self.inventory()["ingredients"]}
        self.assertTrue(any(after[key] < before[key] for key in before))
        self.assertTrue(all(after[key] <= before[key] for key in before))

    def test_phone_payment_is_supported(self):
        """SB-02: simulated phone approval starts a brew; return: None.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        status, order, _ = self.request(
            "POST", "/api/orders", self.order_body(payment_method="phone")
        )
        self.assertEqual(status, 201, order)
        self.assertEqual(order["payment_method"], "phone")

    def test_declined_payment_leaves_inventory_and_sales_unchanged(self):
        """SB-02: failed payment cannot consume ingredients or create sales; return: None.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        self.login_admin()
        before = self.inventory()["ingredients"]
        status, payload, _ = self.request(
            "POST", "/api/orders", self.order_body(payment_result="declined")
        )
        self.assertEqual(status, 402, payload)
        self.assertIn("error", payload)
        self.assertEqual(self.inventory()["ingredients"], before)
        _, dashboard, _ = self.request("GET", "/api/dashboard", client=self.admin)
        self.assertEqual(dashboard["total_orders"], 0)
        self.assertEqual(dashboard["revenue_cents"], 0)

    def test_invalid_customization_is_rejected(self):
        """SB-01: reject values outside milk/sugar ranges; input: none; return: None."""
        for overrides in [
            {"milk_percent": -1}, {"milk_percent": 101},
            {"sugar_grams": -1}, {"sugar_grams": 21},
        ]:
            with self.subTest(overrides=overrides):
                status, payload, _ = self.request(
                    "POST", "/api/orders", self.order_body(**overrides)
                )
                self.assertEqual(status, 400, payload)

    def test_weather_hot_and_offline_scenarios(self):
        """SB-03: controlled weather and unavailable-provider cases work; return: None.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        status, weather, _ = self.request("GET", "/api/weather?scenario=hot&hour=14")
        self.assertEqual(status, 200, weather)
        self.assertEqual(weather["source"], "simulated")
        self.assertTrue(weather["online"])
        self.assertEqual(weather["temperature_c"], 30)
        self.assertEqual(weather["hour"], 14)
        status, weather, _ = self.request("GET", "/api/weather?scenario=offline&hour=8")
        self.assertEqual(status, 200, weather)
        self.assertFalse(weather["online"])
        self.assertIsNone(weather["temperature_c"])

    def test_recommendation_uses_weather_and_survives_offline(self):
        """SB-04: hot weather chooses an iced drink and offline gives fallback; return: None.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        status, suggestion, _ = self.request(
            "POST", "/api/recommendation", {"scenario": "hot", "hour": 14}
        )
        self.assertEqual(status, 200, suggestion)
        chosen = next(p for p in self.products() if p["id"] == suggestion["product_id"])
        self.assertEqual(chosen["category"], "iced")
        self.assertTrue(suggestion["reason"])
        status, fallback, _ = self.request(
            "POST", "/api/recommendation", {"scenario": "offline", "hour": 8}
        )
        self.assertEqual(status, 200, fallback)
        self.assertTrue(fallback["product_id"])
        self.assertFalse(fallback["weather"]["online"])

    def test_inventory_alert_threshold_is_strictly_below_fifteen_percent(self):
        """SB-05: exactly 15% is normal, 10% triggers an alert; return: None.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        self.login_admin()
        ingredient = self.inventory()["ingredients"][0]
        path = "/api/inventory/%s" % ingredient["id"]
        for fraction, expected in [(0.15, False), (0.10, True)]:
            status, payload, _ = self.request(
                "POST", path, {"stock": ingredient["capacity"] * fraction}, self.admin
            )
            self.assertEqual(status, 200, payload)
            current = next(i for i in payload["ingredients"] if i["id"] == ingredient["id"])
            self.assertEqual(current["low"], expected)
            self.assertEqual(
                any(i["id"] == ingredient["id"] for i in payload["alerts"]), expected
            )

    def test_insufficient_inventory_rolls_back_entire_purchase(self):
        """SB-02/05: no partial stock mutation when recipe cannot be filled; return: None.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        self.login_admin()
        for ingredient in self.inventory()["ingredients"]:
            status, payload, _ = self.request(
                "POST", "/api/inventory/%s" % ingredient["id"], {"stock": 0}, self.admin
            )
            self.assertEqual(status, 200, payload)
        before = self.inventory()["ingredients"]
        status, payload, _ = self.request("POST", "/api/orders", self.order_body())
        self.assertEqual(status, 409, payload)
        self.assertEqual(self.inventory()["ingredients"], before)
        self.assertTrue(all(not p["available"] for p in self.products()))

    def test_admin_login_rejects_wrong_credentials_and_logs_out(self):
        """SB-06: bad credentials fail and logout revokes protected access; return: None.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        status, payload, _ = self.request(
            "POST", "/api/auth/login", {"role": "admin", "credential": "wrong"}, self.admin
        )
        self.assertEqual(status, 401, payload)
        self.login_admin()
        status, _, _ = self.request("GET", "/api/inventory", client=self.admin)
        self.assertEqual(status, 200)
        status, session, _ = self.request("POST", "/api/auth/logout", {}, self.admin)
        self.assertEqual(status, 200, session)
        self.assertIsNone(session["role"])
        status, _, _ = self.request("GET", "/api/inventory", client=self.admin)
        self.assertIn(status, (401, 403))

    def test_protected_resources_require_the_correct_role(self):
        """SB-06/08: public or wrong-role clients cannot administer/service; return: None.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        for path in ["/api/inventory", "/api/admin/menu", "/api/dashboard", "/api/service/logs.csv"]:
            with self.subTest(path=path):
                status, _, _ = self.request("GET", path)
                self.assertIn(status, (401, 403))
        self.login_technician()
        status, _, _ = self.request("GET", "/api/inventory", client=self.technician)
        self.assertEqual(status, 403)
        self.login_admin()
        status, _, _ = self.request("GET", "/api/service/logs", client=self.admin)
        self.assertEqual(status, 403)

    def test_admin_can_add_edit_and_hide_menu_item(self):
        """SB-07: new/updated menu items persist and inactive items disappear; return: None.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        self.login_admin()
        status, result, _ = self.request(
            "POST", "/api/admin/menu", {
                "name": "Test Mocha", "description": "A demonstration recipe",
                "category": "hot", "price_cents": 400, "default_milk_percent": 20,
            }, self.admin,
        )
        self.assertEqual(status, 201, result)
        created = next(p for p in self.products() if p["name"] == "Test Mocha")
        self.assertEqual(created["price_cents"], 400)
        status, result, _ = self.request(
            "PATCH", "/api/admin/menu/%s" % created["id"],
            {"price_cents": 450, "name": "Updated Mocha"}, self.admin,
        )
        self.assertEqual(status, 200, result)
        updated = next(p for p in self.products() if p["id"] == created["id"])
        self.assertEqual(updated["name"], "Updated Mocha")
        self.assertEqual(updated["price_cents"], 450)
        status, result, _ = self.request(
            "PATCH", "/api/admin/menu/%s" % created["id"], {"active": False}, self.admin
        )
        self.assertEqual(status, 200, result)
        self.assertNotIn(created["id"], [p["id"] for p in self.products()])

    def test_service_mode_locks_customer_checkout(self):
        """SB-08: technician service mode blocks purchases until released; return: None.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        self.login_technician()
        status, result, _ = self.request(
            "POST", "/api/service/mode", {"enabled": True}, self.technician
        )
        self.assertEqual(status, 200, result)
        self.assertEqual(result["machine_mode"], "service")
        status, result, _ = self.request("POST", "/api/orders", self.order_body())
        self.assertEqual(status, 409, result)
        status, result, _ = self.request(
            "POST", "/api/service/mode", {"enabled": False}, self.technician
        )
        self.assertEqual(status, 200, result)
        status, result, _ = self.request("POST", "/api/orders", self.order_body())
        self.assertEqual(status, 201, result)

    def test_service_mode_cannot_interrupt_active_brew(self):
        """SB-08: maintenance cannot interrupt an active customer order; return: None.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        self.login_technician()
        status, order, _ = self.request("POST", "/api/orders", self.order_body())
        self.assertEqual(status, 201, order)
        status, result, _ = self.request(
            "POST", "/api/service/mode", {"enabled": True}, self.technician
        )
        self.assertEqual(status, 409, result)

    def test_diagnostics_require_service_mode(self):
        """SB-09: diagnostics cannot execute in normal customer mode; return: None.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        self.login_technician()
        status, result, _ = self.request(
            "POST", "/api/service/diagnostics",
            {"component": "milk_pump", "simulate_fault": False}, self.technician,
        )
        self.assertEqual(status, 409, result)

    def test_diagnostics_generate_results_and_exportable_error_logs(self):
        """SB-09/10: pass/fail simulations create readable CSV evidence; return: None.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        self.login_technician()
        self.request("POST", "/api/service/mode", {"enabled": True}, self.technician)
        for component, fault in [("milk_pump", False), ("water_pump", False), ("heater", True)]:
            status, result, _ = self.request(
                "POST", "/api/service/diagnostics",
                {"component": component, "simulate_fault": fault}, self.technician,
            )
            self.assertEqual(status, 200, result)
            self.assertTrue(result["simulated"])
            self.assertEqual(result["passed"], not fault)
            self.assertEqual(result["duration_seconds"], 2)
            self.assertEqual(result["component"], component)
        status, result, _ = self.request("GET", "/api/service/logs", client=self.technician)
        self.assertEqual(status, 200, result)
        self.assertTrue(result["logs"])
        status, text, headers = self.request("GET", "/api/service/logs.csv", client=self.technician)
        self.assertEqual(status, 200)
        self.assertIn("attachment", headers.get("Content-Disposition", ""))
        rows = list(csv.DictReader(io.StringIO(text)))
        self.assertTrue(rows)
        self.assertIn("message", rows[0])
        self.assertTrue(any("heater" in str(row).lower() for row in rows))

    def test_malformed_json_and_unknown_order_are_handled(self):
        """Invalid JSON and absent order IDs return controlled errors; return: None.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        status, payload, _ = self.request("POST", "/api/orders", raw=b"{broken")
        self.assertEqual(status, 400, payload)
        status, payload, _ = self.request("GET", "/api/orders/SB-does-not-exist")
        self.assertEqual(status, 404, payload)

    def test_completed_order_updates_sales_and_is_not_double_collected(self):
        """Progress, collection, and daily sales agree using the real timer; return: None.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        self.login_admin()
        status, order, _ = self.request("POST", "/api/orders", self.order_body())
        self.assertEqual(status, 201, order)
        path = "/api/orders/%s" % order["id"]
        status, payload, _ = self.request("POST", path + "/collect", {})
        self.assertEqual(status, 409, payload)
        deadline = time.monotonic() + 18
        progress = []
        while time.monotonic() < deadline:
            status, current, _ = self.request("GET", path)
            self.assertEqual(status, 200, current)
            progress.append(current["progress"])
            if current["status"] == "ready":
                break
            time.sleep(0.4)
        self.assertEqual(current["status"], "ready", current)
        self.assertEqual(current["progress"], 100)
        self.assertEqual(progress, sorted(progress))
        status, completed, _ = self.request("POST", path + "/collect", {})
        self.assertEqual(status, 200, completed)
        self.assertEqual(completed["status"], "completed")
        _, dashboard, _ = self.request("GET", "/api/dashboard", client=self.admin)
        self.assertEqual(dashboard["completed_orders"], 1)
        self.assertEqual(dashboard["revenue_cents"], order["total_cents"])
        self.assertEqual(dashboard["total_orders"], 1)
        self.assertTrue(dashboard["popular_products"])
        status, _, _ = self.request("POST", path + "/collect", {})
        self.assertIn(status, (200, 409))
        _, again, _ = self.request("GET", "/api/dashboard", client=self.admin)
        self.assertEqual(again["completed_orders"], 1)
        self.assertEqual(again["revenue_cents"], order["total_cents"])

    def test_inventory_and_menu_survive_server_restart(self):
        """SQLite state survives a new server instance without reseeding; return: None.

        Inputs: none explicitly; uses the isolated test fixture.
        """
        self.login_admin()
        ingredient = self.inventory()["ingredients"][0]
        changed_stock = ingredient["capacity"] * 0.1
        self.request(
            "POST", "/api/inventory/%s" % ingredient["id"],
            {"stock": changed_stock}, self.admin,
        )
        product = self.products()[0]
        self.request(
            "PATCH", "/api/admin/menu/%s" % product["id"],
            {"price_cents": 777}, self.admin,
        )
        self.stop_server()
        self.start_server()
        self.admin = self.client()
        self.login_admin()
        current = next(i for i in self.inventory()["ingredients"] if i["id"] == ingredient["id"])
        self.assertEqual(current["stock"], changed_stock)
        updated = next(p for p in self.products() if p["id"] == product["id"])
        self.assertEqual(updated["price_cents"], 777)


if __name__ == "__main__":
    unittest.main()
