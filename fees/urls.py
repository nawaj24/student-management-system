from django.urls import path

from . import views

urlpatterns = [
    path('', views.fee_list, name='fee_list'),
    path('add/', views.add_fee, name='add_fee'),
    path('dues/', views.pending_dues, name='pending_dues'),
    path('student/<str:slug>/', views.student_fees, name='student_fees'),
    path('receipt/<int:pk>/', views.fee_receipt, name='fee_receipt'),
]
