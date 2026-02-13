from ninja import NinjaAPI, Schema
from ninja.pagination import paginate
from typing import List, Optional
from datetime import datetime, date
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db import models as django_models

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
    AIMentorSession,
    Badge,
    StudentBadge,
)
from .grok_service import grok_service

api = NinjaAPI(
    title="XAI Learning Experience Platform API",
    version="1.0.0",
    description="AI-native LXP for personalized learning and progress tracking"
)


# ============================================================================
# SCHEMAS
# ============================================================================

class StudentOutputSchema(Schema):
    id: int
    first_name: str
    last_name: str
    email: str
    date_of_birth: date
    gender: str
    grade_level: int
    is_active: bool
    enrollment_date: date
    phone_number: Optional[str] = None
    address: Optional[str] = None


class StudentInputSchema(Schema):
    first_name: str
    last_name: str
    email: str
    date_of_birth: date
    gender: str
    grade_level: int
    password: str
    phone_number: Optional[str] = None
    address: Optional[str] = None


class SubjectOutputSchema(Schema):
    id: int
    name: str
    code: str
    description: str
    grade_level: int


class ContentOutputSchema(Schema):
    id: int
    subject_id: int
    subject_name: str
    title: str
    content_type: str
    description: str
    content_body: str
    difficulty_level: str
    estimated_duration_minutes: int
    external_url: Optional[str] = None


class LearningPathOutputSchema(Schema):
    id: int
    student_id: int
    student_name: str
    subject_id: int
    subject_name: str
    title: str
    description: str
    difficulty_level: str
    personalized_goals: List[str]
    recommended_resources: List[dict]
    start_date: date
    target_completion_date: date
    is_active: bool
    completion_percentage: float


class LearningPathInputSchema(Schema):
    student_id: int
    subject_id: int
    title: str
    description: str
    difficulty_level: str
    start_date: date
    target_completion_date: date
    content_ids: List[int]  # List of content IDs to assign


class ProgressOutputSchema(Schema):
    id: int
    student_id: int
    learning_path_id: int
    content_id: int
    content_title: str
    status: str
    completion_percentage: float
    time_spent_minutes: int
    mastery_level: float
    score: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ProgressInputSchema(Schema):
    status: Optional[str] = None
    completion_percentage: Optional[float] = None
    time_spent_minutes: Optional[int] = None
    mastery_level: Optional[float] = None
    score: Optional[float] = None


class AssessmentOutputSchema(Schema):
    id: int
    subject_id: int
    subject_name: str
    content_id: Optional[int] = None
    title: str
    assessment_type: str
    description: str
    questions: List[dict]
    total_points: int
    passing_score: int
    difficulty_level: str
    time_limit_minutes: Optional[int] = None


class AssessmentInputSchema(Schema):
    student_id: int
    learning_path_id: Optional[int] = None
    answers: dict
    started_at: datetime
    submitted_at: datetime


class AssessmentResultOutputSchema(Schema):
    id: int
    student_id: int
    assessment_id: int
    assessment_title: str
    score: float
    passed: bool
    answers: dict
    feedback: str
    ai_feedback: str
    started_at: datetime
    submitted_at: datetime
    time_taken_minutes: int


class AIMentorChatInputSchema(Schema):
    student_id: int
    learning_path_id: Optional[int] = None
    content_id: Optional[int] = None
    session_type: str
    query: str


class AIMentorResponseOutputSchema(Schema):
    id: int
    session_type: str
    query: str
    response: str
    created_at: datetime


class AttendanceOutputSchema(Schema):
    id: int
    student_id: int
    date: date
    status: str
    notes: str


class LoginInputSchema(Schema):
    email: str
    password: str
    user_type: str  # 'student' or 'educator'


class LoginResponseSchema(Schema):
    user_id: int
    email: str
    first_name: str
    last_name: str
    user_type: str
    profile_id: int


# ============================================================================
# AUTHENTICATION
# ============================================================================

