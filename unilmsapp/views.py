from django.shortcuts import render, redirect,  get_object_or_404
from unilmsapp.models import Profile, Subject, Material, Enrollment, Quiz, Project, Submission, Assignment, Question, Result, Announcement, Events
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from datetime import date

# Create your views here.
def student_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('pswd')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.profile.role == "Student":
                login(request, user)
                return redirect('student_dashboard')
            else:
                return render(request, 'unilmsapp/login.html', {'error': "Not a student account"})
        else:
            return render(request, 'unilmsapp/login.html', {'error': "Invalid username or password"})

    return render(request, 'unilmsapp/login.html', {'login_type': 'student'})

def faculty_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('pswd')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.profile.role == "Faculty":
                login(request, user)
                return redirect('teachers_dashboard')
            else:
                return render(request, 'unilmsapp/login.html', {'error': "Not a faculty account"})
        else:
            return render(request, 'unilmsapp/login.html', {'error': "Invalid username or password"})

    return render(request, 'unilmsapp/login.html', {'login_type': 'faculty'})

def profile_logout(request):
    logout(request) #this clears session
    return redirect('student_login') #redirect back to login page

@login_required
def student_dashboard(request):
    subjects = []
    curr_user = request.user

    if request.user.profile.role != "Student":
        return redirect('teachers_dashboard')

    enrolled = Enrollment.objects.filter(student_id = curr_user.profile)
    for e in enrolled:
        subjects.append(e.sub)

    materials = Material.objects.filter(sub__in = subjects)

    # print(materials.values())
    # print("Subjects:", subjects)
    # print("Materials:", materials)
    # print(request.user)
    # print(request.user.profile)
    
    #------------Leaderboard-----------

    leaderboard = []

    # Fetch only students
    students = Profile.objects.filter(role="Student")

    for s in students:

        quiz_total = 0
        assignment_total = 0
        project_total = 0

        # Fetch submissions
        submissions = Submission.objects.filter(student=s)

        for submission in submissions:

            # Project Marks
            if submission.project and submission.marks:
                project_total += submission.marks

            # Assignment Marks
            if submission.assignment and submission.marks:
                assignment_total += submission.marks

        # Quiz marks
        quiz_results = Result.objects.filter(student=s)

        for q in quiz_results:
            quiz_total += q.obtained_marks

        # Total score
        total_marks = (
            project_total
            + assignment_total
            + quiz_total
        )

        # Create dictionary
        student_data = {

            'student': s,
            'quiz_total': quiz_total,
            'assignment_total': assignment_total,
            'project_total': project_total,
            'total_marks': total_marks

        }

        # Add into leaderboard
        leaderboard.append(student_data)

    # Sort descending
    leaderboard.sort(
        key=lambda x: x['total_marks'],
        reverse=True
    )

    print(students)

    return render(
        request,
        'unilmsapp/student_dashboard.html',
        {
            'leaderboard': leaderboard,
            'materials' : materials
        }
    )

def my_courses(request):
    curr_user = request.user

    enrollments = Enrollment.objects.filter(student_id = curr_user.profile)

    subjects = []

    #Advanced version
    #subjects = Subject.objects.filter(enrollment__student_id = curr_user.profile).distinct()

    for e in enrollments:
        if e.sub not in subjects:
            subjects.append(e.sub)
    
    return render(request, 'unilmsapp/courses.html', {'subjects' : subjects})

def course_detail(request, sc):

    subject = get_object_or_404(Subject, sub_code=sc)

    is_enrolled = Enrollment.objects.filter(
        student_id=request.user.profile,
        sub=subject
    ).exists()

    if not is_enrolled:
        messages.error(request, "You are not enrolled in this course")
        return redirect('my_courses')

    # Materials
    materials = Material.objects.filter(sub = subject)

    # Assignments
    assignments = Assignment.objects.filter(sub = subject)

    #Projects
    projects = Project.objects.filter(sub = subject)

    # Submissions of current user
    submissions = Submission.objects.filter(student=request.user.profile)

    # Results of current user
    results = Result.objects.filter(student=request.user.profile)

    #Quiz submission of curr user
    quizzes = Quiz.objects.filter(sub = subject)

    #Extract Quiz IDs
    attempted_quiz_ids = []
    for r in results:
        attempted_quiz_ids.append(r.quiz.q_id)

    # Extract assignment IDs
    submitted_ids = []
    for s in submissions:
        submitted_ids.append(s.assignment.assignment_id)

    #Extract project IDs
    submitted_project_ids = []
    for s in submissions:
     if s.project:
        submitted_project_ids.append(s.project.project_id)

    return render(request, 'unilmsapp/course_detail.html', {
        'materials': materials,
        'subject': subject,
        'assignments': assignments,
        'projects' : projects,
        'quizzes' : quizzes,
        'attempted_quiz_ids' : attempted_quiz_ids,
        'submitted_ids': submitted_ids,
        'submitted_project_ids' : submitted_project_ids,
    })

