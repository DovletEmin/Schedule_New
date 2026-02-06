from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db import models
from smart_selects.db_fields import ChainedForeignKey


class Faculty(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Fakultet"

    def __str__(self):
        return self.name


class Course(models.Model):
    number = models.PositiveSmallIntegerField()
    faculty = models.ForeignKey(
        Faculty, on_delete=models.CASCADE, related_name="courses"
    )

    class Meta:
        unique_together = (("number", "faculty"),)
        verbose_name_plural = "Kurs"

    def __str__(self):
        return f"{self.faculty.name} — {self.number} Kurs"


# Группа
class Group(models.Model):
    name = models.CharField(max_length=50)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="groups")

    class Meta:
        unique_together = (("name", "course"),)
        verbose_name_plural = "Topar"

    def __str__(self):
        return f"{self.name}"


# Подгруппа (A/B)
class Subgroup(models.Model):
    SUBGROUP_CHOICES = (
        ("A", "A"),
        ("B", "B"),
    )
    name = models.CharField(max_length=1, choices=SUBGROUP_CHOICES)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="subgroups")

    class Meta:
        unique_together = (("name", "group"),)
        verbose_name_plural = "Podtopar"

    def __str__(self):
        return f"{self.group} - {self.name} podtopar"


# Модель для объявлений (новостей)
class Announcement(models.Model):
    title = models.CharField(max_length=255, verbose_name="Tekst")
    pdf_file = models.FileField(
        upload_to="announcements_pdfs/", verbose_name="PDF faýl"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bildiriş"
        verbose_name_plural = "Bildirişler"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


# Удалять файл при удалении объекта Announcement
@receiver(post_delete, sender=Announcement)
def delete_announcement_pdf_file(sender, instance, **kwargs):
    if instance.pdf_file:
        instance.pdf_file.delete(False)


class Teacher(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Mugallym"

    def __str__(self):
        return self.name


class Week(models.Model):
    number = models.PositiveIntegerField(unique=True)

    class Meta:
        verbose_name_plural = "Hepde"

    def __str__(self):
        return str(self.number)


class DayChoices(models.IntegerChoices):
    MON = 1, "Duşenbe"
    TUE = 2, "Sişenbe"
    WED = 3, "Çarşenbe"
    THU = 4, "Penşenbe"
    FRI = 5, "Anna"
    SAT = 6, "Şenbe"
    SUN = 7, "Ýekşenbe"


class Day(models.Model):
    number = models.PositiveSmallIntegerField(choices=DayChoices.choices, unique=True)

    class Meta:
        ordering = ["number"]
        verbose_name_plural = "Gün"

    def __str__(self):
        return self.get_number_display()


class LessonNumber(models.Model):
    number = models.PositiveSmallIntegerField(unique=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Sapak nomer"

    def __str__(self):
        return str(self.number)


class LessonType(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Sapak görnüşi"

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        verbose_name_plural = "Sapaklaryň ady"

    def __str__(self):
        return self.name


# Обновленная модель расписания с подгруппой
class TimetableEntry(models.Model):
    faculty = models.ForeignKey('Faculty', on_delete=models.PROTECT, verbose_name='Fakultet', null=True, blank=True)
    course = ChainedForeignKey(
        'Course',
        chained_field="faculty",
        chained_model_field="faculty",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.PROTECT,
        verbose_name='Kurs',
        null=True, blank=True
    )
    group = ChainedForeignKey(
        'Group',
        chained_field="course",
        chained_model_field="course",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.PROTECT,
        verbose_name='Topar',
        null=True, blank=True
    )
    subgroup = ChainedForeignKey(
        'Subgroup',
        chained_field="group",
        chained_model_field="group",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.PROTECT,
        verbose_name='Podtopar',
        null=True, blank=True
    )
    week = models.ForeignKey(Week, on_delete=models.PROTECT)
    day = models.ForeignKey(Day, on_delete=models.PROTECT)
    lesson_number = models.ForeignKey(LessonNumber, on_delete=models.PROTECT)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True
    )
    lesson_type = models.ForeignKey(LessonType, on_delete=models.PROTECT)
    room = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = (("week", "day", "subgroup", "lesson_number"),)
        ordering = ["week__number", "day__number", "lesson_number__number"]
        verbose_name_plural = "Sapak tertibi"

    def __str__(self):
        return f"{self.subgroup} | Week {self.week} | {self.day} #{self.lesson_number} — {self.subject}"
