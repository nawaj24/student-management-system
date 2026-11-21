from django.urls import path

from . import views

urlpatterns = [
    path('timetable/', views.timetable, name='timetable'),
    path('timetable/add/', views.add_period, name='add_period'),
    path('events/', views.event_list, name='event_list'),
    path('events/add/', views.add_event, name='add_event'),
]
