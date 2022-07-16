from django.urls import path

from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('login/', views.login, name='login'),
	path('<int:lel>/create/', views.create, name='create'),
	path('show_imgs/', views.show_imgs, name='show_imgs'),
	path('<int:img_id>/show_img/', views.show_img, name='show_img'),
]
