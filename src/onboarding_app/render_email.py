from __future__ import annotations

from email.message import EmailMessage
from email.policy import SMTP
from html import escape
from pathlib import Path


def write_welcome_email(
    path: Path,
    *,
    to_email: str,
    from_email: str,
    subject: str,
    employee_name: str,
    manager: str,
    hr_contact: str,
    buddy: str,
    start_date: str,
    department: str,
    attachments_hint: list[str],
    instruction_mode: str = "linked",
    instruction_links: list[dict[str, str]] | None = None,
    check_links: list[dict[str, str]] | None = None,
    access_items: list[str] | None = None,
) -> tuple[str, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    plain = _plain_body(
        to_email=to_email,
        employee_name=employee_name,
        manager=manager,
        hr_contact=hr_contact,
        buddy=buddy,
        start_date=start_date,
        department=department,
        attachments_hint=attachments_hint,
        instruction_mode=instruction_mode,
        instruction_links=instruction_links or [],
        check_links=check_links or [],
        access_items=access_items or [],
    )
    html = _html_body(
        to_email=to_email,
        employee_name=employee_name,
        manager=manager,
        hr_contact=hr_contact,
        buddy=buddy,
        start_date=start_date,
        department=department,
        attachments_hint=attachments_hint,
        instruction_mode=instruction_mode,
        instruction_links=instruction_links or [],
        check_links=check_links or [],
        access_items=access_items or [],
    )

    message = EmailMessage(policy=SMTP)
    message["To"] = to_email
    message["From"] = from_email or "hr@test12systems.ru"
    message["Subject"] = subject
    message.set_content(plain)
    message.add_alternative(html, subtype="html")
    path.write_bytes(message.as_bytes())
    return plain, html


def _plain_body(
    *,
    to_email: str,
    employee_name: str,
    manager: str,
    hr_contact: str,
    buddy: str,
    start_date: str,
    department: str,
    attachments_hint: list[str],
    instruction_mode: str,
    instruction_links: list[dict[str, str]],
    check_links: list[dict[str, str]],
    access_items: list[str],
) -> str:
    attachments = "\n".join(f"- {item}" for item in attachments_hint)
    manager_value = manager or "уточнить"
    buddy_value = buddy or "не назначен"
    hr_value = hr_contact or "уточнить"
    instruction_section = _plain_link_section(
        "Инструкции приложены в onboarding-пакете:" if instruction_mode == "self-contained" else "Инструкции доступны по ссылкам:",
        instruction_links,
    )
    check_section = _plain_link_section("HTML-проверки знаний:", check_links)
    access_note = _plain_access_note(access_items)
    return f"""Предположительный e-mail нового сотрудника: {to_email}

Откройте письмо в корпоративном почтовом ящике, проверьте корректность заполненного адреса получателя командой "Проверить имя" и только после этого отправьте письмо.

Здравствуйте, {employee_name}!

Добро пожаловать в команду {department}. Дата выхода: {start_date}.

Контакты на период onboarding:
- Руководитель: {manager_value}
- HR / ответственный: {hr_value}
- Buddy: {buddy_value}

Перед первым рабочим днем, пожалуйста, ознакомьтесь с вводными материалами и инструкциями ниже.

Прилагаю документы для onboarding:
{attachments}

{instruction_section}

{check_section}

{access_note}
"""


def _html_body(
    *,
    to_email: str,
    employee_name: str,
    manager: str,
    hr_contact: str,
    buddy: str,
    start_date: str,
    department: str,
    attachments_hint: list[str],
    instruction_mode: str,
    instruction_links: list[dict[str, str]],
    check_links: list[dict[str, str]],
    access_items: list[str],
) -> str:
    list_items = "".join(f"<li>{escape(item)}</li>" for item in attachments_hint)
    manager_value = manager or "уточнить"
    buddy_value = buddy or "не назначен"
    hr_value = hr_contact or "уточнить"
    instruction_title = (
        "Инструкции приложены в onboarding-пакете:"
        if instruction_mode == "self-contained"
        else "Инструкции доступны по ссылкам:"
    )
    instruction_section = _html_link_section(instruction_title, instruction_links)
    check_section = _html_link_section("HTML-проверки знаний:", check_links)
    access_note = _html_access_note(access_items)
    return f"""<!doctype html>
<html lang="ru">
<head><meta charset="utf-8"><title>Welcome</title></head>
<body style="font-family:Arial,sans-serif;line-height:1.45;color:#1f2937">
  <div style="border:1px solid #d9e2ec;padding:12px;margin-bottom:18px;background:#f8fafc">
    <strong>Предположительный e-mail нового сотрудника:</strong> {escape(to_email)}<br>
    Откройте письмо в корпоративном почтовом ящике, проверьте корректность заполненного адреса получателя командой
    &quot;Проверить имя&quot; и только после этого отправьте письмо.
  </div>
  <p>Здравствуйте, {escape(employee_name)}!</p>
  <p>Добро пожаловать в команду {escape(department)}. Дата выхода: <strong>{escape(start_date)}</strong>.</p>
  <p><strong>Контакты на период onboarding:</strong></p>
  <ul>
    <li>Руководитель: {escape(manager_value)}</li>
    <li>HR / ответственный: {escape(hr_value)}</li>
    <li>Buddy: {escape(buddy_value)}</li>
  </ul>
  <p>Перед первым рабочим днем, пожалуйста, ознакомьтесь с вводными материалами и инструкциями ниже.</p>
  <p><strong>Прилагаю документы для onboarding:</strong></p>
  <ul>{list_items}</ul>
  {instruction_section}
  {check_section}
  {access_note}
</body>
</html>
"""


def _plain_link_section(title: str, links: list[dict[str, str]]) -> str:
    if not links:
        return ""
    lines = [title]
    lines.extend(f"- {item.get('title', '')}: {item.get('href', '')}" for item in links)
    return "\n".join(lines)


def _html_link_section(title: str, links: list[dict[str, str]]) -> str:
    if not links:
        return ""
    items = "".join(
        f'<li><a href="{escape(item.get("href", ""), quote=True)}">{escape(item.get("title", ""))}</a></li>'
        for item in links
    )
    return f"<p><strong>{escape(title)}</strong></p><ul>{items}</ul>"


def _plain_access_note(access_items: list[str]) -> str:
    if not access_items:
        return "Служебные записки на доступы оформляются отдельно. Если потребуется уточнение, с вами свяжутся администраторы."
    resources = ", ".join(access_items)
    return (
        "Служебные записки на доступы находятся на оформлении: "
        f"{resources}. Когда учетные записи и доступы будут готовы или потребуется уточнение, "
        "с вами свяжутся администраторы."
    )


def _html_access_note(access_items: list[str]) -> str:
    if not access_items:
        return (
            "<p>Служебные записки на доступы оформляются отдельно. "
            "Если потребуется уточнение, с вами свяжутся администраторы.</p>"
        )
    resources = ", ".join(escape(item) for item in access_items)
    return (
        "<p>Служебные записки на доступы находятся на оформлении: "
        f"{resources}. Когда учетные записи и доступы будут готовы или потребуется уточнение, "
        "с вами свяжутся администраторы.</p>"
    )
