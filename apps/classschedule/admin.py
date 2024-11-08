from django.contrib import admin

from apps.classschedule.models import ClassSchedule

# Register your models here.

class ClassScheduleAdmin(admin.ModelAdmin):
    model = ClassSchedule
    filter_horizontal = ('group',)





admin.site.register(ClassSchedule,ClassScheduleAdmin)