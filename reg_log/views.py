# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from .forms import userRegForm, userExtendeForm, logForm, addorgForm, addInstiForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
# from django.core.mail import send_mail
# from django.core.exceptions import ValidationError
from .models import userprofile, organiser, college, state, district, city
import json
import simplejson


# view for homepage for each user
# if training_manager(is_staff=1) then render training manager homepage
# if organiser(user exists in organiser model) then render organiser homepage
# if authenticated user but none of above then go to normail user homepage
# if none of above render basic homepage 
def home(request):
	if request.user.is_authenticated():

		if userprofile.objects.get(user=request.user).is_staff:
			if request.method == "POST":
				i = college()
				i.clg_name = request.POST['clg_name']
				i.created_by = request.user
				i.state = state.objects.get(id=request.POST['state'])
				i.district = district.objects.get(id=request.POST['district'])
				i.city = city.objects.get(id=request.POST['city'])
				i.code = "354cw7f"
				i.address = request.POST['address']
				i.pincode = request.POST['pincode']
				if request.POST['status']=='on':
					i.status = True
				else:
					i.status = False
				i.save()
			return render(request,"reg_log/tm_dashboard.html",{'addInstiForm':addInstiForm()})

		if organiser.objects.filter(user=request.user).exists():
			return render(request,'reg_log/organiser_home.html',{'status': organiser.objects.get(user=request.user).status })

		if request.method == "POST":
			c = organiser()
			c.user = request.user
			c.collage = college.objects.get(id=int(request.POST['collage']))
			c.save()
			return redirect(home)
		org_form = addorgForm()
		return render(request,'reg_log/home.html',{'orgform':org_form})

	return render(request,'reg_log/home.html')




# for registration page
# verifies username, email, mobile no and then register the user and then redirect to normal user homepage
def registration(request):

	reg_form = userRegForm(request.POST or None)
	userex_form = userExtendeForm(request.POST or None)

	if request.method == "POST":
		# unique username,email,mobile no verifiction
		# checks if username, email or mobie no already exists
		if User.objects.filter(username=request.POST['username']).exists():
			return render(request,'reg_log/registration.html',{'reg_form':reg_form, 'userex_form':userex_form, 
				'uerr':"username already taken"})
		if User.objects.filter(email=request.POST['email']).exists():
			return render(request,'reg_log/registration.html',{'reg_form':reg_form, 'userex_form':userex_form, 
				'eerr':"email id already registered"})
		if userprofile.objects.filter(phn=request.POST['phn']).exists():
			return render(request,'reg_log/registration.html',{'reg_form':reg_form, 'userex_form':userex_form, 
				'perr':"mobile no already registered"})

		if reg_form.is_valid() and userex_form.is_valid():
			r = reg_form.save(commit=False)
			username = reg_form.cleaned_data['username']
			email = reg_form.cleaned_data['email']
			password1 = reg_form.cleaned_data['password']
			r.set_password(password1)
			r.save()
			phone = userex_form.cleaned_data['phn']
			u = userprofile()
			u.user = User.objects.get(username=username)			
			u.phn = phone
			u.save()
			user = authenticate(username=username,password=password1)
			login(request,user)
			return redirect(home)

	return render(request,'reg_log/registration.html',{'reg_form':reg_form, 'userex_form':userex_form})



# process the login
def logIn(request):
	if not request.user.is_authenticated():
		if request.method == "POST":
			form = logForm(request.POST)
			if form.is_valid():
				username = form.cleaned_data['username']
				password = form.cleaned_data['password']
				user = authenticate(username=username,password=password)

				if user is not None:
					login(request,user)
					return redirect(home)
				else:
					log_form = logForm()
					return render(request,'reg_log/login.html',{'log_form':log_form, 'err':"Invalid username or password"})

		log_form = logForm()
		return render(request,'reg_log/login.html',{'log_form':log_form})

	return redirect(home)




