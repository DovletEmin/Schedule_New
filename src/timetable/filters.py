import django_filters
from .models import TimetableEntry


class TimetableEntryFilter(django_filters.FilterSet):
    # Filter by ID
    teacher_id = django_filters.NumberFilter(field_name="teacher__id")
    week_id = django_filters.NumberFilter(field_name="week__id")
    day_id = django_filters.NumberFilter(field_name="day__id")
    group_id = django_filters.NumberFilter(field_name="group__id")
    faculty_id = django_filters.NumberFilter(field_name="group__course__faculty__id")
    course_id = django_filters.NumberFilter(field_name="group__course__id")

    # Filter by name/number (for text search)
    teacher = django_filters.CharFilter(
        field_name="teacher__name", lookup_expr="icontains"
    )
    week = django_filters.NumberFilter(field_name="week__number")
    day = django_filters.NumberFilter(field_name="day__number")
    group = django_filters.CharFilter(field_name="group__name", lookup_expr="icontains")
    lesson_number = django_filters.NumberFilter(field_name="lesson_number__number")
    faculty = django_filters.CharFilter(
        field_name="group__course__faculty__name", lookup_expr="icontains"
    )
    course = django_filters.NumberFilter(field_name="group__course__number")

    class Meta:
        model = TimetableEntry
        fields = [
            "teacher",
            "teacher_id",
            "week",
            "week_id",
            "day",
            "day_id",
            "group",
            "group_id",
            "lesson_number",
            "faculty",
            "faculty_id",
            "course",
            "course_id",
        ]
