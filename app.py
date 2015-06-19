import string, random, hashlib, os
from time import strftime
from shutil import rmtree
from waitress import serve

import flask
from werkzeug import secure_filename

# Load config file
config = {}
with open('config.ini', 'r') as configuration:
    for line in configuration.read().splitlines():
        line = line.split('==')
        config[line[0]] = line[1]

app = flask.Flask(__name__)  # Initialize our application
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # Set the upload limit to 10MiB
app.secret_key = config['SECRET_KEY']


def genHash(seed, leng=5):  # Generate five letter filenames for our files
    base = string.ascii_lowercase + string.digits
    random.seed(seed)
    hash_value = ""
    for i in range(leng):
        hash_value += random.choice(base)
    return hash_value

def handleUpload(f, js=True):
    if secure_filename(f.filename):
        hasher = hashlib.md5() 		
        buf = f.read()		   		
        f.seek(0)
        hasher.update(buf)
        dirname = genHash(hasher.hexdigest())
        if(len(f.filename.split('.')) != 1):
            if('.'.join(f.filename.split('.')[-2:]) == 'tar.gz'):
                extension = '.'.join(f.filename.split('.')[-2:])
            else:
                extension = f.filename.split('.')[-1]
                dirname += '.' + extension
        if not os.path.exists("static/files/%s" % dirname):
            os.mkdir('static/files/%s' % dirname)
            f.save('static/files/%s/%s' % (dirname, secure_filename(f.filename)))
            print 'Uploaded file "%s" to %s' % (secure_filename(f.filename), dirname)
            if js:
                return 'success:' + flask.url_for('getFile', dirname=dirname) + ':' + dirname
            else:
                flask.flash(flask.Markup('Uploaded file %s to <a href="%s">%s</a>') % (secure_filename(f.filename), flask.url_for('getFile', dirname=dirname, filename=secure_filename), f.filename, dirname))
        else:
            if js:
                return 'exists:' + flask.url_for('getFile', dirname=dirname) + ':' + dirname
            else:
                flask.flash(flask.Markup('File %s already exists at <a href="%s">%s</a>') % (secure_filename(f.filename), flask.url_for('getFile', dirname=dirname), dirname))
    else:
        if js:
            return 'error:filenameinvalid'
        else:
            flask.flash('Invalid filename.', flask.url_for('getIndex'))

@app.route('/', methods=['GET'])
def getIndex():
    return flask.render_template('index.html')

@app.route('/', methods=['POST'])
def postIndex():
    """
    File upload happens here.
    We get your filename and convert it to our hash with your extension.
    Then we redirect to the file itself.

    As we are using javascript upload, this is left for noscript users.
    """
    uploaded = flask.request.files.getlist("file[]")
    for f in uploaded:
        handleUpload(f)
    return flask.redirect(flask.url_for('getIndex'))

@app.route('/js', methods=['POST'])
def indexJS():
    """
    File upload for the js happens here.
    the normal one acts as a fallback.
    """
    uploaded = flask.request.files.getlist("file[]")
    for f in uploaded:
        return handleUpload(f)

@app.route('/<dirname>')
@app.route('/<dirname>/<filename>')
def getFile(dirname, filename=None):  # File delivery to the client
    if filename:  # Dir and filename is provided
        return flask.send_from_directory('static/files/%s' % dirname,
                filename)  # Gets the file 'filename' from the directory /static/files/
    elif not filename:  # Filename is absent - we get it for them.
        if os.path.exists('static/files/%s' % dirname):  # Does it even exist?
            files = os.listdir('static/files/%s' % dirname)
            if files:  # Check if there's any file in the directory.
                return flask.redirect(flask.url_for('getFile', dirname=dirname, filename=files[0]))
            # Resend to the proper location to avoid file corruptions.
        else:
            flask.abort(404)  # File has not been found.


if __name__ == '__main__':
    #app.debug = True
        app.run(host="0.0.0.0") #Run our app.
        #serve(app, port=80)
