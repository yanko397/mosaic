from datetime import datetime
from pyexpat import model
from statistics import mode
from django.db import models
from pyrsistent import optional
from datetime import datetime


# class User(models.Model):
# 	name = models.CharField(max_length=100)
# 	user_key = models.CharField(max_length=100)
# 	email = models.CharField(max_length=100, default='')


class Mosaic(models.Model):
	# owner = models.ForeignKey(User, on_delete=models.CASCADE)
	image_path = models.CharField(max_length=200, default='')

	created = models.DateTimeField(auto_now_add=True)
	finished = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.image_path

	def get_owner(self):
		return 'owner gibts noch nich xD'

