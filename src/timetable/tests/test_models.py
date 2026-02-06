import pytest
from timetable.models import (
    Faculty,
    Course,
    Group,
    Week,
    Day,
    Teacher,
    LessonNumber,
    LessonType,
    Subject,
    TimetableEntry,
)


@pytest.mark.django_db
def test_create_timetable_entry():
    faculty = Faculty.objects.create(name="Informatics")
    course = Course.objects.create(number=1, faculty=faculty)
    group = Group.objects.create(name="A", course=course)
    week = Week.objects.create(number=1)
    day = Day.objects.create(number=1)
    teacher = Teacher.objects.create(name="Ali")
    lesson_number = LessonNumber.objects.create(number=1)
    lesson_type = LessonType.objects.create(name="Lecture")
    subject = Subject.objects.create(name="Math")

    entry = TimetableEntry.objects.create(
        week=week,
        day=day,
        group=group,
        lesson_number=lesson_number,
        subject=subject,
        teacher=teacher,
        lesson_type=lesson_type,
        room="101",
    )

    assert (
        str(entry)
        == f"{group} | Week {week.number} | {day} #{lesson_number} — {subject}"
    )
