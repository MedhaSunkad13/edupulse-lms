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
    sub = models.ForeignKey(Subject, on_delete=models.CASCADE)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.title} {self.video_url}"
    
class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
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
    due_date = models.DateField()

    def __str__(self):
        return f"{self.title}"
    
class Submission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(Profile, on_delete=models.CASCADE)
    marks = models.FloatField()
    status = models.BooleanField(default=False)
    
class Quiz(models.Model):
    q_id = models.AutoField(primary_key=True)
    sub = models.ForeignKey(Subject, on_delete=models.CASCADE)
    duration = models.TimeField()
    date = models.DateField()

class Result(models.Model):
    RESULT_CHOICES = [
        ('Pass', 'Pass'),
        ('Fail', 'Fail')
    ]
    res_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Profile, on_delete=models.CASCADE)
    sub = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks = models.FloatField()
    result = models.CharField(max_length=4, choices=RESULT_CHOICES)

    def __str__(self):
        return f"{self.result}"