from __future__ import annotations

from typing import Any


REQUIRED_EMPLOYEE_FIELDS = {
    "full_name": "ФИО",
    "position": "должность",
    "department": "подразделение или команда",
    "start_date": "дата выхода",
    "work_format": "формат работы",
}


def validate_payload(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    employee = data.get("employee", {})
    documents = data.get("documents", {})
    local = data.get("local_procedures", {})
    instructions = data.get("instructions", {})
    errors: list[str] = []
    open_questions: list[str] = list(data.get("open_questions", []))

    for key, label in REQUIRED_EMPLOYEE_FIELDS.items():
        if not str(employee.get(key, "")).strip():
            errors.append(f"Заполните поле: {label}.")

    if not str(employee.get("manager", "")).strip():
        open_questions.append("Руководитель не указан.")

    if not str(employee.get("hr_contact", "")).strip() and not str(employee.get("responsible_contact", "")).strip():
        open_questions.append("HR или контакт ответственного не указан.")

    if not any(bool(value) for value in documents.values()):
        errors.append("Выберите хотя бы один тип документов для генерации.")

    if documents.get("parking") and not str(local.get("parking_space", "")).strip():
        open_questions.append("Парковка выбрана, но место или зона парковки не указаны.")

    if documents.get("room_key") and not str(local.get("room", "")).strip():
        open_questions.append("Ключи выбраны, но кабинет или зона доступа не указаны.")

    if documents.get("equipment_handover") and not local.get("equipment"):
        open_questions.append("Передача оборудования выбрана, но список оборудования пуст.")

    for access in data.get("access_requests", []):
        if access.get("sensitivity") in {"sensitive", "admin", "server", "database"}:
            name = access.get("name") or access.get("resource") or "чувствительный ресурс"
            open_questions.append(f"Доступ к '{name}' требует согласования владельца ресурса.")

    selected_instructions = set(instructions.get("selected", []))
    if "electrical_safety" in selected_instructions:
        open_questions.append("Работы с электрооборудованием требуют профильной проверки и допуска ответственным за электрохозяйство.")

    if "height_work" in selected_instructions:
        open_questions.append("Работы на высоте требуют профильной проверки, обучения и допуска ответственным за ОТ.")

    if "special_work" in selected_instructions:
        open_questions.append("Профильные допуски для особых работ не выдаются автоматически и требуют проверки ОТ.")

    return errors, dedupe(open_questions)


def dedupe(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        normalized = item.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result
