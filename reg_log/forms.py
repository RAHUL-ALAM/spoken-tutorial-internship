from django.contrib.auth.models import User
from django import forms
from .models import userprofile, GENDER_CHOICES, state, college, organiser

#modelform for user registration
class userRegForm(forms.ModelForm):
	
	username = forms.CharField(widget=forms.TextInput(attrs=
		{'name':"username",'id':"username",'class':"form-control",'placeholder':"Desired Username"}))
	first_name = forms.CharField(widget=forms.TextInput(attrs=
		{'name':"firstname",'id':"fname",'class':"form-control",'placeholder':"First Name"})) 
	last_name = forms.CharField(widget=forms.TextInput(attrs=
		{'name':"lastname",'id':"lname",'class':"form-control",'placeholder':"Last Name"}))
	email = forms.CharField(widget=forms.EmailInput(attrs=
		{'name':"email",'id':"email",'class':"form-control",'placeholder':'Your Email'}))
	password = forms.CharField(widget=forms.PasswordInput(attrs=
		{'name':'password','id':'password','class':'form-control','placeholder':'Password'}))
	password2 = forms.CharField(widget=forms.PasswordInput(attrs=
		{'name':'retype_password','id':'r_password','class':'form-control','placeholder':'Retype Password'}))

	class Meta:
		model = User
		fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2']




#form to save data in user extending model
class userExtendeForm(forms.Form):

	gender = forms.ChoiceField(choices=GENDER_CHOICES,widget=forms.Select(attrs={'id':"gender"}))
	phn = forms. IntegerField(widget=forms.NumberInput(attrs=
		{'id':"phn",'class':"form-control",'placeholder':"Phone Number"}))




#form for processing login
class logForm(forms.Form):
	username = forms.CharField(max_length=15,widget = forms.TextInput(attrs=
		{'name':"username",'id':"username",'class':"form-control",'placeholder':"Username"}))
	password = forms.CharField(max_length=15,widget = forms.PasswordInput(attrs=
		{'name':'password','id':'password','class':'form-control','placeholder':'Password'}))




# choices for state (all states from database)
# used in filtering results in the addorgform below
STATE_CHOICES = (('0','Select State'),)
all_states = state.objects.all()
for state in all_states:
	STATE_CHOICES += ((str(state.id), str(state.name)),)




# form to process organiser request
class addorgForm(forms.Form):

	State = forms.ChoiceField(choices=STATE_CHOICES,widget=forms.Select(attrs={'id':"state",'class':"form-control"}))
	collage = forms.ChoiceField(choices=(('-','------'),), widget=forms.Select(attrs=
		{ 'id':"college", 'class':"form-control",'disabled':True }))



# form to add institutiton to database by training manager
class addInstiForm(forms.Form):

	clg_name = forms.CharField(widget=forms.TextInput(attrs=
		{'name':"name", 'id':"clgname",'class':"form-control", 'placeholder':"Enter college Name"}))
	state = forms.ChoiceField(choices=STATE_CHOICES,widget=forms.Select(attrs={'id':"state", 'class':"form-control"}))
	district = forms.ChoiceField(choices=(('-','------'),), widget=forms.Select(attrs=
		{ 'id':"district", 'class':"form-control", 'disabled':True }))
	city = forms.ChoiceField(choices=(('-','------'),), widget=forms.Select(attrs=
		{ 'id':"city", 'class':"form-control", 'disabled':True }))
	address = forms.CharField(widget=forms.TextInput(attrs=
		{'id':"address", 'class':"form-control", 'placeholder': "Enter Address"}))
	pincode = forms.IntegerField(widget=forms.NumberInput(attrs=
		{'id':"pin", 'class':"form-control", 'placeholder':"Enter Pincode"}))
	status = forms.BooleanField(widget=forms.CheckboxInput(attrs=
		{'id':"status", 'class':"form-control"}))


