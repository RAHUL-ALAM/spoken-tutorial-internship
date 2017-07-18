# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from reg_log.models import organiser, userprofile, OrganiserHandover, college
from .models import DeptOrg, MasterBatch, CSV_list, Student, Training, Depertment, Foss, StudentLog
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .forms import Training_Request_Form, add_participants_form, edit_training_form, edit_student_form
from .forms import Training_Request_Form_File, use_existing_csv_form_final
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import simplejson
import csv
import os
import random
from datetime import datetime


# this view is for training planner
# it takes status as a parameter which is empty by default
# but when this view is called after successful creation of a training with no errors then status parameter is set to 
# "success". It helps to so us a success message on that page
@login_required(login_url='/login/')
def training_planner(request, status=''):
	if organiser.objects.filter(user=request.user).exists():
		requested_organiser = organiser.objects.get(user=request.user)
		if requested_organiser.status==1 or requested_organiser.status==3:
			context = {}
			context['trainings'] = Training.objects.filter(this_organiser=requested_organiser)
			trainings_handedover = []
			trainings = Training.objects.exclude(this_organiser=organiser.objects.get(user=request.user))
			for training in trainings:
				if requested_organiser in training.handedoverto.all():
					trainings_handedover.append(training)
			context['trainings_handedover'] = trainings_handedover
			
			if status=='success':
				messages.success(request, 'Training is created')
				return render(request,'TRAINING/training_planner.html',context)
			if status=='deleted':
				messages.success(request, 'Training is deleted')
				return render(request,'TRAINING/training_planner.html',context)
			if status=='edited':
				messages.success(request, 'Training is edited')
				return render(request,'TRAINING/training_planner.html',context)
			if status=='participantsAdded':
				messages.success(request, 'Participants added to Training')
				return render(request,'TRAINING/training_planner.html',context)
			else:
				return render(request,'TRAINING/training_planner.html',context)
		else:
			return HttpResponse('<h1 style="color:red; text-align:center;"\>You don\'t have access to this webpage</h1>')
	else:
		return HttpResponse('<h1 style="color:red; text-align:center;"\>You don\'t have access to this webpage</h1>')


# this view is to show all participant list
# it takes csv_id as parameter 
# we can get the csv associated with that id
# then we will check if the csv is present in any student's csv field. If present the the student is part of this training
# we will check for all student present in this database
@login_required(login_url='/login/')
def training_participant_list(request, csv_id):
	if organiser.objects.filter(user=request.user).exists():
		if organiser.objects.get(user=request.user).status==1:
			csv = CSV_list.objects.get(id=csv_id)
			students = Student.objects.all()
			participants = []
			for student in students:
				if csv in student.csv.all():
					gender = userprofile.objects.get(user=student.user).gender
					student.gender = gender
					participants.append(student)

			# gender = userprofile.objects.get(csv_id=csv_id)

			return render(request,'TRAINING/participant_list.html',{'participants':participants})

		else:
			return HttpResponse('<h1 style="color:red; text-align:center;"\>You don\'t have access to this webpage</h1>')
	else:
		return HttpResponse('<h1 style="color:red; text-align:center;"\>You don\'t have access to this webpage</h1>')


# This function will take email as argument and return True if email is valid els eit will return False
# we have used django's pre-made validate_email function inside this function
def email_validate(email):
    if email and email.strip():
    	email = email.strip().lower()
      	try:
        	validate_email(email)
        	return True
      	except:
        	pass
        return False
    return False