@api.post("/auth/login", response=LoginResponseSchema, tags=["Auth"])
def login(request, payload: LoginInputSchema):
    """Login user and return profile info."""
    from django.contrib.auth import authenticate

    # Authenticate with Django
    user = authenticate(username=payload.email, password=payload.password)

    if not user:
        return api.create_response(
            request,
            {"detail": "Invalid credentials"},
            status=401
        )

    # Check user type and get profile
    if payload.user_type == 'student':
        try:
            profile = Student.objects.get(user=user)
            return {
                "user_id": user.id,
                "email": user.email,
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "user_type": "student",
                "profile_id": profile.id,
            }
        except Student.DoesNotExist:
            return api.create_response(
                request,
                {"detail": "User is not a student"},
                status=403
            )

    elif payload.user_type == 'educator':
        try:
            profile = Educator.objects.get(user=user)
            return {
                "user_id": user.id,
                "email": user.email,
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "user_type": "educator",
                "profile_id": profile.id,
            }
        except Educator.DoesNotExist:
            return api.create_response(
                request,
                {"detail": "User is not an educator"},
                status=403
            )

    return api.create_response(
        request,
        {"detail": "Invalid user type"},
        status=400
    )


# ============================================================================
# STUDENTS
# ============================================================================

@api.get("/students", response=List[StudentOutputSchema], tags=["Students"])
@paginate
def list_students(request):
    """List all students."""
    return Student.objects.select_related('user').all()


@api.get("/students/{student_id}", response=StudentOutputSchema, tags=["Students"])
def get_student(request, student_id: int):
    """Get a specific student."""
    return get_object_or_404(Student, id=student_id)


@api.post("/students", response=StudentOutputSchema, tags=["Students"])
def create_student(request, payload: StudentInputSchema):
    """Create a new student."""
    # Create user
    user = User.objects.create_user(
        username=payload.email,
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
    )

    # Create student profile
    student = Student.objects.create(
        user=user,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        date_of_birth=payload.date_of_birth,
        gender=payload.gender,
        grade_level=payload.grade_level,
        phone_number=payload.phone_number,
        address=payload.address,
    )

    return student


# ============================================================================
# SUBJECTS
# ============================================================================

@api.get("/subjects", response=List[SubjectOutputSchema], tags=["Subjects"])
def list_subjects(request):
    """List all subjects."""
    return Subject.objects.all()


@api.get("/subjects/{subject_id}", response=SubjectOutputSchema, tags=["Subjects"])
def get_subject(request, subject_id: int):
    """Get a specific subject."""
    return get_object_or_404(Subject, id=subject_id)


# ============================================================================
# CONTENT
# ============================================================================

@api.get("/content", response=List[ContentOutputSchema], tags=["Content"])
@paginate
def list_content(request, subject_id: Optional[int] = None, difficulty: Optional[str] = None):
    """List all content, optionally filtered by subject and difficulty."""
    queryset = Content.objects.select_related('subject').all()

    if subject_id:
        queryset = queryset.filter(subject_id=subject_id)
    if difficulty:
        queryset = queryset.filter(difficulty_level=difficulty)

    results = []
    for content in queryset:
        results.append({
            **content.__dict__,
            "subject_name": content.subject.name,
        })

    return results


@api.get("/content/{content_id}", response=ContentOutputSchema, tags=["Content"])
def get_content(request, content_id: int):
    """Get specific content."""
    content = get_object_or_404(Content.objects.select_related('subject'), id=content_id)
    return {
        **content.__dict__,
        "subject_name": content.subject.name,
    }


# ============================================================================
# LEARNING PATHS
# ============================================================================

@api.get("/learning-paths", response=List[LearningPathOutputSchema], tags=["Learning Paths"])
def list_learning_paths(request, student_id: Optional[int] = None):
    """List all learning paths, optionally filtered by student."""
    queryset = LearningPath.objects.select_related('student', 'subject').all()

    if student_id:
        queryset = queryset.filter(student_id=student_id)

    paths = []
    for path in queryset:
        paths.append({
            **path.__dict__,
            "student_name": path.student.full_name,
            "subject_name": path.subject.name,
            "completion_percentage": path.completion_percentage,
        })

    return paths


@api.get("/learning-paths/{path_id}", response=LearningPathOutputSchema, tags=["Learning Paths"])
def get_learning_path(request, path_id: int):
    """Get a specific learning path."""
    path = get_object_or_404(LearningPath.objects.select_related('student', 'subject'), id=path_id)
    return {
        **path.__dict__,
        "student_name": path.student.full_name,
        "subject_name": path.subject.name,
        "completion_percentage": path.completion_percentage,
    }