def submit_assignment(request, id):
    curr_assignment = get_object_or_404(Assignment, assignment_id=id)

    student = request.user.profile

    has_submitted = Submission.objects.filter(
        student=student,
        assignment=curr_assignment
    ).exists()

    if has_submitted:
        messages.error(request, "Already Submitted!")
        return redirect('course_detail', curr_assignment.sub.sub_code)
    
    today = date.today()

    is_expired = today > curr_assignment.due_date

    if request.method == 'POST':

        if is_expired:
            messages.error(
                request,
                "Assignment deadline has passed!"
            )
            return redirect(
                'course_detail',
                curr_assignment.sub.sub_code
            )

        file = request.FILES['file']

        Submission.objects.create(
            student=student,
            assignment=curr_assignment,
            file=file,
            status=True
        )

        messages.success(
            request,
            "Assignment submitted successfully!"
        )

        return redirect(
            'course_detail',
            curr_assignment.sub.sub_code
        )

    return render(request, 'unilmsapp/submit_assignment.html', {
        'assignment': curr_assignment,
        'is_expired' : is_expired
    })
    
def submit_project(request, p_id):

    # Get Project
    project = get_object_or_404(
        Project,
        project_id=p_id
    )

    # Get Student
    student = request.user.profile

    # Check if already submitted
    has_submitted = Submission.objects.filter(
        student=student,
        project=project
    ).exists()

    if has_submitted:

        messages.error(
            request,
            "Already Submitted!"
        )

        return redirect(
            'course_detail',
            project.sub.sub_code
        )

    # Check deadline
    today = date.today()

    is_expired = today > project.deadline

    if request.method == "POST":

        # Deadline validation
        if is_expired:

            messages.error(
                request,
                "Project deadline has passed!"
            )

            return redirect(
                'course_detail',
                project.sub.sub_code
            )

        file = request.FILES.get('file')

        if not file:
            messages.error(
                request,
                "Please select a ZIP file."
            )
            return redirect(
                'submit_project',
                project.project_id
            )

        # ZIP validation
        if not file.name.lower().endswith(".zip"):

            messages.error(
                request,
                "Only .zip files are allowed!"
            )

            return redirect(
                'submit_project',
                project.project_id
            )

        # Create submission
        Submission.objects.create(

            student=student,
            project=project,
            file=file,
            status=True

        )

        messages.success(
            request,
            "Project submitted successfully!"
        )

        return redirect(
            'course_detail',
            project.sub.sub_code
        )

    return render(
        request,
        'unilmsapp/submit_project.html',
        {
            'project': project,
            'is_expired': is_expired
        }
    )

def take_quiz(request, quiz_id):

    quiz = get_object_or_404(Quiz, q_id=quiz_id)

    # Current student
    student = request.user.profile

    # All questions of current quiz
    questions = Question.objects.filter(quiz=quiz)

    # Check if already attempted
    has_attempted = Result.objects.filter(
        student=student,
        quiz=quiz
    ).exists()

    if has_attempted:
        messages.error(request, "Already Attempted!")
        return redirect('course_detail', quiz.sub.sub_code)
    
    today = timezone.now().date()

    if quiz.date > today:
        messages.error(request, "You cannot attempt the quiz today!")
        return redirect('course_detail', quiz.sub.sub_code)

    # ==================== GET ====================
    if request.method == "GET":

        return render(request, 'unilmsapp/show_quiz.html', {
            'quiz': quiz,
            'questions': questions
        })

    # ==================== POST ====================
    else:

        score = 0
        tot_marks = 0

        for question in questions:

            # Add total marks
            tot_marks += question.marks

            # Get selected answer dynamically
            selected_answer = request.POST.get(
                f"question_{question.question_id}"
            )

            # Check answer
            if selected_answer == question.correct_answer:
                score += question.marks

        # Calculate percentage
        percentage = (score / tot_marks) * 100

        # Pass / Fail
        if percentage < 40:
            result = "Fail"
        else:
            result = "Pass"

        # Save result
        quiz_result = Result.objects.create(
            student=student,
            quiz=quiz,
            obtained_marks=score,
            total_marks=tot_marks,
            result=result
        )

        messages.success(request, "Quiz submitted successfully!")

        return redirect('quiz_result', quiz_result.res_id)

