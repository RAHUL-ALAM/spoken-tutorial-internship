# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from reg_log.models import college, organiser
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import datetime

class MasterBatch(models.Model):
	
	college = models.ForeignKey(college, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.college.clg_name)

class CSV_list(models.Model):

	masterbatch = models.ForeignKey(MasterBatch, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.id)+'-'+str(self.masterbatch.id)

class Depertment(models.Model):
	
	name = models.CharField(max_length=128)

	def __str__(self):
		return (self.name)

class Student(models.Model):

	user = models.ForeignKey(User, on_delete=models.CASCADE)
	csv = models.ManyToManyField(CSV_list)
	status = models.BooleanField(default=False)

	def __str__(self):
		return str(self.user.first_name)+'-'+str(self.user.last_name)

class DeptStudent(models.Model):
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	depertment = models.ForeignKey(Depertment, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.student.user.first_name)+'-'+str(self.student.user.last_name)+'-'+str(self.depertment.name)



class DeptOrg(models.Model):

	org = models.ForeignKey(User, on_delete=models.CASCADE)
	dept = models.ForeignKey(Depertment, on_delete=models.CASCADE)
	college = models.ForeignKey(college, on_delete=models.CASCADE)
	
	def __str__(self):
		return str(self.org.username)+'-'+str(self.dept.name)
		
		

class Category(models.Model):

	name = models.CharField(max_length=64)
	
	def __str__(self):
		return str(self.name)

class Foss(models.Model):
	
	name = models.CharField(max_length=64)
	category = models.ForeignKey(Category, on_delete=models.CASCADE)
	with_exam = models.BooleanField(default=True)
	available_for_training = models.BooleanField(default=True)

	def __str__(self):
		return str(self.name)

class Training(models.Model):

	this_organiser = models.ForeignKey(organiser, on_delete=models.CASCADE)
	depertment  = models.ForeignKey(Depertment, on_delete=models.CASCADE)
	csv = models.ForeignKey(CSV_list, on_delete=models.CASCADE)
	foss = models.ForeignKey(Foss, on_delete=models.CASCADE)
	start_date = models.DateField()
	handedoverto = models.ManyToManyField(organiser, blank=True, related_name = 'training_handed_over_to')

	def __str__(self):
		return str(self.this_organiser.user.username)+'-'+str(self.foss.name)
