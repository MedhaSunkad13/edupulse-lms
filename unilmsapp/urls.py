from django.urls import path
# from django.views.generic import TemplateView
from unilmsapp import views

urlpatterns = [
    path('profile/login/', views.profile_login, name='profile_login'),
    # path('dashboard/', TemplateView.as_view(template_name='unilmsapp/dashboard.html'), name='dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/courses/', views.my_courses, name='my_courses'),
    path('course/details/<str:sc>/', views.course_detail, name='course_detail')
]