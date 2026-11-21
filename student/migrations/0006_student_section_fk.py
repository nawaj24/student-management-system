import django.db.models.deletion
from django.db import migrations, models


def link_students_to_sections(apps, schema_editor):
    """Turn the old text values ('10' and 'A') into real Section rows."""
    Student = apps.get_model('student', 'Student')
    SchoolClass = apps.get_model('classroom', 'SchoolClass')
    Section = apps.get_model('classroom', 'Section')

    for student in Student.objects.all():
        text = student.student_class.strip()
        if text.isdigit():
            name, order = f'Class {text}', int(text)
        else:
            name, order = text or 'Unknown', 0
        school_class, _ = SchoolClass.objects.get_or_create(name=name, defaults={'order': order})
        section, _ = Section.objects.get_or_create(
            school_class=school_class,
            name=student.section.strip().upper() or 'A',
        )
        student.class_section = section
        student.save(update_fields=['class_section'])


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0001_initial'),
        ('student', '0005_alter_student_student_id'),
    ]

    operations = [
        # 1. add the new link next to the old text fields
        migrations.AddField(
            model_name='student',
            name='class_section',
            field=models.ForeignKey(
                null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name='students', to='classroom.section',
            ),
        ),
        # 2. copy the old data into it
        migrations.RunPython(link_students_to_sections, migrations.RunPython.noop),
        # 3. drop the old text fields and give the link the old name
        migrations.RemoveField(model_name='student', name='student_class'),
        migrations.RemoveField(model_name='student', name='section'),
        migrations.RenameField(model_name='student', old_name='class_section', new_name='section'),
    ]
