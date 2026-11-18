from django.db.models import Count
from django.utils import timezone

from home_auth.models import CustomUser
from student.models import Student


def class_sort_key(name):
    """Sort classes as 1, 2, ... 10 (not '1', '10', '2')."""
    return (0, int(name), '') if name.isdigit() else (1, 0, name)


def get_dashboard_stats():
    """All the numbers the admin and teacher dashboards show."""
    students = Student.objects.all()
    today = timezone.localdate()

    by_class = students.values('student_class').annotate(total=Count('id'))
    by_class = sorted(by_class, key=lambda row: class_sort_key(row['student_class']))

    by_gender = students.values('gender').annotate(total=Count('id'))
    by_gender = by_gender.order_by('-gender')  # Male first
    gender_names = {'Male': 'Boys', 'Female': 'Girls', 'Others': 'Others'}

    new_this_month = students.filter(
        joining_date__year=today.year,
        joining_date__month=today.month,
    )

    return {
        'total_students': students.count(),
        'total_teachers': CustomUser.objects.filter(is_teacher=True).count(),
        'total_classes': len(by_class),
        'new_this_month': new_this_month.count(),
        'chart_data': {
            'class_labels': [f"Class {row['student_class']}" for row in by_class],
            'class_counts': [row['total'] for row in by_class],
            'gender_labels': [gender_names[row['gender']] for row in by_gender],
            'gender_counts': [row['total'] for row in by_gender],
        },
        'recent_students': students.order_by('-joining_date', '-id')[:5],
    }
