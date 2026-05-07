from django.shortcuts import render, redirect,  get_object_or_404
from unilmsapp.models import Profile, Subject, Material, Enrollment, Quiz, Project, Submission, Assignment, Question, Result
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages

# Create your views here.
def profile_login(request):
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

    return render(request, 'unilmsapp/login.html')

def profile_logout(request):
    logout(request) #this clears session
    return redirect('profile_login') #redirect back to login page

@login_required
def student_dashboard(request):
    subjects = []
    curr_user = request.user
    enrolled = Enrollment.objects.filter(student_id = curr_user.profile)
    for e in enrolled:
        subjects.append(e.sub)

    materials = Material.objects.filter(sub__in = subjects)

    # print(materials.values())
    # print("Subjects:", subjects)
    # print("Materials:", materials)
    # print(request.user)
    # print(request.user.profile)

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

    if request.method == 'POST':
        file = request.FILES['file']

        Submission.objects.create(
            student=student,
            assignment=curr_assignment,
            file=file,
            status=True
        )

        messages.success(request, "Assignment submitted successfully!")
        return redirect('course_detail', curr_assignment.sub.sub_code)

    return render(request, 'unilmsapp/submit_assignment.html', {
        'assignment': curr_assignment
    })
    
def submit_project(request, p_id):
    #Get Porject
    project = get_object_or_404(Project, project_id=p_id)

    #Get Student
    student = request.user.profile

    #Filter Submissions
    has_submitted = Submission.objects.filter(
        student = student,
        project = project
    ).exists()

    if has_submitted:
        messages.error(request, "Already Submitted!")
        return redirect('course_detail', project.sub.sub_code)
    
    if request.method == "POST":
        file = request.FILES['file']

        if not file.name.lower().endswith(".zip"):
            messages.error(request, "Only .zip files are allowed!")
            return redirect('course_detail', project.sub.sub_code)

        Submission.objects.create(
            student = student,
            project = project,
            file = file,
            status = True
        )

        messages.success(request, "Project submitted successfully!")
        return redirect('course_detail', project.sub.sub_code)

    return render(request, 'unilmsapp/submit_project.html', {
        'project': project
    })

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

    result = get_object_or_404(Result, res_id=result_id)

    return render(request, 'unilmsapp/quiz_result.html', {
        'result': result
    })

# def student_leaderboard(request):

    