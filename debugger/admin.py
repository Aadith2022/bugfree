from django.contrib import admin

from .models import Person, Bug, Project, Institution, Message, History


# Register your models here.
admin.site.register(Person)
admin.site.register(Bug)
admin.site.register(Project)
admin.site.register(Institution)
admin.site.register(Message)
admin.site.register(History)