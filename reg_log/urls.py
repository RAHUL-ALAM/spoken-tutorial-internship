from django.conf.urls import url
from django.contrib.auth.views import logout
from . import views

urlpatterns = [
	url(r'^$', views.home),
	url(r'^register/$',views.registration),
	url(r'^login/$',views.logIn),
	url(r'^logout/$', logout, {'next_page': '/'}),
	url(r'^ajax-state-collage/$',views.ajax_college_state),
	url(r'^ajax-state-district/$',views.ajax_state_district),
	url(r'^ajax-district-city/$',views.ajax_district_state),
	url(r'^training-manager/organiser-list/ajax-state-collage/(?P<status>\w+)/$',views.ajax_college_state_organiser_list),
	url(r'^training-manager/organiser-list/ajax-collage-show/(?P<status>\w+)/$',views.ajax_college_organiser_list),
	url(r'^training-manager/organiser-list/reset/(?P<status>\w+)/$',views.reset_organiser_list),
	url(r'^training-manager/organiser-list/(?P<status>\w+)/$',views.organiser_list),
	url(r'^training-manager/organiser-list/(?P<status>\w+)/organiser-request/accept/(?P<user_id>[0-9]+)/$',views.organiser_request_accept),
	url(r'^training-manager/organiser-list/(?P<status>\w+)/organiser-request/reject/(?P<user_id>[0-9]+)/$',views.organiser_request_reject),
]