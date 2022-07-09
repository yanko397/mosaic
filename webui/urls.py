from django.urls import path

from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('login/', views.login, name='login'),
	path('<int:lel>/create/', views.create, name='create'),
	path('show/', views.show_imgs, name='show'),
]
