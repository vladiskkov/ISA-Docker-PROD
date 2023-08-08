from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('testings', views.exams, name='exams'),
    path('profile', views.profile, name='profile'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('results', views.results, name='results'),
    path('aexams', views.aexams, name='aexams'),
    path('aexams_requests', views.aexams_requests, name='aexams_requests'),
    path('aexams_requests_response/', views.exam_request_response, name='aexams_requests_response'),
    path('dashboards/<int:pk>/', views.dashboards, name='dashboards'),
    path('testings/<int:pk>/', views.exam_detail, name='exam_detail'),
    path('testings1/<int:pk>/', views.exam1, name='exam_detail1'),
    path('profile/exam_request/', views.exam_request, name='exam_request'),
    path('retake_exam_request/<int:pk>/', views.retake_exam_request, name='retake_exam_request'),
    path('retake_exam_response/<int:request_pk>/<int:user_exam_pk>/<str:action>/', views.retake_exam_response, name='retake_exam_response'),
    path('read_all_notifications', views.read_all_notifications, name='read_all_notifications'),
    path('assignment_retake_exam/<int:user_exam_pk>/', views.assignment_retake_exam, name='assignment_retake_exam')
]
