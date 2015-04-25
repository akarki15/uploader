# Experiment
import sqlite3, os

from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__)

#########configuration################
DATABASE = os.path.join(app.root_path, 'users.db')
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'


app.config.from_object(__name__)

#########DB STUFF################
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# runs before every request 
@app.before_request
def before_request():
    g.db = connect_db() 	# Storing the db in our special g object

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

#########ROUTE STUFF################
@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if not checkCredentials(request.form['username'], request.form['username']):
            error = 'Invalid credentials'        
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

#########END OF MAIN STUFF################
def checkCredentials(inputU, inputP):
	credentials = (inputU, inputP)
	cur = g.db.execute('select username, pass from users where username = ? and pass = ?', credentials)
	entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
	print entries
	return True

if __name__ == '__main__':
	init_db()
	app.run(debug=True)