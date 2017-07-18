# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from .forms import userRegForm, userExtendeForm, logForm, addorgForm, addInstiForm, OrgDeptForm
from TRAINING.models import DeptOrg, Depertment, MasterBatch, Training
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import userprofile, organiser, college, state, district, city, OrganiserHandover
import json
import simplejson


# view for homepage for each user
# redirecting to the homepage 
# homepage is common to all
def home(request):
	context = { }
	if request.user.is_authenticated():
		context['user'] = request.user
	return render(request, 'reg_log/home.html', context)



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
					return render(request,'reg_log/login.html',
						{'log_form':log_form, 'err':"Invalid username or password"})

		log_form = logForm()
		return render(request,'reg_log/login.html',{'log_form':log_form})

	return redirect(home)





# to the training dashboard
# page will be displayed based on who is the person
# views check the user is organiser or training manager
# if organisr then his status 
@login_required(login_url='/login/')
def training_dashboard(request):
	context = { }

	if userprofile.objects.get(user=request.user).is_staff:
		context['training_manager']=1

	if organiser.objects.filter(user=request.user).exists():
		requested_organiser = organiser.objects.get(user=request.user)
		if requested_organiser.status == 1:
			# this means he is a organsier
			context['organiser']=1       
			this_college = requested_organiser.collage
			context['organisers']=organiser.objects.filter(collage= this_college, status=1).exclude(user=request.user)
		elif requested_organiser.status == 2:
			context['organiser']=2     # this means his orhaniser requested rejected
		elif requested_organiser.status == 3:
			context['organiser']=3     # this means he heaned over his organiser request
		else:
			context['organiser']=4     # represented request neither approved nor rejected

		context['organiserhandoverfrom'] = OrganiserHandover.objects.filter(handedoverto=requested_organiser, status=0)
		context['organiserhandoverto'] = OrganiserHandover.objects.filter(handedoverfrom=requested_organiser)		

	else:
		context['organiser']=0         # not requested for organiser

	return render(request,'reg_log/training_dashboard.html', context)



# simple function normally renders a form
# if there is any post data then create a organiser and deptorg object
@login_required(login_url='/login/')
def request_for_organiser(request):
	addorgform = addorgForm(request.POST or None)
	if request.method == "POST":
		c = organiser()
		c.user = request.user
		c.collage = college.objects.get(id=int(request.POST['collage']))
		c.save()
		d = DeptOrg()
		d.org = request.user
		d.dept = Depertment.objects.get(id=int(request.POST['dept']))
		d.college = c.collage
		d.status = False
		d.save()
		return redirect(training_dashboard)
	
	return render(request,'reg_log/request_for_organiser.html',{'addorgForm':addorgform})



# helps organiser to add more departments under his supervision
@login_required(login_url='/login/')
def add_depertment(request):
	if request.user.is_authenticated():
		if organiser.objects.filter(user=request.user).exists():
			form = OrgDeptForm(request.POST or None)
			err = ""
			e = 0
			if request.method=="POST":
				dept_id = int(request.POST['dept'])
				if DeptOrg.objects.filter(college=organiser.objects.get(user=request.user).collage,
					dept=Depertment.objects.get(id=dept_id)).exists():
					err = "organiser of " + str(Depertment.objects.get(id=dept_id)) +" already exists in " + \
					str(organiser.objects.get(user=request.user).collage)
					e=e+1

				if e==0:
					c = DeptOrg()         # c is a deptorg object to save in database
					c.org = request.user
					c.dept = Depertment.objects.get(id=dept_id)
					c.college = organiser.objects.get(user=request.user).collage
					c.save()
					return redirect(training_dashboard)
			return render(request,'reg_log/add_department.html',{'adddeptform':form, 'err':err})

	return HttpResponse("You can't access this webpage")


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


# this view is only for training manager
# this view is to reject organiser request and redirect to same page
@login_required(login_url='/login/')
def organiser_request_reject(request, user_id, status):
	if userprofile.objects.get(user=request.user).is_staff == True:
		user = organiser.objects.get(user_id=user_id)
		user.approved_by = request.user
		user.status = 2
		user.save()
		return redirect(organiser_list, status)


