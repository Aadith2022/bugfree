from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.core.paginator import Paginator
from django.urls import reverse
from django.shortcuts import redirect
import json
import datetime
from django.http import JsonResponse
from django.db.models import Count
from json import dumps

from .models import User, Bug, Project, Institution, Person, Message, History


# Create your views here.

def index(request):
    if request.method == "POST":

        if 'login' in request.POST:

            email = request.POST['login_email']
            password = request.POST['login_password']


            #checking if the admins password was provided or not
            admin_pass = ''

            if request.POST['login_admin_pass']:
                admin_pass = request.POST['login_admin_pass']

            institution = request.POST['login_institution']

            try:
                user = User.objects.get(email = email, password = password)
            except User.DoesNotExist:
                return render(request, "debugger/index.html", {
                    "message": "Invalid Credentials"
                })

            this_user = User.objects.get(email = email, password = password)

            if admin_pass != '':

                if Institution.objects.filter(name = institution, password = admin_pass).exists():

                    this_institution = Institution.objects.get(name = institution, password = admin_pass)

                    #this is an acceptable way to search for user within an institution because emails are distinct within institutions

                    if this_user in this_institution.admin.all():

                        login(request, this_user)

                        return HttpResponseRedirect(reverse('administrator', kwargs={'institution_id':this_institution.id, 'admin_id':this_user.id}))

                    else:

                        #here we will send an alert message to the administrators of the institution
                        string = f'The user with email: {this_user.email}, has gained access of the Admin Password, please change it immediately'
                        message = Message(title = 'Warning', message = string)
                        message.save()

                        for admin in this_institution.admin.all():
                            admin.person.messages.add(message)
                            admin.save()

                        return render(request, "debugger/index.html", {
                            "message": "You are not a registered administrator for this Institution"
                        })
                else:
                    return render(request, "debugger/index.html", {
                        "message": "Please check your spelling of the Institution name or Admin password"
                    })
            else:
                if Institution.objects.filter(name = institution).exists():
                    this_inst = Institution.objects.get(name = institution)

                    #new admin check

                    # new new checks

                    if ( (this_user in this_inst.users.all()) or (this_user in this_inst.pending.all()) ):
                        
                        if this_user in this_inst.admin.all():
                            return render(request, "debugger/index.html", {
                                "message": "Please enter your Admin Password"
                            })
                        elif this_user in this_inst.project_manager.all():

                            login(request, this_user)
                            return HttpResponseRedirect(reverse('pm', kwargs={'institution_id':this_inst.id, 'user_id':this_user.id}))
                        
                        elif this_user in this_inst.developers.all():
                            
                            login(request, this_user)
                            return HttpResponseRedirect(reverse('developer', kwargs={'institution_id':this_inst.id, 'user_id':this_user.id}))
                        
                        elif this_user in this_inst.submitters.all():

                            login(request, this_user)
                            return HttpResponseRedirect(reverse('submitter', kwargs={'institution_id':this_inst.id, 'user_id':this_user.id}))
                        
                        else:

                            login(request, this_user)
                            return HttpResponseRedirect(reverse('user', kwargs={'institution_id':this_inst.id, 'user_id':this_user.id}))
                        
                    else:
                        return render(request, "debugger/index.html", {
                            "message": "You are not a member of this Institution"
                        })

                    # if this_user in this_inst.submitters.all():
                    #     return HttpResponseRedirect(reverse('submitter', kwargs={'institution_id':this_inst.id, 'user_id':this_user.id}))
                    # elif this_user in this_inst.developers.all():
                    #     return HttpResponseRedirect(reverse('developer', kwargs ={'institution_id':this_inst.id, 'user_id':this_user.id}))
                    # else:
                    #     return HttpResponseRedirect(reverse('user', kwargs={'institution_id':this_inst.id, 'user_id':this_user.id}))
                else:
                    return render(request, "debugger/index.html", {
                        "message": "Institution cannot be found"
                    })
                    

        elif 'register' in request.POST:

            username = request.POST['register_username']

            email = request.POST['register_email']

            password = request.POST['register_password']

            institution = request.POST['register_institution']

            # new new stuff

            # new messages

            if Institution.objects.filter(name = institution).exists():

                if User.objects.filter(username = username).exists():
                    return render(request, "debugger/index.html", {
                        "message": "This username has already been taken, please try again"
                    })
                #this filter will show that there is already someone in this institution using this email, so we wont allow them to reregister
                elif User.objects.filter(institution_user__name = institution, email = email).exists():
                    return render(request, "debugger/index.html", {
                        "message": "This email is already in use for this institution"
                    })
                
            else:

                return render(request, "debugger/index.html", {
                    "message": "This Institution has not been registered"
                })

            # if User.objects.filter(email = email).exists():
            #     return render(request, "debugger/index.html", {
            #         "message": "There is already an account associated with this email"
            #     })
            # elif User.objects.filter(username = username).exists():
            #     return render(request, "debugger/index.html", {
            #         "message": "This username is already taken"
            #     })
            # else:
            #     if not Institution.objects.filter(name = institution).exists():
            #         return render(request, "debugger/index.html", {
            #             "message": "This Institution has not been registered"
            #         })

            new_user = User(username = username, email = email, password = password)
            new_user.save()

            #new
            this_inst = Institution.objects.get(name = institution)
            this_inst.pending.add(new_user)
            this_inst.save()

            # this_inst = Institution.objects.get(name = institution)
            # this_inst.users.add(new_user)
            # this_inst.save()

            login(request, new_user)

            return HttpResponseRedirect(reverse('user', kwargs={'institution_id':this_inst.id, 'user_id':new_user.id}))
    

        elif 'register_in' in request.POST:

            username = request.POST['in_username'], 
            email = request.POST['in_email']

            institution = request.POST['in_institution']

            admin_pass = request.POST['in_admin_password']

            password = request.POST['in_password']

            if Institution.objects.filter(name = institution).exists():
                return render (request, "debugger/index.html", {
                    "message": "Sorry, an Institution with this name already exists"
                })
            elif User.objects.filter(username = username).exists():
                return render(request, "debugger/index.html", {
                    "message": "This username is already in use, please try again"
                })


            new_user = User(username = username, email = email, password = password)
            new_user.save()

            new_institution = Institution(name = institution, password = admin_pass)
            
            new_institution.save()

            new_institution.users.add(new_user)

            new_institution.save()

            new_institution.admin.add(new_user)

            new_institution.save()

            login(request, new_user)

            return HttpResponseRedirect(reverse('administrator', kwargs={'institution_id' : new_institution.id, 'admin_id':new_user.id}))

    else:
        return render(request, 'debugger/index.html')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


@login_required(login_url="/")
def user(request, institution_id, user_id):
    institution = Institution.objects.get(pk = institution_id)
    user = User.objects.get(pk = user_id)

    if (user):

        if request.user.id == user_id:

            inPending = False

            inInstitution = False

            if user in institution.pending.all():
                inPending = True

            if user in institution.users.all():
                inInstitution = True

            if inInstitution == True:

                if user in institution.admin.all():
                    return HttpResponseRedirect(reverse('administrator', kwargs={'institution_id' : institution.id, 'admin_id' : user.id}))
                elif user in institution.developers.all():
                    return HttpResponseRedirect(reverse('developer', kwargs={'institution_id':institution.id, 'user_id':user.id}))
                elif user in institution.submitters.all():
                    return HttpResponseRedirect(reverse('submitter', kwargs={'institution_id':institution.id, 'user_id':user.id}))
                elif user in institution.project_manager.all():
                    return HttpResponseRedirect(reverse('pm', kwargs={'institution_id':institution.id, 'user_id':user.id}))
                
            return render(request, "debugger/user.html", {
                'institution': institution, 'user': user, 'inPending':inPending
            })
        else:
            raise PermissionDenied()

    else:
        return HttpResponseRedirect(reverse('index'))


@login_required(login_url="/")
def admin(request, institution_id, admin_id):
    institution = Institution.objects.get(pk = institution_id)
    user = User.objects.get(pk = admin_id)

    #new

    if request.user in institution.admin.all():

        if request.user.id == admin_id:

            all_bugs = []

            all_projects = institution.projects.all()

            for project in all_projects:
                for bug in project.bugs.all():
                    all_bugs.append(bug)

            all_resolved = []

            for bug in all_bugs:
                if bug.status == "Resolved":
                    all_resolved.append(bug)

            everythingResolved = False

            if len(all_bugs) == len(all_resolved):
                everythingResolved = True

            all_low = []

            all_medium = []

            all_high = []

            all_errors = []

            all_requests = []

            all_other = []

            all_new = []

            all_open = []

            all_progress = []

            all_additional = []

            for bug in all_bugs:
                if bug.priority == 'Low' and bug.status != 'Resolved':
                    all_low.append(bug)
                elif bug.priority == 'Medium' and bug.status != 'Resolved':
                    all_medium.append(bug)
                elif bug.priority == 'High' and bug.status != 'Resolved':
                    all_high.append(bug)

                if bug.type == 'Bugs/Errors' and bug.status != 'Resolved':
                    all_errors.append(bug)
                elif bug.type == 'Additional Feature Requests' and bug.status != 'Resolved':
                    all_requests.append(bug)
                elif bug.type == 'Other' and bug.status != 'Resolved':
                    all_other.append(bug)

                if bug.status == 'New':
                    all_new.append(bug)
                elif bug.status == 'Open':
                    all_open.append(bug)
                elif bug.status == 'In Progress':
                    all_progress.append(bug)
                elif bug.status == 'Additional Info Required':
                    all_additional.append(bug)

            all_messages = user.person.messages.all()

            isUnread = False

            for message in all_messages:
                if message.read == False:
                    isUnread = True

            # pwd check

            # all_titles = []

            # for message in all_messages:
            #     all_titles.append(message.title)

            # change_pwd = False
            
            # if 'Warning' in all_titles:
            #     change_pwd = True

            # #new changing check
            # for message in all_messages:
            #     if message.title == 'Warning':
            #         if message.read == False:
            #             change_pwd = True

            all_pending = institution.pending.all()

            return render(request, "debugger/admin.html", {
                'institution': institution, 'admin' : user, 'all_bugs':all_bugs, 'everythingResolved':everythingResolved, 'all_projects':all_projects, 'all_messages':all_messages, 'isUnread':isUnread, 'low':len(all_low), 'med':len(all_medium), 'high':len(all_high), 'errors':len(all_errors), 'requests':len(all_requests), 'other':len(all_other), 'new':len(all_new), 'open':len(all_open), 'progress':len(all_progress), 'resolved':len(all_resolved), 'info':len(all_additional), 'all_pending':all_pending
            })
        else:
            raise PermissionDenied
    
    else:
        return render(request, 'debugger/index.html')


@login_required(login_url="/")
def admin_leave(request, institution_id, admin_id):
    institution = Institution.objects.get(pk = institution_id)
    user = User.objects.get(pk = admin_id)

    if request.user in institution.admin.all():

        if request.user.id == admin_id:

            all_bugs = []

            all_projects = institution.projects.all()

            for project in all_projects:
                for bug in project.bugs.all():
                    all_bugs.append(bug)

            all_low = []

            all_medium = []

            all_high = []

            all_errors = []

            all_requests = []

            all_other = []

            all_new = []

            all_open = []

            all_progress = []

            all_additional = []

            for bug in all_bugs:
                if bug.priority == 'Low':
                    all_low.append(bug)
                elif bug.priority == 'Medium':
                    all_medium.append(bug)
                elif bug.priority == 'High':
                    all_high.append(bug)

                if bug.type == 'Bugs/Errors':
                    all_errors.append(bug)
                elif bug.type == 'Additional Feature Requests':
                    all_requests.append(bug)
                elif bug.type == 'Other':
                    all_other.append(bug)

                if bug.status == 'New':
                    all_new.append(bug)
                elif bug.status == 'Open':
                    all_open.append(bug)
                elif bug.status == 'In Progress':
                    all_progress.append(bug)
                elif bug.status == 'Additional Info Required':
                    all_additional.append(bug)

            all_messages = user.person.messages.all()

            isUnread = False

            for message in all_messages:
                if message.read == False:
                    isUnread = True

            # pwd check
            # all_titles = []

            # for message in all_messages:
            #     all_titles.append(message.title)

            # change_pwd = False

            # if 'Warning' in all_titles:
            #     change_pwd = True

            all_pending = institution.pending.all()

            if request.method == "POST":

                if 'leave_confirm' in request.POST:

                    institution.admin.remove(user)

                    institution.users.remove(user)
                    institution.save()

                    user.delete()

                    institution_users = institution.users.all()

                    if ( len(institution_users) == 0 ):
                        institution.delete()

                    logout(request)

                    return render(request, "debugger/index.html")

                elif 'leave_deny' in request.POST:

                    return render(request, 'debugger/admin.html', {
                        'institution': institution, 'admin' : user, 'all_bugs':all_bugs, 'all_projects':all_projects, 'all_messages':all_messages, 'isUnread':isUnread, 'low':len(all_low), 'med':len(all_medium), 'high':len(all_high), 'errors':len(all_errors), 'requests':len(all_requests), 'other':len(all_other), 'new':len(all_new), 'open':len(all_open), 'progress':len(all_progress), 'info':len(all_additional), 'all_pending':all_pending
                    })

            return render(request, "debugger/admin_leave.html", {
                'institution':institution, 'admin':user, 'isUnread':isUnread, 'all_pending':all_pending, 'all_messages':all_messages
            })
        
        else:
            raise PermissionDenied
        
    else:
        return render(request, 'debugger/index.html')


