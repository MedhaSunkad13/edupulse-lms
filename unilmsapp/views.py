from django.shortcuts import render, redirect,  get_object_or_404
from unilmsapp.models import Profile, Subject, Material, Enrollment, Quiz, Project, Submission, Assignment, Result
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
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
    return render(request, 'unilmsapp/student_dashboard.html', {'materials' : materials})

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

    materials = Material.objects.filter(sub=subject)

    return render(request, 'unilmsapp/course_detail.html', {
        'materials': materials,
        'subject': subject
    })