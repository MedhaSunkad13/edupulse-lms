from django.urls import path
# from django.views.generic import TemplateView
from unilmsapp import views

urlpatterns = [
    path('profile/login/', views.profile_login, name='profile_login'),
    path('faculty/login/', views.faculty_login, name='faculty_login'),
    path('profile/logout/', views.profile_logout, name='profile_logout'),
    # path('dashboard/', TemplateView.as_view(template_name='unilmsapp/dashboard.html'), name='dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/courses/', views.my_courses, name='my_courses'),
    path('course/details/<str:sc>/', views.course_detail, name='course_detail'),
    path('assignment/<int:id>/submit/',views.submit_assignment, name='submit_assignment'),
    path('project/<int:p_id>/submit/', views.submit_project, name='submit_project'),
    path('take-quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('quiz-result/<int:result_id>/',views.quiz_result, name='quiz_result'),
    path('announcement/', views.announcements, name='announcements'),
    path('create-announcement/', views.create_announcement, name='create_announcement'),
    path('edit-announcement/<int:a_id>/', views.edit_announcement, name='edit_announcement'),
    path('delete-announcement/<int:a_id>/', views.delete_announcement, name='delete_announcement'),
    path('student-announcement/', views.student_announcements, name='student_announcements'),
    # path('leaderboard/', views.student_leaderboard, name='student_leaderboard'),
]