def admin_pwd(request, institution_id, admin_id):
    institution = Institution.objects.get(pk = institution_id)
    user = User.objects.get(pk = admin_id)

    if request.user in institution.admin.all():

        if request.user.id == admin_id:

            all_bugs = []

            all_projects = institution.projects.all()

            for project in all_projects:
                for bug in project.bugs.all():
                    all_bugs.append(bug)

            all_low = []

            all_medium = []

            all_high = []

            all_errors = []

            all_requests = []

            all_other = []

            all_new = []

            all_open = []

            all_progress = []

            all_additional = []

            for bug in all_bugs:
                if bug.priority == 'Low':
                    all_low.append(bug)
                elif bug.priority == 'Medium':
                    all_medium.append(bug)
                elif bug.priority == 'High':
                    all_high.append(bug)

                if bug.type == 'Bugs/Errors':
                    all_errors.append(bug)
                elif bug.type == 'Additional Feature Requests':
                    all_requests.append(bug)
                elif bug.type == 'Other':
                    all_other.append(bug)

                if bug.status == 'New':
                    all_new.append(bug)
                elif bug.status == 'Open':
                    all_open.append(bug)
                elif bug.status == 'In Progress':
                    all_progress.append(bug)
                elif bug.status == 'Additional Info Required':
                    all_additional.append(bug)

            all_messages = user.person.messages.all()

            isUnread = False

            for message in all_messages:
                if message.read == False:
                    isUnread = True

            # pwd check
            # all_titles = []

            # for message in all_messages:
            #     all_titles.append(message.title)

            # change_pwd = False

            # if 'Warning' in all_titles:
            #     change_pwd = True

            all_pending = institution.pending.all()


            if request.method == "POST":

                if 'password_change' in request.POST:

                    old_pwd = request.POST['old_pwd']
            
                    new_pwd = request.POST['new_pwd']

                    confirm_pwd = request.POST['confirm_pwd']

                    if old_pwd == new_pwd:

                        return render(request, "debugger/admin_pwd.html", {
                            'institution':institution, 'admin':user, 'isUnread':isUnread, 'message': 'New password is the same as old password, please try again', 'all_messages':all_messages, 'all_pending':all_pending
                        })

                    elif new_pwd != confirm_pwd:

                        return render(request, "debugger/admin_pwd.html", {
                            'institution':institution, 'admin':user, 'isUnread':isUnread, 'message': 'Passwords did not match, please try again', 'all_messages':all_messages, 'all_pending':all_pending
                        })
                    
                    else:

                        institution.password = new_pwd
                        institution.save()


                        return render(request, 'debugger/admin.html', {
                            'institution': institution, 'admin' : user, 'all_bugs':all_bugs, 'all_projects':all_projects, 'all_messages':all_messages, 'isUnread':isUnread, 'low':len(all_low), 'med':len(all_medium), 'high':len(all_high), 'errors':len(all_errors), 'requests':len(all_requests), 'other':len(all_other), 'new':len(all_new), 'open':len(all_open), 'progress':len(all_progress), 'info':len(all_additional), 'all_pending':all_pending
                        })                 

                elif 'password_cancel' in request.POST:

                    return render(request, 'debugger/admin.html', {
                        'institution': institution, 'admin' : user, 'all_bugs':all_bugs, 'all_projects':all_projects, 'all_messages':all_messages, 'isUnread':isUnread, 'low':len(all_low), 'med':len(all_medium), 'high':len(all_high), 'errors':len(all_errors), 'requests':len(all_requests), 'other':len(all_other), 'new':len(all_new), 'open':len(all_open), 'progress':len(all_progress), 'info':len(all_additional), 'all_pending':all_pending
                    })
            
            return render(request, 'debugger/admin_pwd.html', {
                'institution':institution, 'admin':user, 'isUnread':isUnread, 'all_messages':all_messages, 'all_pending':all_pending
            })

        else:
            raise PermissionDenied
        
    else:
        return render(request, "debugger/index.html")



@login_required(login_url="/")
def admin_pending(request, institution_id, admin_id):
    institution = Institution.objects.get(pk = institution_id)
    user = User.objects.get(pk = admin_id)

    if request.user in institution.admin.all():

        if request.user.id == admin_id:

            all_messages = user.person.messages.all()

            isUnread = False

            for message in all_messages:
                if message.read == False:
                    isUnread = True

            # all_titles = []

            # for message in all_messages:
            #     all_titles.append(message.title)

            # change_pwd = False

            # if 'Warning' in all_titles:
            #     change_pwd = True

            all_pending = institution.pending.all()

            if request.method == "POST":

                if 'pending_clear' in request.POST:

                    for person in institution.pending.all():
                        institution.pending.remove(person)
                        institution.save()

                        person.delete()

                    return HttpResponseRedirect(reverse('administrator', kwargs={'institution_id':institution.id, 'admin_id':user.id}))
                
                else:

                    if 'add_pending' in request.POST['hidden_differ']:

                        id = request.POST['hidden_pending_add']

                        person = User.objects.get(pk = id)

                        institution.pending.remove(person)

                        institution.users.add(person)

                        institution.save()

                        pend = institution.pending.all()

                        if (pend):
                            return HttpResponseRedirect(request.path_info)
                        else:
                            return HttpResponseRedirect(reverse('administrator', kwargs={'institution_id':institution.id, 'admin_id':user.id}))

                    elif 'remove_pending' in request.POST['hidden_differ']:

                        id = request.POST['hidden_pending_remove']

                        person = User.objects.get(pk = id)

                        institution.pending.remove(person)

                        institution.save()

                        person.delete()

                        pend = institution.pending.all()

                        if (pend):
                            return HttpResponseRedirect(request.path_info)
                        else:
                            return HttpResponseRedirect(reverse('administrator', kwargs={'institution_id':institution.id, 'admin_id':user.id}))                

            return render(request, "debugger/admin_manage_pending.html", {
                'institution':institution, 'admin':user, 'all_messages':all_messages, 'isUnread':isUnread, 'all_pending':all_pending
            })
        
        else:
            raise PermissionDenied()
    
    else:
        return render(request, 'debugger/index.html')


@login_required(login_url="/")
def admin_manage_users(request, institution_id, admin_id):
    institution = Institution.objects.get(pk = institution_id)
    admin = User.objects.get(pk = admin_id)

    if request.user in institution.admin.all():

        if request.user.id == admin_id:

            all_admin = institution.admin.all()

            all_users = []

            for person in institution.users.all():
                if person in all_admin:
                    continue
                else:
                    all_users.append(person)

            all_devs = institution.developers.all()

            all_pm = institution.project_manager.all()

            all_submitters = institution.submitters.all()

            all_projects = institution.projects.all()

            # paginator = Paginator(all_users, 10)

            # page_number = request.GET.get('page')
            # page_obj = paginator.get_page(page_number)

            is_admin = False

            is_dev = False

            is_pm = False

            is_submitter = False


            if request.method == "POST":

                # new

                # username = request.POST['user_management']

                if 'user_submit' in request.POST:

                    id = request.POST['hidden_manage_user']

                    user = User.objects.get(pk = id)

                    if user in all_admin:

                        is_admin = True

                    elif user in all_devs:

                        is_dev = True
                    
                    elif user in all_pm:

                        is_pm = True

                    elif user in all_submitters:

                        is_submitter = True

                    role = request.POST['role_assignment']


                    if role == 'admin':

                        if is_dev == True:

                            institution.developers.remove(user)
                            institution.admin.add(user)
                            institution.save()
                            return HttpResponseRedirect(request.path_info)

                        elif is_pm == True:

                            institution.project_manager.remove(user)
                            institution.admin.add(user)
                            institution.save()
                            return HttpResponseRedirect(request.path_info)
                        
                        elif is_submitter == True:

                            institution.submitters.remove(user)
                            institution.admin.add(user)
                            institution.save()
                            return HttpResponseRedirect(request.path_info)

                        elif is_admin == False:

                            institution.admin.add(user)
                            institution.save()
                            return HttpResponseRedirect(request.path_info)

                    elif role == 'project_manager':

                        # if is_admin == True:

                        #     institution.admin.remove(user)
                        #     institution.project_manager.add(user)
                        #     institution.save()
                        #     return HttpResponseRedirect(request.path_info)

                        if is_dev == True:

                            institution.developers.remove(user)
                            institution.project_manager.add(user)
                            institution.save()
                            return HttpResponseRedirect(request.path_info)
                        
                        elif is_submitter == True:

                            institution.submitters.remove(user)
                            institution.project_manager.add(user)
                            institution.save()
                            return HttpResponseRedirect(request.path_info)

                        elif is_pm == False:

                            institution.project_manager.add(user)
                            institution.save()
                            return HttpResponseRedirect(request.path_info)

                    elif role == 'developer':

                        # if is_admin == True:

                        #     institution.admin.remove(user)
                        #     institution.developers.add(user)
                        #     institution.save()
                        #     return HttpResponseRedirect(request.path_info)

                        if is_pm == True:

                            institution.project_manager.remove(user)
                            institution.developers.add(user)
                            institution.save()
                            return HttpResponseRedirect(request.path_info)
                        
                        elif is_submitter == True:

                            institution.submitters.remove(user)
                            institution.developers.add(user)
                            institution.save()
                            return HttpResponseRedirect(request.path_info)

                        elif is_dev == False:

                            institution.developers.add(user)
                            institution.save()
                            return HttpResponseRedirect(request.path_info)
                        
                    elif role == 'submitter':

                        # if is_admin == True:

                        #     institution.admin.remove(user)
                        #     institution.submitters.add(user)
                        #     institution.save()
                        #     return HttpResponseRedirect(request.path_info)
                        
                        if is_pm == True:

                            institution.project_manager.remove(user)
                            institution.submitters.add(user)
                            institution.save()
                            return HttpResponseRedirect(request.path_info)

                        elif is_dev == True:

                            institution.developers.remove(user)
                            institution.submitters.add(user)
                            institution.save()
                            return HttpResponseRedirect(request.path_info)

                        elif is_submitter == False:

                            institution.submitters.add(user)
                            institution.save()
                            return HttpResponseRedirect(request.path_info)

                elif "user_submit_cancel" in request.POST:
                    return HttpResponseRedirect(request.path_info)
                
                elif "user_remove" in request.POST:

                    id = request.POST['hidden_remove_user']

                    user = User.objects.get(pk = id)

                    if user in institution.submitters.all():
                        institution.submitters.remove(user)
                        institution.save()
                    elif user in institution.developers.all():
                        institution.developers.remove(user)
                        institution.save()
                    elif user in institution.project_manager.all():
                        institution.project_manager.remove(user)
                        institution.save()
                    
                    institution.users.remove(user)
                    institution.save()

                    user.delete()

                    return HttpResponseRedirect(request.path_info)


                elif "user_remove_cancel" in request.POST:
                    
                    return HttpResponseRedirect(request.path_info)

            # dynamic changing of project users as well as sending alert notifications

            for this_project in all_projects:

                all_admin = institution.admin.all()

                all_users = []

                for person in institution.users.all():
                    if person in all_admin:
                        continue
                    else:
                        all_users.append(person)

                all_devs = institution.developers.all()

                all_pm = institution.project_manager.all()

                all_submitters = institution.submitters.all()
                # above was taken from beginning

                these_pm = this_project.project_manager.all()

                original_pm_count = len(these_pm)

                not_pm_count = 0

                role_removed_list = []

                for person in this_project.project_manager.all():

                    # basically, for all of the pm in this project, we need to see if they are still pm

                    if person in all_pm:
                        continue
                    else:
                        not_pm_count += 1
                        role_removed_list.append(person)
                        this_project.project_manager.remove(person)
                        this_project.users.remove(person)
                        this_project.save()

                for person in this_project.developers.all():

                    if person in all_devs:
                        continue
                    else:
                        role_removed_list.append(person)
                        this_project.developers.remove(person)
                        this_project.users.remove(person)
                        this_project.save()

                for person in this_project.submitters.all():

                    if person in all_submitters:
                        continue
                    else:
                        role_removed_list.append(person)
                        this_project.submitters.remove(person)
                        this_project.users.remove(person)
                        this_project.save()

                for person in this_project.users.all():

                    if person in all_admin:
                        if person in this_project.admin.all():
                            continue
                        else:
                            # role_removed_list.append(person)
                            # this_project.users.remove(person)
                            # this_project.save()
                            this_project.admin.add(person)
                            this_project.save()

                    elif person in all_pm:
                        if person in this_project.project_manager.all():
                            continue
                        else:
                            role_removed_list.append(person)
                            this_project.users.remove(person)
                            this_project.save()

                    elif person in all_devs:
                        if person in this_project.developers.all():
                            continue
                        else:
                            role_removed_list.append(person)
                            this_project.users.remove(person)
                            this_project.save()

                    elif person in all_submitters:
                        if person in this_project.submitters.all():
                            continue
                        else:
                            role_removed_list.append(person)
                            this_project.users.remove(person)
                            this_project.save()

                if len(role_removed_list) > 0:
                    if not_pm_count == original_pm_count:

                        for user in this_project.admin.all():
                            first_string = f'The following users have been removed from Project: {this_project.title}, because their roles have been changed:'
                            list_string = ' '.join([str(item) for item in role_removed_list])
                            string = first_string + ' ' + list_string
                            new_message = Message(title = 'Alert', message = string)
                            new_message.save()
                            user.person.messages.add(new_message)
                            user.save()

                    else:
                        first_string = f'The following users have been removed from Project: {this_project.title}, because their roles have been changed:'
                        list_string = ' '.join([str(item) for item in role_removed_list])
                        string = first_string + ' ' + list_string
                        new_message = Message(title = 'Alert', message = string)
                        new_message.save()

                        for user in this_project.admin.all():
                            user.person.messages.add(new_message)
                            user.save()

                        for user in this_project.project_manager.all():
                            user.person.messages.add(new_message)
                            user.save()


            all_messages = admin.person.messages.all()

            isUnread = False

            for message in all_messages:
                if message.read == False:
                    isUnread = True

            # all_titles = []

            # for message in all_messages:
            #     all_titles.append(message.title)

            # change_pwd = False

            # if 'Warning' in all_titles:
            #     change_pwd = True

            all_pending = institution.pending.all()

            return render(request, "debugger/admin_manage_user.html", {
                'institution':institution, 'admin':admin, 'all_users':all_users, 'all_admin':all_admin, 'all_devs':all_devs, 'all_pm':all_pm, 'all_submitters':all_submitters, 'all_messages':all_messages, 'isUnread':isUnread, 'all_pending':all_pending
            })
        
        else:
            raise PermissionDenied()
    
    else:
        return render(request, 'debugger/index.html')


