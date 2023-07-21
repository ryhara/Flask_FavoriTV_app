from flask import Flask, render_template, request, g, redirect, url_for, session, flash
import uuid
import hashlib
import sqlite3
import os, datetime
from dataclasses import dataclass
from datetime import datetime, timedelta
import pdb

DATABASE = "database.db"
app = Flask(__name__, static_folder='./static')
app.config['SECRET_KEY'] = '1234'

@app.before_request
def before_request():
    # リクエストのたびにセッションの寿命を更新する
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)
    # app.permanent_session_lifetime = timedelta(seconds=1)
    session.modified = True

"""
データベース接続
"""
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def home():
    if 'user_id' not in session:
        return render_template('home.html')
    return render_template('home.html')

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT username, email, introduction, is_public, pict FROM user WHERE id=?", (session['user_id'],))
        my = cur.fetchone()
        if not my:
            flash("Error: No such a user or session expired", "error")
            cur.close()
            conn.close()
            return redirect(url_for("home"))
        cur.close()
        conn.close()
        return redirect(url_for('my_page'))
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        request_valid = True
        h = hashlib.md5(password.encode())
        conn = get_db()
        cur = conn.cursor()
        if not username:
            flash('Username is required')
            request_valid = False
        if not password:
            flash('Password is required')
            request_valid = False
        if request_valid:
            user = cur.execute('SELECT * FROM user WHERE username = ? AND password = ?', (username, h.hexdigest())).fetchone()
            if user is None:
                flash('Invalid username or password')
            else:
                session['user_id'] = user[0]
                cur.execute("SELECT username, email, introduction, is_public, pict FROM user WHERE id=?", (session['user_id'],))
                my = cur.fetchone()
                if not my:
                    flash("Error: No such a user or session expired", "error")
                    cur.close()
                    conn.close()
                    return redirect(url_for("home"))
                cur.close()
                conn.close()
                flash("Logged in")
                return redirect(url_for('my_page'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    conn = get_db()
    cur = conn.cursor()
    request_valid = True
    if 'user_id' in session:
        cur.execute("SELECT username, email, introduction, is_public, pict FROM user WHERE id=?", (session['user_id'],))
        my = cur.fetchone()
        if not my:
            flash("Error: No such a user or session expired", "error")
            cur.close()
            conn.close()
            return redirect(url_for("home"))
        cur.close()
        conn.close()
        return redirect(url_for('my_page'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        is_public = request.form['is_public']
        password = request.form['password']
        confirm = request.form['confirm']
        if not username:
            flash('Username is required')
            request_valid = False
        if not email:
            flash('Email is required')
            request_valid = False
        if not password:
            flash('Password is required')
            request_valid = False
        if password != confirm:
            flash('Passwords do not match')
            request_valid = False
        if cur.execute('SELECT * FROM user WHERE username = ?',(username,)).fetchone():
            flash('This username is already taken')
            request_valid = False
        if cur.execute('SELECT * FROM user WHERE email = ?',(email,)).fetchone():
            flash('This email is already taken')
            request_valid = False
        if request_valid:
            h = hashlib.md5(password.encode())
            cur.execute('INSERT INTO user (username, email, password, is_public) VALUES (?, ?, ?, ?)', (username, email, h.hexdigest(), int(is_public)))
            conn.commit()
            cur.close()
            conn.close()
            flash('User create!')
            return redirect(url_for('login'))
    else:
        return render_template('signup.html')

@app.route('/logout')
def logout():
    if session.pop('user_id', None):
        flash("Logged out")
    return redirect(url_for('home'))

@app.route("/my_page")
def my_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT username, email, introduction, is_public, pict FROM user WHERE id=?", (session['user_id'],))
    my = cur.fetchone()
    if not my:
        flash("Error: No such a user or session expired", "error")
        cur.close()
        conn.close()
        return redirect(url_for("home"))
    cur.close()
    conn.close()
    return render_template('my_page.html', my=my)

@app.route("/my_page/edit", methods=["GET", "POST"])
def my_page_edit():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor()
    if request.method == 'GET':
        cur.execute("SELECT username, email, introduction, is_public FROM user WHERE id=?", (session['user_id'],))
        my = cur.fetchone()
        cur.close()
        if not my:
            flash("Error: No such a user or session expired", "error")
            conn.close()
            return redirect(url_for("home"))
        conn.close()
        return render_template('my_page_edit.html', my=my)
    if request.method == 'POST':
        request_valid = True; pict_valid = False
        username = request.form['username']; email = request.form['email']
        is_public = request.form['is_public']; introduction = request.form['introduction']
        password = request.form['password']; confirm = request.form['confirm']
        old_password = request.form['old_password']

        if not username:
            flash('Username is required')
            request_valid = False
        if not email:
            flash('Email is required')
            request_valid = False
        if not old_password:
            flash('Old Password is required')
            request_valid = False
        if password != confirm:
            flash('Passwords do not match')
            request_valid = False
        cur.execute('SELECT * FROM user WHERE username = ?',(username,))
        same_username = cur.fetchone()
        if same_username:
            if same_username[0] != session['user_id']:
                flash('This username is already taken')
                request_valid = False
        cur.execute('SELECT * FROM user WHERE email = ?',(email,))
        same_email = cur.fetchone()
        if same_email:
            if same_email[0] != session['user_id']:
                flash('This email is already taken')
                request_valid = False

        if 'pict' in request.files:
            file = request.files["pict"]
            if file.filename == "":
                pass
            elif not file.filename.endswith(('jpg', 'jpeg', 'png')):
                request_valid = False
                flash('Image extension is invalid.')
            else:
                pict_valid = True

        h = hashlib.md5(old_password.encode())
        user = cur.execute('SELECT * FROM user WHERE id = ? AND password = ?', (session['user_id'], h.hexdigest())).fetchone()
        if user is None:
            flash('Old Password is Wrong !')
            request_valid = False

        if request_valid:
            if (pict_valid):
                file = request.files["pict"]
                filename = str(session['user_id']) + os.path.splitext(file.filename)[1]
                file.save(os.path.join('./static/pict', filename))
                if (not password):
                    cur.execute('UPDATE user SET username=?, email=?, introduction=?, is_public=?, pict=? WHERE id=?', [username, email, introduction, int(is_public), filename, session['user_id']])
                else:
                    h = hashlib.md5(password.encode())
                    cur.execute('UPDATE user SET username=?, email=?, introduction=?, password=?, is_public=?, pict=? WHERE id=?', [username, email, introduction, h.hexdigest(), int(is_public), filename, session['user_id']])
            else:
                if (not password):
                    cur.execute('UPDATE user SET username=?, email=?, introduction=?, is_public=? WHERE id=?', [username, email, introduction, int(is_public), session['user_id']])
                else:
                    h = hashlib.md5(password.encode())
                    cur.execute('UPDATE user SET username=?, email=?, introduction=?, password=?, is_public=? WHERE id=?', [username, email, introduction, h.hexdigest(), int(is_public), session['user_id']])
            conn.commit()
            cur.execute("SELECT username, email, introduction, is_public, pict FROM user WHERE id=?", (session['user_id'],))
            my = cur.fetchone()
            cur.close()
            if not my:
                flash("Error: No such a user or session expired", "error")
                conn.close()
                return redirect(url_for("home"))
        else:
            cur.execute("SELECT username, email, introduction, is_public FROM user WHERE id=?", (session['user_id'],))
            my = cur.fetchone()
            cur.close()
            if not my:
                flash("Error: No such a user or session expired", "error")
                conn.close()
                return redirect(url_for("home"))
            conn.close()
            return render_template("my_page_edit.html", my=my)
        conn.close()
        return redirect(url_for('my_page'))


@app.route("/users", methods=["GET", "POST"])
def user_index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        user_list = cur.execute("SELECT u.id, u.username, u.introduction, u.pict FROM user u WHERE u.is_public=1 and u.id <> ? and u.username LIKE ? ORDER BY u.id", (session['user_id'], '%'+request.form["username"]+'%')).fetchall()
        return render_template('user_index.html', counts=len(user_list), user_list=user_list)
    else:
        user_list = cur.execute("SELECT id, username, introduction, pict FROM user WHERE is_public=1 and id <> ? ORDER BY id", (session['user_id'],)).fetchall()
        return render_template("user_index.html", counts=len(user_list), user_list=user_list)
    return render_template('user_index.html')

@app.route("/users/<id>")
def user_show(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE id = ? and is_public=1", (id,))
    user = cur.fetchone()
    if not user:
        flash(f"Error: No user entry {id}", "error")
        cur.close()
        conn.close()
        return redirect(url_for("users"))
    user_program = cur.execute("SELECT program_id, program_name, station, start, end, day FROM favorite_program fp WHERE fp.user_id=?", (id,)).fetchall()

    program_by_day = {}
    for i in ["月", "火", "水", "木", "金", "土", "日", "平日"]:
            program_by_day[i] = []
    for program in user_program:
        program_id, program_name, station, start, end, day = program
        program_by_day[day].append((program_id, station, program_name, start, end))
    return render_template("user_show.html", user=user, program_by_day=program_by_day)

@app.route("/my_program", methods=["GET"])
def my_program():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT program_id, program_name, station, start, end, day FROM favorite_program fp WHERE fp.user_id=? ORDER BY fp.start", (session['user_id'],))
    my_program = cur.fetchall()

    program_by_day = {}
    day_list =  ["月", "火", "水", "木", "金", "土", "日", "平日"]
    for i in day_list:
            program_by_day[i] = []
    for program in my_program:
        program_id, program_name, station, start, end, day = program
        program_by_day[day].append((program_id, station, program_name, start, end))
    cur.close()
    conn.close()
    return render_template('my_program.html', program_by_day=program_by_day)


@app.route('/program/<id>', methods=["GET", "POST"])
def program_show(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        cur.execute("SELECT * FROM favorite f WHERE f.user_id=? and f.program_id=?", (session['user_id'], id))
        favorite_check = cur.fetchone()
        if favorite_check and request.form['is_favorite'] == "0":
            cur.execute("DELETE FROM favorite WHERE user_id=? and program_id=?", (session['user_id'], id))
            # cur.execute("UPDATE favorite set is_favorite=? WHERE user_id=? and program_id=?", (request.form['is_favorite'], session['user_id'], id))
            conn.commit()
        else :
            if not favorite_check and request.form['is_favorite'] == "1":
                cur.execute('INSERT INTO favorite (user_id, program_id, is_favorite) VALUES (?, ?, ?)', (session['user_id'], id, 1))
                conn.commit()
        return redirect(url_for('program_show', id=id))

    program = cur.execute("SELECT * FROM program p WHERE p.id = ?", (id,)).fetchone()
    favorite = cur.execute("SELECT * FROM favorite f WHERE f.user_id=? and f.program_id=?", (session['user_id'], id)).fetchone()
    perform_info = cur.execute("SELECT * FROM perform_info pi WHERE pi.program_id = ?", (id,)).fetchall()
    cur.close()
    conn.close()
    return render_template("program_show.html", program=program, perform_info=perform_info, favorite=favorite)

@app.route("/program_search", methods=["GET", "POST"])
def program_search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        if not request.form['selectedTime']:
            if request.form['day'] == "1":
                program_list = cur.execute("SELECT p.id, s.name as station, p.name, p.start, p.end, p.day FROM program p, stations s WHERE p.station_id=s.id and p.name LIKE ? ORDER BY p.start, p.station_id", ('%'+request.form["program_name"]+'%',)).fetchall()
            else:
                program_list = cur.execute("SELECT p.id, s.name as station, p.name, p.start, p.end, p.day FROM program p, stations s WHERE p.station_id=s.id and p.day=? and p.name LIKE ? ORDER BY p.start, p.station_id", (request.form['day'], '%'+request.form["program_name"]+'%')).fetchall()
        else:
            start_time = request.form["selectedTime"]
            time_obj = datetime.strptime(start_time, "%H:%M")
            new_time_obj = time_obj + timedelta(hours=1)
            start_time_range = new_time_obj.strftime("%H:%M")
            if request.form['day'] == "1":
                program_list = cur.execute("SELECT p.id, s.name as station, p.name, p.start, p.end, p.day FROM program p, stations s WHERE p.station_id=s.id and p.start >= ? and p.start < ? and  p.name LIKE ? ORDER BY p.start, p.station_id", (request.form["selectedTime"], start_time_range, '%'+request.form["program_name"]+'%')).fetchall()
            else:
                program_list = cur.execute("SELECT p.id, s.name as station, p.name, p.start, p.end, p.day FROM program p, stations s WHERE p.station_id=s.id and p.day=? and p.start >= ? and p.start < ? and p.name LIKE ? ORDER BY p.start, p.station_id", (request.form['day'], request.form["selectedTime"], start_time_range, '%'+request.form["program_name"]+'%')).fetchall()
        program_by_day = {}
        day_list = ["月", "火", "水", "木", "金", "土", "日", "平日"]
        for i in day_list:
                program_by_day[i] = []
        for program in program_list:
            program_id, station, name, start, end, day = program
            program_by_day[day].append((program_id, station, name, start, end))
        cur.close()
        conn.close()
        return render_template('program_search.html', counts=len(program_list), program_by_day=program_by_day, day_list=day_list)
    else:
        program_list = cur.execute("SELECT p.id, s.name as station, p.name, p.start, p.end, p.day FROM program p, stations s WHERE p.station_id=s.id ORDER BY p.start ASC, p.station_id ASC").fetchall()
        program_by_day = {}
        day_list = ["月", "火", "水", "木", "金", "土", "日", "平日"]
        for i in day_list:
                program_by_day[i] = []
        for program in program_list:
            program_id, station, name, start, end, day = program
            program_by_day[day].append((program_id, station, name, start, end))
        cur.close()
        conn.close()
        return render_template('program_search.html', counts=len(program_list), program_by_day=program_by_day, day_list=day_list)
    return render_template('program_search.html')

# pdb.set_trace()
@app.route("/program/new", methods=["GET", "POST"])
def program_new():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        station_id = request.form['station_id']
        program_name = request.form['program_name']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        day = request.form['day']
        description = request.form['description']
        request_valid = True

        if station_id == "選択してください":
            flash("Station is required")
            request_valid = False
        if not program_name:
            flash("Program Name is required")
            request_valid = False
        if cur.execute("SELECT * from program WHERE name=?", (program_name,)).fetchone():
            flash("This Program already exists!")
            request_valid = False
        if not start_time:
            flash("Start Time is required")
            request_valid = False
        if not end_time:
            flash("End Time is required")
            request_valid = False
        if day == "選択してください":
            flash("Day is required")
            request_valid = False
        if request_valid:
            cur.execute("INSERT INTO program (name, station_id, start, end, day, description) VALUES (?, ?, ?, ?, ?, ?)", (program_name, station_id, start_time, end_time, day, description))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('program_search'))
    day_list = ["月", "火", "水", "木", "金", "土", "日", "平日"]
    station_list = cur.execute("SELECT id, name FROM stations").fetchall()
    cur.close()
    conn.close()
    return render_template('program_new.html', station_list=station_list, day_list=day_list)

@app.route("/program/<id>/edit", methods=["GET", "POST"])
def program_edit(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        day = request.form['day']
        description = request.form['description']
        request_valid = True

        if not start_time:
            flash("Start Time is required")
            request_valid = False
        if not end_time:
            flash("End Time is required")
            request_valid = False
        if day == "選択してください":
            flash("Day is required")
            request_valid = False
        if request_valid:
            cur.execute("UPDATE program SET start=?, end=?, day=?, description=? WHERE id=?", (start_time, end_time, day, description, id))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('program_show', id=id))
    day_list = ["月", "火", "水", "木", "金", "土", "日", "平日"]
    station_list = cur.execute("SELECT id, name FROM stations").fetchall()
    program = cur.execute("SELECT * FROM program p WHERE p.id = ?", (id,)).fetchone()
    cur.close()
    conn.close()
    return render_template('program_edit.html', station_list=station_list, day_list=day_list, program=program)


@app.route('/program/<id>/perform/new', methods=["GET", "POST"])
def perform_new(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        performer_name = request.form['performer_name']
        role = request.form['role']
        request_valid = True
        if not performer_name:
            flash("Performer Name is required")
            request_valid = False
        if request_valid:
            if cur.execute("SELECT * FROM celebrity WHERE name=?", (performer_name, )).fetchone():
                pass
            else:
                cur.execute("INSERT INTO celebrity (name) VALUES (?)", (performer_name,))
                conn.commit()
            celebrity = cur.execute("SELECT * FROM celebrity WHERE name=?", (performer_name, )).fetchone()
            if cur.execute("SELECT * FROM perform WHERE program_id=? and celebrity_id=?", (id, celebrity[0])).fetchone():
                flash("This celebrity already registered!")
            else:
                cur.execute("INSERT INTO perform (program_id, celebrity_id, role) VALUES (?, ?, ?)", (id, celebrity[0], role))
                conn.commit()
                cur.close()
                conn.close()
                return redirect(url_for("perform_edit", id=id))

    program = cur.execute("SELECT * FROM program WHERE id=?", (id,)).fetchone()
    cur.close()
    conn.close()
    return (render_template('perform_new.html', program=program))


@app.route('/program/<id>/perform/edit', methods=["GET", "POST"])
def perform_edit(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor()
    celebrity_list = []
    if request.method == "POST":
        if 'celebrity_name' in request.form:
            celebrity_list = cur.execute("SELECT * FROM celebrity WHERE name LIKE ? ORDER BY id", ('%'+request.form["celebrity_name"]+'%',)).fetchall()
        elif 'register' in request.form:
            if cur.execute("SELECT * FROM perform WHERE program_id=? and celebrity_id=?", (id, request.form['register'])).fetchone():
                pass
            else:
                cur.execute("INSERT INTO perform (program_id, celebrity_id) VALUES (?, ?)", (id, request.form['register']))
                conn.commit()
                return redirect(url_for('perform_edit', id=id))
        elif 'delete' in request.form:
            cur.execute("DELETE FROM perform WHERE program_id=? and celebrity_id=?", (id, request.form['delete']))
            conn.commit()
            return redirect(url_for('perform_edit', id=id))

    program = cur.execute("SELECT * FROM program WHERE id=?", (id,)).fetchone()
    perform_info = cur.execute("SELECT * FROM perform_info pi WHERE pi.program_id = ?", (id,)).fetchall()
    cur.close()
    conn.close()
    return render_template("perform_edit.html", celebrity_list=celebrity_list, perform_info=perform_info, program=program)


if __name__ == '__main__':
    app.run(debug=True)
