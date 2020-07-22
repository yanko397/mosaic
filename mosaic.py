import os
import sys
from PIL import Image
from random import shuffle
import numpy as np
import argparse
import ast

import time
current_time_milli = lambda: int(round(time.time() * 1000))
current_time_micro = lambda: int(round(time.time() * 1000000))


def progress(count, total, status=''):
	bar_len = 40
	filled_len = int(round(bar_len * count / float(total)))
	percents = round(100.0 * count / float(total), 1)
	bar = '#' * filled_len + '-' * (bar_len - filled_len)
	sys.stdout.write('[%s] %s%s %s\r' % (bar, percents, '%', status))
	sys.stdout.flush()


def squarify(img, size):
	if img.size[0] < img.size[1]:
		img = img.resize((size, int(size*max(img.size)/min(img.size)))) # this takes about 12 times longer than img.crop
		img = img.crop((0, (max(img.size)-size)/2, size, (max(img.size)-size)/2+size))
	elif img.size[0] > img.size[1]:
		img = img.resize((int(size*max(img.size)/min(img.size)), size))
		img = img.crop(((max(img.size)-size)/2, 0, (max(img.size)-size)/2+size, size))
	else:
		img = img.resize((size, size))
	return img


def normalize_images(indir, outdir, normal_size, mode='crop'): # TODO mode (crop/fill)
	piclist = get_imglist(indir)
	ensure_dir(outdir)
	for x in range(len(piclist)):
		progress(x, len(piclist), 'copying and resizing images..')
		outfile = os.path.join(outdir, f'pic{x}.jpg')
		if not os.path.exists(outfile):
			try:
				img = Image.open(piclist[x])
				if img.mode != 'RGB':
					img = img.convert('RGB')
				img = squarify(img, normal_size) # this takes about 10 times longer than img.save
				img.save(outfile)
			except OSError:
				print(f'Skipping broken image: {piclist[x]}...                ')
	print()


def ensure_dir(path):
	if not os.path.exists(path):
		os.makedirs(path)


def get_imglist(path):
	infiles = []
	for x in os.listdir(path):
		if os.path.splitext(x)[1] in ['.png','.jpg']:
			infiles.append(os.path.join(path, x))
	return infiles


def get_index_closest_color(color, colors):
	color = np.array(color)
	colors = np.array(colors)
	distances = np.sqrt(np.sum((colors-color)**2, axis=1))
	index_of_smallest = np.where(distances==np.amin(distances))
	return int(index_of_smallest[0][0])


def get_image_average(img):
	# stride = int(img.size[0]+(img.size[0]/8))-1
	points = min(img.size[0]**2, 231)
	stride = int(img.size[0]**2 / points)
	average = np.mean(list(img.getdata())[::stride], axis=0)
	return tuple(np.floor(average).astype('int'))


def get_concat_x(im1, im2):
	dst = Image.new('RGB', (im1.width+im2.width, im1.height))
	dst.paste(im1, (0, 0))
	dst.paste(im2, (im1.width, 0))
	return dst


def get_concat_y(im1, im2):
	dst = Image.new('RGB', (im1.width, im1.height+im2.height))
	dst.paste(im1, (0, 0))
	dst.paste(im2, (0, im1.height))
	return dst


def save_average_colors(path, colors):
	file = open(path, 'w')
	for color in colors:
		file.write(f'{str(color)}\n')


def read_average_colors(path):
	colors = []
	for color in open(path):
		colors.append(ast.literal_eval(color))
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
		piccolors = []
		for x in range(len(piclist)):
			progress(x+1, len(piclist), 'calc average colors...')
			piccolors.append(get_image_average(Image.open(piclist[x])))
		print()
		save_average_colors(average_color_f, piccolors)

	## strink target image to squared image of size (images_per_line, images_per_line)
	## then put the colors into a list
	targetcolors = list(squarify(Image.open(original_image_path), size=images_per_line).getdata())

	randomized_indexes = [x for x in range(len(targetcolors))]
	## fill result array with stuff so elements can be placed at randomized indexes
	matches = [x for x in randomized_indexes]
	shuffle(randomized_indexes)
	i = 1
	for x in randomized_indexes:
		progress(i, len(targetcolors), 'find matching imgs...')
		good_image_index = get_index_closest_color(targetcolors[x], piccolors)
		## using pop so images won't appear multiple times
		matches[x] = piclist.pop(good_image_index)
		piccolors.pop(good_image_index)
		i += 1
	print()

	stitched = None
	for y in range(images_per_line):
		row = None
		progress(y+1, images_per_line, 'stitching...')
		for x in range(images_per_line):
			firstinrow = y*images_per_line
			if x == 0:
				row = Image.open(matches[firstinrow])
			else:
				row = get_concat_x(row, Image.open(matches[firstinrow+x]))
		if y == 0:
			stitched = row
		else:
			stitched = get_concat_y(stitched, row)
	print()

	print('saving stitched image...')
	stitched.save(stitched_out_path)
	return stitched


def main():
	parser = argparse.ArgumentParser(description='Mosaic Image Generator v1.0')
	parser.add_argument('src_dir', type=str, help="directory with a lot of images")
	parser.add_argument('src_pic', type=str, help="the image that will be recreated with small images")
	parser.add_argument('-w', '--width', type=int, default=256, help="the width of individual images of the mosaic in pixels (default: 256)")
	parser.add_argument('-n', '--number', type=int, default=32, help="number of images per row of the mosaic (default: 32)")
	parser.add_argument('-o', '--out_pic', type=str, help="the path of the generated mosaic (default: 'mosaic_{n}x{w}.jpg')")
	args = parser.parse_args()

	source_path = f'{args.src_dir}_normal_{args.width}'
	if not args.out_pic:
		args.out_pic = f'mosaic_{args.number}x{args.width}.jpg'
	if os.path.splitext(args.out_pic) not in ['.jpg', '.png']:
		args.out_pic += '.jpg'

	if len(get_imglist(args.src_dir)) < args.number**2:
		print(f'There are not enough images in {args.src_dir}')
		print(f'for a {args.number} by {args.number} mosaic.')
		exit()
	if not os.path.exists(source_path):
		normalize_images(args.src_dir, source_path, args.width)

	mosaic(args.src_pic, args.out_pic, source_path, args.number)


if __name__ == '__main__':
	main()
