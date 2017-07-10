from django import forms
from .models import Depertment, DeptOrg, Foss, Training, Student
from reg_log.forms import DEPT_CHOICES
from django.core.exceptions import ValidationError
import csv
import io

# DEPT_CHOICES = (('-','Select Depatrments'),)
# all_depts = DeptOrg.objects.fiter(org=O)
# for dept in all_depts:
# 	DEPT_CHOICES += ((str(dept.id), str(dept.name)),)


# class OrgDeptForm(forms.Form):
	
# 	dept = forms.ChoiceField(choices=DEPT_CHOICES, widget=forms.Select(attrs={'id':"dept", 'class':"form-control"}))

# 	# class Meta:
# 	# 	model = DeptOrg
# 	# 	fields = ['dept']
# 	# 	widgets = {
# 	# 		'dept':floppyforms.widgets.Input(datalist=Depertment.objects.all()),
# 	# 	}

# 	# def __init__(self, *args, **kwargs):
# 	# 	super(OrgDeptForm, self).__init__(*args, **kwargs)
# 	# 	self.fields['dept'] =  forms.ModelMultipleChoiceField(queryset=Depertment.objects.all(),empty_label="Choose depts",
# 	# 		widget=forms.CheckboxSelectMultiple(attrs={'id':"dept", 'class':'form-control' }))


FOSS_CHOICES = [
	['---Select Foss---', [['0', 'Select Foss']]],
	['---With Exams---', []], 
    ['---Without Exams---', []],
]

all_foss_with_exam = Foss.objects.filter(with_exam=True)
for foss in all_foss_with_exam:
	FOSS_CHOICES[1][1].append([str(foss.id), str(foss.name)])

all_foss_without_exam = Foss.objects.filter(with_exam=False)
for foss in all_foss_without_exam:
	FOSS_CHOICES[2][1].append([str(foss.id), str(foss.name)])

def is_csv(value):
    if not value.name.endswith('.csv'):
        raise ValidationError("This File Don't have a .csv Extension")

    try:
        csvreader = csv.reader((value.file.read()), delimiter=',', quotechar='|')
    except csv.Error:
        raise ValidationError('Not a valid CSV file')


class Training_Request_Form(forms.Form):

	dept = forms.ChoiceField(choices=DEPT_CHOICES, widget=forms.Select(attrs={'id':"dept", 'class':"form-control"}))
	start_date = forms.DateField(widget=forms.DateInput(attrs=
		{'type':"date", 'id':"start-date", 'class':"form-control"}))
	foss = forms.ChoiceField(choices=FOSS_CHOICES, widget=forms.Select(attrs={'id':"foss"}))


class Training_Request_Form_File(forms.Form):
	csv_file = forms.FileField(validators=[is_csv], widget=forms.FileInput(attrs=
		{'id':"csv-file",'class':"form-control", 'required':False, 'accept': ".csv"}))


class edit_training_form(forms.Form):

	dept = forms.ChoiceField(choices=DEPT_CHOICES, widget=forms.Select(attrs={'id':"dept", 'class':"form-control"}))
	start_date = forms.DateField(widget=forms.DateInput(attrs=
		{'type':"date", 'id':"start-date", 'class':"form-control"}))
	foss = forms.ChoiceField(choices=FOSS_CHOICES, widget=forms.Select(attrs={'id':"foss"}))


class add_participants_form(forms.Form):

	csv_file = forms.FileField(validators=[is_csv], widget=forms.FileInput(attrs=
		{'id':"csv-file",'class':"form-control", 'accept': ".csv"}))


GENDER_CHOICES = (
    ('M', "Male"),
    ('F', "Female"),
    ('O', "Others")
)

class edit_student_form(forms.Form):

	first_name = forms.CharField(widget=forms.TextInput(attrs={ 'id':"first-name", 'class':"form-control"}))
	last_name = forms.CharField(widget=forms.TextInput(attrs={ 'id':"last-name", 'class':"form-control"}))
	email = forms.CharField(widget=forms.EmailInput(attrs={ 'id':"email", 'class':"form-control"}))
	dept = forms.ChoiceField(choices=DEPT_CHOICES, widget=forms.Select(attrs=
		{ 'id':"dept", 'class':"form-control" }))
	gender = forms.ChoiceField(choices=GENDER_CHOICES , widget=forms.Select(attrs=
		{ 'id':"gender", 'class':"form-control"}))


STUDENT_CHOICES = (('-','Select Depatrments'),)
all_students = Student.objects.all()
for student in all_students:
	STUDENT_CHOICES += ((str(student.id), str(student.user.first_name)+' '+str(student.user.last_name)),)

class use_existing_csv_form_final(forms.Form):
	participants = forms.MultipleChoiceField(choices=STUDENT_CHOICES,widget=forms.SelectMultiple(attrs=
		{'id':"participants", 'class':"form-control"}))


