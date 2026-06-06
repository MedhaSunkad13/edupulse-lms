from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    USER_ROLE = [
        ('Student','Student'),
        ('Faculty', 'Faculty')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=100, default='')
    dept = models.CharField(max_length=50)
    email = models.EmailField(max_length=30, unique=True)
    sem = models.IntegerField(blank=True, null=True)
    role = models.CharField(max_length=10, choices=USER_ROLE)
    profile_img = models.ImageField(upload_to='profile/', blank=True, null=True)

    def __str__(self):
        return f"{self.name}"
    
class Subject(models.Model):
    sub_code = models.CharField(max_length=10, primary_key=True)
    sub_name = models.CharField(max_length=30)
    faculty = models.ForeignKey(Profile, on_delete=models.CASCADE)
    colour = models.CharField(max_length=20, default="#c084f5") 
    avatar = models.ImageField(upload_to='subject/', blank=True, null=True)

    def __str__(self):
        return f"{self.sub_name}"
    
class Enrollment(models.Model):
    enroll_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Profile, on_delete=models.CASCADE)
    sub = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date_enrolled = models.DateTimeField(default=timezone.now, blank=True)

    def __str__(self):
        return f"{self.enroll_id}"
    
class Material(models.Model):
    material_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    video_url = models.URLField(null=True, blank=True)
    notes = models.FileField(upload_to='notes/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    sub = models.ForeignKey(Subject, on_delete=models.CASCADE)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} {self.video_url}"
    
class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    project_file = models.FileField(
        upload_to='project_files/',
        blank=True,
        null=True
    )
    sub = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Profile, on_delete=models.CASCADE)
    deadline = models.DateField()
    max_marks = models.FloatField()

    def __str__(self):
        return f"{self.title}"

class Assignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    sub = models.ForeignKey(Subject, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    assignment_file = models.FileField(
        upload_to='assignment_files/',
        blank=True,
        null=True
    )
    max_marks = models.FloatField(
        default=10
    )
    due_date = models.DateField()

    def __str__(self):
        return f"{self.title}"
    
class Submission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(Profile, on_delete=models.CASCADE)
    marks = models.FloatField(null=True, blank=True)
    file = models.FileField(upload_to='assignments/', null=True, blank=True)
    status = models.BooleanField(default=False)
    
class Quiz(models.Model):
    q_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    sub = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    duration = models.IntegerField() 
    date = models.DateField()

    def __str__(self):
        return f"{self.title}"


class Question(models.Model):
    question_id = models.AutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=500)
    option1 = models.CharField(max_length=100)
    option2 = models.CharField(max_length=100)
    option3 = models.CharField(max_length=100)
    option4 = models.CharField(max_length=100)
    # stores: 1 / 2 / 3 / 4
    correct_answer = models.CharField(max_length=1)
    marks = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.question_text}"

class Announcement(models.Model):
    announcement_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"
    
class Events(models.Model):
    EVENT_CHOICES = [
        ('Quiz', 'Quiz'),
        ('Assignment', 'Assignment'),
        ('Project', 'Project'),
        ('Holiday', 'Holiday')
    ]

    event_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    date = models.DateField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    color = models.CharField(max_length=10, default="#c084f5")
    event_type = models.CharField(max_length=25, choices=EVENT_CHOICES)

    def __str__(self):
        return f"{self.title}"
    

class Result(models.Model):

    RESULT_CHOICES = [
        ('Pass', 'Pass'),
        ('Fail', 'Fail')
    ]

    res_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Profile, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True)
    obtained_marks = models.FloatField()
    total_marks = models.FloatField()
    result = models.CharField(max_length=4, choices=RESULT_CHOICES)
    attempted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.name} - {self.quiz.title}"