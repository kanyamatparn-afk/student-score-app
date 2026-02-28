from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

def connect_db():
    return sqlite3.connect("database.db")

def init_db():
    con = connect_db()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS scores(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student TEXT,
        subject TEXT,
        score INTEGER
    )
    """)

    con.commit()
    con.close()

init_db()

# ---------- REGISTER ----------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        con = connect_db()
        cur = con.cursor()
        cur.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)",
                    (username,password,role))
        con.commit()
        con.close()
        return redirect("/")

    return render_template("register.html")

# ---------- LOGIN ----------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]

        con = connect_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?",
                    (username,password))
        user = cur.fetchone()
        con.close()

        if user:
            session["role"] = user[3]
            session["username"] = user[1]
            return redirect("/dashboard")

    return render_template("login.html")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "role" not in session:
        return redirect("/")

    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM scores")
    data = cur.fetchall()
    con.close()

    labels = [d[2] for d in data]
    scores = [d[3] for d in data]

    avg = sum(scores)/len(scores) if scores else 0

    return render_template("dashboard.html",
                           data=data,
                           labels=labels,
                           scores=scores,
                           role=session["role"],
                           avg=avg)

# ---------- ADD ----------
@app.route("/add", methods=["GET","POST"])
def add_score():
    if session.get("role")!="teacher":
        return redirect("/dashboard")

    if request.method=="POST":
        student = request.form["student"]
        subject = request.form["subject"]
        score = int(request.form["score"])

        con = connect_db()
        cur = con.cursor()
        cur.execute("INSERT INTO scores(student,subject,score) VALUES(?,?,?)",
                    (student,subject,score))
        con.commit()
        con.close()
        return redirect("/dashboard")

    return render_template("add_score.html")

# ---------- EDIT ----------
@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):
    if session.get("role")!="teacher":
        return redirect("/dashboard")

    con = connect_db()
    cur = con.cursor()

    if request.method=="POST":
        student = request.form["student"]
        subject = request.form["subject"]
        score = request.form["score"]

        cur.execute("""
        UPDATE scores SET student=?,subject=?,score=? WHERE id=?
        """,(student,subject,score,id))

        con.commit()
        con.close()
        return redirect("/dashboard")

    cur.execute("SELECT * FROM scores WHERE id=?", (id,))
    data = cur.fetchone()
    con.close()

    return render_template("edit_score.html", data=data)

# ---------- DELETE ----------
@app.route("/delete/<int:id>")
def delete(id):
    if session.get("role")!="teacher":
        return redirect("/dashboard")

    con = connect_db()
    cur = con.cursor()
    cur.execute("DELETE FROM scores WHERE id=?", (id,))
    con.commit()
    con.close()
    return redirect("/dashboard")

if __name__=="__main__":
    app.run(debug=True)
