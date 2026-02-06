from django.urls import reverse

# PDF.js viewer для PDF

from django.http import FileResponse, Http404
import os
import mimetypes

from django.shortcuts import get_object_or_404, render

from .models import (
    Week,
    Day,
    TimetableEntry,
    Faculty,
    Course,
    Group,
    Teacher,
    LessonNumber,
    Announcement,
    Subgroup,
)
from .services import build_timetable

# View для списка объявлений (новостей)
# View для списка объявлений (новостей)


def pdf_viewer(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    relative_url = reverse("announcement-file-view", args=[pk])
    file_url = request.build_absolute_uri(relative_url)
    return render(
        request, "pdf_viewer.html", {"file_url": file_url, "announcement": announcement}
    )


# View для страницы просмотра PDF через iframe
def announcement_pdf_page(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    return render(request, "announcement_pdf_page.html", {"announcement": announcement})


def announcements_list(request):
    sort = request.GET.get("sort", "desc")
    if sort == "asc":
        announcements = Announcement.objects.all().order_by("created_at")
    else:
        announcements = Announcement.objects.all().order_by("-created_at")
    return render(
        request,
        "announcements_list.html",
        {"announcements": announcements, "sort": sort},
    )


# View для отдачи PDF с Content-Disposition: inline
def announcement_file_view(request, pk):
    try:
        announcement = Announcement.objects.get(pk=pk)
        file_path = announcement.pdf_file.path
        if not os.path.exists(file_path):
            raise Http404()
        # Определяем тип файла
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"
        response = FileResponse(open(file_path, "rb"), content_type=mime_type)
        response["Content-Disposition"] = (
            f'inline; filename="{os.path.basename(file_path)}"'
        )
        return response
    except Announcement.DoesNotExist:
        raise Http404()


# Frontend Views


def timetable_view(request):
    """Main timetable view with filters (now with subgroups)"""
    from django.core.cache import cache

    faculties = cache.get_or_set(
        "faculties", lambda: list(Faculty.objects.all().order_by("name")), 60 * 10
    )
    courses = cache.get_or_set(
        "courses",
        lambda: list(Course.objects.select_related("faculty").all().order_by("number")),
        60 * 10,
    )
    groups = cache.get_or_set(
        "groups",
        lambda: list(Group.objects.select_related("course").all().order_by("name")),
        60 * 10,
    )
    subgroups = cache.get_or_set(
        "subgroups",
        lambda: list(
            Subgroup.objects.select_related("group").order_by("group__name", "name")
        ),
        60 * 10,
    )
    teachers = cache.get_or_set(
        "teachers", lambda: list(Teacher.objects.all().order_by("name")), 60 * 10
    )
    weeks = cache.get_or_set(
        "weeks", lambda: list(Week.objects.all().order_by("number")), 60 * 10
    )
    days = cache.get_or_set(
        "days", lambda: list(Day.objects.all().order_by("number")), 60 * 10
    )

    selected_faculty = request.GET.get("faculty", "")
    selected_course = request.GET.get("course", "")
    selected_group = request.GET.get("group", "")
    selected_subgroup = request.GET.get("subgroup", "")
    selected_teacher = request.GET.get("teacher", "")
    selected_week = request.GET.get("week", "")
    selected_day = request.GET.get("day", "")

    # Корректно формируем groups и subgroups для фильтров
    if selected_faculty:
        courses = courses.filter(faculty_id=selected_faculty)

    # Для выбранного курса показываем все группы этого курса
    if selected_course:
        try:
            course_id = int(selected_course)
        except (ValueError, TypeError):
            course_id = None
        if course_id:
            groups = Group.objects.filter(course_id=course_id).order_by("name")
        else:
            groups = Group.objects.none()
    else:
        groups = Group.objects.none()

    # Для выбранной группы показываем все подгруппы этой группы
    if selected_group:
        subgroups = Subgroup.objects.filter(group_id=selected_group).order_by("name")
    elif selected_course:
        group_ids = Group.objects.filter(course_id=selected_course).values_list(
            "id", flat=True
        )
        subgroups = Subgroup.objects.filter(group_id__in=group_ids).order_by(
            "group__name", "name"
        )
    else:
        subgroups = Subgroup.objects.none()

    entries = TimetableEntry.objects.select_related(
        "week",
        "day",
        "subgroup",
        "subgroup__group",
        "subgroup__group__course",
        "subgroup__group__course__faculty",
        "lesson_number",
        "subject",
        "teacher",
        "lesson_type",
    ).all()

    if selected_faculty:
        # Получаем id курсов выбранного факультета
        faculty_course_ids = list(
            Course.objects.filter(faculty_id=selected_faculty).values_list(
                "id", flat=True
            )
        )
        entries = entries.filter(subgroup__group__course_id__in=faculty_course_ids)
    if selected_course:
        entries = entries.filter(subgroup__group__course_id=selected_course)
    if selected_group:
        entries = entries.filter(subgroup__group_id=selected_group)
    if selected_subgroup:
        entries = entries.filter(subgroup_id=selected_subgroup)
    if selected_teacher:
        entries = entries.filter(teacher_id=selected_teacher)
    if selected_week:
        entries = entries.filter(week_id=selected_week)
    if selected_day:
        entries = entries.filter(day_id=selected_day)

    week1_entries = week2_entries = None
    if not selected_week or selected_week == "ahli" or selected_week == "0":
        week1_entries = entries.filter(week__number=1).order_by(
            "week__number",
            "subgroup__group__course__faculty__id",
            "subgroup__group__course__number",
            "subgroup__group__name",
            "subgroup__name",
            "day__number",
            "lesson_number__number",
        )
        week2_entries = entries.filter(week__number=2).order_by(
            "week__number",
            "subgroup__group__course__faculty__id",
            "subgroup__group__course__number",
            "subgroup__group__name",
            "subgroup__name",
            "day__number",
            "lesson_number__number",
        )
        context = {
            "faculties": faculties,
            "courses": courses,
            "groups": groups,
            "subgroups": subgroups,
            "teachers": teachers,
            "weeks": weeks,
            "days": days,
            "week1_entries": week1_entries,
            "week2_entries": week2_entries,
            "entries": None,
            "selected_faculty": selected_faculty,
            "selected_course": selected_course,
            "selected_group": selected_group,
            "selected_subgroup": selected_subgroup,
            "selected_teacher": selected_teacher,
            "selected_week": selected_week,
            "selected_day": selected_day,
        }
    else:
        entries = entries.order_by(
            "week__number",
            "subgroup__group__course__faculty__id",
            "subgroup__group__course__number",
            "subgroup__group__name",
            "subgroup__name",
            "day__number",
            "lesson_number__number",
        )
        context = {
            "faculties": faculties,
            "courses": courses,
            "groups": groups,
            "subgroups": subgroups,
            "teachers": teachers,
            "weeks": weeks,
            "days": days,
            "entries": entries,
            "week1_entries": None,
            "week2_entries": None,
            "selected_faculty": selected_faculty,
            "selected_course": selected_course,
            "selected_group": selected_group,
            "selected_subgroup": selected_subgroup,
            "selected_teacher": selected_teacher,
            "selected_week": selected_week,
            "selected_day": selected_day,
        }

    return render(request, "timetable.html", context)


# --- Вспомогательные функции для timetable_grid ---
def get_filter_options():
    from django.core.cache import cache

    return {
        "faculties": cache.get_or_set(
            "faculties", lambda: list(Faculty.objects.all().order_by("name")), 60 * 10
        ),
        "courses": cache.get_or_set(
            "courses",
            lambda: list(
                Course.objects.select_related("faculty").all().order_by("number")
            ),
            60 * 10,
        ),
        "teachers": cache.get_or_set(
            "teachers", lambda: list(Teacher.objects.all().order_by("name")), 60 * 10
        ),
        "weeks": cache.get_or_set(
            "weeks", lambda: list(Week.objects.all().order_by("number")), 60 * 10
        ),
        "days": cache.get_or_set(
            "days", lambda: list(Day.objects.all().order_by("number")), 60 * 10
        ),
        "groups": cache.get_or_set(
            "groups",
            lambda: list(Group.objects.select_related("course").all().order_by("name")),
            60 * 10,
        ),
    }


def get_selected_filters(request):
    return {
        "faculty": request.GET.get("faculty", ""),
        "course": request.GET.get("course", ""),
        "group": request.GET.get("group", ""),
        "teacher": request.GET.get("teacher", ""),
        "week": request.GET.get("week", ""),
        "day": request.GET.get("day", ""),
        "subgroup": request.GET.get("subgroup", ""),
    }


def get_filter_groups(selected_course):
    if selected_course:
        try:
            course_id = int(selected_course)
        except (ValueError, TypeError):
            return Group.objects.none()
        return Group.objects.filter(course_id=course_id).order_by("name")
    return Group.objects.none()


def get_subgroups(selected_group, selected_course):
    if selected_group:
        return (
            Subgroup.objects.select_related("group")
            .filter(group_id=selected_group)
            .order_by("name")
        )
    elif selected_course:
        group_ids = Group.objects.filter(course_id=selected_course).values_list(
            "id", flat=True
        )
        return (
            Subgroup.objects.select_related("group")
            .filter(group_id__in=group_ids)
            .order_by("group__name", "name")
        )
    return Subgroup.objects.none()


def get_teachers(selected_faculty, selected_course):
    from django.core.cache import cache

    if selected_faculty:
        faculty_course_ids = list(
            Course.objects.filter(faculty_id=selected_faculty).values_list(
                "id", flat=True
            )
        )
        return (
            Teacher.objects.filter(
                timetableentry__subgroup__group__course_id__in=faculty_course_ids
            )
            .distinct()
            .order_by("name")
        )
    elif selected_course:
        return (
            Teacher.objects.filter(
                timetableentry__subgroup__group__course_id=selected_course
            )
            .distinct()
            .order_by("name")
        )
    return cache.get_or_set(
        "teachers", lambda: list(Teacher.objects.all().order_by("name")), 60 * 10
    )


def get_courses_query(selected_faculty, selected_course, selected_teacher):
    qs = (
        Course.objects.select_related("faculty")
        .all()
        .order_by("faculty__name", "number")
    )
    if selected_faculty:
        qs = qs.filter(faculty_id=selected_faculty)
    if selected_course:
        qs = qs.filter(id=selected_course)
    if selected_teacher:
        courses_with_teacher = (
            TimetableEntry.objects.filter(teacher_id=selected_teacher)
            .values_list("subgroup__group__course_id", flat=True)
            .distinct()
        )
        qs = qs.filter(id__in=courses_with_teacher)
    return qs


def get_week_day_objs(selected_week, selected_day):
    week_obj = None
    day_obj = None
    if selected_week:
        try:
            week_obj = Week.objects.get(id=selected_week)
        except (Week.DoesNotExist, ValueError):
            pass
    if selected_day:
        try:
            day_obj = Day.objects.get(id=selected_day)
        except (Day.DoesNotExist, ValueError):
            pass
    return week_obj, day_obj


def collect_grid_data(filters, filter_groups, subgroups, teachers, weeks, days, groups):
    # Если не выбраны фильтры (только неделя или вообще ничего)
    group_order = ["course__faculty__name", "course__number", "name"]
    subgroup_order = ["group__name", "name"]
    week1_groups_data, week2_groups_data = [], []
    faculties_qs = Faculty.objects.all().order_by("name")
    # Фильтрация недель
    if filters["week"] and filters["week"] not in ("ahli", "0", ""):
        weeks_qs = Week.objects.filter(id=filters["week"]).order_by("number")
    else:
        weeks_qs = Week.objects.all().order_by("number")
    # Фильтрация дней
    if filters["day"]:
        days_qs = [d for d in days if str(d.id) == str(filters["day"])]
    else:
        days_qs = days
    # Определяем группы для отображения
    if not any(
        [
            filters["faculty"],
            filters["course"],
            filters["group"],
            filters["teacher"],
            filters["day"],
        ]
    ):
        # Без фильтров — как раньше
        for week in weeks_qs:
            for faculty in faculties_qs:
                courses_qs = Course.objects.filter(faculty=faculty).order_by("number")
                for course in courses_qs:
                    groups_qs = Group.objects.filter(course=course).order_by(
                        *group_order
                    )
                    for group in groups_qs:
                        subgroups_qs = Subgroup.objects.filter(group=group).order_by(
                            *subgroup_order
                        )
                        entries_query = TimetableEntry.objects.select_related(
                            "week",
                            "day",
                            "subgroup",
                            "subgroup__group",
                            "lesson_number",
                            "subject",
                            "teacher",
                            "lesson_type",
                        ).filter(week=week, subgroup__group=group)
                        timetable_data, lesson_number_objs = build_timetable(
                            entries_query,
                            days_qs,
                            list(subgroups_qs),
                            filters["teacher"],
                        )
                        group_data = {
                            "faculty": faculty,
                            "course": course,
                            "group": group,
                            "subgroups": list(subgroups_qs),
                            "timetable": timetable_data,
                            "lesson_numbers": lesson_number_objs,
                            "week_numbers": [week.number],
                            "group_colspan": subgroups_qs.count() * 2,
                        }
                        if week.number == 1:
                            week1_groups_data.append(group_data)
                        else:
                            week2_groups_data.append(group_data)
        return week1_groups_data, week2_groups_data, []
    # С фильтрами — всегда по группам, а не по курсам!
    # Получаем группы согласно фильтрам
    groups_qs = Group.objects.all().order_by(*group_order)
    if filters["faculty"]:
        groups_qs = groups_qs.filter(course__faculty_id=filters["faculty"])
    if filters["course"]:
        groups_qs = groups_qs.filter(course_id=filters["course"])
    if filters["group"]:
        groups_qs = groups_qs.filter(id=filters["group"])
    if not groups_qs.exists():
        return [], [], []
    # Если выбрана конкретная группа, показываем только её
    if filters["group"]:
        groups_qs = groups_qs.filter(id=filters["group"])
    all_lesson_numbers = list(LessonNumber.objects.all().order_by("number"))
    for week in weeks_qs:
        for group in groups_qs:
            subgroups_qs = Subgroup.objects.filter(group=group).order_by(
                *subgroup_order
            )
            entries_query = TimetableEntry.objects.select_related(
                "week",
                "day",
                "subgroup",
                "subgroup__group",
                "lesson_number",
                "subject",
                "teacher",
                "lesson_type",
            ).filter(week=week, subgroup__group=group)
            if filters["teacher"]:
                entries_query = entries_query.filter(teacher_id=filters["teacher"])
            if filters["day"]:
                entries_query = entries_query.filter(day_id=filters["day"])
            if filters["week"] and filters["week"] not in ("ahli", "0"):
                entries_query = entries_query.filter(week_id=filters["week"])
            # Передаем days_qs вместо days для корректной структуры
            timetable_data, lesson_number_objs = build_timetable(
                entries_query, days_qs, list(subgroups_qs), filters["teacher"]
            )
            # Заменяем lesson_number_objs на полный список для таблицы
            group_data = {
                "faculty": group.course.faculty,
                "course": group.course,
                "group": group,
                "subgroups": list(subgroups_qs),
                "timetable": timetable_data,
                "lesson_numbers": all_lesson_numbers,
                "week_numbers": [week.number],
                "group_colspan": subgroups_qs.count() * 2,
            }
            if week.number == 1:
                week1_groups_data.append(group_data)
            else:
                week2_groups_data.append(group_data)
    return week1_groups_data, week2_groups_data, []


def timetable_grid(request):
    """Grid view of timetable - Excel-like format with days as rows and lesson numbers as columns"""
    filter_options = get_filter_options()
    filters = get_selected_filters(request)
    filter_groups = get_filter_groups(filters["course"])
    subgroups = get_subgroups(filters["group"], filters["course"])
    teachers = get_teachers(filters["faculty"], filters["course"])
    weeks = filter_options["weeks"]
    days = filter_options["days"]
    groups = filter_options["groups"]
    week_obj, day_obj = get_week_day_objs(filters["week"], filters["day"])
    # Фильтруем курсы по факультету для выпадающего списка
    courses = filter_options["courses"]
    if filters["faculty"]:
        courses = [c for c in courses if str(c.faculty_id) == str(filters["faculty"])]
    context = {
        "faculties": filter_options["faculties"],
        "courses": courses,
        "filter_groups": filter_groups,
        "groups": groups,
        "subgroups": subgroups,
        "teachers": teachers,
        "weeks": weeks,
        "days": days,
        "selected_faculty": filters["faculty"],
        "selected_course": filters["course"],
        "selected_group": filters["group"],
        "selected_subgroup": filters["subgroup"],
        "selected_teacher": filters["teacher"],
        "selected_week": filters["week"],
        "selected_day": filters["day"],
        "selected_week_obj": week_obj,
        "selected_day_obj": day_obj,
    }
    week1_courses_data, week2_courses_data, all_courses_data = collect_grid_data(
        filters, filter_groups, subgroups, teachers, weeks, days, groups
    )
    context["week1_courses_data"] = week1_courses_data
    context["week2_courses_data"] = week2_courses_data
    context["courses_data"] = all_courses_data
    return render(request, "timetable_grid.html", context)
