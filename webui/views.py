from django.shortcuts import render
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
	return render(request, 'webui/show/index.html', context)

