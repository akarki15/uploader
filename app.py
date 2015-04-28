# Experiment
import sqlite3, os

from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import dicom
from werkzeug import secure_filename

app = Flask(__name__)

#########configuration################
DATABASE = os.path.join(app.root_path, 'uploader.db')
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['dcm'])

app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
	entries = ""
	if not session.get('logged_in'):
		return render_template('login.html')
	# id integer primary key autoincrement,
 #  filename text not null,
 #  annotation text,
 #  patientname text,
 #  patientid text
 	t = (session['username'],)
	cur = g.db.execute('SELECT id, filename, patientname, patientid, annotation from entries where  username = ? order by id desc ', t)
	entries = [dict(id=row[0], filename=row[1], patientname=row[2], patientid=row[3], annotation=row[4]) for row in cur.fetchall()]	
	return render_template('show_entries.html',entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)	
	files = request.files.getlist('file[]')	
	print len(files)
	# clear the tags if we get default values
	tags = request.form["tags"]
	if  tags == "Enter tags separated by comma":
		tags = None

	isDCM = False
	for file in files:	
		if file and allowed_file(file.filename):			
			isDCM = True
			ds = dicom.read_file(file)
			# save file
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			
			# extracts info from dicom, insert tuple into record
			entry = (session['username'],filename, tags, ds.PatientName, ds.PatientID)
			g.db.execute('INSERT INTO entries (username, filename, annotation, patientname, patientid) VALUES (?,?,?,?,?)', entry)	
			g.db.commit()


	if not isDCM:	
		flash ("Nothing happened! Upload a .dcm file!")
	else: 
		flash ("DCM uploaded!")	

	return redirect(url_for('show_entries'))		

	
	
		# if allowed_file(file.filename):

		#     filename = secure_filename(file.filename)
		#     file.save(UPLOAD_FOLDER, filename))
		#     return redirect(url_for('uploaded_file',
		#                             filename=filename))
		# 	entry = (, inputP)
		# 	g.db.execute('INSERT INTO users VALUES (?,?)', credentials)	
		# 	g.db.commit()


	return redirect(url_for('show_entries'))


	# fileName text not null,
 #  annotation text,
 #  patientName text,
 #  patientID text

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if not checkCredentials(request.form['username']):
			error = 'Invalid credentials'        
		else:
			session['username'] = request.form['username']
			session['logged_in'] = True
			flash('Logged in')			
			return redirect(url_for('show_entries'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():

	error = None
	if request.method == 'POST':
		if request.form['username']=="":
			print "wow12"
			error = "Username cannot be blank!"
		elif not checkCredentials(request.form['username']):
			createAccount(request.form['username'], request.form['password'])            			
			flash('Account created!')
			return render_template('login.html', error=error)
		else:
			error = 'Username already exists. Go to login page.'        			
	return render_template('signup.html', error=error)

#########END OF MAIN STUFF################
def checkCredentials(inputU):	
	t = (inputU,)
	cur = g.db.execute('select username from users where username = ?', t)
	entries = [dict(title=row[0]) for row in cur.fetchall()]	
	if len(entries) == 0:
		return False
	else:
		return True

def createAccount(inputU, inputP):
	credentials = (inputU, inputP)
	g.db.execute('INSERT INTO users VALUES (?,?)', credentials)	
	g.db.commit()
	
def listToString(list):
	return str(list)[1:-1]

def stringToList(s):
	return s.split(',')

def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
if __name__ == '__main__':	
	init_db()
	app.run(debug=True)