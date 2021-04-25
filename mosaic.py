import argparse
import ast
import os
import random
import sys
import time
from functools import partial
from multiprocessing import Value, Lock
from multiprocessing.pool import ThreadPool

import numpy as np
from PIL import Image
from skimage import io, transform

current_time_milli = lambda: int(round(time.time() * 1000))
current_time_micro = lambda: int(round(time.time() * 1000000))


class Counter(object):
	def __init__(self, initval=0):
		self.val = Value('i', initval)
		self.lock = Lock()

	def increment(self):
		with self.lock:
			self.val.value += 1

	def value(self):
		with self.lock:
			return self.val.value


def progress(count, total, status=''):
	bar_len = 40
	filled_len = int(round(bar_len * count / float(total)))
	percents = round(100.0 * count / float(total), 1)
	bar = '#' * filled_len + '-' * (bar_len - filled_len)
	sys.stdout.write('[%s] %s%s %s\r' % (bar, percents, '%', status))
	sys.stdout.flush()


def squarify_skimage(path, size, outfile='-1'):
	img = io.imread(path)

	if img.shape[0] < img.shape[1]:
		img = transform.resize(img, (size, int(size * max(img.shape[:-1]) / min(img.shape[:-1]))), anti_aliasing=False)
		a = 0
		b = int((max(img.shape[:-1])-size)/2)
		c = size
		d = int((max(img.shape[:-1])-size)/2+size)
		img = img[a:c, b:d]
	elif img.shape[0] > img.shape[1]:
		img = transform.resize(img, (int(size * max(img.shape[:-1]) / min(img.shape[:-1])), size), anti_aliasing=False)
		img = img[int((max(img.shape[:-1])-size)/2):int((max(img.shape[:-1])-size)/2+size), 0:size]
	else:
		img = transform.resize(img, (size, size))

	if outfile == '-1':
		return img
	else:
		io.imsave(outfile, img)


def squarify(path, size, outfile='-1', fill=False, fill_color=(255, 0, 255)):
	img = Image.open(path)
	if img.mode != 'RGB':
		img = img.convert('RGB')

	if fill:
		new_img = Image.new('RGB', (size, size), fill_color)
		img.thumbnail((size, size))
		(w, h) = img.size
		new_img.paste(img, (int((size - w) / 2), int((size - h) / 2)))
		img = new_img
	else:
		if img.size[0] < img.size[1]:
			img = img.resize((size, int(size * max(img.size) / min(img.size)))) # this takes about 12 times longer than img.crop
			img = img.crop((0, (max(img.size) - size) / 2, size, (max(img.size) - size) / 2 + size))
		elif img.size[0] > img.size[1]:
			img = img.resize((int(size * max(img.size) / min(img.size)), size), Image.NEAREST)
			img = img.crop(((max(img.size) - size) / 2, 0, (max(img.size) - size) / 2 + size, size))
		else:
			img = img.resize((size, size))

	if outfile != '-1':
		img.save(outfile)
	return img


def normalize_images(indir, outdir, normal_size, mode='crop'):  # TODO mode (crop/fill)
	"""Load and rescale Images by using multiple threads

	Args:
		indir (:obj:`str`): Input directory
		outdir (:obj:`str`): Output directory
		normal_size (int): target width and height of new images
	"""

	piclist = get_imglist(indir)
	ensure_dir(outdir)

	pool = ThreadPool(4)
	counter = Counter(0)

	normalize_image_partial = partial(
		normalize_image,
		counter=counter, max_value=len(piclist), out=outdir, normal_size=normal_size,
	)

	pool.map(normalize_image_partial, piclist)
	pool.close()
	pool.join()


def normalize_image(path, counter, max_value, out, normal_size):
	outfile = os.path.join(out, f'pic{counter.value()}.jpg')
	if not os.path.exists(outfile):
		try:
			squarify(path, normal_size, outfile)
		except OSError:
			print(f'Skipping OSError image: {path}...                ')
		except UnboundLocalError:
			print(f'Skipping UnboundLocalError image: {path}...      ')
	counter.increment()
	progress(counter.value(), max_value, 'copying and resizing images..')


def calculate_average_colors(piclist, average_color_f):
	pool = ThreadPool(4)
	counter = Counter(0)

	calculate_average_color_partial = partial(
		calculate_average_color, counter=counter, max_value=len(piclist),
	)

	avg_colors = pool.map(calculate_average_color_partial, piclist)
	pool.close()
	pool.join()
	save_average_colors(average_color_f, avg_colors)
	return avg_colors


def calculate_average_color(path, *, counter, max_value):
	img = io.imread(path)
	avg_color = tuple(np.rint(img.mean(axis=(0, 1))).astype(int))

	counter.increment()
	progress(counter.value(), max_value, 'calc average colors...')

	return (path, tuple(avg_color))


def ensure_dir(path):
	if not os.path.exists(path):
		os.makedirs(path)


