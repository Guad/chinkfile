import string, random, hashlib, os
from time import strftime
from shutil import rmtree
from waitress import serve
from flask import Flask, url_for, flash, Markup, render_template, request, redirect, abort, send_from_directory

from werkzeug import secure_filename

# Load config file
config = {}
with open('config.ini', 'r') as configuration:
    for line in configuration.read().splitlines():
        line = line.split('==')
        config[line[0]] = line[1]

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MiB upload limit
app.secret_key = config['SECRET_KEY']

def genHash(seed, leng=5):
    """ Generate five letter filenames for our files. """
    base = string.ascii_lowercase + string.digits
    random.seed(seed)
    hash_value = ""
    for i in range(leng):
        hash_value += random.choice(base)
    return hash_value

def getDirnameExtension(f):
    """ Gets the dirname and extension of the file. """
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
    return [dirname, extension]

def handleUpload(f, js=True):
    """ Handles the main file upload behavior. """
    value = ""
    if secure_filename(f.filename):
        # get variables
        dirname, extension = getDirnameExtension(f)
        sfilename = secure_filename(f.filename)
        # do the file saving
        if not os.path.exists("static/files/%s" % dirname):
            # if it it's not there, make the directory and save the file
            os.mkdir('static/files/%s' % dirname)
            f.save('static/files/%s/%s' % (dirname, sfilename))
            print('Uploaded file "%s" to %s' % (sfilename, dirname))

            # value is used with /js route, otherwise it's ignored
            url = url_for('getFile', dirname=dirname)
            value = 'success:' + url + ':' + dirname
            # if not js, then flash
            # used to prevent flashes from showing up upon refresh
            if not js:
                message = 'Uploaded file %s to <a href="%s">%s</a>'
                flash(Markup(message) % (sfilename, url, dirname))
        else:
            url = url_for('getFile', dirname=dirname)
            value = 'exists:' + url + ':' + dirname
            if not js:
                message = 'File %s already exists at <a href="%s">%s</a>'
                flash(Markup(message) % (sfilename, url, dirname))
    else:
        value = 'error:filenameinvalid'
        if not js:
            flash('Invalid filename.', url_for('getIndex'))
    return value

@app.route('/', methods=['GET'])
def getIndex():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def postIndex():
    """
    File upload happens here.
    We get your filename and convert it to our hash with your extension.
    Then we redirect to the file itself.

    As we are using javascript upload, this is left for noscript users.
    """
    uploaded = request.files.getlist("file[]")
    for f in uploaded:
        handleUpload(f, js=False)
    return redirect(url_for('getIndex'))

@app.route('/js', methods=['POST'])
def indexJS():
    """
    File upload for the js happens here.
    the normal one acts as a fallback.
    """
    uploaded = request.files.getlist("file[]")
    # handling value this way allows for multiple uploads to work
    # not that the web gui does this at the moment, but it's nice through curl
    value = []
    for f in uploaded:
        v = handleUpload(f)
        value.append(v)
    # it will return the return values delimited by a newline
    # doesn't break existing functionality
    return '\n'.join(value)

@app.route('/<dirname>')
@app.route('/<dirname>/<filename>')
def getFile(dirname, filename=None):
    """
    Flie delivery to the client.
    """
    if filename:
        # If dir and filename  is provided, serve it directly
        return send_from_directory('static/files/%s' % dirname, filename)
    elif not filename:
        # Otherwise, find the filename and redirect back with it
        if os.path.exists('static/files/%s' % dirname):
            files = os.listdir('static/files/%s' % dirname)
            if files:
                # redirect back
                return redirect(url_for('getFile', dirname=dirname, filename=files[0]))
        else:
            abort(404)

if __name__ == '__main__':
    #app.debug = True
    #app.run(host="0.0.0.0")
    serve(app, port=80)