@login_required(login_url="/")
def admin_manage_project_users(request, institution_id, admin_id, project_id):
    institution = Institution.objects.get(pk = institution_id)
    the_admin = User.objects.get(pk = admin_id)

    if request.user in institution.admin.all():

        if request.user.id == admin_id:

            project = Project.objects.get(pk = project_id)

            all_admin = institution.admin.all()

            all_devs = institution.developers.all()

            all_pm = institution.project_manager.all()

            all_submitters = institution.submitters.all()

            all_pending = institution.pending.all()

            these_users = []

            for person in project.users.all():
                if person in all_admin:
                    continue
                else:
                    these_users.append(person)

            all_messages = the_admin.person.messages.all()

            isUnread = False

            for message in all_messages:
                if message.read == False:
                    isUnread = True

            # all_titles = []

            # for message in all_messages:
            #     all_titles.append(message.title)

            # change_pwd = False

            # if 'Warning' in all_titles:
            #     change_pwd = True

            # new

            # paginator = Paginator(these_users, 10)

            # page_number = request.GET.get('page')
            # page_obj = paginator.get_page(page_number)

            # now we shall get all of the users that are not in the current project
            non_project_users = []

            all_users = institution.users.all()

            every_user = project.users.all()

            for my_user in all_users:
                if my_user in every_user:
                    continue
                else:
                    non_project_users.append(my_user)

            if request.method == "POST":

                if "pruser_edit" in request.POST:

                    id = request.POST['hidden_pruser_input']

                    this_user = User.objects.get(pk = id)

                    role = request.POST['role_assignment']

                    if this_user in all_pm:
                        institution.project_manager.remove(this_user)
                        institution.save()

                        project.project_manager.remove(this_user)
                        project.save()

                        all_projects = institution.projects.all()

                        for this_project in all_projects:
                            if this_user in this_project.project_manager.all():
                                this_project.project_manager.remove(this_user)
                                this_project.users.remove(this_user)
                                this_project.save()

                                string = f'User with email: {this_user.email} has been removed from Project: {this_project.title}, because their role has been changed'
                                new_message = Message(title = 'Alert', message = string)
                                new_message.save()

                                for admin in this_project.admin.all():
                                    admin.person.messages.add(new_message)
                                    admin.save()

                                for pm in this_project.project_manager.all():
                                    pm.person.messages.add(new_message)
                                    pm.save()

                    elif this_user in all_devs:
                        institution.developers.remove(this_user)
                        institution.save()

                        project.developers.remove(this_user)
                        project.save()

                        all_projects = institution.projects.all()

                        for this_project in all_projects:
                            if this_user in this_project.developers.all():

                                this_project.developers.remove(this_user)
                                this_project.users.remove(this_user)
                                this_project.save()

                                string = f'User with email: {this_user.email}, has been removed from Project: {this_project.title}, because their role has been changed'
                                new_message = Message(title = 'Alert', message = string)
                                new_message.save()

                                for admin in this_project.admin.all():
                                    admin.person.messages.add(new_message)
                                    admin.save()

                                for pm in this_project.project_manager.all():
                                    pm.person.messages.add(new_message)
                                    pm.save()


                    elif this_user in all_submitters:
                        institution.submitters.remove(this_user)
                        institution.save()

                        project.submitters.remove(this_user)
                        project.save()

                        all_projects = institution.projects.all()

                        for this_project in all_projects:
                            if this_user in this_project.submitters.all():
                                this_project.submitters.remove(this_user)
                                this_project.users.remove(this_user)
                                this_project.save()

                                string = f'User with email: {this_user.email}, has been removed from Project: {this_project.title}, because their role has been changed'
                                new_message = Message(title = 'Alert', message = string)
                                new_message.save()

                                for admin in this_project.admin.all():
                                    admin.person.messages.add(new_message)
                                    admin.save()

                                for pm in this_project.project_manager.all():
                                    pm.person.messages.add(new_message)
                                    pm.save()

                    if role == 'admin':
                        institution.admin.add(this_user)
                        institution.save()

                        # new stuff
                        all_projects = institution.projects.all()

                        for project in all_projects:

                            if this_user in project.developers.all():
                                project.developers.remove(this_user)
                                project.save()
                            elif this_user in project.project_manager.all():
                                project.project_manager.remove(this_user)
                                project.save()
                            elif this_user in project.submitters.all():
                                project.submitters.remove(this_user)
                                project.save()

                            project.admin.add(this_user)
                            project.save()

                    elif role == 'project_manager':
                        institution.project_manager.add(this_user)
                        institution.save()

                        project.project_manager.add(this_user)
                        project.save()


                    elif role == 'developer':
                        institution.developers.add(this_user)
                        institution.save()

                        project.developers.add(this_user)
                        project.save() 

                    elif role == 'submitter':
                        institution.submitters.add(this_user)
                        institution.save()
                    
                        project.submitters.add(this_user)
                        project.save()

                    return HttpResponseRedirect(request.path_info)
                
                
                elif "add_non_pruser" in request.POST:

                    # users = request.POST.getlist('non_pruser_select')

                    ids = request.POST.getlist('non_pruser_select')

                    for id in ids:

                        # new new

                        this_person = User.objects.get(pk = id)

                        # this_person = User.objects.get(username = person)

                        if this_person in all_devs:
                            project.developers.add(this_person)
                            project.save()
                            project.users.add(this_person)
                            project.save()
                        elif this_person in all_pm:
                            project.project_manager.add(this_person)
                            project.save()
                            project.users.add(this_person)
                            project.save()
                        elif this_person in all_submitters:
                            project.submitters.add(this_person)
                            project.save()
                            project.users.add(this_person)
                            project.save()
                        else:
                            project.users.add(this_person)

                        
                    return HttpResponseRedirect(request.path_info)
                

                elif "pruser_remove" in request.POST:

                    id = request.POST['hidden_remove_input']

                    this_user = User.objects.get(pk = id)

                    if this_user in all_admin:
                        project.admin.remove(this_user)
                        project.save()
                        project.users.remove(this_user)
                        project.save()
                    elif this_user in all_pm:
                        project.project_manager.remove(this_user)
                        project.save()
                        project.users.remove(this_user)
                        project.save()
                    elif this_user in all_devs:
                        project.developers.remove(this_user)
                        project.save()
                        project.users.remove(this_user)
                        project.save()
                    elif this_user in all_submitters:
                        project.submitters.remove(this_user)
                        project.save()
                        project.users.remove(this_user)
                        project.save()
                    else:
                        project.users.remove(this_user)
                        project.save()

                    return HttpResponseRedirect(request.path_info)
                    
            return render(request, "debugger/admin_project_users.html", {
                'institution':institution, 'admin':the_admin, 'this_project':project, 'all_messages':all_messages, 'isUnread':isUnread, 'these_users':these_users, 'all_admin':all_admin, 'all_devs':all_devs, 'all_pm':all_pm, 'all_submitters':all_submitters, 'non_project_users':non_project_users, 'all_pending':all_pending
            })
        
        else:
            raise PermissionDenied()
    
    else:
        logout(request)
        return render(request, "debugger/index.html")


@login_required(login_url="/")
def admin_manage_projects(request, institution_id, admin_id):
    institution = Institution.objects.get(pk = institution_id)
    user = User.objects.get(pk = admin_id)

    if request.user in institution.admin.all():

        if request.user.id == admin_id:

            all_projects = institution.projects.all()

            all_admin = institution.admin.all()

            all_users = []

            for person in institution.users.all():
                if person in all_admin:
                    continue
                else:
                    all_users.append(person)

            all_devs = institution.developers.all()

            all_pm = institution.project_manager.all()

            all_submitters = institution.submitters.all()

            all_pending = institution.pending.all()
            
            all_messages = user.person.messages.all()

            isUnread = False

            for message in all_messages:
                if message.read == False:
                    isUnread = True

            # all_titles = []

            # for message in all_messages:
            #     all_titles.append(message.title)

            # change_pwd = False

            # if 'Warning' in all_titles:
            #     change_pwd = True

            if request.method == 'POST':

                if "project_create" in request.POST:

                    title = request.POST['project_title']
                    content = request.POST['project_description']

                    #new

                    for this_project in all_projects:
                        if this_project.title == title:
                            return render(request, "debugger/admin_manage_projects.html", {
                                'institution':institution, 'message': 'There already is a project with this title', 'admin':user, 'all_projects':all_projects, 'all_users':all_users, 'all_admin':all_admin, 'all_devs':all_devs, 'all_pm':all_pm, 'all_submitters':all_submitters, 'all_messages':all_messages, 'isUnread':isUnread, 'all_pending':all_pending
                            })
                        else:
                            continue                            

                    new_project = Project(title = title, description = content)
                    new_project.save()


                    # here we will add all of the admin in the institution to the project by default
                    for person in all_admin:
                        new_project.admin.add(person)
                        new_project.save()
                        new_project.users.add(person)
                        new_project.save()

                    if user in all_pm:
                        new_project.project_manager.add(user)
                        new_project.save()
                        new_project.users.add(user)
                        new_project.save()

                        # new new

                    ids = request.POST.getlist('select_users')

                    for id in ids:

                        this_person = User.objects.get(pk = id)

                        if this_person in all_devs:
                            new_project.developers.add(this_person)
                            new_project.save()
                            new_project.users.add(this_person)
                            new_project.save()
                        elif this_person in all_pm:
                            new_project.project_manager.add(this_person)
                            new_project.save()
                            new_project.users.add(this_person)
                            new_project.save()
                        elif this_person in all_submitters:
                            new_project.submitters.add(this_person)
                            new_project.save()
                            new_project.users.add(this_person)
                            new_project.save()
                        else:
                            new_project.users.add(this_person)
                            new_project.save()

                    institution.projects.add(new_project)
                    institution.save()
                    return HttpResponseRedirect(request.path_info)


                    # now that we have the list of users, we will need to check what roles these users have, then ultimately put all of the information into a new Project instance

            return render(request, "debugger/admin_manage_projects.html", {
                'institution':institution, 'admin':user, 'all_projects':all_projects, 'all_users':all_users, 'all_admin':all_admin, 'all_devs':all_devs, 'all_pm':all_pm, 'all_submitters':all_submitters, 'all_messages':all_messages, 'isUnread':isUnread, 'all_pending':all_pending
            })
        
        else:
            raise PermissionDenied()
    
    else:
        logout(request)
        return render(request, "debugger/index.html")


