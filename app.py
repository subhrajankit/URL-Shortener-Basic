from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import string, random

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  original_url TEXT NOT NULL,
                  short_url TEXT NOT NULL UNIQUE)''')
    conn.commit()
    conn.close()

init_db()

def generate_short_url():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=6))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['original_url']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT short_url FROM urls WHERE original_url = ?", (original_url,))    
        existing = c.fetchone()

        if existing:
            short_url = existing[0]
        else:
            short_url = generate_short_url()
            c.execute("INSERT INTO urls (original_url, short_url) VALUES (?, ?)", (original_url, short_url))
            conn.commit()
        
        conn.close()

        return render_template('index.html', short_url= short_url, original_url=original_url)

    return render_template('index.html')

@app.route('/<short_url>')
def redirect_short_url(short_url):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT original_url FROM urls WHERE short_url = ?", (short_url,))
    result = c.fetchone()
    conn.close()

    if result:
        return redirect(result[0])
    else:
        return "URL not found", 404
    
if __name__ == '__main__':
    app.run(debug=True)