@api.post("/learning-paths", response=LearningPathOutputSchema, tags=["Learning Paths"])
def create_learning_path(request, payload: LearningPathInputSchema):
    """Create a new learning path and assign content."""
    student = get_object_or_404(Student, id=payload.student_id)
    subject = get_object_or_404(Subject, id=payload.subject_id)

    # Generate personalized goals using Grok AI with error handling
    try:
        personalized_goals = grok_service.generate_personalized_goals(
            student_grade=student.grade_level,
            subject=subject.name,
            difficulty=payload.difficulty_level
        )
    except Exception as e:
        print(f"Error generating goals, using defaults: {e}")
        personalized_goals = [
            f"Master core concepts in {subject.name}",
            "Complete assigned content with understanding",
            f"Achieve proficiency at {payload.difficulty_level} level"
        ]

    recommended_resources = [
        {"title": "Khan Academy", "url": "https://khanacademy.org", "type": "external"},
    ]

    # Create learning path
    learning_path = LearningPath.objects.create(
        student=student,
        subject=subject,
        title=payload.title,
        description=payload.description,
        difficulty_level=payload.difficulty_level,
        personalized_goals=personalized_goals,
        recommended_resources=recommended_resources,
        start_date=payload.start_date,
        target_completion_date=payload.target_completion_date,
    )

    # Assign content in order
    for order, content_id in enumerate(payload.content_ids, start=1):
        content = get_object_or_404(Content, id=content_id)
        ContentAssignment.objects.create(
            learning_path=learning_path,
            content=content,
            order=order,
            is_required=True,
        )

        # Create initial progress record
        Progress.objects.create(
            student=student,
            learning_path=learning_path,
            content=content,
            status='not_started',
        )

    return {
        **learning_path.__dict__,
        "student_name": student.full_name,
        "subject_name": subject.name,
        "completion_percentage": 0.0,
    }


# ============================================================================
# PROGRESS
# ============================================================================

@api.get("/progress", response=List[ProgressOutputSchema], tags=["Progress"])
def list_progress(request, student_id: Optional[int] = None, learning_path_id: Optional[int] = None):
    """List progress records, optionally filtered."""
    queryset = Progress.objects.select_related('student', 'learning_path', 'content').all()

    if student_id:
        queryset = queryset.filter(student_id=student_id)
    if learning_path_id:
        queryset = queryset.filter(learning_path_id=learning_path_id)

    results = []
    for progress in queryset:
        results.append({
            **progress.__dict__,
            "content_title": progress.content.title,
        })

    return results


@api.put("/progress/{progress_id}", response=ProgressOutputSchema, tags=["Progress"])
def update_progress(request, progress_id: int, payload: ProgressInputSchema):
    """Update progress record."""
    progress = get_object_or_404(Progress, id=progress_id)

    if payload.status:
        progress.status = payload.status
        if payload.status == 'in_progress' and not progress.started_at:
            progress.started_at = datetime.now()
        elif payload.status == 'completed' and not progress.completed_at:
            progress.completed_at = datetime.now()

    if payload.completion_percentage is not None:
        progress.completion_percentage = payload.completion_percentage

    if payload.time_spent_minutes is not None:
        progress.time_spent_minutes = payload.time_spent_minutes

    if payload.mastery_level is not None:
        progress.mastery_level = payload.mastery_level

    if payload.score is not None:
        progress.score = payload.score

    progress.save()

    return {
        **progress.__dict__,
        "content_title": progress.content.title,
    }


# ============================================================================
# ASSESSMENTS
# ============================================================================

@api.get("/assessments", response=List[AssessmentOutputSchema], tags=["Assessments"])
def list_assessments(request, subject_id: Optional[int] = None):
    """List all assessments."""
    queryset = Assessment.objects.select_related('subject').all()

    if subject_id:
        queryset = queryset.filter(subject_id=subject_id)

    results = []
    for assessment in queryset:
        results.append({
            **assessment.__dict__,
            "subject_name": assessment.subject.name,
        })

    return results


@api.get("/assessments/{assessment_id}", response=AssessmentOutputSchema, tags=["Assessments"])
def get_assessment(request, assessment_id: int):
    """Get a specific assessment."""
    assessment = get_object_or_404(Assessment.objects.select_related('subject'), id=assessment_id)
    return {
        **assessment.__dict__,
        "subject_name": assessment.subject.name,
    }


