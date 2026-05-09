from django.contrib import admin
from .models import (
    Faculty,
    Course,
    Group,
    Subgroup,
    Teacher,
    Week,
    Day,
    LessonType,
    LessonNumber,
    Subject,
    TimetableEntry,
    Announcement,
)
from django import forms
from django.contrib.admin.widgets import AutocompleteSelect
from django.contrib.admin import AdminSite
from smart_selects.db_fields import ChainedForeignKey


DEFAULT_ADMIN_GET_APP_LIST = AdminSite.get_app_list


TIMETABLE_ADMIN_MODEL_ORDER = {
    "Fakultet": 1,
    "Kurs": 2,
    "Topar": 3,
    "Podtopar": 4,
    "Mugallym": 5,
    "Sapaklaryň ady": 6,
    "Sapak görnüşi": 7,
    "Sapak nomer": 8,
    "Hepde": 9,
    "Gün": 10,
    "Sapak tertibi": 11,
    "Bildirişler": 12,
}


# Inline для подгрупп внутри группы
class SubgroupInline(admin.TabularInline):
    model = Subgroup
    extra = 1
    show_change_link = True


# Inline для групп внутри курса
class GroupInline(admin.TabularInline):
    model = Group
    extra = 1
    show_change_link = True


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ("name",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("number", "faculty")
    list_filter = ("faculty",)
    inlines = [GroupInline]
    search_fields = ("number", "faculty__name")


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "course")
    list_filter = ("course__faculty", "course__number")
    inlines = [SubgroupInline]
    search_fields = ("name", "course__number", "course__faculty__name")


class SubgroupAdminForm(forms.ModelForm):
    class Meta:
        model = Subgroup
        fields = "__all__"

    def label_from_instance(self, obj):
        return f"{obj.group.course.faculty} | {obj.group.course} | {obj.group} | {obj.get_name_display()}"


@admin.register(Subgroup)
class SubgroupAdmin(admin.ModelAdmin):
    list_display = ("name", "group")
    list_filter = ("group__course",)
    search_fields = ("name", "group__name", "group__course__number")
    form = SubgroupAdminForm


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Week)
class WeekAdmin(admin.ModelAdmin):
    list_display = ("number",)
    ordering = ("number",)
    search_fields = ("number",)


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ("number", "day_name")
    ordering = ("number",)
    search_fields = ("number",)

    def day_name(self, obj):
        return obj.get_number_display()

    day_name.short_description = "Название дня"


@admin.register(LessonNumber)
class LessonNumberAdmin(admin.ModelAdmin):
    list_display = ("number", "start_time", "end_time")
    ordering = ("number",)
    search_fields = ("number",)


@admin.register(LessonType)
class LessonTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name",)


class CustomSubgroupAutocomplete(AutocompleteSelect):
    def get_label(self, obj):
        faculty = obj.group.course.faculty.name if hasattr(obj.group.course.faculty, 'name') else str(obj.group.course.faculty)
        course = obj.group.course.number if hasattr(obj.group.course, 'number') else str(obj.group.course)
        group = obj.group.name if hasattr(obj.group, 'name') else str(obj.group)
        subgroup = obj.get_name_display() if hasattr(obj, 'get_name_display') else str(obj)
        return f"{faculty} | {course} курс | {group} группа | {subgroup} подгруппа"


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = (
        "faculty",
        "course",
        "group",
        "subgroup",
        "week",
        "day",
        "lesson_number",
        "subject",
        "teacher",
        "lesson_type",
        "room",
    )
    list_filter = (
        "faculty",
        "course",
        "group",
        "subgroup",
        "week",
        "day",
        "lesson_type",
        "teacher",
    )
    search_fields = ("subject__name", "teacher__name", "group__name", "room")
    autocomplete_fields = (
        "subject",
        "teacher",
        "lesson_number",
        "lesson_type",
        "week",
        "day",
    )
    list_select_related = (
        "faculty",
        "course",
        "group",
        "subgroup",
        "lesson_number",
        "subject",
        "teacher",
        "lesson_type",
        "week",
        "day",
    )
    ordering = ("faculty", "course", "group", "subgroup", "week", "day", "lesson_number")
    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    ("faculty", "course", "group", "subgroup"),
                    ("week", "day"),
                    ("lesson_number", "lesson_type"),
                    "subject",
                    "teacher",
                    "room",
                ),
                "description": "Заполните все поля для корректного отображения расписания.",
            },
        ),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_group_course(self, obj):
        return obj.subgroup.group.course

    get_group_course.short_description = "Курс"

    def get_group_faculty(self, obj):
        return obj.subgroup.group.course.faculty

    get_group_faculty.short_description = "Факультет"

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        help_texts = {
            "week": "Выберите неделю (1 или 2)",
            "day": "Выберите день недели",
            "lesson_number": "Порядковый номер урока (1, 2, 3...)",
            "lesson_type": "Тип занятия (лекция, практика и т.д.)",
            "subject": "Название предмета",
            "teacher": "ФИО преподавателя",
            "room": "Аудитория (необязательно)",
            "subgroup": "Подгруппа (A/B)",
        }
        if db_field.name in help_texts:
            formfield.help_text = help_texts[db_field.name]
        return formfield


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title",)
    date_hierarchy = "created_at"
    fieldsets = (
        (None, {"fields": ("title", "pdf_file")}),
        ("Дата", {"fields": ("created_at",)}),
    )
    readonly_fields = ("created_at",)


# Кастомизация порядка моделей в меню админки
admin.site.index_title = "Панель управления расписанием"
admin.site.site_header = "OKUW DERSLERINIŇ TERTIBI - Admin"
admin.site.site_title = "OKUW DERSLERINIŇ TERTIBI"

# Переопределение get_app_list для сортировки моделей


def custom_get_app_list(self, request, app_label=None):
    app_list = DEFAULT_ADMIN_GET_APP_LIST(self, request, app_label=app_label)

    for app in app_list:
        if app["app_label"] != "timetable":
            continue

        app["models"].sort(
            key=lambda model: (
                TIMETABLE_ADMIN_MODEL_ORDER.get(model["name"], 999),
                model["name"],
            )
        )

    return app_list


AdminSite.get_app_list = custom_get_app_list
