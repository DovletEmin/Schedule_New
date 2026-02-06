from django.core.management.base import BaseCommand
from timetable.models import (
    Faculty,
    Course,
    Group,
    Subgroup,
    Week,
    Day,
    LessonType,
    LessonNumber,
    Subject,
    Teacher,
    TimetableEntry,
)
from datetime import time


class Command(BaseCommand):
    help = "Заполняет базу начальными тестовыми данными"

    def handle(self, *args, **options):
        # Очистка всех данных
        TimetableEntry.objects.all().delete()
        Subgroup.objects.all().delete()
        Group.objects.all().delete()
        Course.objects.all().delete()
        Faculty.objects.all().delete()
        Week.objects.all().delete()
        Day.objects.all().delete()
        LessonType.objects.all().delete()
        LessonNumber.objects.all().delete()
        Subject.objects.all().delete()
        Teacher.objects.all().delete()

        # Факультеты
        faculties = [
            {"name": "Факультет 1"},
            {"name": "Факультет 2"},
        ]
        faculty_objs = []
        for fdata in faculties:
            faculty_objs.append(Faculty.objects.create(name=fdata["name"]))

        # Курсы
        course_objs = []
        for faculty in faculty_objs:
            for course_num in range(1, 6):
                course_objs.append(Course.objects.create(number=course_num, faculty=faculty))

        # Для каждого курса — по две группы, в каждой по две подгруппы (A/B)
        group_objs = []
        for course in course_objs:
            for i in range(1, 3):
                group = Group.objects.create(name=f"{i} группа", course=course)
                group_objs.append(group)
                for sub in ["A", "B"]:
                    Subgroup.objects.create(name=sub, group=group)

        # Недели
        for i in range(1, 3):
            Week.objects.create(number=i)

        # Дни недели (1-6)
        for num in range(1, 7):
            Day.objects.create(number=num)

        # Типы занятий: только лекция и практика
        for lt in ["Umumy", "Praktika"]:
            LessonType.objects.create(name=lt)

        # Только 3 урока
        times = [
            (1, "08:00", "08:45"),
            (2, "08:55", "09:40"),
            (3, "09:50", "10:35"),
        ]
        for num, start, end in times:
            LessonNumber.objects.create(
                number=num,
                start_time=time.fromisoformat(start),
                end_time=time.fromisoformat(end),
            )

        # Пример предметов
        for subj in ["Matematika", "Fizika", "Informatika"]:
            Subject.objects.create(name=subj)

        # Пример учителей
        for t in ["Aman Amanow", "Gurban Gurbanow", "Aýna Aýnadowa"]:
            Teacher.objects.create(name=t)


        # Новая логика: для каждой подгруппы — создать расписание с заполнением faculty, course, group, subgroup
        weeks = list(Week.objects.all())
        days = list(Day.objects.all())
        lesson_numbers = list(LessonNumber.objects.all())
        subjects = list(Subject.objects.all())
        teachers = list(Teacher.objects.all())
        lesson_types = list(LessonType.objects.all())
        subgroups = list(Subgroup.objects.select_related('group__course__faculty').all())

        for subgroup in subgroups:
            group = subgroup.group
            course = group.course
            faculty = course.faculty
            for week in weeks:
                for day in days:
                    # Лекция (только подгруппа A, lesson_number=1)
                    if subgroup.name == "A" and len(lesson_numbers) > 0:
                        lesson_number_lecture = lesson_numbers[0]  # 1
                        subject = subjects[(day.number + week.number) % len(subjects)]
                        teacher = teachers[(day.number + week.number) % len(teachers)]
                        TimetableEntry.objects.create(
                            faculty=faculty,
                            course=course,
                            group=group,
                            subgroup=subgroup,
                            week=week,
                            day=day,
                            lesson_number=lesson_number_lecture,
                            subject=subject,
                            teacher=teacher,
                            lesson_type=LessonType.objects.get(name="Umumy"),
                            room="101",
                        )
                    # Практика (обе подгруппы, lesson_number=2 и 3)
                    for idx, practice_lesson_idx in enumerate([1, 2]):
                        if practice_lesson_idx < len(lesson_numbers):
                            lesson_number_practice = lesson_numbers[practice_lesson_idx]  # 2 или 3
                            subject = subjects[(day.number + week.number + idx + 1) % len(subjects)]
                            teacher = teachers[(day.number + week.number + idx + 1) % len(teachers)]
                            TimetableEntry.objects.create(
                                faculty=faculty,
                                course=course,
                                group=group,
                                subgroup=subgroup,
                                week=week,
                                day=day,
                                lesson_number=lesson_number_practice,
                                subject=subject,
                                teacher=teacher,
                                lesson_type=LessonType.objects.get(name="Praktika"),
                                room=f"{200 + lesson_number_practice.number}",
                            )

        self.stdout.write(
            self.style.SUCCESS("База данных успешно заполнена начальными данными!")
        )