@api.post("/assessments/{assessment_id}/submit", response=AssessmentResultOutputSchema, tags=["Assessments"])
def submit_assessment(request, assessment_id: int, payload: AssessmentInputSchema):
    """Submit an assessment and get results."""
    assessment = get_object_or_404(Assessment, id=assessment_id)
    student = get_object_or_404(Student, id=payload.student_id)

    # Calculate score (simple implementation)
    total_questions = len(assessment.questions)
    correct_answers = 0

    for question in assessment.questions:
        question_id = str(question.get('id'))
        if question_id in payload.answers:
            if payload.answers[question_id] == question.get('correct_answer'):
                correct_answers += 1

    score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    passed = score >= assessment.passing_score

    # Calculate time taken
    time_taken = int((payload.submitted_at - payload.started_at).total_seconds() / 60)

    # Identify questions missed for personalized feedback
    questions_missed = []
    for question in assessment.questions:
        question_id = str(question.get('id'))
        if question_id in payload.answers:
            if payload.answers[question_id] != question.get('correct_answer'):
                questions_missed.append(question.get('question', 'Unknown question'))

    # Generate personalized feedback using Grok AI
    ai_feedback = grok_service.generate_assessment_feedback(
        score=score,
        subject=assessment.subject.name,
        questions_missed=questions_missed if questions_missed else None
    )

    # Create assessment result
    result = AssessmentResult.objects.create(
        student=student,
        assessment=assessment,
        learning_path_id=payload.learning_path_id,
        answers=payload.answers,
        score=score,
        passed=passed,
        started_at=payload.started_at,
        submitted_at=payload.submitted_at,
        time_taken_minutes=time_taken,
        feedback="",
        ai_feedback=ai_feedback,
        graded=True,
    )

    # Update progress if linked to learning path
    if payload.learning_path_id and assessment.content:
        try:
            progress = Progress.objects.get(
                student=student,
                learning_path_id=payload.learning_path_id,
                content=assessment.content,
            )
            progress.score = score
            progress.mastery_level = score
            if passed:
                progress.status = 'completed'
                progress.completed_at = datetime.now()
                progress.completion_percentage = 100
            else:
                progress.status = 'needs_review'
            progress.save()
        except Progress.DoesNotExist:
            pass

    return {
        **result.__dict__,
        "assessment_title": assessment.title,
    }


# ============================================================================
# AI MENTOR
# ============================================================================

@api.post("/ai-mentor/chat", response=AIMentorResponseOutputSchema, tags=["AI Mentor"])
def chat_with_ai_mentor(request, payload: AIMentorChatInputSchema):
    """Chat with the AI mentor (Grok) with full learning context."""
    student = get_object_or_404(Student, id=payload.student_id)

    # Prepare rich context with student data
    context_data = {
        "student_grade": student.grade_level,
        "student_name": student.first_name,
    }

    # Build detailed system context for the AI
    system_context_parts = []

    if payload.learning_path_id:
        learning_path = get_object_or_404(LearningPath, id=payload.learning_path_id)
        context_data["subject"] = learning_path.subject.name
        context_data["difficulty"] = learning_path.difficulty_level

        # Add learning path details
        system_context_parts.append(
            f"The student is working on: '{learning_path.title}' "
            f"(Completion: {learning_path.completion_percentage:.0f}%)"
        )

        # Fetch progress for this learning path
        progress_records = Progress.objects.filter(
            student=student,
            learning_path=learning_path
        ).select_related('content')

        if progress_records.exists():
            # Calculate mastery statistics
            completed_count = progress_records.filter(status='completed').count()
            in_progress_count = progress_records.filter(status='in_progress').count()
            avg_mastery = progress_records.aggregate(avg=django_models.Avg('mastery_level'))['avg'] or 0

            system_context_parts.append(
                f"Progress: {completed_count} items completed, {in_progress_count} in progress. "
                f"Average mastery: {avg_mastery:.0f}%."
            )

            # Identify struggling areas (low mastery)
            struggling = progress_records.filter(mastery_level__lt=60).select_related('content')
            if struggling.exists():
                struggling_topics = [p.content.title for p in struggling[:3]]
                system_context_parts.append(
                    f"Areas needing support: {', '.join(struggling_topics)}."
                )

            # Identify strengths (high mastery)
            strengths = progress_records.filter(mastery_level__gte=80).select_related('content')
            if strengths.exists():
                strong_topics = [p.content.title for p in strengths[:3]]
                system_context_parts.append(
                    f"Strong areas: {', '.join(strong_topics)}."
                )

    # Add specific content context if student is viewing a particular content item
    if payload.content_id:
        content = get_object_or_404(Content, id=payload.content_id)
        context_data["current_content"] = content.title
        context_data["content_type"] = content.content_type

        system_context_parts.append(
            f"The student is currently viewing: '{content.title}' ({content.content_type}). "
            f"Focus your help on this specific content."
        )

    system_context = " ".join(system_context_parts) if system_context_parts else None

    # Get AI response from Grok with enhanced context
    response_text = grok_service.chat(
        user_message=payload.query,
        system_context=system_context,
        student_context=context_data
    )

    # Save session
    session = AIMentorSession.objects.create(
        student=student,
        learning_path_id=payload.learning_path_id,
        session_type=payload.session_type,
        query=payload.query,
        response=response_text,
        context_data=context_data,
    )

    return {
        **session.__dict__,
    }