# This function will do some  necessary csv validation
# This function will return some list that contains the row having errors in the csv
# and also returns some list contains the ineligible students
def csv_validate(reader, foss):
	less_cols = []                      # contains row having less columns
	more_cols = []						# contains row having more columns
	wrong_email = []                    # contains row having invalid email_address
	invalid_gender = []					# contains row having not a valod gender
	email_registered = []				# contains the row which have already registered email_address
	done_this_foss = []                 # contains row having email_address already associated with the foss
	foss_time = []                      # contains the training_date in order if already done the foss 
	training_limit_exceeded = []        # contains row in which user exceeded the training_limit 

	i=1
	for row in reader:
		if  len(row) <4:
			less_cols.append(row)
			i = i+1
			continue
		if len(row) >4:
			more_cols.append(row)
			i = i+1
			continue
		if not email_validate(row[2]):
			wrong_email.append(row)
			i = i+1
			continue
		if row[3].lower() not in ['m','male','f','female']:
			invalid_gender.append(row)
			i=i+1
			continue

		#if email exists
		if User.objects.filter(email=row[2]).exists():
			email_registered.append(row)
			# get all training for this foss
			trainings = Training.objects.filter(foss=Foss.objects.get(id=int(foss)))
			csvs =Student.objects.get(user=User.objects.get(email=row[2])).csv.all()
			# for all filtered training check if csv of training is in th list of the student's csv
			for training in trainings:
				if training.csv in csvs:
					done_this_foss.append(row)
					foss_time.append(training.start_date)
					break
			i=i+1
			continue

		i=i+1

	return less_cols,more_cols,wrong_email,invalid_gender,email_registered,done_this_foss,training_limit_exceeded,foss_time


# function to create a user and return the user object
def create_user(row):
	user_object = User()
	user_object.first_name = row[0]
	user_object.last_name = row[1]
	user_object.email = row[2]
	user_object.username = row[2]
	# generating passowrd automatically
	user_object.set_password(random.choice(row[0])+str(random.randint(0,9))+random.choice(row[2]+row[0])+
		random.choice(row[1])+str(random.randint(100,999))+ random.choice(row[2]))
	user_object.save()
	userprofile_object = userprofile()
	userprofile_object.user = user_object
	userprofile_object.gender = row[3].upper()[0]
	userprofile_object.is_staff = False
	userprofile_object.is_active = True
	userprofile_object.save()

	return user_object

# function to create a student
def create_student(row, user, csv_object, dept):
	student_object = Student()
	student_object.user = user
	student_object.status = True
	student_object.save()
	student_object.csv.add(csv_object)

	d = StudentLog()
	d.student = student_object
	d.college = csv_object.masterbatch.college
	d.depertment = dept
	d.is_active = True
	d.save()


# this view is for creating new training
@login_required(login_url='/login/')
def training_request(request):
	
	form = Training_Request_Form(request.POST or None)
	fileform = Training_Request_Form_File(request.POST or None, request.FILES or None)
	all_dept = DeptOrg.objects.filter(org=request.user)

	if request.method=="POST":
		if form.is_valid() and fileform.is_valid():
			csv_object = CSV_list()
			csv_object.masterbatch = MasterBatch.objects.get(college=organiser.objects.get(user=request.user).collage)
			csv_object.save()

	  		reader = csv.reader(request.FILES['csv_file'])
	  		less_cols,more_cols,wrong_email,invalid_gender,email_registered,done_this_foss,training_limit_exceeded, \
	  		foss_time = csv_validate(reader, form.cleaned_data['foss'])

	  		# this will contain rows if in csv some rows have same email
	  		email_repeated_in_csv = []

	  		# e is a counter to count no of errors
	  		e=0   
	  		reader = csv.reader(request.FILES['csv_file'])

	  		# here based on check user and student will be created
	  		for i in reader:
	  			if not (i in less_cols or i in more_cols or i in wrong_email or i in invalid_gender):
	  				if not i in email_registered:
	  					if not User.objects.filter(email=i[2]).exists():
			  				user = create_user(i)
			  				create_student(i, user, csv_object, Depertment.objects.get(id=int(form.cleaned_data['dept'])))
			  			else:
			  				email_repeated_in_csv.append(i)
			  				e+=1
		  			else:
		  				if not i in done_this_foss:
		  					Student.objects.get(user=User.objects.get(email=i[2])).csv.add(csv_object)
		  				else:
		  					e+=1
	  			else:
	  				e+=1

	  		if e==0:
	  			all_correct=True
	  		else:
	  			all_correct=False

	  		# creating a training 
  			training_object = Training()
  			training_object.this_organiser = organiser.objects.get(user=request.user)
  			training_object.depertment = Depertment.objects.get(id=int(form.cleaned_data['dept'])) 
  			training_object.csv = csv_object
  			training_object.foss = Foss.objects.get(id=int(form.cleaned_data['foss']))
  			training_object.start_date = form.cleaned_data['start_date']
  			training_object.save()

	  		context={}
	  		context['less_cols']=less_cols
	  		context['more_cols']=more_cols
	  		context['wrong_email']=wrong_email
	  		context['invalid_gender']=invalid_gender
	  		context['email_repeated_in_csv']=email_repeated_in_csv

	  		i=0
	  		for row in done_this_foss:
	  			row.append(foss_time[i])
	  			i=i+1
	  		context['done_this_foss']=done_this_foss

	  		# no error redirect to training planner else show the error page
	  		if all_correct:
	  			return redirect(training_planner, 'success')
	  		else:
	  			messages.success(request, 'Training is created')
	  			return render(request,'TRAINING/training_request_success.html',context)

	return render(request,'TRAINING/training_request.html',{'form':form , 'fileform':fileform, 'all_dept':all_dept})