# this view is only for training manager
# this view is to show organiser all the list of organisers based on status
@login_required(login_url='/login/')
def organiser_list(request, status):
	states = state.objects.filter(training_manager=request.user)
	colleges = college.objects.filter(state__in=states)
	if status=="new":
		org_list = organiser.objects.filter(status=0, collage__in=college.objects.filter(state__in=states))
	if status=="current":
		org_list = organiser.objects.filter(status=1, collage__in=college.objects.filter(state__in=states))
	if status=="rejected":
		org_list = organiser.objects.filter(status=2, collage__in=college.objects.filter(state__in=states))



	return render(request,'reg_log/tm_organiserlist.html',{'states':states, 
		'colleges':colleges, 'organisers':org_list, 'status':str(status)})


# this view is only for training manager
# this view is to accept organiser request and redirect to same page
@login_required(login_url='/login/')
def organiser_request_accept(request, user_id, status):
	if userprofile.objects.get(user=request.user).is_staff == True:
		user = organiser.objects.get(user_id=user_id)
		user.status = 1
		user.approved_by = request.user
		user.save()
		return redirect(organiser_list, status)
		# states = state.objects.filter(training_manager=request.user)
		# colleges = college.objects.filter(state__in=states)
		# # org_list = organiser.objects.filter(status=status, collage__in=college.objects.filter(state__in=states))
		# if status=="new":
		# 	org_list = organiser.objects.filter(status=0, collage__in=college.objects.filter(state__in=states))
		# elif status=="current":
		# 	org_list = organiser.objects.filter(status=1, collage__in=college.objects.filter(state__in=states))
		# if status=="rejected":
		# 	org_list = organiser.objects.filter(status=2, collage__in=college.objects.filter(state__in=states))

		# return render(request,'reg_log/tm_organiserlist.html',{'states':states, 
		# 	'colleges':colleges, 'organisers':org_list, 'status':str(status)})




# this view is only for training manager
# this view is to reject organiser request and redirect to same page
@login_required(login_url='/login/')
def organiser_request_reject(request, user_id, status):
	if userprofile.objects.get(user=request.user).is_staff == True:
		user = organiser.objects.get(user_id=user_id)
		user.approved_by = request.user
		user.status = 2
		# user.approved_by = trainingManager.objects.filter(user=request.user).first()
		user.save()
		return redirect(organiser_list, status)



# calling through ajax
# showing colleges from a particular state
# this view has used in add organiser form and home view 
def ajax_college_state(request):
	state=request.POST["state"]
	data1=list(college.objects.filter(state=state))
	tmp = '<option value = "0"> Choose Institution </option>'
	if data1:
		for i in data1:
			tmp +='<option value='+str(i.id)+'>'+i.clg_name+'</option>'

	return HttpResponse(json.dumps(tmp), content_type="application/json")


# calling through ajax
# showing districts from a particular state
# this view has used in add institution form and **** view 
def ajax_state_district(request):
	state=request.POST["state"]
	data=list(district.objects.filter(state=state))
	tmp = '<option value = "0"> Select District </option>'
	if data:
		for i in data:
			tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
	return HttpResponse(json.dumps(tmp), content_type="application/json")


# calling through ajax
# showing cities from a particular district
# this view has used in add institution form and **** view 
def ajax_district_state(request):
	district=request.POST["district"]
	data=list(city.objects.filter(district=district))
	tmp = '<option value = "0"> Select City </option>'
	if data:
		for i in data:
			tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
	return HttpResponse(json.dumps(tmp), content_type="application/json")