def quiz_result(request, result_id):

    result = get_object_or_404(
        Result,
        res_id=result_id
    )

    if result.student != request.user.profile:
        return redirect(
            'student_dashboard'
        )

    return render(
        request,
        'unilmsapp/quiz_result.html',
        {
            'result': result
        }
    )

def announcements(request):

    announcements = Announcement.objects.filter(
        sender=request.user.profile
    ).order_by('-timestamp')

    return render(
        request,
        'unilmsapp/announcements.html',
        {'announcements': announcements}
    )


def create_announcement(request):

    subjects_taught = Subject.objects.filter(
        faculty=request.user.profile
    )

    if request.method == "POST":

        title = request.POST.get("title")
        content = request.POST.get("content")
        subject = request.POST.get("subject")

        curr_subject = Subject.objects.get(
            sub_code=subject
        )

        Announcement.objects.create(
            sender=request.user.profile,
            subject=curr_subject,
            title=title,
            content=content,
        )

        return redirect('announcements')

    return render(
        request,
        'unilmsapp/create_announcement.html',
        {'subjects': subjects_taught}
    )

def edit_announcement(request, a_id):

    curr_announcement = get_object_or_404(
        Announcement,
        announcement_id=a_id
    )

    if curr_announcement.sender != request.user.profile:
        messages.error(request, "You cannot edit others announcement.")
        return redirect('announcements')

    subjects_taught = Subject.objects.filter(
        faculty=request.user.profile
    )

    if request.method == "POST":

        new_title = request.POST.get("title")
        new_content = request.POST.get("content")
        new_subject = request.POST.get("subject")

        curr_subject = Subject.objects.get(
            sub_code=new_subject
        )

        curr_announcement.title = new_title
        curr_announcement.content = new_content
        curr_announcement.subject = curr_subject

        curr_announcement.save()

        return redirect('announcements')

    return render(
        request,
        'unilmsapp/edit_announcement.html',
        {
            'announcement': curr_announcement,
            'subjects': subjects_taught
        }
    )

def delete_announcement(request, a_id):
    curr_announcement = get_object_or_404(
        Announcement,
        announcement_id=a_id
    )

    if curr_announcement.sender != request.user.profile:
        messages.error(request, "You cannot delete others announcement.")
        return redirect('announcements')
    
    if request.method == "POST":
        curr_announcement.delete()
        messages.success(request, "Announcement deleted successfully.")
        return redirect('announcements')
    else:
        return render(
         request,
            'unilmsapp/delete_announcement.html',
            {'announcement': curr_announcement}
        )
    
def student_announcements(request):

    enrolled_subjects = Enrollment.objects.filter(
        student_id=request.user.profile
    )

    subjects = []

    for e in enrolled_subjects:
        subjects.append(e.sub)

    announcements = Announcement.objects.filter(
        subject__in=subjects
    ).order_by('-timestamp')

    return render(
        request,
        'unilmsapp/student_announcement.html',
        {'announcements': announcements}
    )

def create_event(request):

    subjects_taught = Subject.objects.filter(
        faculty=request.user.profile
    )

    # ========== POST ==========
    if request.method == "POST":

        title = request.POST.get('title')
        date = request.POST.get('date')
        subject = request.POST.get('subject')
        event_type = request.POST.get('event_type')

        curr_subject = Subject.objects.get(
            sub_code=subject
        )

        Events.objects.create(
            title=title,
            date=date,
            subject=curr_subject,
            event_type=event_type
        )

        return redirect('create_event')

    # ========== GET ==========
    return render(
        request,
        'unilmsapp/event_creation.html',
        {'subjects_taught': subjects_taught}
    )

def display_events(request):

    events = Events.objects.all().order_by('date')

    return render(
        request,
        'unilmsapp/events.html',
        {'events': events}
    )

