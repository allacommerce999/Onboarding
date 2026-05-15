from __future__ import annotations

import json
import shutil
from datetime import date
from html import escape
from pathlib import Path
from typing import Any

from .account_naming import make_employee_slug, split_full_name
from .models import instruction_catalog, normalize_payload
from .render_docx import write_docx
from .render_email import write_welcome_email
from .render_xlsx import write_xlsx
from .validation import validate_payload


class PackageBuildError(ValueError):
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


def build_package(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    project_root = project_root.resolve()
    data = normalize_payload(payload, project_root)
    errors, open_questions = validate_payload(data)
    if errors:
        raise PackageBuildError(errors)
    data["open_questions"] = open_questions

    employee = data["employee"]
    generation = data["generation"]
    output_dir = _safe_output_dir(project_root, generation.get("output_dir", "employees"))
    slug = generation.get("output_slug") or make_employee_slug(employee["full_name"], employee["start_date"])
    package_dir = _unique_package_dir(output_dir, slug)
    _ensure_inside(project_root, package_dir)

    dirs = {
        "input": package_dir / "00_input",
        "summary": package_dir / "01_summary",
        "access": package_dir / "02_access",
        "local": package_dir / "03_local_procedures",
        "instructions": package_dir / "04_instructions",
        "email": package_dir / "05_email",
    }
    for folder in dirs.values():
        folder.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    created.append(_write_json(dirs["input"] / "employee_input.json", data))
    created.extend(_write_summary(dirs["summary"], data))
    created.extend(_write_access_docs(dirs["access"], data))
    created.extend(_write_local_docs(dirs["local"], data))
    created.extend(_write_instruction_docs(project_root, dirs["instructions"], data))
    created.extend(_write_email_docs(dirs["email"], data))
    created.append(_write_quality_check(package_dir / "Проверка.docx", data))

    relative_files = [str(path.relative_to(package_dir)).replace("\\", "/") for path in created]
    return {
        "package_dir": str(package_dir),
        "relative_package_dir": str(package_dir.relative_to(project_root)).replace("\\", "/"),
        "created_files": relative_files,
        "open_questions": data["open_questions"],
    }


def _unique_package_dir(output_dir: Path, slug: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    candidate = output_dir / slug
    if not candidate.exists():
        return candidate
    for index in range(2, 100):
        next_candidate = output_dir / f"{slug}-{index:02d}"
        if not next_candidate.exists():
            return next_candidate
    raise PackageBuildError([f"Не удалось подобрать свободное имя папки для {slug}."])


def _safe_output_dir(project_root: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        resolved = (project_root / candidate).resolve()
    try:
        resolved.relative_to(project_root)
    except ValueError as error:
        raise PackageBuildError(["Папка вывода должна находиться внутри Onboarding-Public."]) from error
    return resolved


def _ensure_inside(root: Path, path: Path) -> None:
    path.resolve().relative_to(root)


def _write_json(path: Path, data: dict[str, Any]) -> Path:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _write_summary(folder: Path, data: dict[str, Any]) -> list[Path]:
    employee = data["employee"]
    accounts = data["accounts"]
    files = []
    files.append(
        _write_text(
            folder / "employee_card.md",
            f"""# Карточка сотрудника

| Поле | Значение |
|------|----------|
| ФИО | {employee.get('full_name', '')} |
| Должность | {employee.get('position', '')} |
| Подразделение | {employee.get('department', '')} |
| Дата выхода | {employee.get('start_date', '')} |
| Формат работы | {employee.get('work_format', '')} |
| Руководитель | {employee.get('manager', '')} |
| HR / ответственный | {employee.get('hr_contact') or employee.get('responsible_contact', '')} |
| Buddy | {employee.get('buddy', 'не назначен')} |
| Предполагаемый логин | {accounts.get('suggested_login', '')} |
| Предполагаемый e-mail | {accounts.get('suggested_email', '')} |

Статус: карточка подготовлена для проверки. Доступы и допуски не считаются выданными автоматически.
""",
        )
    )
    files.append(
        _write_text(
            folder / "onboarding_plan.md",
            f"""# Onboarding-план

## До первого дня

- Подтвердить дату выхода: {employee.get('start_date', '')}.
- Проверить руководителя, HR-контакт и buddy.
- Передать заявки ответственным службам.

## Первый день

- Встреча с руководителем: {employee.get('manager', '')}.
- Проверка рабочего места, пропуска, ключей и оборудования.
- Ознакомление с назначенными инструкциями.

## Первая неделя

- Настроить доступы после согласования владельцев ресурсов.
- Провести вводные встречи по процессам команды.
- Зафиксировать открытые вопросы из `Проверка.docx`.

## 30/60/90 дней

- 30 дней: проверить адаптацию и базовые задачи.
- 60 дней: сверить доступы, обучение и регулярные процессы.
- 90 дней: провести итоговую встречу по испытательному сроку или адаптационному периоду.
""",
        )
    )
    files.append(_write_text(folder / "package_index.md", _package_index(data)))
    return files


def _package_index(data: dict[str, Any]) -> str:
    open_questions = "\n".join(f"- {item}" for item in data["open_questions"]) or "- Нет открытых вопросов."
    return f"""# Индекс onboarding-пакета

Пакет создан: {date.today().isoformat()}

## Навигация

- `00_input/employee_input.json` - исходные данные.
- `01_summary/employee_card.md` - карточка сотрудника.
- `01_summary/onboarding_plan.md` - onboarding-план.
- `02_access/` - доступы и матрица ресурсов.
- `03_local_procedures/` - пропуск, ключи, парковка, оборудование.
- `04_instructions/` - назначенные инструкции и проверки знаний.
- `05_email/welcome_email.eml` - черновик welcome-письма.
- `Проверка.docx` - открытые вопросы.

## Важные статусы

- Доступы, пропуска, ключи, оборудование и инструктажи имеют статус `требует оформления` или `требует согласования`.
- Письмо не отправляется автоматически.
- Чувствительные доступы не помечаются как выданные.

## Открытые вопросы

{open_questions}
"""


def _write_access_docs(folder: Path, data: dict[str, Any]) -> list[Path]:
    documents = data["documents"]
    if not documents.get("resource_access"):
        return []
    employee = data["employee"]
    access_requests = data.get("access_requests") or _default_access_requests()
    rows = [
        [
            item.get("name", ""),
            item.get("type", ""),
            item.get("owner", "владелец ресурса"),
            item.get("status", "требует согласования"),
        ]
        for item in access_requests
    ]
    files = []
    files.append(
        _docx(
            folder / "service_memo_resource_access.docx",
            "Служебная записка на доступы к ресурсам",
            [
                f"Просим рассмотреть предоставление доступов сотруднику: {employee.get('full_name', '')}.",
                f"Должность: {employee.get('position', '')}. Подразделение: {employee.get('department', '')}.",
                "Документ является публичным шаблоном и не подтверждает фактическую выдачу доступов.",
            ],
            [{"title": "Запрашиваемые ресурсы", "headers": ["Ресурс", "Тип", "Владелец", "Статус"], "rows": rows}],
        )
    )
    files.append(
        _xlsx(
            folder / "domain_account_register_row.xlsx",
            "Domain account",
            [
                ["ФИО", "Логин", "E-mail", "Подразделение", "Статус"],
                [
                    employee.get("full_name", ""),
                    data["accounts"].get("suggested_login", ""),
                    data["accounts"].get("suggested_email", ""),
                    employee.get("department", ""),
                    "требует оформления",
                ],
            ],
        )
    )
    files.append(
        _write_text(
            folder / "access_matrix.md",
            "# Матрица доступов\n\n"
            + "\n".join(
                f"- {item.get('name', '')}: {item.get('status', 'требует согласования')} ({item.get('owner', 'владелец ресурса')})"
                for item in access_requests
            )
            + "\n",
        )
    )
    return files


def _write_local_docs(folder: Path, data: dict[str, Any]) -> list[Path]:
    employee = data["employee"]
    documents = data["documents"]
    local = data["local_procedures"]
    files: list[Path] = []
    if documents.get("inventory_inclusion"):
        files.append(
            _docx(
                folder / "service_memo_inventory_inclusion.docx",
                "Служебная записка на включение в инвентаризационную ведомость",
                [
                    f"Сотрудник: {employee.get('full_name', '')}.",
                    f"Подразделение: {employee.get('department', '')}.",
                    "Статус: требует оформления материально ответственным лицом.",
                ],
                [
                    {
                        "title": "Оборудование",
                        "headers": ["Наименование", "Инвентарный номер", "Статус"],
                        "rows": _equipment_rows(local),
                    }
                ],
            )
        )
    if documents.get("building_pass"):
        files.append(
            _docx(
                folder / "building_pass_request.docx",
                "Заявка на пропуск",
                [
                    f"Просим оформить пропуск сотруднику: {employee.get('full_name', '')}.",
                    f"Дата выхода: {employee.get('start_date', '')}.",
                    f"Формат работы: {employee.get('work_format', '')}.",
                    "Статус: требует подтверждения службой пропусков.",
                ],
            )
        )
    if documents.get("room_key"):
        files.append(
            _docx(
                folder / "room_key_request.docx",
                "Заявка на право получения ключей",
                [
                    f"Сотрудник: {employee.get('full_name', '')}.",
                    f"Кабинет или зона: {local.get('room', 'требует уточнения')}.",
                    "Статус: требует подтверждения АХО или ответственного за помещение.",
                ],
            )
        )
    if documents.get("parking"):
        files.append(
            _xlsx(
                folder / "parking_access_list_updated.xlsx",
                "Parking",
                [
                    ["ФИО", "Подразделение", "Парковочная зона", "Автомобиль", "Статус"],
                    [
                        employee.get("full_name", ""),
                        employee.get("department", ""),
                        local.get("parking_space", "требует уточнения"),
                        local.get("car_number", "не указан"),
                        "требует согласования",
                    ],
                ],
            )
        )
    if documents.get("equipment_handover"):
        files.append(
            _write_text(
                folder / "equipment_handover.md",
                "# Передача оборудования\n\n"
                + "\n".join(f"- {row[0]} / инв. номер: {row[1]} / {row[2]}" for row in _equipment_rows(local))
                + "\n\nСтатус: требует ручного подтверждения передачи.\n",
            )
        )
    return files


def _write_instruction_docs(project_root: Path, folder: Path, data: dict[str, Any]) -> list[Path]:
    if not data["documents"].get("instructions"):
        return []
    selected = set(data["instructions"].get("selected", []))
    catalog = [item for item in instruction_catalog() if item["id"] in selected]
    mode = data["instructions"].get("mode", "linked")
    files = []
    files.append(
        _write_text(
            folder / "assigned_instructions.md",
            "# Назначенные инструкции\n\n"
            + "\n".join(f"- {item['title']} (`{item['id']}`)" for item in catalog)
            + "\n\nСтатус: назначено к ознакомлению, факт прохождения подтверждается отдельно.\n",
        )
    )
    files.append(_write_text(folder / "instruction_links.html", _links_html("Инструкции", catalog, "public_file")))
    files.append(_write_text(folder / "knowledge_check_links.html", _links_html("Проверки знаний", catalog, "check_file")))
    files.append(
        _write_text(
            folder / "knowledge_check_results.md",
            "# Результаты проверок знаний\n\nФайл заполняется после ручной проверки или выгрузки результатов.\n",
        )
    )
    if mode == "self-contained":
        instruction_target = folder / "instruction_sources"
        checks_target = folder / "knowledge_checks"
        instruction_target.mkdir(exist_ok=True)
        checks_target.mkdir(exist_ok=True)
        for item in catalog:
            for key, target_dir in (("public_file", instruction_target), ("check_file", checks_target)):
                source = project_root / item[key]
                if source.exists():
                    target = target_dir / source.name
                    shutil.copy2(source, target)
                    files.append(target)
    return files


def _links_html(title: str, catalog: list[dict[str, str]], file_key: str) -> str:
    items = "\n".join(
        f'<li><a href="../../../{escape(item[file_key])}">{escape(item["title"])}</a></li>'
        for item in catalog
    )
    return f"""<!doctype html>
<html lang="ru">
<head><meta charset="utf-8"><title>{escape(title)}</title></head>
<body>
  <h1>{escape(title)}</h1>
  <ul>{items}</ul>
</body>
</html>
"""


def _write_email_docs(folder: Path, data: dict[str, Any]) -> list[Path]:
    if not data["documents"].get("welcome_email"):
        return []
    employee = data["employee"]
    accounts = data["accounts"]
    instruction_mode = data["instructions"].get("mode", "linked")
    selected_instructions: list[dict[str, str]] = []
    if data["documents"].get("instructions"):
        selected = set(data["instructions"].get("selected", []))
        selected_instructions = [item for item in instruction_catalog() if item["id"] in selected]
    first_name, patronymic = _first_patronymic(employee.get("full_name", ""))
    subject_name = " ".join(part for part in [first_name, patronymic] if part) or employee.get("full_name", "")
    attachments = [
        "onboarding-план",
    ]
    eml_path = folder / "welcome_email.eml"
    plain, _html = write_welcome_email(
        eml_path,
        to_email=accounts.get("suggested_email", ""),
        from_email=accounts.get("sender_email", ""),
        subject=f"Добро пожаловать в команду, {subject_name}",
        employee_name=employee.get("full_name", ""),
        manager=employee.get("manager", ""),
        hr_contact=employee.get("hr_contact") or employee.get("responsible_contact", ""),
        buddy=employee.get("buddy", ""),
        start_date=employee.get("start_date", ""),
        department=employee.get("department", ""),
        attachments_hint=attachments,
        instruction_mode=instruction_mode,
        instruction_links=_email_instruction_links(instruction_mode, selected_instructions),
        check_links=_email_check_links(instruction_mode, selected_instructions),
        access_items=_email_access_items(data),
    )
    preview = _write_text(
        folder / "welcome_email_preview.md",
        f"# Предпросмотр welcome-письма\n\n```text\n{plain}\n```\n",
    )
    return [eml_path, preview]


def _email_access_items(data: dict[str, Any]) -> list[str]:
    if not data["documents"].get("resource_access"):
        return []
    access_requests = data.get("access_requests") or _default_access_requests()
    items = []
    for access in access_requests:
        name = str(access.get("name") or access.get("resource") or "").strip()
        access_type = str(access.get("type") or "").strip()
        if name and access_type:
            items.append(f"{name} ({access_type})")
        elif name:
            items.append(name)
        elif access_type:
            items.append(access_type)
    return items


def _email_instruction_links(mode: str, catalog: list[dict[str, str]]) -> list[dict[str, str]]:
    links = []
    for item in catalog:
        if mode == "self-contained":
            href = f"../04_instructions/instruction_sources/{Path(item['public_file']).name}"
        else:
            href = f"../../../{item['public_file']}"
        links.append({"title": item["title"], "href": href})
    return links


def _email_check_links(mode: str, catalog: list[dict[str, str]]) -> list[dict[str, str]]:
    links = []
    for item in catalog:
        if mode == "self-contained":
            href = f"../04_instructions/knowledge_checks/{Path(item['check_file']).name}"
        else:
            href = f"../../../{item['check_file']}"
        links.append({"title": item["title"], "href": href})
    return links


def _write_quality_check(path: Path, data: dict[str, Any]) -> Path:
    open_questions = data["open_questions"] or ["Открытых вопросов нет."]
    paragraphs = ["Открытые вопросы"]
    paragraphs.extend(f"- {item}" for item in open_questions)

    title = str(data.get("employee", {}).get("full_name") or "ФИО не указано").strip()
    write_docx(path, title, paragraphs)
    return path


def _default_access_requests() -> list[dict[str, str]]:
    return [
        {"name": "TEST-DOMAIN account", "type": "доменная учетная запись", "owner": "IT Service Desk"},
        {"name": "TEST-MAIL", "type": "корпоративная почта", "owner": "IT Service Desk"},
        {"name": "TEST-WIKI", "type": "база знаний", "owner": "PeopleOps"},
    ]


def _equipment_rows(local: dict[str, Any]) -> list[list[str]]:
    equipment = local.get("equipment") or []
    if not equipment:
        return [["Ноутбук тестовый", "TEST-ASSET-001", "требует оформления"]]
    rows = []
    for item in equipment:
        if isinstance(item, str):
            rows.append([item, "требует присвоения", "требует оформления"])
        else:
            rows.append(
                [
                    item.get("name", ""),
                    item.get("inventory_number", "требует присвоения"),
                    item.get("status", "требует оформления"),
                ]
            )
    return rows


def _first_patronymic(full_name: str) -> tuple[str, str]:
    _last, first, patronymic = split_full_name(full_name)
    return first, patronymic


def _docx(path: Path, title: str, paragraphs: list[str], tables: list[dict[str, object]] | None = None) -> Path:
    write_docx(path, title, paragraphs, tables)
    return path


def _xlsx(path: Path, sheet_name: str, rows: list[list[object]]) -> Path:
    write_xlsx(path, sheet_name, rows)
    return path


def _write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