def get_imglist(path):
	infiles = []
	for x in os.listdir(path):
		if os.path.splitext(x)[1] in ['.png', '.jpg', '.jpeg']:
			infiles.append(os.path.join(path, x))
	return infiles


def get_index_closest_color(color, colors): # TODO improve that (sort list beforehand, than pivot search if possible)
	color = np.array(color)
	colors = np.array([x[1] for x in colors])
	distances = np.sqrt(np.sum((colors - color) ** 2, axis=1))
	index_of_smallest = np.where(distances == np.amin(distances))
	return int(index_of_smallest[0][0])


def get_concat_x(im1, im2):
	dst = Image.new('RGB', (im1.width + im2.width, im1.height))
	dst.paste(im1, (0, 0))
	dst.paste(im2, (im1.width, 0))
	return dst


def get_concat_y(im1, im2):
	dst = Image.new('RGB', (im1.width, im1.height + im2.height))
	dst.paste(im1, (0, 0))
	dst.paste(im2, (0, im1.height))
	return dst


def save_average_colors(path, colors):
	file = open(path, 'w')
	for path, color in colors:
		file.write(f'{path}\t{str(color)}\n')


def read_average_colors(path):
	colors = []
	for line in open(path):
		path, color = line.strip().split('\t')
		colors.append((path, ast.literal_eval(color)))
	return colors


def file_len(file):
	with open(file) as f:
		for i, l in enumerate(f):
			pass
	return i + 1


def mosaic(original_image_path, stitched_out_path, source_path, images_per_line):
	piclist = get_imglist(source_path)

	average_color_f = os.path.join(source_path, 'colors.txt')
	if os.path.exists(average_color_f) and file_len(average_color_f) == len(piclist):
		print('reading stored average colors..')
		piccolors = read_average_colors(average_color_f)
	else:
		piccolors = calculate_average_colors(piclist, average_color_f)
		print()

	## strink target image to squared image of size (images_per_line, images_per_line)
	## then put the colors into a list
	targetcolors = list(squarify(original_image_path, size=images_per_line, fill=True).getdata())

	randomized_indexes = [x for x in range(len(targetcolors))]
	## fill result array with stuff so elements can be placed at randomized indexes
	matches = [x for x in randomized_indexes]
	random.shuffle(randomized_indexes)
	i = 1
	for x in randomized_indexes:
		progress(i, len(targetcolors), 'find matching images...')
		if targetcolors[x] != (255, 0, 255):
			good_image_index = get_index_closest_color(targetcolors[x], piccolors)
			## using pop so images won't appear multiple times
			matches[x] = piclist.pop(good_image_index)
			piccolors.pop(good_image_index)
		else:
			matches[x] = None
		i += 1
	print()

	stitched = None
	for y in range(images_per_line):
		row = None
		progress(y + 1, images_per_line, 'stitching...')
		for x in range(images_per_line):
			firstinrow = y * images_per_line
			match = matches[firstinrow + x]
			if not match:
				continue
			mini_img = Image.open(match)
			row = mini_img if not row else get_concat_x(row, mini_img)
		if row:
			stitched = row if not stitched else get_concat_y(stitched, row)
	print()

	print('saving stitched image...')
	stitched.save(stitched_out_path)
	return stitched


def main():
	version = 'v1.1'
	description = f'Mosaic Image Generator {version}'
	print(f'Welcome to {description}')
	parser = argparse.ArgumentParser(description=description)
	parser.add_argument('src_dir', type=str,
						help="directory with a lot of images")
	parser.add_argument('src_pic', type=str,
						help="the image that will be recreated with small images")
	parser.add_argument('-w', '--width', type=int, default=256,
						help="the width of individual images of the mosaic in pixels (default: 256)")
	parser.add_argument('-n', '--number', type=int, default=32,
						help="number of images per row of the mosaic (default: 32)")
	parser.add_argument('-o', '--out_pic', type=str,
						help="the path of the generated mosaic (default: '[src_pic]_[src_dir]_{n}x{w}.png')")
	args = parser.parse_args()

	source_path = f'{args.src_dir}_normal_{args.width}'
	if not args.out_pic:
		args.out_pic = f'{os.path.splitext(args.src_pic)[0]}_{args.src_dir.split(os.path.sep)[-1]}_{args.number}x{args.width}.png'
	if os.path.splitext(args.out_pic)[1].lower() not in ['.jpg', '.png', '.jpeg']:
		args.out_pic += '.png'

	print('scanning image directory...')
	if len(get_imglist(args.src_dir)) < args.number ** 2:
		print(f'There are not enough images in {args.src_dir}')
		print(f'for a {args.number} by {args.number} mosaic.')
		exit()
	if not os.path.exists(source_path):
		normalize_images(args.src_dir, source_path, args.width)
		print()

	mosaic(args.src_pic, args.out_pic, source_path, args.number)


if __name__ == '__main__':
	main()
