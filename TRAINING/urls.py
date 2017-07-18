from django.conf.urls import url
from .import views

urlpatterns = [
	url(r'^planner(?:/(?P<status>[a-zA-Z]+))?/$', views.training_planner),
	url(r'^planner/training-request/$', views.training_request),
	url(r'^planner/training-request/use-existing-csv/$', views.use_existing_csv),
	url(r'^planner/training-request/use-existing-csv/step-2/$', views.use_existing_csv_step_2),
	url(r'^planner/training-request/use-existing-csv/final-step/$', views.use_existing_csv_step_3),
	url(r'^planner/participant-list/(?P<csv_id>[0-9]+)/$', views.training_participant_list),
	url(r'^planner/participant-list/(?P<csv_id>[0-9]+)/edit-student-(?P<student_id>[0-9]+)/$', views.edit_student),
	url(r'^planner/delete-training/(?P<training_id>[0-9]+)/$', views.delete_training),
	url(r'^planner/edit-training/(?P<training_id>[0-9]+)/$', views.edit_training),
	url(r'^planner/add-participant/(?P<training_id>[0-9]+)/$', views.add_participants),
	url(r'^student-dashboard/$', views.student_dashboard),
	url(r'^student-dashboard/edit-profile/$', views.edit_profile_by_student),
	url(r'^student-dashboard/edit-academic-info/$', views.edit_academic_info_by_student),
]