def student_events(request):
    enrolled_subjects = Enrollment.objects.filter(
        student_id=request.user.profile
    )

    subjects = []
    for e in enrolled_subjects:
        subjects.append(e.sub)

    events = Events.objects.filter(
        subject__in = subjects
    ).order_by('date')

    return render(request, 'unilmsapp/view_events.html', {'events' : events})

def edit_profile(request):

    curr_user = request.user.profile

    if request.method == "POST":

        new_email = request.POST.get("email")
        new_address = request.POST.get("address")
        new_image = request.FILES.get("image")

        curr_user.email = new_email
        curr_user.address = new_address

        if new_image:
            curr_user.profile_img = new_image

        curr_user.save()

        return redirect('student_dashboard')

    return render(request, 'unilmsapp/edit_profile.html', {
        'curr_user': curr_user
    })

def change_password(request):

    curr_user = request.user

    if request.method == "POST":

        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if curr_user.check_password(old_password):

            if new_password == confirm_password:

                curr_user.set_password(new_password)
                curr_user.save()

                messages.success(request, "Password changed successfully!")

                return redirect('student_login')

            else:
                messages.error(request, "New password and confirm password must match!")

        else:
            messages.error(request, "Old password is incorrect!")

    return render(request, "unilmsapp/change_password.html", {
        'curr_user': curr_user
    })

                    # Teachers Dashboard

@login_required
def teachers_dashboard(request):
    curr_teacher = request.user.profile

    if request.user.profile.role != "Faculty":
        return redirect('student_dashboard')

    #Subjects
    my_subjects = Subject.objects.filter(faculty = curr_teacher)

    #Count total subjects
    total_subjects = my_subjects.count()

    #Materials
    my_materials = Material.objects.filter(sub__in = my_subjects)

    #Count total materials
    total_materials = my_materials.count()

    #Assignments
    my_assignments = Assignment.objects.filter(sub__in = my_subjects)

    #Count total assignments
    total_assignments = my_assignments.count()

    #Projects
    my_projects = Project.objects.filter(sub__in = my_subjects)

    #Count total Projects
    total_projects = my_projects.count()

    #Quiz
    my_quizzes = Quiz.objects.filter(sub__in = my_subjects)

    #Count total quizzes
    total_quizzes = my_quizzes.count()

    return render(request, 'unilmsapp/teachers_dashboard.html', {

    'curr_teacher': curr_teacher,

    'total_subjects': total_subjects,
    'total_materials': total_materials,
    'total_assignments': total_assignments,
    'total_projects': total_projects,
    'total_quizzes': total_quizzes,

    'my_subjects': my_subjects,

})

def teacher_my_subjects(request):
    curr_logged_in = request.user.profile

    my_subjects = Subject.objects.filter(faculty = curr_logged_in)

    return render(request, 'unilmsapp/my_subjects.html', {

        'curr_logged_in': curr_logged_in,
        'my_subjects': my_subjects,

    })

def upload_materials(request):

    curr_user = request.user.profile

    # Subjects assigned to current teacher
    my_subjects = Subject.objects.filter(
        faculty=curr_user
    )

    if request.method == "POST":

        title = request.POST.get("title")
        description = request.POST.get("description")
        subject = request.POST.get("subject")
        video_url = request.POST.get("video_url")
        notes = request.FILES.get("notes")

        # Get selected subject object
        curr_subject = Subject.objects.get(
            sub_code=subject
        )

        # Create material
        Material.objects.create(

            title=title,
            description=description,
            video_url=video_url,
            notes=notes,
            sub=curr_subject

        )

        messages.success(
            request,
            "Material uploaded successfully!"
        )

        return redirect('upload_materials')

    return render(
        request,
        'unilmsapp/upload_materials.html',
        {

            'curr_user': curr_user,
            'my_subjects': my_subjects,

        }
    )

