from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from .models import Mosaic


def index(request):
	return HttpResponse('Ja lol ey du bist beim webui index!')


def login(request):
	return HttpResponse('You can log in here')


def create(request, lel):
	return HttpResponse(f'You can create a mosaic here. Your param is btw {lel}')


def show_imgs(request):
	latest_mosaics = Mosaic.objects.order_by('-created')[:5]
	context = {
		'latest_mosaics': latest_mosaics,
	}
	return render(request, 'webui/show_imgs.html', context)

def show_img(request, img_id):
	img = get_object_or_404(Mosaic, pk=img_id);
	context = {
		'img': img.image_path,
	}
	return render(request, 'webui/show_img.html', context)