@login_required(login_url="/")
def notifications(request, institution_id, admin_id):
    user = User.objects.get(pk = admin_id)

    institution = Institution.objects.get(pk = institution_id)

    if request.user in institution.admin.all():

        if request.user.id == admin_id:

            user_messages = user.person.messages.all()

            all_pending = institution.pending.all()

            user_messages = user_messages.order_by("-timestamp").all()

            # all_titles = []

            # for message in user_messages:
            #     all_titles.append(message.title)

            # change_pwd = False

            # if 'Warning' in all_titles:
            #     change_pwd = True

            for message in user_messages:
                message.read = True
                message.save()

            isUnread = False

            return render(request, "debugger/notifications.html", {
                'institution':institution, 'admin':user, 'all_messages':user_messages, 'isUnread':isUnread, 'user_messages':user_messages, 'all_pending':all_pending
            })
        
        else:
            raise PermissionDenied()
    
    else:
        logout(request)
        return render(request ,"debugger/index.html")


@login_required(login_url="/")
def admin_manage_tickets(request, institution_id, admin_id):
    institution = Institution.objects.get(pk = institution_id)
    user = User.objects.get(pk = admin_id)

    if request.user in institution.admin.all():

        if request.user.id == admin_id:

            all_pending = institution.pending.all()

            all_messages = user.person.messages.all()

            isUnread = False

            for message in all_messages:
                if message.read == False:
                    isUnread = True

            # all_titles = []

            # for message in all_messages:
            #     all_titles.append(message.title)

            # change_pwd = False

            # if 'Warning' in all_titles:
            #     change_pwd = True

            all_projects = institution.projects.all()

            all_bugs = []

            for project in all_projects:
                for bug in project.bugs.all():
                    all_bugs.append(bug)

            if request.method == "POST":

                if 'ticket_submit' in request.POST:

                    this_bug_id = request.POST['hidden_ticket']

                    this_bug = Bug.objects.get(pk = this_bug_id)

                    new_title = request.POST['ticket_title']

                    if (this_bug.title != new_title):

                        for bug in all_bugs:
                            if bug.title == new_title:
                                return render(request, "debugger/admin_manage_tickets.html", {
                                    'institution':institution, 'message':'There already is a ticket with this title', 'message_bug':this_bug, 'message_bug_dev':this_bug.developer, 'admin':user, 'all_messages':all_messages, 'isUnread':isUnread, 'all_bugs':all_bugs, 'all_projects':all_projects, 'all_pending':all_pending
                                })
                            else:
                                continue                                

                        history = History(bug = this_bug, old = this_bug.title, new = new_title, property = 'Title Altered', changer = user)
                        history.save()

                        updated_time = history.date

                        this_bug.title = new_title
                        this_bug.updated = updated_time
                        this_bug.save()

                    new_description = request.POST['ticket_description']

                    if (this_bug.content != new_description):
                        history = History(bug = this_bug, old = this_bug.content, new = new_description, property = 'Description Altered', changer = user)
                        history.save()

                        updated_time = history.date

                        this_bug.content = new_description
                        this_bug.updated = updated_time
                        this_bug.save()    

                    new_type = request.POST['ticket_type']

                    if (this_bug.type != new_type):
                        history = History(bug = this_bug, old = this_bug.type, new = new_type, property = "Type Altered", changer = user)
                        history.save()

                        updated_time = history.date

                        this_bug.type = new_type
                        this_bug.updated = updated_time
                        this_bug.save()

                    new_priority = request.POST['ticket_priority']

                    if (this_bug.priority != new_priority):
                        history = History(bug = this_bug, old = this_bug.priority, new = new_priority, property = "Priority Altered", changer = user)
                        history.save()

                        updated_time = history.date

                        this_bug.priority = new_priority
                        this_bug.updated = updated_time
                        this_bug.save()            

                    new_project_id = request.POST['ticket_project']

                    new_project = Project.objects.get(pk = new_project_id)

                    bug_project = []

                    for project in this_bug.project_bugs.all():
                        bug_project.append(project)

                    this_bug_project = bug_project[0]

                    if (this_bug_project.title != new_project.title):
                        history = History(bug = this_bug, old = this_bug_project.title, new = new_project.title, property = "Project Reassigned", changer = user)
                        history.save()

                        updated_time = history.date

                        this_b_project = Project.objects.get(pk = this_bug_project.id)

                        this_b_project.bugs.remove(this_bug)
                        this_b_project.save()

                        new_project.bugs.add(this_bug)
                        new_project.save()

                        this_bug.updated = updated_time
                        this_bug.save()            

                    new_status = request.POST['status_update']

                    if (this_bug.status != new_status):
                        history = History(bug = this_bug, old = this_bug.status, new = new_status, property = "Status Upated", changer = user)
                        history.save()

                        updated_time = history.date

                        this_bug.status = new_status
                        this_bug.updated = updated_time
                        this_bug.save()

                        if new_status == 'Additional Info Required':

                            string = f'You have been asked to provide additional information on ticket: {this_bug.title} in Project: {new_project}'

                            info_message = Message(title = 'Important', message = string)
                            info_message.save()

                            bug_submitter = this_bug.submitter

                            bug_submitter.person.messages.add(info_message)
                            bug_submitter.save()

                    # new new

                    new_developer_email = request.POST['ticket_developer_email']

                    # if (this_bug.developer == None or this_bug.developer.username != new_developer):
                    if (this_bug.developer == None or this_bug.developer.email != new_developer_email):

                        # if new_developer == 'None':
                        if (new_developer_email == 'None' or new_developer_email == ''):
                            
                            if this_bug.developer != None:
                                
                                this_bug.developer = None
                                this_bug.save()

                        # elif User.objects.filter(username = new_developer).exists():
                        elif User.objects.filter(institution_user__name = institution.name, email = new_developer_email).exists():

                            # this_dev = User.objects.get(username = new_developer)
                            this_dev = User.objects.get(institution_user__name = institution.name, email = new_developer_email)

                            if this_dev in new_project.developers.all():

                                if this_bug.developer != None:

                                    history = History(bug = this_bug, old = this_bug.developer.email, new = new_developer_email, property = "New Developer Assigned", changer = user)
                                    history.save()

                                    updated_time = history.date

                                    this_bug.developer = this_dev
                                    this_bug.updated = updated_time
                                    this_bug.save()

                                else:

                                    history = History(bug = this_bug, old = 'None', new = new_developer_email, property = "New Developer Assigned", changer = user)
                                    history.save()

                                    updated_time = history.date

                                    this_bug.developer = this_dev
                                    this_bug.updated = updated_time
                                    this_bug.save()

                            else:

                                string = f'The developer with the email: {new_developer_email}, is not an authorized developer of the Project you have specified, please try again'

                                return render(request, "debugger/admin_manage_tickets.html", {
                                    'institution':institution, 'message': string, 'message_bug':this_bug, 'message_bug_dev':this_bug.developer, 'admin':user, 'all_messages':all_messages, 'isUnread':isUnread, 'all_bugs':all_bugs, 'all_projects':all_projects, 'all_pending':all_pending
                                })
                                # new_message = Message(title = 'Error', message = string)
                                # new_message.save()

                                # user.person.messages.add(new_message)
                                # user.save()

                        else:

                            string = f'The developer with the email: {new_developer_email} cannot be found, please try again'

                            return render(request, "debugger/admin_manage_tickets.html", {
                                'institution':institution, 'message': string, 'message_bug':this_bug, 'message_bug_dev':this_bug.developer, 'admin':user, 'all_messages':all_messages, 'isUnread':isUnread, 'all_bugs':all_bugs, 'all_projects':all_projects, 'all_pending':all_pending
                            })

                            # new_message = Message(title = 'Error', message = string)
                            # new_message.save()

                            # user.person.messages.add(new_message)
                            # user.save()

                all_messages = user.person.messages.all()

                isUnread = False

                for message in all_messages:
                    if message.read == False:
                        isUnread = True

                # all_titles = []

                # for message in all_messages:
                #     all_titles.append(message.title)

                # change_pwd = False

                # if 'Warning' in all_titles:
                #     change_pwd = True

                return HttpResponseRedirect(request.path_info)

            return render(request, "debugger/admin_manage_tickets.html", {
                'institution':institution, 'admin':user, 'all_messages':all_messages, 'isUnread':isUnread, 'all_bugs':all_bugs, 'all_projects':all_projects, 'all_pending':all_pending
            })
        else:
            raise PermissionDenied()

    else:
        logout(request)
        return render(request, "debugger/index.html")


@login_required(login_url="/")
def admin_ticket_details(request, institution_id, admin_id, ticket_id):
    institution = Institution.objects.get(pk = institution_id)
    user = User.objects.get(pk = admin_id)

    if request.user in institution.admin.all():

        if request.user.id == admin_id:

            bug = Bug.objects.get(pk = ticket_id)

            all_pending = institution.pending.all()

            all_messages = user.person.messages.all()

            isUnread = False

            for message in all_messages:
                if message.read == False:
                    isUnread = True

            # all_titles = []

            # for message in all_messages:
            #     all_titles.append(message.title)

            # change_pwd = False

            # if 'Warning' in all_titles:
            #     change_pwd = True
        
            this_dev = bug.developer

            this_submitter = bug.submitter

            bug_project = []

            for project in bug.project_bugs.all():
                bug_project.append(project)

            this_project = bug_project[0]

            update_date = bug.updated

            this_history = History.objects.filter(bug = bug)

            this_history = this_history.order_by("-date").all()

            # paginator = Paginator(this_history, 5)
            # page_number = request.GET.get('page')
            # page_obj = paginator.get_page(page_number)

            # new stuff

            # all_properties = []

            # all_dates = []

            # all_changers = []

            # for history in this_history:
            #     all_properties.append(history.property)
            #     all_dates.append(history.date)
            #     all_changers.append(history.changer)


            # property_paginator = Paginator(all_properties, 5)
            # property_page_number = request.GET.get('page')
            # property_page_obj = property_paginator.get_page(property_page_number)

            # dates_paginator = Paginator(all_dates, 5)
            # dates_page_number = request.GET.get('page')
            # dates_page_obj = dates_paginator.get_page(dates_page_number)

            # changer_paginator = Paginator(all_changers, 5)
            # changer_page_number = request.GET.get('page')
            # changer_page_obj = changer_paginator.get_page(changer_page_number)


            all_bug_comments = bug.comments.all()

            all_bug_comments = all_bug_comments.order_by("-timestamp").all()

            # new_paginator = Paginator(all_bug_comments, 5)
            # new_page_number = request.GET.get('page')
            # new_page_obj = new_paginator.get_page(new_page_number)

            if request.method == "POST":

                if 'comment_create' in request.POST:

                    string = request.POST['create_ticket_comment']

                    new_comment = Message(message = string, commenter = user)
                    new_comment.save()

                    bug.comments.add(new_comment)
                    bug.save()

                    submitter = bug.submitter

                    developer = bug.developer

                    new_string = f'User with email {user.email}, has left a comment on Ticket: {bug.title} in Project: {this_project.title}'

                    newer_comment = Message(title = 'New Comment', message = new_string, commenter = user)
                    newer_comment.save()

                    submitter.person.messages.add(newer_comment)
                    submitter.save()

                    if (developer != None):
                        developer.person.messages.add(newer_comment)
                        developer.save()

                    return HttpResponseRedirect(request.path_info)

            return render(request, "debugger/admin_ticket_details.html", {
                'institution':institution, 'admin':user, 'bug':bug, 'isUnread':isUnread, 'all_messages':all_messages, 'this_dev':this_dev, 'this_submitter':this_submitter, 'this_project':this_project, 'updated':update_date, 'this_history':this_history, 'all_bug_comments':all_bug_comments, 'all_pending':all_pending
            })
        
        else:
            raise PermissionDenied()
    
    else:
        logout(request)
        return render(request, "debugger/index.html")


