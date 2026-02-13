from django.contrib import admin
from .models import (
    Student,
    Educator,
    Subject,
    Content,
    LearningPath,
    ContentAssignment,
    Assessment,
    Progress,
    AssessmentResult,
    Attendance,
    Badge,
    StudentBadge,
    AIMentorSession,
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'grade_level', 'is_active', 'enrollment_date']
    list_filter = ['grade_level', 'is_active', 'gender']
    search_fields = ['first_name', 'last_name', 'email']
    ordering = ['-created_at']


@admin.register(Educator)
class EducatorAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'department']
    search_fields = ['first_name', 'last_name', 'email']
    ordering = ['-created_at']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'grade_level', 'created_at']
    list_filter = ['grade_level']
    search_fields = ['code', 'name']
    ordering = ['grade_level', 'name']


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'content_type', 'difficulty_level', 'created_at']
    list_filter = ['content_type', 'difficulty_level', 'subject']
    search_fields = ['title', 'description']
    ordering = ['subject', 'difficulty_level', 'title']


class ContentAssignmentInline(admin.TabularInline):
    model = ContentAssignment
    extra = 1
    ordering = ['order']


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ['title', 'student', 'subject', 'difficulty_level', 'is_active', 'start_date', 'target_completion_date']
    list_filter = ['difficulty_level', 'is_active', 'subject']
    search_fields = ['title', 'student__first_name', 'student__last_name']
    inlines = [ContentAssignmentInline]
    ordering = ['-created_at']


@admin.register(ContentAssignment)
class ContentAssignmentAdmin(admin.ModelAdmin):
    list_display = ['learning_path', 'content', 'order', 'is_required', 'created_at']
    list_filter = ['is_required']
    search_fields = ['learning_path__title', 'content__title']
    ordering = ['learning_path', 'order']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'assessment_type', 'difficulty_level', 'total_points']
    list_filter = ['assessment_type', 'difficulty_level', 'subject']
    search_fields = ['title', 'description']
    ordering = ['subject', 'difficulty_level', 'title']


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'content', 'status', 'completion_percentage', 'mastery_level', 'score', 'updated_at']
    list_filter = ['status', 'learning_path__subject']
    search_fields = ['student__first_name', 'student__last_name', 'content__title']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']


@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'assessment', 'score', 'passed', 'submitted_at', 'graded']
    list_filter = ['passed', 'graded', 'assessment__subject']
    search_fields = ['student__first_name', 'student__last_name', 'assessment__title']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'created_at']
    list_filter = ['status', 'date']
    search_fields = ['student__first_name', 'student__last_name']
    ordering = ['-date']


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'points', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(StudentBadge)
class StudentBadgeAdmin(admin.ModelAdmin):
    list_display = ['student', 'badge', 'earned_at']
    list_filter = ['badge']
    search_fields = ['student__first_name', 'student__last_name', 'badge__name']
    ordering = ['-earned_at']


@admin.register(AIMentorSession)
class AIMentorSessionAdmin(admin.ModelAdmin):
    list_display = ['student', 'session_type', 'learning_path', 'helpful', 'rating', 'created_at']
    list_filter = ['session_type', 'helpful', 'rating']
    search_fields = ['student__first_name', 'student__last_name', 'query', 'response']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
