from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Student(models.Model):
    """Student model with demographics and enrollment information."""

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say'),
    ]

    GRADE_CHOICES = [
        (1, 'Grade 1'),
        (2, 'Grade 2'),
        (3, 'Grade 3'),
        (4, 'Grade 4'),
        (5, 'Grade 5'),
        (6, 'Grade 6'),
        (7, 'Grade 7'),
        (8, 'Grade 8'),
        (9, 'Grade 9'),
        (10, 'Grade 10'),
        (11, 'Grade 11'),
        (12, 'Grade 12'),
    ]

    # Authentication
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')

    # Demographics
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    # Enrollment
    grade_level = models.IntegerField(choices=GRADE_CHOICES)
    enrollment_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # Optional fields
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Educator(models.Model):
    """Educator/Teacher model."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='educator_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Subject(models.Model):
    """Subject/Course model - shared across all students."""

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    grade_level = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['grade_level', 'name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Content(models.Model):
    """Learning content/materials - SHARED library available to all students."""

    CONTENT_TYPE_CHOICES = [
        ('lesson', 'Lesson'),
        ('video', 'Video'),
        ('reading', 'Reading Material'),
        ('exercise', 'Exercise'),
        ('quiz', 'Quiz'),
        ('project', 'Project'),
    ]

    # Belongs to subject, NOT to a specific learning path (shared!)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='contents')

    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    description = models.TextField()

    # Content details
    content_body = models.TextField(help_text="Main content body (can be HTML, Markdown, or plain text)")

    # Metadata
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ], default='beginner')
    estimated_duration_minutes = models.IntegerField(default=30)

    # Resources
    external_url = models.URLField(blank=True, null=True)
    file_attachments = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['subject', 'difficulty_level', 'title']

    def __str__(self):
        return f"{self.title} ({self.content_type})"


class LearningPath(models.Model):
    """Personalized learning path for a student - assigns shared content in custom order."""

    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='learning_paths')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='learning_paths')

    # Path metadata
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')

    # ManyToMany relationship with Content through ContentAssignment (for ordering)
    assigned_content = models.ManyToManyField(Content, through='ContentAssignment', related_name='learning_paths')

    # AI-generated personalization (specific to THIS student)
    personalized_goals = models.JSONField(default=list, blank=True, help_text="AI-generated goals for this student")
    recommended_resources = models.JSONField(default=list, blank=True, help_text="AI-recommended resources for this student")

    # Dates
    start_date = models.DateField()
    target_completion_date = models.DateField()

    # Status
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.student.full_name}"

    @property
    def completion_percentage(self):
        """Calculate completion percentage based on progress records."""
        total_content = self.content_assignments.count()
        if total_content == 0:
            return 0.0

        completed_content = Progress.objects.filter(
            learning_path=self,
            completed_at__isnull=False
        ).count()

        return round((completed_content / total_content) * 100, 2)


class ContentAssignment(models.Model):
    """Through model linking LearningPath to Content with personalized ordering."""

    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='content_assignments')
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='content_assignments')

    # Personalized ordering for this learning path
    order = models.IntegerField(default=0, help_text="Order of content in this specific learning path")
    is_required = models.BooleanField(default=True, help_text="Is this content required or optional?")

    # Optional: AI can suggest estimated time for THIS student
    estimated_completion_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['learning_path', 'order']
        unique_together = ['learning_path', 'content']

    def __str__(self):
        return f"{self.learning_path.title} - {self.content.title} (#{self.order})"


class Assessment(models.Model):
    """Assessment/Quiz model - SHARED across students, can be linked to content."""

    ASSESSMENT_TYPE_CHOICES = [
        ('quiz', 'Quiz'),
        ('test', 'Test'),
        ('assignment', 'Assignment'),
        ('project', 'Project'),
    ]

    # Belongs to subject, optionally linked to specific content
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assessments')
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='assessments', null=True, blank=True)

    title = models.CharField(max_length=200)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPE_CHOICES)
    description = models.TextField()

    # Questions and grading
    questions = models.JSONField(default=list, help_text="List of questions with answers")
    total_points = models.IntegerField(default=100)
    passing_score = models.IntegerField(default=70)

    # Metadata
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ], default='beginner')
    time_limit_minutes = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['subject', 'difficulty_level', 'title']

    def __str__(self):
        return f"{self.title} ({self.assessment_type})"


class Progress(models.Model):
    """Track student progress on shared content - personalized tracking."""

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('needs_review', 'Needs Review'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='progress_records')
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='progress_records')
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='progress_records')

    # Progress tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    completion_percentage = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])

    # Time tracking (historical data for AI adaptation)
    time_spent_minutes = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Mastery tracking (separate from completion - KEY REQUIREMENT)
    mastery_level = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Mastery level based on assessment performance (0-100)"
    )

    # Performance score
    score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Latest score on related assessment"
    )

    # Teacher intervention
    notes = models.TextField(blank=True, help_text="Teacher notes for intervention")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ['student', 'learning_path', 'content']

    def __str__(self):
        return f"{self.student.full_name} - {self.content.title} - {self.status}"


class AssessmentResult(models.Model):
    """Store assessment results and submissions - personalized results on shared assessments."""

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='assessment_results')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='results')
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='assessment_results', null=True, blank=True)

    # Results
    answers = models.JSONField(default=dict, help_text="Student's answers to questions")
    score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    passed = models.BooleanField()

    # Timing
    started_at = models.DateTimeField()
    submitted_at = models.DateTimeField()
    time_taken_minutes = models.IntegerField()

    # Feedback
    feedback = models.TextField(blank=True)
    ai_feedback = models.TextField(blank=True, help_text="AI-generated personalized feedback from Grok")

    # Grading
    graded = models.BooleanField(default=True)
    graded_by = models.ForeignKey(Educator, on_delete=models.SET_NULL, null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.full_name} - {self.assessment.title} - {self.score}%"


class Attendance(models.Model):
    """Track student attendance."""

    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['student', 'date']

    def __str__(self):
        return f"{self.student.full_name} - {self.date} - {self.status}"


class Badge(models.Model):
    """Gamification: Badges for achievements - shared definitions."""

    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=100, help_text="Icon identifier or emoji")
    criteria = models.TextField(help_text="Criteria for earning this badge")
    points = models.IntegerField(default=10)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class StudentBadge(models.Model):
    """Track badges earned by students - personalized achievements."""

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='earned_by')
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-earned_at']
        unique_together = ['student', 'badge']

    def __str__(self):
        return f"{self.student.full_name} - {self.badge.name}"


class AIMentorSession(models.Model):
    """Track AI mentor interactions with Grok - personalized conversations."""

    SESSION_TYPE_CHOICES = [
        ('guidance', 'General Guidance'),
        ('help', 'Help Request'),
        ('assessment', 'Assessment Support'),
        ('feedback', 'Feedback Session'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='mentor_sessions')
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='mentor_sessions', null=True, blank=True)

    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES)
    query = models.TextField(help_text="Student's query or request")
    response = models.TextField(help_text="AI mentor's response from Grok")

    # Context for Grok API
    context_data = models.JSONField(default=dict, help_text="Additional context (current content, performance, etc.)")

    # Feedback on AI quality
    helpful = models.BooleanField(null=True, blank=True, help_text="Was this session helpful?")
    rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.full_name} - {self.session_type} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
