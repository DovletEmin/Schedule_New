from .models import LessonNumber


def build_timetable(entries, days, subgroup_order=None, selected_teacher_id=None):
    # Оптимизация: минимизируем количество запросов, работаем с уже загруженными данными
    # entries - QuerySet, days - QuerySet или list
    entries = list(
        entries.select_related(
            "lesson_number",
            "subject",
            "teacher",
            "lesson_type",
            "subgroup",
            "subgroup__group",
        )
    )
    # Словарь: (day_id, lesson_number_id) -> [entry, ...]
    entry_map = {}
    for e in entries:
        key = (e.day_id, e.lesson_number_id)
        entry_map.setdefault(key, []).append(e)
    # lesson_number_objs - теперь ВСЕ номера уроков
    lesson_number_objs = list(LessonNumber.objects.all().order_by("number"))
    timetable_data = {}
    for day in days:
        lesson_data = {}
        for lesson_num_obj in lesson_number_objs:
            lesson_entries = entry_map.get((day.id, lesson_num_obj.id), [])
            if not lesson_entries:
                # Пустая ячейка (нет занятия)
                lesson_data[lesson_num_obj.number] = None
                continue
            first_entry = lesson_entries[0]
            is_same_subject = all(
                e.subject_id == first_entry.subject_id
                and e.lesson_type_id == first_entry.lesson_type_id
                for e in lesson_entries
            )
            is_lecture = first_entry.lesson_type.name.lower() in [
                "umumy",
                "лекция",
                "lecture",
            ]
            teacher_matches = False
            if selected_teacher_id:
                for e in lesson_entries:
                    if e.teacher_id and str(e.teacher_id) == str(selected_teacher_id):
                        teacher_matches = True
                        break
            if is_lecture and is_same_subject:
                if selected_teacher_id and not teacher_matches:
                    lesson_data[lesson_num_obj.number] = {
                        "is_lecture": True,
                        "subject": None,
                        "lesson_type": first_entry.lesson_type.name,
                        "teacher": None,
                        "room": None,
                        "subgroups": [
                            f"{e.subgroup.group.name} - {e.subgroup.name}"
                            for e in lesson_entries
                        ],
                    }
                else:
                    lesson_data[lesson_num_obj.number] = {
                        "is_lecture": True,
                        "subject": first_entry.subject.name,
                        "lesson_type": first_entry.lesson_type.name,
                        "teacher": first_entry.teacher.name
                        if first_entry.teacher
                        else None,
                        "room": first_entry.room or None,
                        "subgroups": [
                            f"{e.subgroup.group.name} - {e.subgroup.name}"
                            for e in lesson_entries
                        ],
                    }
            else:
                # Use subgroup.id as keys so templates can lookup by subgroup.id
                subgroup_lessons_dict = {}
                for e in lesson_entries:
                    key = e.subgroup.id
                    subgroup_lessons_dict[key] = {
                        "subgroup": f"{e.subgroup.group.name} - {e.subgroup.name}",
                        "subgroup_id": key,
                        "subject": e.subject.name,
                        "lesson_type": e.lesson_type.name,
                        "teacher": e.teacher.name if e.teacher else None,
                        "teacher_id": e.teacher_id,
                        "room": e.room or None,
                    }
                subgroup_lessons_map = {}
                if subgroup_order:
                    for sg in subgroup_order:
                        sg_key = sg.id if hasattr(sg, "id") else sg
                        gl = subgroup_lessons_dict.get(sg_key)
                        if (
                            selected_teacher_id
                            and gl
                            and gl.get("teacher_id")
                            and str(gl.get("teacher_id")) != str(selected_teacher_id)
                        ):
                            subgroup_lessons_map[sg_key] = None
                        else:
                            subgroup_lessons_map[sg_key] = gl
                else:
                    for sg_key, glesson in subgroup_lessons_dict.items():
                        if (
                            selected_teacher_id
                            and glesson
                            and glesson.get("teacher_id")
                            and str(glesson.get("teacher_id"))
                            != str(selected_teacher_id)
                        ):
                            subgroup_lessons_map[sg_key] = None
                        else:
                            subgroup_lessons_map[sg_key] = glesson
                lesson_data[lesson_num_obj.number] = {
                    "is_lecture": False,
                    "subgroup_lessons": [v for v in subgroup_lessons_map.values() if v],
                    "subgroup_lessons_map": subgroup_lessons_map,
                }
        # timetable_data теперь всегда содержит все lesson_numbers (даже если пусто)
        timetable_data[day.id] = {
            "day_name": day.get_number_display(),
            "lessons": lesson_data,
            "lesson_count": len(lesson_data),
        }
    return timetable_data, lesson_number_objs
