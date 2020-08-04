# Mosaic Image Generator #
Automated generation of mosaic images from a set of images.

## Installation/Preparation ##
Python 3 is required.

1. Clone the repository.
2. Install dependencies by running `python3 -m pip install -r requirements.txt` inside the repo.
3. Get a huge amount of images and put them in one single folder.

For the default settings 1024 images will be used. So to get any result with default settings at least that many images are required. For a _good_ result a few times as many are recommended. Also the diversity of colors in the images has a big impact on the result. (Representing yellow pixels is hard if you don't have yellowish images in your dataset.)

## Usage ##
Running `python3 mosaic.py --help` will get you the following help text:
```
usage: mosaic.py [-h] [-n NORMAL] [-w WIDTH] [-o OUT_PIC] src_dir src_pic

Mosaic Image Generator v1.0

positional arguments:
  src_dir               directory with a lot of images
  src_pic               the image that will be recreated with small images

optional arguments:
  -h, --help            show this help message and exit
  -n NORMAL, --normal NORMAL
                        size of individual images of the mosaic in pixels
                        (default: 256)
  -w WIDTH, --width WIDTH
                        number of images per row of the mosaic (default: 32)
  -o OUT_PIC, --out_pic OUT_PIC
                        the path of the generated mosaic (default:
                        'mosaic_{w}x{n}.jpg')
```
You need at least `width`² images in the `src_dir` directory.
Only png and jpg images will be used.

## TODO ##
- make calculation of average colors async or multithreaded
