from django.contrib import admin

from apps.group.form import GroupForm
from apps.group.models import Group


class GroupAdmin(admin.ModelAdmin):
    model = Group
    form = GroupForm
    filter_horizontal = ('students',)
    list_display = ['name','id']



admin.site.register(Group, GroupAdmin)
