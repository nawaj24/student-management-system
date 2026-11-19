from django.urls import path

from . import views

urlpatterns = [
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.add_department, name='add_department'),
    path('departments/<slug:slug>/', views.department_detail, name='department_detail'),
    path('departments/<slug:slug>/edit/', views.edit_department, name='edit_department'),
    path('departments/<slug:slug>/delete/', views.delete_department, name='delete_department'),

    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/add/', views.add_subject, name='add_subject'),
    path('subjects/<int:pk>/edit/', views.edit_subject, name='edit_subject'),
    path('subjects/<int:pk>/delete/', views.delete_subject, name='delete_subject'),
]