@login_required(login_url="/")
def admin_project_details(request, institution_id, admin_id, project_id):
    institution = Institution.objects.get(pk = institution_id)
    user = User.objects.get(pk = admin_id)

    if request.user in institution.admin.all():

        project = Project.objects.get(pk = project_id)

        all_pending = institution.pending.all()

        all_messages = user.person.messages.all()

        isUnread = False

        for message in all_messages:
            if message.read == False:
                isUnread = True

        # all_titles = []

        # for message in all_messages:
        #     all_titles.append(message.title)

        # change_pwd = False

        # if 'Warning' in all_titles:
        #     change_pwd = True

        all_users = project.users.all()

        all_admin = institution.admin.all()

        all_devs = institution.developers.all()

        all_submitters = institution.submitters.all()

        all_pm = institution.project_manager.all()

        all_bugs = project.bugs.all()

        return render(request, "debugger/admin_project_details.html", {
            'institution':institution, 'admin':user, 'project':project, 'all_messages':all_messages, 'isUnread':isUnread, 'all_users':all_users, 'all_admin':all_admin, 'all_devs':all_devs, 'all_submitters':all_submitters, 'all_pm':all_pm, 'all_bugs':all_bugs, 'all_pending':all_pending
        })
    
    else:
        logout(request)
        return render(request, "debugger/index.html")


@login_required(login_url="/")
def submitter(request, institution_id, user_id):
    user = User.objects.get(pk = user_id)
    institution = Institution.objects.get(pk = institution_id)

    if request.user in institution.submitters.all():

        if request.user.id == user_id:

            all_messages = user.person.messages.all()

            isUnread = False

            for message in all_messages:
                if message.read == False:
                    isUnread = True

            # check if this person is associated with a project first

            inProject = False

            all_projects = institution.projects.all()

            these_projects = []

            for project in all_projects:
                if user in project.submitters.all():
                    inProject = True
                    these_projects.append(project)
                else:
                    continue

            all_bugs = []

            for project in these_projects:
                for bug in project.bugs.all():
                    all_bugs.append(bug)
            
            all_my_bugs = []

            for bug in all_bugs:
                if user == bug.submitter:
                    all_my_bugs.append(bug)

            all_resolved = []

            for bug in all_my_bugs:
                if bug.status == "Resolved":
                    all_resolved.append(bug)

            everythingResolved = False

            if len(all_my_bugs) == len(all_resolved):
                everythingResolved = True

            
            all_low = []

            all_medium = []

            all_high = []

            all_errors = []

            all_requests = []

            all_other = []

            all_new = []

            all_open = []

            all_progress = []

            all_additional = []

            for bug in all_my_bugs:
                if bug.priority == 'Low' and bug.status != 'Resolved':
                    all_low.append(bug)
                elif bug.priority == 'Medium' and bug.status != 'Resolved':
                    all_medium.append(bug)
                elif bug.priority == 'High' and bug.status != 'Resolved':
                    all_high.append(bug)

                if bug.type == 'Bugs/Errors' and bug.status != 'Resolved':
                    all_errors.append(bug)
                elif bug.type == 'Additional Feature Requests' and bug.status != 'Resolved':
                    all_requests.append(bug)
                elif bug.type == 'Other' and bug.status != 'Resolved':
                    all_other.append(bug)

                if bug.status == 'New':
                    all_new.append(bug)
                elif bug.status == 'Open':
                    all_open.append(bug)
                elif bug.status == 'In Progress':
                    all_progress.append(bug)
                elif bug.status == 'Additional Info Required':
                    all_additional.append(bug)
            
            return render(request, "debugger/submitter.html", {
                'institution':institution, 'user':user, 'all_messages':all_messages, 'isUnread':isUnread, 'inProject':inProject, 'all_my_bugs':all_my_bugs ,'all_bugs':all_bugs, 'everythingResolved':everythingResolved, 'these_projects':these_projects, 'low':len(all_low), 'med':len(all_medium), 'high':len(all_high), 'errors':len(all_errors), 'requests':len(all_requests), 'other':len(all_other), 'new':len(all_new), 'open':len(all_open), 'progress':len(all_progress), 'info':len(all_additional), 'resolved':len(all_resolved)
            })
        else:
            raise PermissionDenied()

    else:
        logout(request)
        return render(request, "debugger/index.html")


@login_required(login_url="/")
def submitter_leave(request, institution_id, user_id):
    user = User.objects.get(pk = user_id)
    institution = Institution.objects.get(pk = institution_id)

    if request.user in institution.submitters.all():

        if request.user.id == user_id:

            all_messages = user.person.messages.all()

            isUnread = False

            for message in all_messages:
                if message.read == False:
                    isUnread = True

            inProject = False

            all_projects = institution.projects.all()

            these_projects = []

            for project in all_projects:
                if user in project.submitters.all():
                    inProject = True
                    these_projects.append(project)
                else:
                    continue

            all_bugs = []

            for project in these_projects:
                for bug in project.bugs.all():
                    all_bugs.append(bug)

            
            all_my_bugs = []

            for bug in all_bugs:
                if user == bug.submitter:
                    all_my_bugs.append(bug)

            
            all_low = []

            all_medium = []

            all_high = []

            all_errors = []

            all_requests = []

            all_other = []

            all_new = []

            all_open = []

            all_progress = []

            all_additional = []

            for bug in all_my_bugs:
                if bug.priority == 'Low':
                    all_low.append(bug)
                elif bug.priority == 'Medium':
                    all_medium.append(bug)
                elif bug.priority == 'High':
                    all_high.append(bug)

                if bug.type == 'Bugs/Errors':
                    all_errors.append(bug)
                elif bug.type == 'Additional Feature Requests':
                    all_requests.append(bug)
                elif bug.type == 'Other':
                    all_other.append(bug)

                if bug.status == 'New':
                    all_new.append(bug)
                elif bug.status == 'Open':
                    all_open.append(bug)
                elif bug.status == 'In Progress':
                    all_progress.append(bug)
                elif bug.status == 'Additional Info Required':
                    all_additional.append(bug)

            if request.method == "POST":

                if 'leave_confirm' in request.POST:

                    institution.submitters.remove(user)

                    institution.users.remove(user)
                    institution.save()

                    user.delete()

                    institution_users = institution.users.all()

                    if ( len(institution_users) == 0 ):
                        institution.delete()

                    logout(request)

                    return render(request, "debugger/index.html")

                elif 'leave_deny' in request.POST:

                    return render(request, "debugger/submitter.html", {
                        'institution':institution, 'user':user, 'all_messages':all_messages, 'isUnread':isUnread, 'inProject':inProject ,'all_bugs':all_bugs, 'these_projects':these_projects, 'low':len(all_low), 'med':len(all_medium), 'high':len(all_high), 'errors':len(all_errors), 'requests':len(all_requests), 'other':len(all_other), 'new':len(all_new), 'open':len(all_open), 'progress':len(all_progress), 'info':len(all_additional)
                    })

            return render(request, "debugger/submitter_leave.html", {
                'institution':institution, 'user':user, 'isUnread':isUnread, 'inProject':inProject
            })
        
        else:
            raise PermissionDenied
        
    else:
        return render(request, 'debugger/index.html')


@login_required(login_url="/")
def submitter_view_ticket(request, institution_id, user_id):
    user = User.objects.get(pk = user_id)
    institution = Institution.objects.get(pk = institution_id)

    if request.user in institution.submitters.all():

        if request.user.id == user_id:

            all_messages = user.person.messages.all()

            isUnread = False

            for message in all_messages:
                if message.read == False:
                    isUnread = True

            inProject = False

            all_projects = institution.projects.all()

            these_projects = []

            for project in all_projects:
                if user in project.submitters.all():
                    inProject = True
                    these_projects.append(project)
                else:
                    continue

            all_bugs = []

            for project in these_projects:
                for bug in project.bugs.all():
                    all_bugs.append(bug)

            my_bugs = Bug.objects.filter(submitter = user)

            change_bug = Bug.objects.filter(submitter = user, status = 'Additional Info Required')

            for bug in my_bugs:
                if bug in all_bugs:
                    continue
                else:
                    all_bugs.append(bug)

            if request.method == 'POST':

                if 'ticket_submit' in request.POST:

                    project_id = request.POST['ticket_project']

                    this_project = Project.objects.get(pk = project_id)

                    title = request.POST['ticket_title']
                    description = request.POST['ticket_description']
                    type = request.POST['ticket_type']
                    priority = request.POST['ticket_priority']
                    status = request.POST['ticket_status']

                    inst_projects = institution.projects.all()

                    every_bug = []

                    for exact_project in inst_projects:
                        for exact_project_bug in exact_project.bugs.all():
                            every_bug.append(exact_project_bug)

                    for exact_bug in every_bug:
                        if exact_bug.title == title:
                            return render(request, "debugger/submitter_view_tickets.html", {
                                'institution':institution, 'message': 'There already is a ticket with this title', 'user':user, 'all_messages':all_messages, 'isUnread':isUnread, 'inProject':inProject, 'all_bugs':all_bugs, 'these_projects':these_projects, 'change_bug':change_bug
                            })
                        else:
                            continue

                    new_bug = Bug(title = title, content = description, type = type, status = status, priority = priority, submitter = user)
                    new_bug.save()
                    this_project.bugs.add(new_bug)
                    this_project.save()

                elif 'action_ticket_submit' in request.POST:

                    new_title = request.POST['ticket_title']

                    new_description = request.POST['ticket_description']

                    bugid = request.POST['hidden_ticket']

                    this_bug = Bug.objects.get(pk = bugid)

                    bug_project = []

                    for project in bug.project_bugs.all():
                        bug_project.append(project)

                    this_project = bug_project[0]

                    if (this_bug.title == new_title and this_bug.content == new_description):

                        string = f'Please try again, as you have not added the additional information as requested for Ticket: {this_bug.title} in Project: {this_project.title}'
                        new_message = Message(title = 'Alert', message = string)
                        new_message.save()

                        user.person.messages.add(new_message)
                        user.save()

                    elif (this_bug.title == new_title):
                        
                        new_history = History(bug = this_bug, old = this_bug.content, new = new_description, property = 'Additional Info Added', changer = user)
                        new_history.save()

                        updated_time = new_history.date
                        this_bug.content = new_description
                        this_bug.updated = updated_time
                        this_bug.status = 'New'
                        this_bug.save()

                    elif (this_bug.content == new_description):

                        inst_projects = institution.projects.all()

                        every_bug = []

                        for exact_project in inst_projects:
                            for exact_project_bug in exact_project.bugs.all():
                                every_bug.append(exact_project_bug)

                        for exact_bug in every_bug:
                            if exact_bug.title == new_title:

                                this_proj = []

                                for project in this_bug.project_bugs.all():
                                    this_proj.append(project)

                                our_project = this_proj[0]

                                return render(request, "debugger/submitter_view_tickets.html", {
                                    'institution':institution, 'message': 'Please choose a different title', 'message_bug':this_bug, 'message_bug_project':our_project, 'user':user, 'all_messages':all_messages, 'isUnread':isUnread, 'inProject':inProject, 'all_bugs':all_bugs, 'these_projects':these_projects, 'change_bug':change_bug
                                })

                            else:
                                continue
                        

                        new_history = History(bug = this_bug, old = this_bug.title, new = new_title, property = 'Additional Info Added', changer = user)
                        new_history.save()

                        updated_time = new_history.date
                        
                        this_bug.title = new_title
                        this_bug.updated = updated_time
                        this_bug.status = 'New'
                        this_bug.save()

                    else:

                        inst_projects = institution.projects.all()

                        every_bug = []

                        for exact_project in inst_projects:
                            for exact_project_bug in exact_project.bugs.all():
                                every_bug.append(exact_project_bug)

                        for exact_bug in every_bug:
                            if exact_bug.title == new_title:

                                this_proj = []

                                for project in this_bug.project_bugs.all():
                                    this_proj.append(project)

                                our_project = this_proj[0]
                                
                                return render(request, "debugger/submitter_view_tickets.html", {
                                    'institution':institution, 'message': 'Please choose a different title', 'message_bug':this_bug, 'message_bug_project':our_project, 'user':user, 'all_messages':all_messages, 'isUnread':isUnread, 'inProject':inProject, 'all_bugs':all_bugs, 'these_projects':these_projects, 'change_bug':change_bug
                                })

                            else:
                                continue

                        new_history = History(bug = this_bug, old = this_bug.content, new = new_description, property = 'Additional Info added', changer = user)
                        new_history.save()

                        newer_history = History(bug = this_bug, old = this_bug.title, new = new_title, property = 'Additional Info added', changer = user)
                        newer_history.save()

                        updated_time = newer_history.date

                        this_bug.title = new_title
                        this_bug.content = new_description
                        this_bug.updated = updated_time
                        this_bug.status = 'New'
                        this_bug.save()

                return HttpResponseRedirect(request.path_info)

            return render(request, "debugger/submitter_view_tickets.html", {
                'institution':institution, 'user':user, 'all_messages':all_messages, 'isUnread':isUnread, 'inProject':inProject, 'all_bugs':all_bugs, 'these_projects':these_projects, 'change_bug':change_bug
            })
        else:
            raise PermissionDenied()

    else:
        logout(request)
        return render(request, "debugger/index.html")


