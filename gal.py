import os
import PIL

from PIL import Image
from flask import Flask, render_template, redirect, request

imgdir = '/path/to/images'
thumbdir = imgdir + '.thumbs/'
urlbase = 'http://baseurl/'
thumbprefix = 'thumb.'
thumbsize = 400, 400
allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
num_per_row = 3

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def main():
  images = get_files(imgdir, allowed_extensions)
  gen_thumbs(images, imgdir, thumbdir, thumbprefix, thumbsize)
  return render_template('index.html', urlbase=urlbase, images=images, numrow=num_per_row)

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
      print thumbfile
      print "Making thumb for %s" % origfile
      mkthumb(origfile, thumbfile, thumbsize)

def mkthumb(orig, thumbfile, thumbsize):
  size = thumbsize
  im = Image.open(orig)
  im.thumbnail(size, Image.ANTIALIAS)
  im.save(thumbfile)

@app.route('/delete/<image>', methods=['GET'])
def delete(image):
  anchor = request.args.get('anchor')
  filepath = imgdir + image
  thumbpath = thumbdir + 'thumb.' + image
  os.remove(filepath)
  print "Deleting image %s" % filepath
  os.remove(thumbpath)
  print "Deleting thumb %s" % thumbpath
  return redirect('/#' + anchor)
  
if __name__ == "__main__":
  # app.debug = True
  app.run(host='0.0.0.0', port=9712)
