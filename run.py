import os
from flask import send_from_directory
from flask import Flask, url_for, render_template, request, redirect
from werkzeug import secure_filename

UPLOAD_FOLDER = 'templates/save/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/hello/')
@app.route('/hello/<name>')
def hey(name=None):
    return render_template('hello.html', name=name)

@app.route('/hey2')
def handleHey2():
    return url_for('hey')
 

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload():

    files = request.files.getlist('file[]')
    s = ""
    for file in files:
        s+=file.filename
    return s
    # return file.filename
    # if file and allowed_file(file.filename):

    # filename = secure_filename(file.filename)
    # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    # return redirect(url_for('uploaded_file',
    #                         filename=filename))
@app.route('/', methods=['GET', 'POST'])
def index():        
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id

if __name__ == '__main__':
	app.run(debug=True)