"""Flask URL shortener with click tracking."""
import secrets, sqlite3
from pathlib import Path
from urllib.parse import urlparse
from flask import Flask, request, redirect, render_template_string, abort, url_for

app=Flask(__name__)
DB=Path(__file__).with_name("shortener.db")
PAGE="""<!doctype html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'><title>LinkLite</title>
<style>body{font:16px system-ui;background:#10121b;color:#eee;max-width:760px;margin:50px auto;padding:0 20px}main{background:#1b2030;padding:28px;border-radius:16px}input{padding:12px;width:65%;max-width:450px}button{padding:12px;background:#9b8cff;border:0;border-radius:8px}a{color:#b7aaff}li{margin:12px 0}.muted{color:#aab}</style></head>
<body><main><h1>LinkLite</h1><p class='muted'>Shorten links and track visits on this server.</p>
<form method='post'><input name='url' placeholder='https://example.com' required><button>Shorten</button></form>
{% if error %}<p>{{error}}</p>{% endif %}<h2>Your links</h2><ul>{% for row in rows %}<li><a href='{{ url_for("go", code=row["code"], _external=True) }}'>{{ url_for("go", code=row["code"], _external=True) }}</a> → {{row["target"]}} <b>({{row["clicks"]}} clicks)</b></li>{% else %}<li>No links created yet.</li>{% endfor %}</ul></main></body></html>"""

def connect():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
    c.execute("CREATE TABLE IF NOT EXISTS links(code TEXT PRIMARY KEY,target TEXT NOT NULL,clicks INTEGER NOT NULL DEFAULT 0)")
    return c

@app.route("/",methods=["GET","POST"])
def home():
    error=None
    if request.method=="POST":
        target=request.form.get("url","").strip()
        parsed=urlparse(target)
        if parsed.scheme not in ("http","https") or not parsed.netloc:
            error="Enter a valid http:// or https:// URL."
        else:
            with connect() as c:
                code=secrets.token_urlsafe(5)
                while c.execute("SELECT 1 FROM links WHERE code=?",(code,)).fetchone():
                    code=secrets.token_urlsafe(5)
                c.execute("INSERT INTO links(code,target) VALUES(?,?)",(code,target))
    with connect() as c: rows=c.execute("SELECT * FROM links ORDER BY rowid DESC").fetchall()
    return render_template_string(PAGE,rows=rows,error=error)

@app.get("/<code>")
def go(code):
    with connect() as c:
        row=c.execute("SELECT target FROM links WHERE code=?",(code,)).fetchone()
        if not row: abort(404)
        c.execute("UPDATE links SET clicks=clicks+1 WHERE code=?",(code,))
    return redirect(row["target"],code=302)

if __name__=="__main__": app.run(debug=True)
