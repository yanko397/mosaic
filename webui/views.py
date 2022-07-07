from django.shortcuts import render
from django.http import HttpResponse


def index(request):
	return HttpResponse("Ja lol ey du bist beim webui index!")