def create_assignment(request):
    logged_in_user = request.user.profile

    subjects = Subject.objects.filter(faculty = logged_in_user)

    if request.user.profile.role != "Faculty":
        return redirect('student_dashboard')

    if request.method == "POST":
        title = request.POST.get("title")
        sub = request.POST.get("subject")
        description = request.POST.get("description")
        file = request.FILES.get("file")
        due_date = request.POST.get("due_date")
        max_marks = request.POST.get("max_marks")

        curr_subject = get_object_or_404(
         Subject,
         sub_code=sub
        )

        Assignment.objects.create( 
            title = title,
            sub = curr_subject,
            description = description,
            file = file,
            due_date = due_date,
            max_marks = max_marks
        )

        messages.success(
            request,
            "Assignment created successfully!"
        )
    
        return redirect('create_assignment')

    return render(request, 'unilmsapp/create_assignment.html', {'logged_in_user' : logged_in_user, 'subjects' : subjects})

def create_project(request):
    
    if request.user.profile.role != "Faculty":
        return redirect('student_dashboard')

    # Get logged in faculty
    curr_user = request.user.profile

    # Subjects taught by faculty
    subjects = Subject.objects.filter(
        faculty=curr_user
    )

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        sub = request.POST.get("subject")
        project_file = request.FILES.get("file")
        deadline = request.POST.get("deadline")
        max_marks = request.POST.get("max_marks")

        curr_subject = get_object_or_404(Subject, sub_code = sub)

        Project.objects.create(
            title=title,
            description=description,
            sub=curr_subject,
            project_file=project_file,
            faculty=curr_user,
            deadline=deadline,
            max_marks=max_marks
        )

        messages.success(request, "Project created successfully!")
        return redirect('create_project')
    
    return render(request, 'unilmsapp/create_project.html', {'curr_user' : curr_user, 'subjects' : subjects})

def create_quiz(request):

    # Get logged-in faculty
    curr_user = request.user.profile

    # Only faculty can create quizzes
    if curr_user.role != "Faculty":
        return redirect('student_dashboard')

    # Subjects taught by faculty
    subjects = Subject.objects.filter(
        faculty=curr_user
    )

    if request.method == "POST":

        title = request.POST.get("title")
        sub = request.POST.get("subject")
        duration = request.POST.get("duration")
        date = request.POST.get("date")

        curr_sub = get_object_or_404(
            Subject,
            sub_code=sub
        )

        # Save quiz object in a variable
        quiz = Quiz.objects.create(

            title=title,
            sub=curr_sub,
            faculty=curr_user,
            duration=duration,
            date=date

        )

        messages.success(
            request,
            "Quiz created successfully!"
        )

        return redirect(
            'add_questions',
            quiz.q_id
        )

    return render(
        request,
        'unilmsapp/create_quiz.html',
        {
            'curr_user': curr_user,
            'subjects': subjects
        }
    )

def add_questions(request, q_id):

    # Fetch current quiz
    curr_quiz = get_object_or_404(
        Quiz,
        q_id=q_id
    )

    if request.method == "POST":

        question_text = request.POST.get("question_text")
        option1 = request.POST.get("opt_1")
        option2 = request.POST.get("opt_2")
        option3 = request.POST.get("opt_3")
        option4 = request.POST.get("opt_4")
        correct_answer = request.POST.get("correct_answer")
        marks = request.POST.get("marks")

        Question.objects.create(

            quiz=curr_quiz,
            question_text=question_text,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_answer=correct_answer,
            marks=marks

        )

        messages.success(
            request,
            "Question added successfully!"
        )

        return redirect(
            'add_questions',
            curr_quiz.q_id
        )

    questions = Question.objects.filter(
        quiz=curr_quiz
    )

    return render(
        request,
        'unilmsapp/add_questions.html',
        {
            'curr_quiz': curr_quiz,
            'questions': questions
        }
    )

def attempt_quiz(request, q_id):
    #Fetch the quiz object
    quiz = get_object_or_404(
        Quiz,
        q_id=q_id
    )

    #Fetch the questions belonging to that quiz
    questions = Question.objects.filter(
        quiz=quiz
    )

    #Fetch student who have attempted that quiz
    student = request.user.profile

    already_attempted = Result.objects.filter(
        student=student,
        quiz=quiz
    ).exists()

    if already_attempted:

        messages.error(
            request,
            "You have already attempted this quiz!"
        )

        return redirect(
            'quiz_result',
            quiz_result.res_id
        )

    if request.method == "POST":

        score = 0
        total_marks = 0

        for question in questions:

            selected_answer = request.POST.get(
                f"question_{question.question_id}"
            )

            if selected_answer == question.correct_answer:

                score += question.marks

            total_marks += question.marks

        percentage = (
            score / total_marks
        ) * 100

        if percentage >= 50:
            result_status = "Pass"
        else:
            result_status = "Fail"

        quiz_result = Result.objects.create(

            student=student,
            quiz=quiz,
            obtained_marks=score,
            total_marks=total_marks,
            result=result_status

        )

        messages.success(
            request,
            f"Quiz submitted successfully! Score: {score}/{total_marks}"
        )

        return redirect(
            'quiz_result',
            quiz_result.res_id
        )

    return render(
        request,
        'unilmsapp/attempt_quiz.html',
        {
            'quiz': quiz,
            'questions': questions,
        }
    )
    
