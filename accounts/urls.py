from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),  
    
    path('student-signup/', views.student_signup, name='stu_signup'),
    path('teacher-signup/', views.teacher_signup, name='teacher_signup'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),

    path('upload-marks/', views.upload_marks, name='upload_marks'),
    path('upload-attendance/', views.upload_attendance, name='upload_attendance'),
    path('upload-assignment/', views.upload_assignment, name='upload_assignment'),
    path('chatbot/', views.chatbot_response, name='chatbot'),
    path('predict/', views.teacher_dashboard, name='predict'),

    path('admin/', admin.site.urls),



]
