from django.urls import path

from . import views

urlpatterns = [
    path('', views.class_list, name='class_list'),
    path('add/', views.add_class, name='add_class'),
    path('sections/add/', views.add_section, name='add_section'),
    path('sections/<int:pk>/', views.section_detail, name='section_detail'),
    path('sections/<int:pk>/edit/', views.edit_section, name='edit_section'),
]