# ============================================================================
# ATTENDANCE
# ============================================================================

@api.get("/attendance", response=List[AttendanceOutputSchema], tags=["Attendance"])
def list_attendance(request, student_id: Optional[int] = None, date_from: Optional[date] = None):
    """List attendance records."""
    queryset = Attendance.objects.all()

    if student_id:
        queryset = queryset.filter(student_id=student_id)
    if date_from:
        queryset = queryset.filter(date__gte=date_from)

    return queryset


# ============================================================================
# DASHBOARD / ANALYTICS
# ============================================================================

@api.get("/dashboard/student/{student_id}", tags=["Dashboard"])
def get_student_dashboard(request, student_id: int):
    """Get student dashboard data."""
    student = get_object_or_404(Student, id=student_id)

    # Get learning paths
    learning_paths = LearningPath.objects.filter(student=student, is_active=True)

    # Get recent progress
    recent_progress = Progress.objects.filter(student=student).order_by('-updated_at')[:5]

    # Get recent assessment results
    recent_results = AssessmentResult.objects.filter(student=student).order_by('-created_at')[:5]

    # Calculate overall stats
    total_paths = learning_paths.count()
    avg_completion = sum(path.completion_percentage for path in learning_paths) / total_paths if total_paths > 0 else 0
    avg_mastery = Progress.objects.filter(student=student).aggregate(avg=models.Avg('mastery_level'))['avg'] or 0

    return {
        "student": StudentOutputSchema.from_orm(student),
        "learning_paths": [LearningPathOutputSchema.from_orm(path) for path in learning_paths],
        "recent_progress": [ProgressOutputSchema.from_orm(p) for p in recent_progress],
        "recent_results": [AssessmentResultOutputSchema.from_orm(r) for r in recent_results],
        "stats": {
            "total_learning_paths": total_paths,
            "average_completion": round(avg_completion, 2),
            "average_mastery": round(avg_mastery, 2),
            "total_assessments_taken": recent_results.count(),
        }
    }


@api.get("/dashboard/educator", tags=["Dashboard"])
def get_educator_dashboard(request, subject_id: Optional[int] = None):
    """Get educator dashboard data."""
    # Get all learning paths, optionally filtered by subject
    queryset = LearningPath.objects.select_related('student', 'subject').all()

    if subject_id:
        queryset = queryset.filter(subject_id=subject_id)

    # Get students needing attention
    students_needing_attention = Progress.objects.filter(
        status='needs_review'
    ).select_related('student').distinct()

    # Get recent assessment results
    recent_results = AssessmentResult.objects.select_related('student', 'assessment').order_by('-created_at')[:10]

    return {
        "learning_paths": [LearningPathOutputSchema.from_orm(path) for path in queryset],
        "students_needing_attention": list(students_needing_attention.values('student_id', 'student__first_name', 'student__last_name', 'content__title')),
        "recent_results": [AssessmentResultOutputSchema.from_orm(r) for r in recent_results],
    }