@login_required(login_url="/")
def submitter_ticket_details(request, institution_id, user_id, ticket_id):
    institution = Institution.objects.get(pk = institution_id)
    user = User.objects.get(pk = user_id)

    if request.user in institution.submitters.all():

        if request.user.id == user_id:

            bug = Bug.objects.get(pk = ticket_id)

            inProject = False

            all_projects = institution.projects.all()

            these_projects = []

            for project in all_projects:
                if user in project.submitters.all():
                    inProject = True
                    these_projects.append(project)
                else:
                    continue

            all_messages = user.person.messages.all()

            isUnread = False

            for message in all_messages:
                if message.read == False:
                    isUnread = True

            this_dev = bug.developer

            this_submitter = bug.submitter

            bug_project = []

            for project in bug.project_bugs.all():
                bug_project.append(project)

            this_project = bug_project[0]

            update_date = bug.updated

            this_history = History.objects.filter(bug = bug)

            this_history = this_history.order_by("-date").all()

            all_bug_comments = bug.comments.all()

            all_bug_comments = all_bug_comments.order_by("-timestamp").all()

            return render(request, "debugger/submitter_ticket_details.html", {
                'institution':institution, 'user':user, 'bug':bug, 'inProject':inProject, 'isUnread':isUnread, 'this_dev':this_dev, 'this_submitter':this_submitter, 'this_project':this_project, 'updated':update_date, 'this_history':this_history, 'all_bug_comments':all_bug_comments
            })
        else:
            raise PermissionDenied()

    else:
        logout(request)
        return render(request, "debugger/index.html")


@login_required(login_url="/")
def submitter_notifications(request, institution_id, user_id):
    user = User.objects.get(pk = user_id)

    institution = Institution.objects.get(pk = institution_id)

    if request.user in institution.submitters.all():

        if request.user.id == user_id:

            user_messages = user.person.messages.all()

            user_messages = user_messages.order_by("-timestamp").all()

            for message in user_messages:
                message.read = True
                message.save()

            isUnread = False

            inProject = False

            all_projects = institution.projects.all()

            for project in all_projects:
                if user in project.users.all():
                    inProject = True
                    break
                else:
                    continue

            return render(request, "debugger/submitter_notifications.html", {
                'institution':institution, 'user':user, 'isUnread':isUnread, 'user_messages':user_messages, 'inProject':inProject
            })
        else:
            raise PermissionDenied()

    else:
        logout(request)
        return render(request, "debugger/index.html")


@login_required(login_url="/")
def developer(request, institution_id, user_id):
    user = User.objects.get(pk = user_id)
    institution = Institution.objects.get(pk = institution_id)

    if request.user in institution.developers.all():

        if request.user.id == user_id:

            inProject = False

            these_projects = []

            all_projects = institution.projects.all()

            for project in all_projects:
                if user in project.developers.all():
                    inProject = True
                    these_projects.append(project)
                else:
                    continue

            all_bugs = []

            every_bug = []

            for project in these_projects:
                for bug in project.bugs.all():

                    every_bug.append(bug)

                    if user == bug.developer:
                        all_bugs.append(bug)

            all_resolved = []

            for bug in all_bugs:
                if bug.status == "Resolved":
                    all_resolved.append(bug)

            everythingResolved = False

            if len(all_bugs) == len(all_resolved):
                everythingResolved = True

            all_low = []

            all_medium = []

            all_high = []

            all_errors = []

            all_requests = []

            all_other = []

            all_new = []

            all_open = []

            all_progress = []

            all_additional = []

            for bug in all_bugs:
                if bug.priority == 'Low' and bug.status != 'Resolved':
                    all_low.append(bug)
                elif bug.priority == 'Medium' and bug.status != 'Resolved':
                    all_medium.append(bug)
                elif bug.priority == 'High' and bug.status != 'Resolved':
                    all_high.append(bug)

                if bug.type == 'Bugs/Errors' and bug.status != 'Resolved':
                    all_errors.append(bug)
                elif bug.type == 'Additional Feature Requests' and bug.status != 'Resolved':
                    all_requests.append(bug)
                elif bug.type == 'Other' and bug.status != 'Resolved':
                    all_other.append(bug)

                if bug.status == 'New':
                    all_new.append(bug)
                elif bug.status == 'Open':
                    all_open.append(bug)
                elif bug.status == 'In Progress':
                    all_progress.append(bug)
                elif bug.status == 'Additional Info Required':
                    all_additional.append(bug)

            all_messages = user.person.messages.all()

            isUnread = False

            for message in all_messages:
                if message.read == False:
                    isUnread = True


            return render(request, "debugger/developer.html", {
                'institution':institution, 'user':user, 'inProject':inProject, 'all_bugs':all_bugs, 'everythingResolved':everythingResolved, 'every_bug':every_bug, 'isUnread':isUnread, 'low':len(all_low), 'med':len(all_medium), 'high':len(all_high), 'errors':len(all_errors), 'requests':len(all_requests), 'other':len(all_other), 'new':len(all_new), 'open':len(all_open), 'progress':len(all_progress), 'info':len(all_additional), 'resolved':len(all_resolved)
            })
        
        else:
            raise PermissionDenied()
    
    else:
        logout(request)
        return render(request, "debugger/index.html")
    

@login_required(login_url="/")
def developer_leave(request, institution_id, user_id):
    user = User.objects.get(pk = user_id)
    institution = Institution.objects.get(pk = institution_id)

    if request.user in institution.developers.all():

        if request.user.id == user_id:

            inProject = False

            these_projects = []

            all_projects = institution.projects.all()

            for project in all_projects:
                if user in project.developers.all():
                    inProject = True
                    these_projects.append(project)
                else:
                    continue

            all_bugs = []

            every_bug = []

            for project in these_projects:
                for bug in project.bugs.all():

                    every_bug.append(bug)

                    if user == bug.developer:
                        all_bugs.append(bug)

            all_low = []

            all_medium = []

            all_high = []

            all_errors = []

            all_requests = []

            all_other = []

            all_new = []

            all_open = []

            all_progress = []

            all_additional = []

            for bug in all_bugs:
                if bug.priority == 'Low':
                    all_low.append(bug)
                elif bug.priority == 'Medium':
                    all_medium.append(bug)
                elif bug.priority == 'High':
                    all_high.append(bug)

                if bug.type == 'Bugs/Errors':
                    all_errors.append(bug)
                elif bug.type == 'Additional Feature Requests':
                    all_requests.append(bug)
                elif bug.type == 'Other':
                    all_other.append(bug)

                if bug.status == 'New':
                    all_new.append(bug)
                elif bug.status == 'Open':
                    all_open.append(bug)
                elif bug.status == 'In Progress':
                    all_progress.append(bug)
                elif bug.status == 'Additional Info Required':
                    all_additional.append(bug)

            all_messages = user.person.messages.all()

            isUnread = False

            for message in all_messages:
                if message.read == False:
                    isUnread = True

            if request.method == "POST":

                if 'leave_confirm' in request.POST:

                    institution.developers.remove(user)

                    institution.users.remove(user)
                    institution.save()

                    user.delete()

                    institution_users = institution.users.all()

                    if ( len(institution_users) == 0 ):
                        institution.delete()

                    logout(request)

                    return render(request, "debugger/index.html")

                elif 'leave_deny' in request.POST:

                    return render(request, "debugger/developer.html", {
                        'institution':institution, 'user':user, 'inProject':inProject, 'all_bugs':all_bugs, 'every_bug':every_bug, 'isUnread':isUnread, 'low':len(all_low), 'med':len(all_medium), 'high':len(all_high), 'errors':len(all_errors), 'requests':len(all_requests), 'other':len(all_other), 'new':len(all_new), 'open':len(all_open), 'progress':len(all_progress), 'info':len(all_additional)
                    })

            return render(request, "debugger/developer_leave.html", {
                'institution':institution, 'user':user, 'isUnread':isUnread, 'inProject':inProject, 'all_bugs':all_bugs
            })
        
        else:
            raise PermissionDenied
        
    else:
        return render(request, 'debugger/index.html')




@login_required(login_url="/")
def developer_view_tickets(request, institution_id, user_id):
    user = User.objects.get(pk = user_id)
    institution = Institution.objects.get(pk = institution_id)

    if request.user in institution.developers.all():

        if request.user.id == user_id:

            inProject = False

            these_projects = []

            all_messages = user.person.messages.all()

            isUnread = False

            for message in all_messages:
                if message.read == False:
                    isUnread = True

            all_projects = institution.projects.all()

            for project in all_projects:
                if user in project.developers.all():
                    inProject = True
                    these_projects.append(project)
                else:
                    continue

            all_bugs = []

            for project in these_projects:
                for bug in project.bugs.all():
                    if user == bug.developer:
                        all_bugs.append(bug)

            if request.method == "POST":

                if "update_ticket_status" in request.POST:

                    ticket_id = request.POST['hidden_ticket_id']

                    this_ticket = Bug.objects.get(pk = ticket_id)

                    old_status = this_ticket.status

                    new_status = request.POST['status_update']

                    old_priority = this_ticket.priority

                    new_priority = request.POST['ticket_priority_update']

                    if old_status != new_status:

                        this_bug_history = History(bug = this_ticket, old = old_status, new = new_status, property = 'Status Updated', changer = user)
                        this_bug_history.save()
                        update_time = this_bug_history.date

                        this_ticket.status = new_status
                        this_ticket.updated = update_time
                        this_ticket.save()

                    if old_priority != new_priority:

                        this_bug_history = History(bug = this_ticket, old = old_priority, new = new_priority, property = 'Priority Updated', changer = user)
                        this_bug_history.save()
                        update_time = this_bug_history.date

                        this_ticket.priority = new_priority
                        this_ticket.updated = update_time
                        this_ticket.save()

                    return HttpResponseRedirect(request.path_info)

            return render(request, "debugger/developer_view_tickets.html", {
                'institution':institution, 'user':user, 'inProject':inProject, 'all_bugs':all_bugs, 'isUnread':isUnread
            })
        else:
            raise PermissionDenied()
    
    else:
        logout(request)
        return render(request, "debugger/index.html")


@login_required(login_url="/")
def developer_ticket_details(request, institution_id, user_id, ticket_id):
    institution = Institution.objects.get(pk = institution_id)
    user = User.objects.get(pk = user_id)

    if request.user in institution.developers.all():

        if request.user.id == user_id:

            bug = Bug.objects.get(pk = ticket_id)

            inProject = False

            all_projects = institution.projects.all()

            these_projects = []

            for project in all_projects:
                if user in project.developers.all():
                    inProject = True
                    these_projects.append(project)
                else:
                    continue

            all_messages = user.person.messages.all()

            isUnread = False

            for message in all_messages:
                if message.read == False:
                    isUnread = True

            this_dev = bug.developer

            this_submitter = bug.submitter

            bug_project = []

            for project in bug.project_bugs.all():
                bug_project.append(project)

            this_project = bug_project[0]

            update_date = bug.updated

            this_history = History.objects.filter(bug = bug)

            this_history = this_history.order_by("-date").all()

            all_bug_comments = bug.comments.all()

            all_bug_comments = all_bug_comments.order_by("-timestamp").all()

            all_bugs = []

            for project in these_projects:
                for solo_bug in project.bugs.all():
                    if user == bug.developer:
                        all_bugs.append(solo_bug)

            return render(request, "debugger/developer_ticket_details.html", {
                'institution':institution, 'user':user, 'bug':bug, 'inProject':inProject, 'isUnread':isUnread, 'this_dev':this_dev, 'this_submitter':this_submitter, 'this_project':this_project, 'updated':update_date, 'this_history':this_history, 'all_bug_comments':all_bug_comments, 'all_bugs':all_bugs
            })
        
        else:

            raise PermissionDenied()
    
    else:
        logout(request)
        return render(request, "debugger/index.html")


