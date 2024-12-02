from django.contrib import admin

from apps.group.form import GroupForm
from apps.group.models import Group
from apps.semester.models import Semester


class SemesterInline(admin.TabularInline):  # yoki StackedInline
    model = Semester


class GroupAdmin(admin.ModelAdmin):
    model = Group
    form = GroupForm
    filter_horizontal = ('students',)
    list_display = ['name','id']
    inlines = [SemesterInline]



admin.site.register(Group, GroupAdmin)
