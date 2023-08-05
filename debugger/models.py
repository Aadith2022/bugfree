from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class Message(models.Model):
    title = models.CharField(blank = False, max_length = 200)
    message = models.TextField(blank = False)
    timestamp = models.DateTimeField(auto_now_add = True)
    read = models.BooleanField(default=False)
    commenter = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "message_creator", null = True)


class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    messages = models.ManyToManyField(Message, related_name = "user_notifications")

@receiver(post_save, sender = User)
def create_person(sender, instance, created, **kwargs):
    if created:
        Person.objects.create(user = instance)

@receiver(post_save, sender = User)
def save_person(sender, instance, **kwargs):
    instance.person.save()

class Bug(models.Model):
    submitter = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "bug_submitter", null=True)
    developer = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "bug_fixer", null = True)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now_add = True)
    title = models.CharField(blank = False, max_length = 200)
    content = models.TextField(blank = False)
    priority = models.CharField(blank = False, max_length = 200)
    type = models.CharField(blank = False, max_length = 200)
    status = models.CharField(blank = False, max_length = 200)
    comments = models.ManyToManyField(Message, related_name = "ticket_comments")


class History(models.Model):
    bug = models.ForeignKey(Bug, on_delete = models.CASCADE, related_name = "bug_history", null = True)
    old = models.TextField(blank = True, null = True)
    new = models.TextField(blank = False)
    property = models.CharField(blank = False, max_length = 200)
    date = models.DateTimeField(auto_now_add = True)
    changer = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "ticket_changer")


class Project(models.Model):
    title = models.CharField(blank = False, max_length = 200)
    description = models.TextField(blank = False)
    bugs = models.ManyToManyField(Bug, related_name = "project_bugs")
    admin = models.ManyToManyField(User, related_name = "project_admins")
    users = models.ManyToManyField(User, related_name = "project_users")
    developers = models.ManyToManyField(User, related_name = "project_developers")
    project_manager = models.ManyToManyField(User, related_name = "project_manager")
    submitters = models.ManyToManyField(User, related_name = "project_submitters")
    timestamp = models.DateTimeField(auto_now_add = True)


class Institution(models.Model):
    name = models.TextField(blank = False)
    users = models.ManyToManyField(User, related_name = "institution_users", related_query_name = "institution_user")
    admin = models.ManyToManyField(User, related_name = "institution_admin")
    developers = models.ManyToManyField(User, related_name = "institution_developers")
    projects = models.ManyToManyField(Project, related_name = "institution_projects")
    project_manager = models.ManyToManyField(User, related_name = "institution_project_manager")
    submitters = models.ManyToManyField(User, related_name = "institution_bug_submitter")
    pending = models.ManyToManyField(User, related_name="institution_pending_users")
    password = models.TextField(blank = False)