# if organiser uses existing csv then this is the 1st view to be used
# this will send all college csvs to the user
@login_required(login_url='/login/')
def use_existing_csv(request):
	if request.method=="POST":
		form = Training_Request_Form(request.POST or None)
		if form.is_valid():
			dept = Depertment.objects.get(id=int(form.cleaned_data['dept']))
			date = form.cleaned_data['start_date']
			foss = Foss.objects.get(id=int(form.cleaned_data['foss']))

			organiser_college = organiser.objects.get(user=request.user).collage
			college_masterbatch = MasterBatch.objects.get(college=organiser_college)
			csvs = CSV_list.objects.filter(masterbatch=college_masterbatch)

			for csv in csvs:
				if Training.objects.filter(csv=csv).exists():
					training = Training.objects.get(csv=csv)
					csv.training=training

			context={}
			context['csvs']=csvs
			context['dept']=dept
			context['date']=date.strftime('%Y-%m-%d')
			context['foss']=foss

			return render(request,'TRAINING/use_existing_csv.html',context)

	return redirect(training_request)


# this will send all student in that csv to the the next page
@login_required(login_url='/login/')
def use_existing_csv_step_2(request):
	if request.method=="POST":
		dept = request.POST['dept']
		date = request.POST['date']
		foss = request.POST['foss']
		csv = CSV_list.objects.get(id=int(request.POST['choose-csv']))

		participants=[]
		students = Student.objects.all()
		for student in students:
			if csv in student.csv.all():
				participants.append(student)

		context={}
		context['dept']=dept
		context['date']=date
		context['foss']=foss
		context['participants']=participants
		context['form']=use_existing_csv_form_final()

		return render(request,'TRAINING/use_existing_csv_2.html',context)

	return redirect(training_request)


# this view will check all students if they have already done this foss or not
@login_required(login_url='/login/')
def use_existing_csv_step_3(request):
	if request.method=="POST":
		dept = request.POST['dept']
		date = request.POST['date']
		foss = request.POST['foss']

		form = use_existing_csv_form_final(request.POST or None)
		if form.is_valid():
			# create csv
			organiser_college = organiser.objects.get(user=request.user).collage
			college_masterbatch = MasterBatch.objects.get(college=organiser_college)
			csv_object=CSV_list()
			csv_object.masterbatch = college_masterbatch
			csv_object.save()

			# add csv to student csv_field
			requested_organiser = organiser.objects.get(user=request.user)
			trainings = Training.objects.filter(foss=Foss.objects.get(name=foss), this_organiser= requested_organiser)
			participants = form.cleaned_data['participants']
			done_this_foss = []
			for participant in participants:
				student = Student.objects.get(id=int(participant))
				csvs = student.csv.all()
				count = 0
				for training in trainings:
					# checking if students have done this foss
					if training.csv in csvs:
						count += 1
						l = [student.user.first_name,student.user.last_name, student.user.email]
						l.append(userprofile.objects.get(user=student.user).gender)
						l.append(training.start_date)
						done_this_foss.append(l)
						break
				if count==0:
					student.csv.add(csv_object)

			# create training
			training_object = Training()
  			training_object.this_organiser = organiser.objects.get(user=request.user)
  			training_object.depertment = Depertment.objects.get(name=dept) 
  			training_object.csv = csv_object
  			training_object.foss = Foss.objects.get(name=foss)
  			training_object.start_date = date
  			training_object.save()

  			# redirect
  			if len(done_this_foss)==0:
  				return redirect(training_planner, 'success')
  			# show error
  			else:
  				messages.success(request, 'Training is created')
	  			return render(request,'TRAINING/training_request_success.html',{'done_this_foss':done_this_foss})


	return redirect(training_request)


