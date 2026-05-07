from django.contrib import admin
from unilmsapp.models import Profile, Subject, Enrollment, Material, Submission, Project, Quiz, Assignment, Question, Result
from django.utils.html import format_html

# Register your models here.
class ProfileAdmin(admin.ModelAdmin):

    list_display= ['profile_id', 'name', 'address', 'dept', 'email', 'sem', 'role', 'profile_img_display']

    def profile_img_display(self, obj):
        if obj.profile_img:
            return format_html('<img src="{}" width="30" height="30" />', obj.profile_img.url)
        return "No Image"
    
    profile_img_display.short_description = 'Profile Image'

admin.site.register(Profile, ProfileAdmin)

class SubjectAdmin(admin.ModelAdmin):

    list_display = ['sub_code', 'sub_name', 'faculty', 'colour', 'avatar_display']

    def formfield_for_foreignkey(
        self,
        db_field,
        request,
        **kwargs
    ):

        if db_field.name == "faculty":

            kwargs["queryset"] = Profile.objects.filter(
                role="Faculty"
            )

        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )

    def avatar_display(self, obj):
        if obj.faculty and obj.faculty.profile_img:
            return format_html('<img src="{}" width="30" height="30" />', obj.faculty.profile_img.url)
        return "No Avatar"
    
    avatar_display.short_description = 'Avatar'

admin.site.register(Subject, SubjectAdmin)

class EnrollmentAdmin(admin.ModelAdmin):

    list_display = [
        'enroll_id',
        'student_id',
        'sub',
        'date_enrolled'
    ]

    def formfield_for_foreignkey(
        self,
        db_field,
        request,
        **kwargs
    ):

        if db_field.name == "student_id":

            kwargs["queryset"] = Profile.objects.filter(
                role="Student"
            )

        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )

admin.site.register(Enrollment, EnrollmentAdmin)

class MaterialAdmin(admin.ModelAdmin):

    list_display = ['material_id', 'title', 'video_url', 'sub']

admin.site.register(Material, MaterialAdmin)

class ProjectAdmin(admin.ModelAdmin):

    list_display = ['project_id', 'title', 'description', 'sub', 'faculty', 'deadline', 'max_marks']

    def formfield_for_foreignkey(
        self,
        db_field,
        request,
        **kwargs
    ):

        if db_field.name == "faculty":

            kwargs["queryset"] = Profile.objects.filter(
                role="Faculty"
            )

        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )

admin.site.register(Project, ProjectAdmin)

class AssignmentAdmin(admin.ModelAdmin):

    list_display = ['assignment_id', 'title', 'sub', 'due_date']

admin.site.register(Assignment, AssignmentAdmin)

class SubmissionAdmin(admin.ModelAdmin):

    list_display = ['submission_id', 'assignment', 'project', 'student', 'student', 'marks', 'status']

admin.site.register(Submission, SubmissionAdmin)

class QuizAdmin(admin.ModelAdmin):

    list_display = ['q_id', 'title', 'sub', 'duration', 'date']

admin.site.register(Quiz, QuizAdmin)

class QuestionAdmin(admin.ModelAdmin):

    list_display = ['question_id', 'quiz', 'option1', 'option2', 'option3', 'option4', 'question_text', 'correct_answer', 'marks']

admin.site.register(Question, QuestionAdmin)

class ResultAdmin(admin.ModelAdmin):

    list_display = ['res_id', 'student', 'quiz', 'obtained_marks', 'total_marks', 'result', 'attempted_at']

admin.site.register(Result, ResultAdmin)