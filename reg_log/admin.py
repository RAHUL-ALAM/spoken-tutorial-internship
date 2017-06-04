# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import userprofile, college, state, organiser, city, district
# Register your models here.
admin.site.register(userprofile)
admin.site.register(college)
admin.site.register(state)
admin.site.register(city)
admin.site.register(district)
admin.site.register(organiser)