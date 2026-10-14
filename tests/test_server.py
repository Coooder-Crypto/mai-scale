import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import AsyncMock, patch
from urllib.request import Request, urlopen

from server import Handler


class ServerConnectionTests(unittest.TestCase):
    def test_local_token_is_verified_cached_and_not_returned(self):
        Handler.session_token = None
        Handler.session_foods = None
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        origin = f"http://127.0.0.1:{server.server_port}"
        try:
            with patch("server.fetch_food_names", new_callable=AsyncMock, return_value=["巨无霸"]) as fetch:
                request = Request(
                    origin + "/api/connect",
                    data=json.dumps({"token": "test-token-12345"}).encode(),
                    headers={"Origin": origin, "Content-Type": "application/json"},
                    method="POST",
                )
                with urlopen(request, timeout=5) as response:
                    connected = response.read().decode()
                with urlopen(origin + "/api/foods", timeout=5) as response:
                    foods = response.read().decode()
                self.assertIn("巨无霸", connected)
                self.assertIn("巨无霸", foods)
                self.assertNotIn("test-token-12345", connected + foods)
                fetch.assert_awaited_once_with("test-token-12345")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            Handler.session_token = None
            Handler.session_foods = None


if __name__ == "__main__":
    unittest.main()