@login_required(login_url='/login/')
def addInstitution(request):
	form = addInstiForm(request.POST or None)
	if request.method == "POST":
		i = college()                              # i is a college_object to save in database
		i.clg_name = request.POST['clg_name']
		i.created_by = request.user
		i.state = state.objects.get(id=request.POST['state'])
		i.district = district.objects.get(id=request.POST['district'])
		i.city = city.objects.get(id=request.POST['city'])
		count = college.objects.filter(clg_name=i.state).count()   # counting no of colleges in state
		state_code = i.state.code  
		i.code = str(state_code)+str(count+1)                      # generating code in daaatbase
		i.address = request.POST['address']
		i.pincode = request.POST['pincode']
		if request.POST['status']=='on':
			i.status = True
		else:
			i.status = False
		i.save()

		masterbatch_object = MasterBatch()              # auto-geenrating masterbatch fro college
		masterbatch_object.college = i 
		masterbatch_object.save()               
		return redirect(training_dashboard)
	return render(request, 'reg_log/addInstitution.html',{'addInstiForm':form})

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
			tmp2 += '<tr><td>'+str(i.user.username)+'</td><td>'+str(i.user.email)+'</td><td>'+str(i.collage)+ \
			'</td><td>'+str(i.collage.state)+'</td><td><a href="/organiser-request/accept/'+str(i.user_id)+ \
			'/">accept</a>&nbsp|&nbsp <a href="/organiser-request/reject/'+str(i.user_id)+'/">reject</a></td></tr>'
	else:
		for i in data2:
			tmp2 += '<tr><td>'+str(i.user.username)+'</td><td>'+str(i.user.email)+'</td><td>'+str(i.collage)+ \
			'</td><td>'+str(i.collage.state)+'</td><td>'+i.updated.strftime('%Y-%m-%d %H:%M')+'</td></tr>'
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
			tmp += '<tr><td>'+str(i.user.username)+'</td><td>'+str(i.user.email)+'</td><td>'+ \
			str(i.collage)+'</td><td>'+str(i.collage.state)+'</td><td><a href="organiser-request/accept/'+ \
			str(i.user_id)+'/">accept</a>&nbsp|&nbsp <a href="organiser-request/reject/'+str(i.user_id)+ \
			'/">reject</a></td></tr>'
	else:
		for i in data:
			tmp += '<tr><td>'+str(i.user.username)+'</td><td>'+str(i.user.email)+'</td><td>'+str(i.collage)+ \
			'</td><td>'+str(i.collage.state)+'</td><td>'+i.updated.strftime('%Y-%m-%d %H:%M')+'</td></tr>'

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
			tmp3 += '<tr><td>'+str(i.user.username)+'</td><td>'+str(i.user.email)+'</td><td>'+str(i.collage)+ \
			'</td><td>'+str(i.collage.state)+'</td><td><a href="organiser-request/accept/'+str(i.user_id)+ \
			'/">accept</a>&nbsp|&nbsp <a href="organiser-request/reject/'+str(i.user_id)+'/">reject</a></td></tr>'
	else:
		for i in data:
			tmp3 += '<tr><td>'+str(i.user.username)+'</td><td>'+str(i.user.email)+'</td><td>'+str(i.collage)+ \
			'</td><td>'+str(i.collage.state)+'</td><td>'+i.updated.strftime('%Y-%m-%d %H:%M')+'</td></tr>'

	return HttpResponse(simplejson.dumps(
		{'states':tmp, 'colleges':tmp2, 'table':tmp3}), content_type="application/json")





# to perform organiser handover
def organiser_handover(request):

	from_organiser = organiser.objects.get(user = request.user)
	to_organiser = organiser.objects.get(id=int(request.POST['select-organiser']))


	# create a object to save in databse with status=0
	# on approval status will be 1
	model_object = OrganiserHandover()
	model_object.handedoverfrom = from_organiser
	model_object.handedoverto = to_organiser
	model_object.status = 0
	model_object.save()

	return redirect(training_dashboard)


def organiserhandover_accept(request, object_id):

	model_object = OrganiserHandover.objects.get(id=object_id)
	model_object.status = 1        # on accept status will be 1
	model_object.save()

	# organiser will get access to the trainings of past organiser
	trainings = Training.objects.filter(this_organiser=model_object.handedoverfrom)
	for training in trainings:
		training.handedoverto.add(model_object.handedoverto)

	from_organiser = model_object.handedoverfrom
	from_organiser.status = 3    # organiser status will be 3 to show that he is no more orgaiser
	from_organiser.save()

	return redirect(training_dashboard)

def organiserhandover_reject(request,object_id):

	model_object = OrganiserHandover.objects.get(id=object_id)
	model_object.status = 2       # request status will be 2
	model_object.save()

	return redirect(training_dashboard)
