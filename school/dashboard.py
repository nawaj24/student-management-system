from django.db.models import Count
from django.utils import timezone

from classroom.models import SchoolClass
from student.models import Student
from teacher.models import Teacher


def get_dashboard_stats():
    """All the numbers the admin and teacher dashboards show."""
    students = Student.objects.all()
    today = timezone.localdate()

    # order = 1, 2 ... 10, so 'Class 10' comes last (not after 'Class 1')
    classes = SchoolClass.objects.annotate(
        total=Count('sections__students')
    ).order_by('order')

    by_gender = students.values('gender').annotate(total=Count('id'))
    by_gender = by_gender.order_by('-gender')  # Male first
    gender_names = {'Male': 'Boys', 'Female': 'Girls', 'Others': 'Others'}

    recent = students.select_related('section__school_class')

    new_this_month = students.filter(
        joining_date__year=today.year,
        joining_date__month=today.month,
    )

    return {
        'total_students': students.count(),
        'total_teachers': Teacher.objects.count(),
        'total_classes': classes.count(),
        'new_this_month': new_this_month.count(),
        'chart_data': {
            'class_labels': [school_class.name for school_class in classes],
            'class_counts': [school_class.total for school_class in classes],
            'gender_labels': [gender_names[row['gender']] for row in by_gender],
            'gender_counts': [row['total'] for row in by_gender],
        },
        'recent_students': recent.order_by('-joining_date', '-id')[:5],
    }
