from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import date, timedelta
from lxp.models import (
    Student,
    Educator,
    Subject,
    Content,
    Badge,
)


class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # Create subjects
        subjects_data = [
            {'name': 'Mathematics - Algebra', 'code': 'MATH-ALG-9', 'description': 'Fundamental algebra concepts for 9th grade', 'grade_level': 9},
            {'name': 'Science - Biology', 'code': 'SCI-BIO-9', 'description': 'Introduction to biology and life sciences', 'grade_level': 9},
            {'name': 'English Literature', 'code': 'ENG-LIT-9', 'description': 'Literary analysis and writing skills', 'grade_level': 9},
        ]

        subjects = {}
        for subject_data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                code=subject_data['code'],
                defaults=subject_data
            )
            subjects[subject.code] = subject
            self.stdout.write(f'  {"Created" if created else "Found"} subject: {subject.name}')

        # Create content for Math
        math_content_data = [
            {
                'title': 'Introduction to Variables',
                'content_type': 'lesson',
                'description': 'Learn what variables are and how to use them in algebra',
                'content_body': 'A variable is a symbol (usually a letter) that represents an unknown value...',
                'difficulty_level': 'beginner',
                'estimated_duration_minutes': 30,
            },
            {
                'title': 'Solving Linear Equations',
                'content_type': 'video',
                'description': 'Step-by-step guide to solving linear equations',
                'content_body': 'Video content: How to isolate variables and solve for x...',
                'difficulty_level': 'beginner',
                'estimated_duration_minutes': 45,
            },
            {
                'title': 'Practice: Linear Equations',
                'content_type': 'exercise',
                'description': 'Practice problems for linear equations',
                'content_body': 'Solve the following equations: 1) 2x + 5 = 13, 2) 3x - 7 = 8...',
                'difficulty_level': 'beginner',
                'estimated_duration_minutes': 20,
            },
            {
                'title': 'Graphing Linear Functions',
                'content_type': 'lesson',
                'description': 'Understanding how to graph lines on a coordinate plane',
                'content_body': 'A linear function can be graphed using slope-intercept form y = mx + b...',
                'difficulty_level': 'intermediate',
                'estimated_duration_minutes': 40,
            },
            {
                'title': 'Quadratic Equations Introduction',
                'content_type': 'lesson',
                'description': 'Introduction to quadratic equations and their properties',
                'content_body': 'Quadratic equations are in the form ax² + bx + c = 0...',
                'difficulty_level': 'advanced',
                'estimated_duration_minutes': 50,
            },
        ]

        for content_data in math_content_data:
            Content.objects.get_or_create(
                subject=subjects['MATH-ALG-9'],
                title=content_data['title'],
                defaults=content_data
            )
            self.stdout.write(f'  Created content: {content_data["title"]}')

        # Create content for Biology
        bio_content_data = [
            {
                'title': 'Introduction to Cells',
                'content_type': 'lesson',
                'description': 'Basic cell structure and function',
                'content_body': 'Cells are the basic unit of life. They contain organelles...',
                'difficulty_level': 'beginner',
                'estimated_duration_minutes': 35,
            },
            {
                'title': 'Photosynthesis Explained',
                'content_type': 'video',
                'description': 'How plants convert light energy into chemical energy',
                'content_body': 'Video: The process of photosynthesis involves chloroplasts...',
                'difficulty_level': 'beginner',
                'estimated_duration_minutes': 30,
            },
            {
                'title': 'DNA and Genetics',
                'content_type': 'lesson',
                'description': 'Understanding genetic information and inheritance',
                'content_body': 'DNA is the hereditary material in organisms...',
                'difficulty_level': 'intermediate',
                'estimated_duration_minutes': 45,
            },
        ]

        for content_data in bio_content_data:
            Content.objects.get_or_create(
                subject=subjects['SCI-BIO-9'],
                title=content_data['title'],
                defaults=content_data
            )
            self.stdout.write(f'  Created content: {content_data["title"]}')

        # Create content for English
        eng_content_data = [
            {
                'title': 'Essay Writing Basics',
                'content_type': 'lesson',
                'description': 'How to structure and write effective essays',
                'content_body': 'An essay consists of an introduction, body paragraphs, and conclusion...',
                'difficulty_level': 'beginner',
                'estimated_duration_minutes': 40,
            },
            {
                'title': 'Poetry Analysis',
                'content_type': 'reading',
                'description': 'Techniques for analyzing poetry',
                'content_body': 'When analyzing poetry, consider literary devices, theme, tone...',
                'difficulty_level': 'intermediate',
                'estimated_duration_minutes': 35,
            },
        ]

        for content_data in eng_content_data:
            Content.objects.get_or_create(
                subject=subjects['ENG-LIT-9'],
                title=content_data['title'],
                defaults=content_data
            )
            self.stdout.write(f'  Created content: {content_data["title"]}')

        # Create badges
        badges_data = [
            {'name': 'First Steps', 'description': 'Completed your first lesson', 'icon': '🎯', 'criteria': 'Complete 1 content item', 'points': 10},
            {'name': 'Knowledge Seeker', 'description': 'Completed 5 lessons', 'icon': '📚', 'criteria': 'Complete 5 content items', 'points': 25},
            {'name': 'High Achiever', 'description': 'Achieved 90%+ on an assessment', 'icon': '⭐', 'criteria': 'Score 90% or higher on any assessment', 'points': 50},
            {'name': 'Persistent Learner', 'description': 'Logged in 5 days in a row', 'icon': '🔥', 'criteria': 'Login streak of 5 days', 'points': 30},
            {'name': 'Master of Mastery', 'description': 'Achieved 100% mastery in a subject', 'icon': '🏆', 'criteria': 'Reach 100% mastery in any subject', 'points': 100},
        ]

        for badge_data in badges_data:
            badge, created = Badge.objects.get_or_create(
                name=badge_data['name'],
                defaults=badge_data
            )
            self.stdout.write(f'  {"Created" if created else "Found"} badge: {badge.name}')

        # Create test students
        students_data = [
            {
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'email': 'sarah.johnson@student.lxp.com',
                'date_of_birth': date(2010, 3, 15),
                'gender': 'F',
                'grade_level': 9,
                'password': 'student123',
            },
            {
                'first_name': 'Michael',
                'last_name': 'Chen',
                'email': 'michael.chen@student.lxp.com',
                'date_of_birth': date(2010, 7, 22),
                'gender': 'M',
                'grade_level': 9,
                'password': 'student123',
            },
            {
                'first_name': 'Emma',
                'last_name': 'Davis',
                'email': 'emma.davis@student.lxp.com',
                'date_of_birth': date(2010, 11, 8),
                'gender': 'F',
                'grade_level': 9,
                'password': 'student123',
            },
        ]

        for student_data in students_data:
            if not Student.objects.filter(email=student_data['email']).exists():
                # Create user
                user = User.objects.create_user(
                    username=student_data['email'],
                    email=student_data['email'],
                    password=student_data['password'],
                    first_name=student_data['first_name'],
                    last_name=student_data['last_name'],
                )
                # Create student
                student = Student.objects.create(
                    user=user,
                    first_name=student_data['first_name'],
                    last_name=student_data['last_name'],
                    email=student_data['email'],
                    date_of_birth=student_data['date_of_birth'],
                    gender=student_data['gender'],
                    grade_level=student_data['grade_level'],
                )
                self.stdout.write(f'  Created student: {student.full_name}')
            else:
                self.stdout.write(f'  Student already exists: {student_data["first_name"]} {student_data["last_name"]}')

        # Create test educator
        if not Educator.objects.filter(email='mr.smith@teacher.lxp.com').exists():
            teacher_user = User.objects.create_user(
                username='mr.smith@teacher.lxp.com',
                email='mr.smith@teacher.lxp.com',
                password='teacher123',
                first_name='John',
                last_name='Smith',
            )
            educator = Educator.objects.create(
                user=teacher_user,
                first_name='John',
                last_name='Smith',
                email='mr.smith@teacher.lxp.com',
                department='Mathematics',
            )
            self.stdout.write(f'  Created educator: {educator.full_name}')
        else:
            self.stdout.write('  Educator already exists: Mr. Smith')

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write('\nTest credentials:')
        self.stdout.write('  Students: sarah.johnson@student.lxp.com / student123')
        self.stdout.write('           michael.chen@student.lxp.com / student123')
        self.stdout.write('           emma.davis@student.lxp.com / student123')
        self.stdout.write('  Educator: mr.smith@teacher.lxp.com / teacher123')