# simply delete the training
def delete_training(request, training_id):
	training = Training.objects.get(id=training_id)
	training.delete()

	return redirect(training_planner, 'deleted')


# edit the training
# if foss is changed then it checks if the existing students have done that foss or not 
# if they did already they are removed
def edit_training(request, training_id):
	form = edit_training_form(request.POST or None)
	all_dept = DeptOrg.objects.filter(org=request.user)
	training = Training.objects.get(id=training_id)
	context = {}
	context['form']=form
	context['all_dept']=all_dept
	context['current_dept']=training.depertment
	context['current_date']=training.start_date.strftime('%Y-%m-%d')
	context['current_foss']=training.foss

	if request.method=="POST":
		if form.is_valid():
			training.depertment = Depertment.objects.get(id=int(form.cleaned_data['dept']))
			old_date = training.start_date
			training.start_date = form.cleaned_data['start_date']
			training.foss = Foss.objects.get(id=int(form.cleaned_data['foss']))

			removed = []
			csv = training.csv
			this_foss_trainings = Training.objects.filter(foss=training.foss)
			students = Student.objects.all()
			for student in students:
				if csv in student.csv.all():
					for i in this_foss_trainings:
						if i.csv in student.csv.all():
							student.csv.remove(csv)
							l = [student.user.first_name,student.user.last_name, student.user.email]
							l.append(userprofile.objects.get(user=student.user).gender)
							l.append(old_date)
							removed.append(l)

			training.save()
			if len(removed)==0:
				return redirect(training_planner, 'edited')
			else:
				messages.success(request, 'Training edited successfully')
				return render(request,'TRAINING/edit_training_success.html',{'removed':removed})

	return render(request,'TRAINING/edit_training.html',context)


# add participants with same validation as create new training 
def add_participants(request, training_id):
	form = add_participants_form(request.POST or None, request.FILES or None)
	if request.method=="POST":
		if form.is_valid():
			training = Training.objects.get(id=training_id)
			reader = csv.reader(request.FILES['csv_file'])
			less_cols,more_cols,wrong_email,invalid_gender,email_registered,done_this_foss,training_limit_exceeded, \
	  		foss_time = csv_validate(reader, training.foss.id)

	  		error_count = 0
	  		reader = csv.reader(request.FILES['csv_file'])
	  		for i in reader:
	  			if not (i in less_cols or i in more_cols or i in wrong_email or i in invalid_gender):
	  				if not i in email_registered:
		  				user = create_user(i)
		  				create_student(i, user, training.csv)
		  			else:
		  				if not i in done_this_foss:
		  					Student.objects.get(user=User.objects.get(email=i[2])).csv.add(training.csv)
		  				else:
		  					error_count += 1
	  			else:
	  				error_count += 1

	  		context={}
	  		context['less_cols']=less_cols
	  		context['more_cols']=more_cols
	  		context['wrong_email']=wrong_email
	  		context['invalid_gender']=invalid_gender
	  		i=0
	  		for row in done_this_foss:
	  			row.append(foss_time[i])
	  			i=i+1
	  		context['done_this_foss']=done_this_foss

	  		if error_count==0:
	  			return redirect(training_planner, 'participantsAdded')
	  		else:
	  			messages.success(request, 'Participant added to this Training')
	  			return render(request,'TRAINING/training_request_success.html',context)

	return render(request,'TRAINING/add_participant.html',{'form':form})