@login_required(login_url="/")
def developer_notifications(request, institution_id, user_id):
    user = User.objects.get(pk = user_id)
    institution = Institution.objects.get(pk = institution_id)

    if request.user in institution.developers.all():

        if request.user.id == user_id:

            user_messages = user.person.messages.all()

            user_messages = user_messages.order_by("-timestamp").all()

            for message in user_messages:
                message.read = True
                message.save()

            isUnread = False

            inProject = False

            all_projects = institution.projects.all()

            these_projects = []

            for project in all_projects:
                if user in project.developers.all():
                    inProject = True
                    these_projects.append(project)
                else:
                    continue

            all_bugs = []

            for project in these_projects:
                for bug in project.bugs.all():
                    if user == bug.developer:
                        all_bugs.append(bug)

            return render(request, "debugger/developer_notifications.html", {
                'institution':institution, 'user':user, 'inProject':inProject, 'isUnread':isUnread, 'user_messages':user_messages, 'all_bugs':all_bugs
            })
        
        else:
            raise PermissionDenied()
    
    else:
        logout(request)
        return render(request, "debugger/index.html")


@login_required(login_url="/")
def pm(request, institution_id, user_id):
    institution = Institution.objects.get(pk = institution_id)
    user = User.objects.get(pk = user_id)

    if request.user in institution.project_manager.all():

        if request.user.id == user_id:

            these_projects = []

            inProject = False

            for project in institution.projects.all():
                if user in project.project_manager.all():
                    inProject = True
                    these_projects.append(project)

            all_bugs = []

            for project in these_projects:
                for bug in project.bugs.all():
                    all_bugs.append(bug)

            all_resolved = []

            for bug in all_bugs:
                if bug.status == "Resolved":
                    all_resolved.append(all_bugs)

            everythingResolved = False

            if len(all_bugs) == len(all_resolved):
                everythingResolved = True

            all_low = []

            all_medium = []

            all_high = []

            all_errors = []

            all_requests = []

            all_other = []

            all_new = []

            all_open = []

            all_progress = []

            all_additional = []

            for bug in all_bugs:
                if bug.priority == 'Low' and bug.status != 'Resolved':
                    all_low.append(bug)
                elif bug.priority == 'Medium' and bug.status != 'Resolved':
                    all_medium.append(bug)
                elif bug.priority == 'High' and bug.status != 'Resolved':
                    all_high.append(bug)

                if bug.type == 'Bugs/Errors' and bug.status != 'Resolved':
                    all_errors.append(bug)
                elif bug.type == 'Additional Feature Requests' and bug.status != 'Resolved':
                    all_requests.append(bug)
                elif bug.type == 'Other' and bug.status != 'Resolved':
                    all_other.append(bug)

                if bug.status == 'New':
                    all_new.append(bug)
                elif bug.status == 'Open':
                    all_open.append(bug)
                elif bug.status == 'In Progress':
                    all_progress.append(bug)
                elif bug.status == 'Additional Info Required':
                    all_additional.append(bug)


            all_messages = user.person.messages.all()

            isUnread = False

            for message in all_messages:
                if message.read == False:
                    isUnread = True


            return render(request, 'debugger/pm.html', {
                'institution':institution, 'user':user, 'isUnread':isUnread, 'inProject':inProject, 'these_projects':these_projects, 'all_bugs':all_bugs, 'everythingResolved':everythingResolved, 'low':len(all_low), 'med':len(all_medium), 'high':len(all_high), 'errors':len(all_errors), 'requests':len(all_requests), 'other':len(all_other), 'new':len(all_new), 'open':len(all_open), 'progress':len(all_progress), 'info':len(all_additional), 'resolved':len(all_resolved)
            })
        
        else:
            raise PermissionDenied()
    
    else:
        logout(request)
        return render(request, "debugger/index.html")


@login_required(login_url="/")
def pm_leave(request, institution_id, user_id):
    user = User.objects.get(pk = user_id)
    institution = Institution.objects.get(pk = institution_id)

    if request.user in institution.project_manager.all():

        if request.user.id == user_id:

            these_projects = []

            inProject = False

            for project in institution.projects.all():
                if user in project.project_manager.all():
                    inProject = True
                    these_projects.append(project)

            all_bugs = []

            for project in these_projects:
                for bug in project.bugs.all():
                    all_bugs.append(bug)


            all_low = []

            all_medium = []

            all_high = []

            all_errors = []

            all_requests = []

            all_other = []

            all_new = []

            all_open = []

            all_progress = []

            all_additional = []

            for bug in all_bugs:
                if bug.priority == 'Low':
                    all_low.append(bug)
                elif bug.priority == 'Medium':
                    all_medium.append(bug)
                elif bug.priority == 'High':
                    all_high.append(bug)

                if bug.type == 'Bugs/Errors':
                    all_errors.append(bug)
                elif bug.type == 'Additional Feature Requests':
                    all_requests.append(bug)
                elif bug.type == 'Other':
                    all_other.append(bug)

                if bug.status == 'New':
                    all_new.append(bug)
                elif bug.status == 'Open':
                    all_open.append(bug)
                elif bug.status == 'In Progress':
                    all_progress.append(bug)
                elif bug.status == 'Additional Info Required':
                    all_additional.append(bug)


            all_messages = user.person.messages.all()

            isUnread = False

            for message in all_messages:
                if message.read == False:
                    isUnread = True

            if request.method == "POST":

                if 'leave_confirm' in request.POST:

                    institution.project_manager.remove(user)

                    institution.users.remove(user)
                    institution.save()

                    user.delete()

                    institution_users = institution.users.all()

                    if ( len(institution_users) == 0 ):
                        institution.delete()

                    logout(request)

                    return render(request, "debugger/index.html")

                elif 'leave_deny' in request.POST:

                    return render(request, 'debugger/pm.html', {
                        'institution':institution, 'user':user, 'isUnread':isUnread, 'inProject':inProject, 'these_projects':these_projects, 'all_bugs':all_bugs, 'low':len(all_low), 'med':len(all_medium), 'high':len(all_high), 'errors':len(all_errors), 'requests':len(all_requests), 'other':len(all_other), 'new':len(all_new), 'open':len(all_open), 'progress':len(all_progress), 'info':len(all_additional)
                    })

            return render(request, "debugger/pm_leave.html", {
                'institution':institution, 'user':user, 'isUnread':isUnread, 'inProject':inProject
            })
        
        else:
            raise PermissionDenied
        
    else:
        return render(request, 'debugger/index.html')



@login_required(login_url="/")
def pm_view_tickets(request, institution_id, user_id):
    user = User.objects.get(pk = user_id)
    institution = Institution.objects.get(pk = institution_id)

    if request.user in institution.project_manager.all():

        if request.user.id == user_id:

            user_messages = user.person.messages.all()

            isUnread = False

            for message in user_messages:
                if message.read == False:
                    isUnread = True

            inProject = False

            all_projects = institution.projects.all()

            these_projects = []

            for project in all_projects:
                if user in project.project_manager.all():
                    inProject = True
                    these_projects.append(project)
                else:
                    continue

            all_bugs = []

            for project in these_projects:
                for bug in project.bugs.all():
                    all_bugs.append(bug)

            inst_projects = institution.projects.all()

            every_bug = []

            for exact_project in inst_projects:
                for exact_project_bug in exact_project.bugs.all():
                    every_bug.append(exact_project_bug)

            if request.method == "POST":

                if 'ticket_submit' in request.POST:

                    this_bug_id = request.POST['hidden_ticket']

                    this_bug = Bug.objects.get(pk = this_bug_id)

                    new_title = request.POST['ticket_title']

                    if (this_bug.title != new_title):

                        for bug in every_bug:
                            if bug.title == new_title:
                                return render(request, "debugger/pm_view_tickets.html", {
                                    'institution':institution, 'message':'There already is a ticket with this title', 'message_bug':this_bug, 'message_bug_dev':this_bug.developer, 'user':user, 'isUnread':isUnread, 'inProject':inProject, 'user_messages':user_messages, 'all_bugs':all_bugs, 'these_projects':these_projects
                                })
                            else:
                                continue                                

                        history = History(bug = this_bug, old = this_bug.title, new = new_title, property = 'Title Altered', changer = user)
                        history.save()

                        updated_time = history.date

                        this_bug.title = new_title
                        this_bug.updated = updated_time
                        this_bug.save()

                    new_description = request.POST['ticket_description']

                    if (this_bug.content != new_description):
                        history = History(bug = this_bug, old = this_bug.content, new = new_description, property = 'Description Altered', changer = user)
                        history.save()

                        updated_time = history.date

                        this_bug.content = new_description
                        this_bug.updated = updated_time
                        this_bug.save()    

                    new_type = request.POST['ticket_type']

                    if (this_bug.type != new_type):
                        history = History(bug = this_bug, old = this_bug.type, new = new_type, property = "Type Altered", changer = user)
                        history.save()

                        updated_time = history.date

                        this_bug.type = new_type
                        this_bug.updated = updated_time
                        this_bug.save()

                    new_priority = request.POST['ticket_priority']

                    if (this_bug.priority != new_priority):
                        history = History(bug = this_bug, old = this_bug.priority, new = new_priority, property = "Priority Altered", changer = user)
                        history.save()

                        updated_time = history.date

                        this_bug.priority = new_priority
                        this_bug.updated = updated_time
                        this_bug.save()            

                    new_project_id = request.POST['ticket_project']

                    new_project = Project.objects.get(pk =  new_project_id)

                    bug_project = []

                    for project in this_bug.project_bugs.all():
                        bug_project.append(project)

                    this_bug_project = bug_project[0]

                    if (this_bug_project.title != new_project.title):
                        history = History(bug = this_bug, old = this_bug_project.title, new = new_project, property = "Project Reassigned", changer = user)
                        history.save()

                        updated_time = history.date

                        this_b_project = Project.objects.get(pk = this_bug_project.id)

                        this_b_project.bugs.remove(this_bug)
                        this_b_project.save()

                        new_project.bugs.add(this_bug)
                        new_project.save()

                        this_bug.updated = updated_time
                        this_bug.save()            

                    new_status = request.POST['status_update']

                    if (this_bug.status != new_status):
                        history = History(bug = this_bug, old = this_bug.status, new = new_status, property = "Status Upated", changer = user)
                        history.save()

                        updated_time = history.date

                        this_bug.status = new_status
                        this_bug.updated = updated_time
                        this_bug.save()

                        if new_status == 'Additional Info Required':

                            string = f'You have been asked to provide additional information on ticket: {this_bug.title} in Project: {new_project}'

                            info_message = Message(title = 'Important', message = string)
                            info_message.save()

                            bug_submitter = this_bug.submitter

                            bug_submitter.person.messages.add(info_message)
                            bug_submitter.save()

                    # new new

                    new_developer_email = request.POST['ticket_developer_email']

                    # if (this_bug.developer == None or this_bug.developer.username != new_developer):
                    if (this_bug.developer == None or this_bug.developer.email != new_developer_email):

                        # if new_developer == 'None':
                        if (new_developer_email == 'None' or new_developer_email == ''):
                            
                            if this_bug.developer != None:
                                
                                this_bug.developer = None
                                this_bug.save()

                        # elif User.objects.filter(username = new_developer).exists():
                        elif User.objects.filter(institution_user__name = institution.name, email = new_developer_email).exists():

                            # this_dev = User.objects.get(username = new_developer)
                            this_dev = User.objects.get(institution_user__name = institution.name, email = new_developer_email)

                            if this_dev in new_project.developers.all():

                                if this_bug.developer != None:

                                    history = History(bug = this_bug, old = this_bug.developer.email, new = new_developer_email, property = "New Developer Assigned", changer = user)
                                    history.save()

                                    updated_time = history.date

                                    this_bug.developer = this_dev
                                    this_bug.updated = updated_time
                                    this_bug.save()

                                else:

                                    history = History(bug = this_bug, old = 'None', new = new_developer_email, property = "New Developer Assigned", changer = user)
                                    history.save()

                                    updated_time = history.date

                                    this_bug.developer = this_dev
                                    this_bug.updated = updated_time
                                    this_bug.save()

                            else:

                                string = f'The developer with the email: {new_developer_email}, is not an authorized developer of the Project you have specified, please try again'

                                return render(request, "debugger/pm_view_tickets.html", {
                                    'institution':institution, 'message': string, 'message_bug':this_bug, 'message_bug_dev':this_bug.developer, 'user':user, 'isUnread':isUnread, 'inProject':inProject, 'user_messages':user_messages, 'all_bugs':all_bugs, 'these_projects':these_projects
                                })
                                # new_message = Message(title = 'Error', message = string)
                                # new_message.save()

                                # user.person.messages.add(new_message)
                                # user.save()

                        else:

                            string = f'The developer with the email: {new_developer_email} cannot be found, please try again'

                            return render(request, "debugger/pm_view_tickets.html", {
                                'institution':institution, 'message': string, 'message_bug':this_bug, 'message_bug_dev':this_bug.developer, 'user':user, 'isUnread':isUnread, 'inProject':inProject, 'user_messages':user_messages, 'all_bugs':all_bugs, 'these_projects':these_projects
                            })

                            # new_message = Message(title = 'Error', message = string)
                            # new_message.save()

                            # user.person.messages.add(new_message)
                            # user.save()

                user_messages = user.person.messages.all()

                isUnread = False

                for message in user_messages:
                    if message.read == False:
                        isUnread = True

                return HttpResponseRedirect(request.path_info)

            return render(request, "debugger/pm_view_tickets.html", {
                'institution':institution, 'user':user, 'isUnread':isUnread, 'inProject':inProject, 'user_messages':user_messages, 'all_bugs':all_bugs, 'these_projects':these_projects
            })
        
        else:
            raise PermissionDenied()
    
    else:
        logout(request)
        return render(request, "debugger/index.html")


