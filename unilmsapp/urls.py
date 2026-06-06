from django.urls import path
# from django.views.generic import TemplateView
from unilmsapp import views

urlpatterns = [
    path('student/login/', views.student_login, name='student_login'),
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
    path('create-event/', views.create_event, name='create_event'),
    path('events/', views.display_events, name='display_events'),
    path('student-events/', views.student_events, name='student_events'),
    path('edit/profile/', views.edit_profile, name='edit_profile'),
    path('change/password/', views.change_password, name = 'change_password'),
    # path('leaderboard/', views.student_leaderboard, name='student_leaderboard'),

    #Teachers Dashboard
    path('teachers/dashboard/', views.teachers_dashboard, name='teachers_dashboard'),
    path('teachers/subjects/', views.teacher_my_subjects, name='teacher_subjects'),
    path('upload/materials/', views.upload_materials, name='upload_materials'),
    path('create/assignment/', views.create_assignment, name='create_assignment'),
    path('create/project/', views.create_project, name='create_project'),
    path('create/quiz/', views.create_quiz, name='create_quiz'),
    path('add/questions/<int:q_id>/', views.add_questions, name='add_questions'),
    path('attempt_quiz/<int:q_id>/', views.attempt_quiz, name='attempt_quiz'),
    path('teacher/quiz_result/<int:q_id>/', views.teacher_quiz_results, name='teacher_quiz_results'),
    path('view_assignment_submissions/<int:assignment_id>/', views.view_assignment_submissions, name='view_assignment_submissions'),
    path('allocate_assignment_marks/<int:submission_id>/', views.allocate_assignment_marks, name='allocate_assignment_marks'),
    path('view_project_submissions/<int:project_id>/', views.view_project_submissions, name='view_project_submissions'),
    # path('allocate_project_marks/<int:submission_id>/', views.allocate_project_marks, name='allocate_project_marks'),
]