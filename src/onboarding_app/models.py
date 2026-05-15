from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .account_naming import suggest_email, suggest_login


DEFAULT_DOCUMENTS = {
    "resource_access": True,
    "inventory_inclusion": True,
    "building_pass": True,
    "room_key": False,
    "parking": False,
    "equipment_handover": True,
    "welcome_email": True,
    "instructions": True,
}

DEFAULT_INSTRUCTIONS = ["pvtr", "occupational_safety", "fire_safety", "first_aid", "information_security"]
FIELD_WORK_INSTRUCTIONS = ["electrical_safety", "height_work"]


def load_defaults(project_root: Path) -> dict[str, str]:
    defaults = {
        "email_domain": "test12systems.ru",
        "sender_email": "hr@test12systems.ru",
        "default_instruction_mode": "linked",
        "output_dir": "employees",
    }
    path = project_root / "config" / "defaults.yml"
    if not path.exists():
        return defaults
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip().strip('"').strip("'")
        if key.strip() in defaults and value:
            defaults[key.strip()] = value
    return defaults


def normalize_payload(payload: dict[str, Any], project_root: Path) -> dict[str, Any]:
    defaults = load_defaults(project_root)
    data = deepcopy(payload)
    employee = data.setdefault("employee", {})
    accounts = data.setdefault("accounts", {})
    documents = data.setdefault("documents", {})
    local = data.setdefault("local_procedures", {})
    instructions = data.setdefault("instructions", {})
    generation = data.setdefault("generation", {})

    for key, value in DEFAULT_DOCUMENTS.items():
        documents.setdefault(key, value)

    if not str(employee.get("work_format", "")).strip():
        employee["work_format"] = "офис"

    full_name = employee.get("full_name", "").strip()
    email_domain = accounts.get("email_domain") or defaults["email_domain"]
    accounts["email_domain"] = email_domain
    accounts["sender_email"] = accounts.get("sender_email") or defaults["sender_email"]
    accounts["suggested_login"] = accounts.get("suggested_login") or suggest_login(full_name)
    accounts["suggested_email"] = accounts.get("known_email") or accounts.get("suggested_email") or suggest_email(
        full_name, email_domain
    )

    instructions.setdefault("mode", defaults["default_instruction_mode"])
    selected = instructions.get("selected") or DEFAULT_INSTRUCTIONS
    normalized_selected = [item for item in selected if item]
    if _is_field_work(employee.get("work_format", "")):
        for item in FIELD_WORK_INSTRUCTIONS:
            if item not in normalized_selected:
                normalized_selected.append(item)
    instructions["selected"] = normalized_selected

    data.setdefault("access_requests", [])
    data.setdefault("open_questions", [])
    generation.setdefault("package_mode", "draft")
    generation.setdefault("output_dir", defaults["output_dir"])
    generation.setdefault("output_slug", "")

    local.setdefault("equipment", [])
    return data


def instruction_catalog() -> list[dict[str, str]]:
    return [
        {
            "id": "pvtr",
            "title": "Правила внутреннего трудового распорядка",
            "public_file": "examples/instructions/pvtr_public_fragment.md",
            "check_file": "templates/knowledge-checks/knowledge_check_pvtr.html",
        },
        {
            "id": "occupational_safety",
            "title": "Охрана труда при офисной работе",
            "public_file": "examples/instructions/occupational_safety_public_fragment.md",
            "check_file": "templates/knowledge-checks/knowledge_check_occupational_safety.html",
        },
        {
            "id": "fire_safety",
            "title": "Пожарная безопасность",
            "public_file": "examples/instructions/fire_safety_public_fragment.md",
            "check_file": "templates/knowledge-checks/knowledge_check_fire_safety.html",
        },
        {
            "id": "first_aid",
            "title": "Первая помощь",
            "public_file": "examples/instructions/first_aid_public_fragment.md",
            "check_file": "templates/knowledge-checks/knowledge_check_first_aid.html",
        },
        {
            "id": "information_security",
            "title": "Информационная безопасность и работа в сети",
            "public_file": "examples/instructions/information_security_public_fragment.md",
            "check_file": "templates/knowledge-checks/knowledge_check_information_security.html",
            "default": "true",
        },
        {
            "id": "electrical_safety",
            "title": "Электробезопасность и работы с электрооборудованием",
            "public_file": "examples/instructions/electrical_safety_public_fragment.md",
            "check_file": "templates/knowledge-checks/knowledge_check_electrical_safety.html",
            "default": "false",
            "field_work": "true",
        },
        {
            "id": "height_work",
            "title": "Работы на высоте",
            "public_file": "examples/instructions/height_work_public_fragment.md",
            "check_file": "templates/knowledge-checks/knowledge_check_height_work.html",
            "default": "false",
            "field_work": "true",
        },
    ]


def _is_field_work(work_format: str) -> bool:
    normalized = work_format.strip().lower()
    return "выезд" in normalized or "объект" in normalized