# to filter results by state in training manager page to see list of organisers 
# view name organiser_list
def ajax_college_state_organiser_list(request,status):
	state=request.POST["state"]
	data1=list(college.objects.filter(state=state))
	tmp = '<option value = "0"> Choose Institution </option>'
	if data1:
		for i in data1:
			tmp +='<option value='+str(i.id)+'>'+i.clg_name+'</option>'

	tmp2=" "
	if status=="new":
		data2 = list(organiser.objects.filter(status=0, collage__in=college.objects.filter(state=state)))
	elif status=="current":
		data2 = list(organiser.objects.filter(status=1, collage__in=college.objects.filter(state=state)))
	elif status=="rejected":
		data2 = list(organiser.objects.filter(status=2, collage__in=college.objects.filter(state=state)))
	if data2 and status=="new":
		for i in data2:
			tmp2 += '<tr><td>'+str(i.user.username)+'</td><td>'+str(i.user.email)+'</td><td>'+str(i.collage)+'</td><td>'+str(i.collage.state)+'</td><td><a href="/organiser-request/accept/'+str(i.user_id)+'/">accept</a>&nbsp|&nbsp <a href="/organiser-request/reject/'+str(i.user_id)+'/">reject</a></td></tr>'
	else:
		for i in data2:
			tmp2 += '<tr><td>'+str(i.user.username)+'</td><td>'+str(i.user.email)+'</td><td>'+str(i.collage)+'</td><td>'+str(i.collage.state)+'</td><td>'+i.updated.strftime('%Y-%m-%d %H:%M')+'</td></tr>'
	return HttpResponse(simplejson.dumps({'tmp1':tmp, 'tmp2':tmp2}), content_type="application/json")



# to filter results by college in training manager page to see list of organisers 
# view name organiser_list
def ajax_college_organiser_list(request,status):
	clg = int(request.POST["college"])
	tmp = " "
	if status=="new":
		data = list(organiser.objects.filter(status=0, collage=college.objects.get(id=clg)))
	elif status=="current":
		data = list(organiser.objects.filter(status=1, collage=college.objects.get(id=clg)))
	elif status=="rejected":
		data = list(organiser.objects.filter(status=2, collage=college.objects.get(id=clg)))
	if data and status=="new":
		for i in data:
			tmp += '<tr><td>'+str(i.user.username)+'</td><td>'+str(i.user.email)+'</td><td>'+str(i.collage)+'</td><td>'+str(i.collage.state)+'</td><td><a href="organiser-request/accept/'+str(i.user_id)+'/">accept</a>&nbsp|&nbsp <a href="organiser-request/reject/'+str(i.user_id)+'/">reject</a></td></tr>'
	else:
		for i in data:
			tmp += '<tr><td>'+str(i.user.username)+'</td><td>'+str(i.user.email)+'</td><td>'+str(i.collage)+'</td><td>'+str(i.collage.state)+'</td><td>'+i.updated.strftime('%Y-%m-%d %H:%M')+'</td></tr>'

	return HttpResponse(simplejson.dumps(tmp), content_type="application/json")





# to reset the filters in training manager page to see list of organisers 
# view name organiser_list
def reset_organiser_list(request, status):
	states = state.objects.filter(training_manager=request.user)
	tmp = '<option value = "0"> Choose State </option>'
	if states:
		for i in states:
			tmp += '<option value='+str(i.id)+'>'+str(i.name)+'</option>'

	colleges = list(college.objects.filter(state__in=states))
	tmp2 = '<option value = "0"> Choose Institution </option>'
	if colleges:
		for i in colleges:
			tmp2 +='<option value='+str(i.id)+'>'+str(i.clg_name)+'</option>'

	tmp3 = " "
	if status=="new":
		data = list(organiser.objects.filter(status=0, collage__in=colleges))
	elif status=="current":
		data = list(organiser.objects.filter(status=1, collage__in=colleges))
	elif status=="rejected":
		data = list(organiser.objects.filter(status=2, collage__in=colleges))
	if data and status=="new":
		for i in data:
			tmp3 += '<tr><td>'+str(i.user.username)+'</td><td>'+str(i.user.email)+'</td><td>'+str(i.collage)+'</td><td>'+str(i.collage.state)+'</td><td><a href="organiser-request/accept/'+str(i.user_id)+'/">accept</a>&nbsp|&nbsp <a href="organiser-request/reject/'+str(i.user_id)+'/">reject</a></td></tr>'
	else:
		for i in data:
			tmp3 += '<tr><td>'+str(i.user.username)+'</td><td>'+str(i.user.email)+'</td><td>'+str(i.collage)+'</td><td>'+str(i.collage.state)+'</td><td>'+i.updated.strftime('%Y-%m-%d %H:%M')+'</td></tr>'

	return HttpResponse(simplejson.dumps({'states':tmp, 'colleges':tmp2, 'table':tmp3}), content_type="application/json")