@login_required(login_url="/")
def pm_ticket_details(request, institution_id, user_id, ticket_id):
    institution = Institution.objects.get(pk = institution_id)
    user = User.objects.get(pk = user_id)

    if request.user in institution.project_manager.all():

        if request.user.id == user_id:

            bug = Bug.objects.get(pk = ticket_id)

            inProject = True

            all_messages = user.person.messages.all()

            isUnread = False

            for message in all_messages:
                if message.read == False:
                    isUnread = True
        
            this_dev = bug.developer

            this_submitter = bug.submitter

            bug_project = []

            for project in bug.project_bugs.all():
                bug_project.append(project)

            this_project = bug_project[0]

            update_date = bug.updated

            this_history = History.objects.filter(bug = bug)

            this_history = this_history.order_by("-date").all()

            all_bug_comments = bug.comments.all()

            all_bug_comments = all_bug_comments.order_by("-timestamp").all()

            if request.method == "POST":

                if 'comment_create' in request.POST:

                    string = request.POST['create_ticket_comment']

                    new_comment = Message(message = string, commenter = user)
                    new_comment.save()

                    bug.comments.add(new_comment)
                    bug.save()

                    submitter = bug.submitter

                    developer = bug.developer

                    new_string = f'User with email {user.email}, has left a comment on Ticket: {bug.title} in Project: {this_project.title}'

                    newer_comment = Message(title = 'New Comment', message = new_string, commenter = user)
                    newer_comment.save()

                    submitter.person.messages.add(newer_comment)
                    submitter.save()

                    if (developer != None):
                        developer.person.messages.add(newer_comment)
                        developer.save()

                    return HttpResponseRedirect(request.path_info)


            return render(request, "debugger/pm_ticket_details.html", {
                'institution':institution, 'user':user, 'bug':bug, 'isUnread':isUnread, 'all_messages':all_messages, 'this_dev':this_dev, 'this_submitter':this_submitter, 'this_project':this_project, 'updated':update_date, 'this_history':this_history, 'all_bug_comments':all_bug_comments, 'inProject':inProject
            })
        
        else:
            raise PermissionDenied()
    
    else:
        logout(request)
        return render(request, "debugger/index.html")


@login_required(login_url="/")
def pm_notifications(request, institution_id, user_id):
    institution = Institution.objects.get(pk = institution_id)
    user = User.objects.get(pk = user_id)

    if request.user in institution.project_manager.all():

        if request.user.id == user_id:

            user_messages = user.person.messages.all()

            user_messages = user_messages.order_by("-timestamp").all()

            for message in user_messages:
                message.read = True
                message.save()

            isUnread = False

            inProject = False

            all_projects = institution.projects.all()

            for project in all_projects:
                if user in project.project_manager.all():
                    inProject = True
                    break
                else:
                    continue

            return render(request, "debugger/pm_notifications.html", {
                'institution':institution, 'user':user, 'inProject':inProject, 'isUnread':isUnread, 'user_messages':user_messages
            })
        
        else:
            raise PermissionDenied()
    
    else:
        logout(request)
        return render(request, "debugger/index.html")


@login_required(login_url="/")
def pm_manage_projects(request, institution_id, user_id):
    institution = Institution.objects.get(pk = institution_id)
    user = User.objects.get(pk = user_id)

    if request.user in institution.project_manager.all():

        if request.user.id == user_id:

            inProject = False

            user_messages = user.person.messages.all()

            isUnread = False

            for message in user_messages:
                if message.read == False:
                    isUnread = True


            all_projects = institution.projects.all()

            these_projects = []

            for project in all_projects:
                if user in project.project_manager.all():
                    inProject = True
                    these_projects.append(project)
                else:
                    continue

            all_bugs = []

            for project in these_projects:
                for bug in project.bugs.all():
                    all_bugs.append(bug)

            
            all_admin = institution.admin.all()

            all_users = []

            for person in institution.users.all():
                if person in all_admin:
                    continue
                else:
                    all_users.append(person)

            all_devs = institution.developers.all()

            all_pm = institution.project_manager.all()

            all_submitters = institution.submitters.all()

            return render(request, "debugger/pm_manage_projects.html", {
                'institution':institution, 'user':user, 'isUnread':isUnread, 'inProject':inProject, 'these_projects':these_projects, 'all_projects':all_projects, 'all_bugs':all_bugs, 'all_admin':all_admin, 'all_users':all_users, 'all_pm':all_pm, 'all_devs':all_devs, 'all_submitters':all_submitters, 'user_messages':user_messages
            })
        
        else:
            raise PermissionDenied()
    
    else:
        logout(request)
        return render(request, "debugger/index.html")


@login_required(login_url="/")
def pm_manage_project_users(request, institution_id, user_id, project_id):
    institution = Institution.objects.get(pk = institution_id)
    user = User.objects.get(pk = user_id)

    if request.user in institution.project_manager.all():

        if request.user.id == user_id:

            project = Project.objects.get(pk = project_id)

            all_admin = institution.admin.all()

            all_devs = institution.developers.all()

            all_pm = institution.project_manager.all()

            all_submitters = institution.submitters.all()

            inProject = True

            these_users = []

            for person in project.users.all():
                if person in all_admin:
                    continue
                elif person in all_pm:
                    continue
                else:
                    these_users.append(person)

            user_messages = user.person.messages.all()

            isUnread = False

            for message in user_messages:
                if message.read == False:
                    isUnread = True

            # now we shall get all of the users that are not in the current project
            non_project_users = []

            all_users = institution.users.all()

            every_user = project.users.all()

            for my_user in all_users:
                if my_user in every_user:
                    continue
                elif my_user in all_pm:
                    continue
                else:
                    non_project_users.append(my_user)

            if request.method == "POST":

                if "pruser_edit" in request.POST:

                    id = request.POST['hidden_pruser_input']

                    this_user = User.objects.get(pk = id)

                    role = request.POST['role_assignment']

                    if this_user in all_devs:
                        institution.developers.remove(this_user)
                        institution.save()

                        project.developers.remove(this_user)
                        project.save()

                        all_projects = institution.projects.all()

                        for this_project in all_projects:
                            if this_user in this_project.developers.all():

                                this_project.developers.remove(this_user)
                                this_project.users.remove(this_user)
                                this_project.save()

                                string = f'User with email: {this_user.email}, has been removed from Project: {this_project.title}, because their role has been changed'
                                new_message = Message(title = 'Alert', message = string)
                                new_message.save()

                                for admin in this_project.admin.all():
                                    admin.person.messages.add(new_message)
                                    admin.save()

                                for pm in this_project.project_manager.all():
                                    pm.person.messages.add(new_message)
                                    pm.save()


                    elif this_user in all_submitters:
                        institution.submitters.remove(this_user)
                        institution.save()

                        project.submitters.remove(this_user)
                        project.save()

                        all_projects = institution.projects.all()

                        for this_project in all_projects:
                            if this_user in this_project.submitters.all():
                                this_project.submitters.remove(this_user)
                                this_project.users.remove(this_user)
                                this_project.save()

                                string = f'User with email: {this_user.email}, has been removed from Project: {this_project.title}, because their role has been changed'
                                new_message = Message(title = 'Alert', message = string)
                                new_message.save()

                                for admin in this_project.admin.all():
                                    admin.person.messages.add(new_message)
                                    admin.save()

                                for pm in this_project.project_manager.all():
                                    pm.person.messages.add(new_message)
                                    pm.save()

                    if role == 'developer':
                        institution.developers.add(this_user)
                        institution.save()

                        project.developers.add(this_user)
                        project.save() 

                    elif role == 'submitter':
                        institution.submitters.add(this_user)
                        institution.save()
                    
                        project.submitters.add(this_user)
                        project.save()

                    return HttpResponseRedirect(request.path_info)
                
                
                elif "add_non_pruser" in request.POST:

                    # new new

                    ids = request.POST.getlist('non_pruser_select')

                    for id in ids:

                        this_person = User.objects.get(pk = id)

                        if this_person in all_devs:
                            project.developers.add(this_person)
                            project.save()
                            project.users.add(this_person)
                            project.save()
                        elif this_person in all_submitters:
                            project.submitters.add(this_person)
                            project.save()
                            project.users.add(this_person)
                            project.save()
                        else:
                            project.users.add(this_person)

                        
                    return HttpResponseRedirect(request.path_info)
                

                elif "pruser_remove" in request.POST:

                    id = request.POST['hidden_remove_input']

                    this_user = User.objects.get(pk = id)

                    if this_user in all_devs:
                        project.developers.remove(this_user)
                        project.save()
                        project.users.remove(this_user)
                        project.save()
                    elif this_user in all_submitters:
                        project.submitters.remove(this_user)
                        project.save()
                        project.users.remove(this_user)
                        project.save()
                    else:
                        project.users.remove(this_user)
                        project.save()

                    return HttpResponseRedirect(request.path_info)

            return render(request, "debugger/pm_project_users.html", {
                'institution':institution, 'user':user, 'isUnread':isUnread, 'this_project':project, 'user_messages':user_messages, 'these_users':these_users, 'all_admin':all_admin, 'all_devs':all_devs, 'all_pm':all_pm, 'all_submitters':all_submitters, 'non_project_users':non_project_users, 'inProject':inProject
            })
        
        else:
            raise PermissionDenied()
    
    else:
        logout(request)
        return render(request, "debugger/index.html")


@login_required(login_url="/")
def pm_project_details(request, institution_id, user_id, project_id):
    institution = Institution.objects.get(pk = institution_id)
    user = User.objects.get(pk = user_id)

    if request.user in institution.project_manager.all():

        if request.user.id == user_id:

            project = Project.objects.get(pk = project_id)

            inProject = True

            user_messages = user.person.messages.all()

            isUnread = False

            for message in user_messages:
                if message.read == False:
                    isUnread = True

            all_users = project.users.all()

            all_admin = institution.admin.all()

            all_devs = institution.developers.all()

            all_submitters = institution.submitters.all()

            all_pm = institution.project_manager.all()

            all_bugs = project.bugs.all()
            
            return render(request, "debugger/pm_project_details.html", {
                'institution':institution, 'user':user, 'isUnread':isUnread, 'project':project, 'user_messages':user_messages, 'inProject':inProject, 'all_users':all_users, 'all_admin':all_admin, 'all_devs':all_devs, 'all_submitters':all_submitters, 'all_pm':all_pm, 'all_bugs':all_bugs
            })

        else:
            raise PermissionDenied()
    
    else:
        logout(request)
        return render(request, "debugger/index.html")