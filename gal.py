import logging
import os

import flask_bootstrap

from PIL import Image
from flask import Flask, render_template, redirect, request
from configobj import ConfigObj

# Configs
config = ConfigObj('gal.conf')
allowed_extensions = str.split(config['allowed_extensions'], ' ')
imgdir = config['imgdir']
thumbdir = config['thumbdir']
thumbprefix = config['thumbprefix']
THUMBSIZE = 400, 400

# App contructs
app = Flask(__name__)
flask_bootstrap.Bootstrap(app)
app.logger.setLevel(logging.INFO)
app.debug = True


# Routes
@app.route('/gal/')
@app.route('/gal/index')
def index():
    images = get_files(imgdir, allowed_extensions)
    gen_thumbs(images, imgdir, thumbdir, thumbprefix)

    return render_template('index.html', config=config, images=images)


@app.route('/gal/delete/<image>', methods=['GET'])
def delete(image):
    anchor = request.args.get('anchor')
    filepath = imgdir + image
    thumbpath = thumbdir + 'thumb.' + image
    os.remove(filepath)
    app.logger.info('Deleting image %s' % filepath)
    os.remove(thumbpath)
    app.logger.info('Deleting thumb %s' % thumbpath)

    return redirect('/gal/index#' + anchor)

# Functions


def get_files(image_dir, allowed_extensions):
    listing = os.listdir(image_dir)
    images = []
    for image in listing:
        if os.path.splitext(image)[1] in allowed_extensions:
            images.append(image)
    images.sort(key=lambda x: os.path.getmtime(image_dir + x))
    images.reverse()

    return images


def gen_thumbs(images, imgdir, thumbdir, thumbprefix):
    for image in images:
        origfile = imgdir + image
        thumbfile = thumbdir + thumbprefix + image
        exists = os.path.exists(thumbfile)
        if not exists:
            app.logger.info('Making thumb for %s' % origfile)
            mkthumb(origfile, thumbfile)


def mkthumb(orig, thumbfile):
    size = THUMBSIZE
    print size
    im = Image.open(orig)
    im.thumbnail(size, Image.ANTIALIAS)
    im.save(thumbfile)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=9712)
