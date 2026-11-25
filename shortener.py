"""Local URL shortener service with SQLite and click counting."""
import argparse, secrets, sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

DB="links.db"
def init(db=DB):
    con=sqlite3.connect(db);con.execute("CREATE TABLE IF NOT EXISTS links(code TEXT PRIMARY KEY,url TEXT NOT NULL,clicks INTEGER NOT NULL DEFAULT 0)");con.commit();return con
def create_link(con,url):
    parsed=urlparse(url)
    if parsed.scheme not in {"http","https"} or not parsed.netloc: raise ValueError("Enter a valid http(s) URL.")
    code=secrets.token_urlsafe(5)
    con.execute("INSERT INTO links(code,url) VALUES(?,?)",(code,url));con.commit();return code
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        code=self.path.strip("/")
        row=self.server.db.execute("SELECT url FROM links WHERE code=?",(code,)).fetchone()
        if not row:self.send_error(404,"Short link not found");return
        self.server.db.execute("UPDATE links SET clicks=clicks+1 WHERE code=?",(code,));self.server.db.commit()
        self.send_response(302);self.send_header("Location",row[0]);self.end_headers()
    def log_message(self,*args): pass
def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest="cmd",required=True)
    c=sub.add_parser("create");c.add_argument("url")
    sub.add_parser("stats");s=sub.add_parser("serve");s.add_argument("--port",type=int,default=8000)
    args=parser.parse_args();con=init()
    if args.cmd=="create":
        try: print("Short code:",create_link(con,args.url))
        except ValueError as e: parser.error(str(e))
    elif args.cmd=="stats":
        for code,url,clicks in con.execute("SELECT code,url,clicks FROM links ORDER BY clicks DESC"):print(f"{code} | {clicks} clicks | {url}")
    else:
        server=HTTPServer(("127.0.0.1",args.port),Handler);server.db=con
        print(f"Local shortener running at http://127.0.0.1:{args.port}/");server.serve_forever()
if __name__=="__main__":main()
