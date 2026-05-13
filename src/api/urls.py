"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

#from django.contrib import admin
from django.urls import include, path



from rest_framework import routers
from api.auth.views import health_check, login, register
from api.workout.views import list_workouts, get_or_edit_workout
from api.person.views import list_persons, get_or_edit_person, person_leaving
from api.permissions.views import query_permissions, create_default_permission, edit_options, assign_custom_permission



urlpatterns = [
    #path('admin/', admin.site.urls),
    
    #auth
    path('health_check/hello/', health_check)
    ,path('api/auth/login', login)
    ,path('api/auth/register', register)
    
    #workout
    ,path('api/workouts', list_workouts)
    ,path('api/workouts/<int:id>', get_or_edit_workout, name='get-or-edit-workout')

    #person
    ,path('api/persons', list_persons)
    ,path('api/persons/<int:id>', get_or_edit_person, name='get-or-edit-workout')
    ,path('api/persons/<int:id>/status_leave', person_leaving, name='person-leaving')

    #permissions
    ,path('api/permissions', query_permissions)
    ,path('api/permissions/default-entry', create_default_permission, name='post-default-permission')
    ,path('api/permissions/<int:id>/options', edit_options, name='edit-options')
    ,path('api/permissions/<int:base_perm_id>/persons/<int:person_id>', assign_custom_permission, name='assign-custom-permission')

]
