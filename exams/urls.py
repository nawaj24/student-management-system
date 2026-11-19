from django.urls import path

from . import views

urlpatterns = [
    path('', views.exam_list, name='exam_list'),
    path('add/', views.add_exam, name='add_exam'),
    path('<int:pk>/marks/', views.enter_marks, name='enter_marks'),
    path('<int:pk>/result/', views.exam_result, name='exam_result'),
    path('<int:pk>/report/<int:student_pk>/', views.report_card, name='report_card'),
]
