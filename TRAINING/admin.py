# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import MasterBatch, CSV_list, Depertment, DeptOrg, Category, Foss, Training, Student, StudentLog

admin.site.register(MasterBatch)
admin.site.register(CSV_list)
admin.site.register(Depertment)
admin.site.register(DeptOrg)
admin.site.register(Category)
admin.site.register(Foss)
admin.site.register(Training)
admin.site.register(Student)
admin.site.register(StudentLog)