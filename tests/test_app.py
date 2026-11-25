import tempfile
import unittest
from pathlib import Path
import app as shortener

class ShortenerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        shortener.DB = Path(self.tmp.name) / "links.db"
        self.client = shortener.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def test_rejects_invalid_url(self):
        response = self.client.post("/", data={"url": "javascript:alert(1)"})
        self.assertIn(b"valid http", response.data)

    def test_creates_and_counts_link(self):
        response = self.client.post("/", data={"url": "https://example.com"})
        self.assertEqual(response.status_code, 200)
        with shortener.connect() as con:
            row = con.execute("SELECT code FROM links").fetchone()
        self.assertIsNotNone(row)
        redirect = self.client.get("/" + row["code"])
        self.assertEqual(redirect.status_code, 302)
        self.assertEqual(redirect.headers["Location"], "https://example.com")
        with shortener.connect() as con:
            count = con.execute("SELECT clicks FROM links WHERE code=?", (row["code"],)).fetchone()["clicks"]
        self.assertEqual(count, 1)

if __name__ == "__main__":
    unittest.main()
