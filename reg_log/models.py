# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import datetime


#Choices for gender of the person
GENDER_CHOICES = (
    ('M', "Male"),
    ('F', "Female"),
    ('O', "Others")
)

# extending the existing user model to save some necessary information about user
# for training manager both is_staff and is_active is true
# for students is_active is false by default and will be true after some verification
class userprofile(models.Model):

	user = models.OneToOneField(User, on_delete=models.CASCADE)
	gender = models.CharField(choices=GENDER_CHOICES,default='M',max_length=1)
	phn = models.BigIntegerField(null=True)
	is_active = models.BooleanField(default=False)             
	is_staff = models.BooleanField(default=False)              

	def __str__(self):
		return str(self.user.username)



# model for saving state
# manually saved to the database
# each state will have one training manager
class state(models.Model):

	name = models.CharField(max_length=128)
	code = models.CharField(max_length=32)
	training_manager = models.ForeignKey(User, on_delete=models.CASCADE)
	created = models.DateTimeField(auto_now_add = True, null=True)
  	updated = models.DateTimeField(auto_now = True, null=True)

	def __str__(self):
		return str(self.name)



#model for district
#manually saved to the database
class district(models.Model):

	name = models.CharField(max_length=128)
	state = models.ForeignKey(state, on_delete=models.CASCADE)
	code = models.CharField(max_length=32)
	created = models.DateTimeField(auto_now_add = True, null=True)
  	updated = models.DateTimeField(auto_now = True, null=True)

	def __str__(self):
		return str(self.name)


#model for city
#manually saved to the database
class city(models.Model):

	name = models.CharField(max_length=128)
	district = models.ForeignKey(district, on_delete=models.CASCADE)
	code = models.CharField(max_length=32)
	pincode = models.IntegerField()
	created = models.DateTimeField(auto_now_add = True, null=True)
  	updated = models.DateTimeField(auto_now = True, null=True)

	def __str__(self):
		return str(self.name)


# model for colleges of each state
# saved to the database by training manager through addInstiForm
# code will be generated by backend algorithm and it'll be unique
# status will be 0 or 1 based on input in form
class college(models.Model):

	clg_name = models.CharField(max_length=256)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE)      #created_by some training manager
	state = models.ForeignKey(state, on_delete=models.CASCADE)
	district = models.ForeignKey(district, on_delete=models.CASCADE)
	city = models.ForeignKey(city, on_delete=models.CASCADE)
	code = models.CharField(max_length=32)
	address = models.CharField(max_length=256, null=True)
	pincode = models.IntegerField()
	created = models.DateTimeField(auto_now_add = True, null=True)
  	updated = models.DateTimeField(auto_now = True, null=True)
  	status = models.BooleanField(default=False)

	def __str__(self):
		return str(self.clg_name)



# model to save details of organiser
# approved_by some training manager
# status will be 0 by default, 1 if accepted and 2 if rejected
class organiser(models.Model):

	user = models.OneToOneField(User, on_delete=models.CASCADE)
	collage = models.ForeignKey(college, on_delete=models.CASCADE)
	approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'organiser_approved_by', null=True)   
	status = models.PositiveSmallIntegerField(default=0)
	created = models.DateTimeField(auto_now_add = True, null=True)
  	updated = models.DateTimeField(auto_now = True, null=True)

	def __str__(self):
		return str(self.user.username)



class OrganiserHandover(models.Model):

	handedoverfrom = models.ForeignKey(organiser, on_delete=models.CASCADE)
	handedoverto = models.ForeignKey(organiser, on_delete=models.CASCADE, related_name = 'organiser_handed_over_to')
	handedoveron = models.DateTimeField(auto_now_add = True, null=True)
	status = models.PositiveSmallIntegerField(default=0)

	def __str__(self):
		return str(self.handedoverfrom.user.username) + 'to' + str(self.handedoverto.user.username)