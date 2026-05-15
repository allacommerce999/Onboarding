# Employee Input Form

Основная форма находится в локальном HTML-интерфейсе. Этот файл фиксирует поля для резервного сценария.

## Обязательные поля

- ФИО
- Должность
- Подразделение или команда
- Дата выхода
- Формат работы
- Минимум один тип документов

## Необязательные поля

- Buddy
- Руководитель
- HR или ответственный
- Город
- Телефон
- Известный e-mail
- Кабинет или зона
- Парковочная зона
- Оборудование
- Дополнительные ресурсы

## JSON

```json
{
  "employee": {
    "full_name": "Иванов Иван Иванович",
    "position": "Инженер сопровождения",
    "department": "Тестовая команда корпоративных систем",
    "start_date": "2026-05-25",
    "work_format": "офис",
    "manager": "Петров Петр Петрович",
    "hr_contact": "Сидорова Анна Сергеевна",
    "buddy": "Кузнецов Алексей Игоревич"
  },
  "accounts": {
    "known_email": "",
    "email_domain": "test12systems.ru"
  },
  "documents": {
    "resource_access": true,
    "inventory_inclusion": true,
    "building_pass": true,
    "room_key": false,
    "parking": false,
    "equipment_handover": true,
    "welcome_email": true,
    "instructions": true
  },
  "access_requests": [],
  "local_procedures": {},
  "instructions": {
    "mode": "linked",
    "selected": ["pvtr", "occupational_safety", "fire_safety", "first_aid", "information_security"]
  },
  "open_questions": []
}
```