# edit the students simply
# first checks if email is changed
# if yes then if changed email already exists 
def edit_student(request, csv_id, student_id):
	form = edit_student_form(request.POST or None)
	student = Student.objects.get(id=student_id)
	context = {}
	if request.method=="POST":
		if form.is_valid():
			user_to_change = User.objects.get(id=student.user.id)
			user_to_change.first_name = form.cleaned_data['first_name']
			user_to_change.last_name = form.cleaned_data['last_name']
			user_to_change_profile = userprofile.objects.get(user=student.user)
			user_to_change_profile.gender = form.cleaned_data['gender']

			if form.cleaned_data['email'] != user_to_change.email:
				if(email_validate(form.cleaned_data['email'])):
					# checks if new email already exist is database or not
					if not User.objects.filter(email=form.cleaned_data['email']).exists():
						user_to_change.email = form.cleaned_data['email']
						user_to_change.save()
						user_to_change_profile.save()

					else:
						context['err1'] = "This email already exists"
				else:
					context['err2']= "This email is invalid"

			changed_dept = Depertment.objects.get(id=int(form.cleaned_data['dept']))
			studentlog_instance = StudentLog.objects.get(student=student, is_active=True)
			current_dept = studentlog_instance.depertment

			if current_dept != changed_dept:
				studentlog_instance.is_active = False
				studentlog_instance.save()
				s = StudentLog()
				s.student = student
				s.depertment = changed_dept
				s.college = studentlog_instance.college
				s.is_active = True
				s.save()

			return redirect(training_participant_list, csv_id)

	student.gender = userprofile.objects.get(user=student.user).gender
	student.dept = StudentLog.objects.get(student=student, is_active=True).depertment
	context['form']=form
	context['student']=student
	return render(request,'TRAINING/edit_student.html',context)


@login_required(login_url='/login/')
def student_dashboard(request):
	if Student.objects.filter(user=request.user).exists():
		context = {}
		context['current'] = []
		context['upcoming'] = []

		student = Student.objects.get(user=request.user)
		context['student'] = student

		trainings = Training.objects.all()
		for training in trainings:
			if training.csv in student.csv.all():
				current_date = datetime.date(datetime.now())
				if current_date<training.start_date:
					context['upcoming'].append(training)
				elif current_date >= training.start_date:
					context['current'].append(training)

		context['current_clg'] = StudentLog.objects.get(student=student, is_active=True)
		context['past_clg'] = StudentLog.objects.filter(student=student, is_active=False)

		context['colleges'] = college.objects.all()
		context['departments'] = Depertment.objects.all()

		return render(request, 'TRAINING/student_dashboard.html', context)




def edit_profile_by_student(request):
	if request.method == "POST":
		user_to_change = User.objects.get(id=request.user.id)
		user_to_change.first_name = request.POST['fname']
		user_to_change.last_name = request.POST['lname']

		if request.POST['email'] != user_to_change.email:
			if(email_validate(request.POST['email'])):
				# checks if new email already exist is database or not
				if not User.objects.filter(email=request.POST['email']).exists():
					user_to_change.email = request.POST['email']
				else:
					context['err1'] = "This email already exists"
			else:
				context['err2']= "This email is invalid"
					
		user_to_change.save()

		return redirect(student_dashboard)




def edit_academic_info_by_student(request):
	if request.method == "POST":
		student = Student.objects.get(user=request.user)
		studentlog_to_change = StudentLog.objects.get(student=student, is_active=True)
		studentlog_to_change.is_active = False
		studentlog_to_change.save()

		new_studentlog_object = StudentLog()
		new_studentlog_object.student = student
		new_studentlog_object.college = college.objects.get(id=int(request.POST['clg']))
		new_studentlog_object.depertment = Depertment.objects.get(id=request.POST['dept'])
		new_studentlog_object.is_active = True
		new_studentlog_object.save()

		return redirect(student_dashboard)


