import os
import ConfigParser

from PIL import Image
from flask import Flask, render_template, redirect, request

config = ConfigParser.ConfigParser()
config.read('gal.conf')
imgdir = config.get('gal', 'imgdir')
thumbdir = config.get('gal', 'thumbdir')
urlbase = config.get('gal', 'urlbase')
thumbprefix = config.get('gal', 'thumbprefix')
thumbsize = config.get('gal', 'thumbsize')
allowed_extensions = str.split(config.get('gal', 'allowed_extensions'), ' ')
num_per_row = config.getint('gal', 'num_per_row')
bootstrapurl = config.get('gal', 'bootstrapurl')

app = Flask(__name__)


@app.route('/gal/')
@app.route('/gal/index')
def index():
    images = get_files(imgdir, allowed_extensions)
    gen_thumbs(images, imgdir, thumbdir, thumbprefix, thumbsize)

    return render_template('index.html', urlbase=urlbase, images=images,
                           numrow=num_per_row, bootstrapurl=bootstrapurl)


def get_files(image_dir, allowed_extensions):
    listing = os.listdir(image_dir)
    images = []
    for image in listing:
        if os.path.splitext(image)[1] in allowed_extensions:
            images.append(image)
    images.sort(key=lambda x: os.path.getctime(image_dir + x))
    images.reverse()

    return images


def gen_thumbs(images, imgdir, thumbdir, thumbprefix, thumbsize):
    for image in images:
        origfile = imgdir + image
        thumbfile = thumbdir + thumbprefix + image
        exists = os.path.exists(thumbfile)
        if not exists:
            print "Making thumb for %s" % origfile
            mkthumb(origfile, thumbfile, thumbsize)


def mkthumb(orig, thumbfile, thumbsize):
    size = thumbsize
    im = Image.open(orig)
    im.thumbnail(size, Image.ANTIALIAS)
    im.save(thumbfile)


@app.route('/gal/delete/<image>', methods=['GET'])
def delete(image):
    anchor = request.args.get('anchor')
    filepath = imgdir + image
    thumbpath = thumbdir + 'thumb.' + image
    os.remove(filepath)
    print "Deleting image %s" % filepath
    os.remove(thumbpath)
    print "Deleting thumb %s" % thumbpath
    return redirect('/gal/index#' + anchor)


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=9712)