# def quiz_result(request, q_id):
#     #Fetch the quiz belonging to this q_id
#     quiz = get_object_or_404(Quiz, q_id=q_id)

#     #Fetch the student who have attempted that quiz
#     student = request.user.profile

#     #Fetch result of that student
#     result = get_object_or_404(
#         Result,
#         quiz=quiz,
#         student=student
#     )

#     #Calculate percentage
#     percentage = round(
#         (result.obtained_marks / result.total_marks) * 100,
#         2
#     )

#     return render(request, 'unilmsapp/quiz_result.html', {'quiz' : quiz, 'student' : student, 'result': result, 'percentage' : percentage})

def teacher_quiz_results(request, q_id):

    # Fetch quiz
    quiz = get_object_or_404(
        Quiz,
        q_id=q_id
    )

    # Fetch all results of this quiz
    results = Result.objects.filter(
        quiz=quiz
    )

    # Security check
    if quiz.faculty != request.user.profile:
        return redirect(
            'teachers_dashboard'
        )

    return render(
        request,
        'unilmsapp/teacher_quiz_results.html',
        {
            'quiz': quiz,
            'results': results
        }
    )

def view_assignment_submissions(request, assignment_id):

    assignment = get_object_or_404(
        Assignment,
        assignment_id=assignment_id
    )

    submissions = Submission.objects.filter(
        assignment=assignment
    )

    if assignment.sub.faculty != request.user.profile:
        return redirect('teachers_dashboard')

    return render(
        request,
        'unilmsapp/view_assignment_submissions.html',
        {
            'assignment': assignment,
            'submissions': submissions
        }
    )

def allocate_assignment_marks(request, submission_id):

    # Fetch submission
    submission = get_object_or_404(
        Submission,
        submission_id=submission_id
    )

    # Security check
    if submission.assignment.sub.faculty != request.user.profile:
        return redirect('teachers_dashboard')

    if request.method == "POST":

        marks = request.POST.get('marks')

        submission.marks = marks
        submission.save()

        messages.success(
            request,
            f"Marks awarded to {submission.student.name} successfully!"
        )

        return redirect(
            'view_assignment_submissions',
            submission.assignment.assignment_id
        )

    return render(
        request,
        'unilmsapp/allocate_assignment_marks.html',
        {
            'submission': submission
        }
    )

def view_project_submissions(request, project_id):
    #Fetch the project_id from Project Model
    project = get_object_or_404(Project, project_id=project_id)

    #Fetch all submissions belonging to that project
    submissions = Submission.objects.filter(project=project)

    #Security Check
    if project.faculty != request.user.profile:
        return redirect('teachers_dashboard')
    
    return render(
        request,
        'unilmsapp/view_project_submissions.html',
        {
            'project' : project,
            'submissions' : submissions
        }
    )

def allocate_project_marks(request, submission_id):

    # Fetch submission
    submission = get_object_or_404(
        Submission,
        submission_id=submission_id
    )

    # Security Check
    if submission.project.faculty != request.user.profile:
        return redirect('teachers_dashboard')

    if request.method == "POST":

        marks = float(
            request.POST.get("marks")
        )

        if marks > submission.project.max_marks:

            messages.error(
                request,
                f"Marks cannot exceed {submission.project.max_marks}"
            )

            return redirect(
                'allocate_project_marks',
                submission.submission_id
            )

        submission.marks = marks
        submission.save()

        messages.success(
            request,
            f"Marks awarded to {submission.student.name} successfully!"
        )

        return redirect(
            'view_project_submissions',
            submission.project.project_id
        )

    return render(
        request,
        'unilmsapp/allocate_project_marks.html',
        {
            'submission': submission
        }
    )