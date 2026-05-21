# Onboarding Agent

Local web app for preparing structured employee onboarding packages for HR, PeopleOps, managers, mentors, IT admins, facilities, and training owners.

Русское пояснение: это локальный генератор пакета адаптации нового сотрудника. Он помогает собрать документы, заявки, инструкции, проверки знаний и welcome-письмо для ручной проверки, но не выдает доступы, не создает реальные заявки и не заменяет согласования HR, IT, руководителя или ответственных служб.

## What It Does

Onboarding Agent reads employee details from the web form and creates a folder with:

- employee card and onboarding plan;
- access matrix, domain account register row, and access request memos;
- equipment handover, building pass, room key, parking, and inventory documents;
- assigned instruction links and optional self-contained instruction fragments;
- knowledge-check links or copied HTML checks;
- draft welcome email as `.eml`;
- quality-check document with open questions.

It does not send emails, create accounts, grant permissions, order equipment, issue passes or keys, confirm training completion, or replace HR/IT/legal review.

## Quick Start

```powershell
git clone https://github.com/allacommerce999/Onboarding.git
cd Onboarding
.\tools\start_onboarding_agent.ps1
```

The app opens at `http://127.0.0.1:8765/`. Fill in the required fields, choose document and instruction options, then generate the package.

Headless start:

```powershell
.\tools\start_onboarding_agent.ps1 -NoBrowser
```

## Input Form

Required fields are marked in the UI. At minimum, provide:

- full name;
- position;
- department or team;
- start date;
- work format;
- at least one document type.

Русская подсказка: спорные или неполные данные, например пустой руководитель, HR-контакт или ответственный за выдачу оборудования, попадут в `Проверка.docx` и `package_index.md` как открытые вопросы.

## Output Package

Generated packages are written to `employees/YYYY-MM-DD_login/` by default:

```text
employees/
└── YYYY-MM-DD_login/
    ├── 00_input/employee_input.json
    ├── 01_summary/
    ├── 02_access/
    ├── 03_local_procedures/
    ├── 04_instructions/
    ├── 05_email/
    └── Проверка.docx
```

Instruction mode `linked` keeps the package lightweight: it records assignments and links to canonical public instruction fragments. Mode `self-contained` copies selected instruction fragments and HTML knowledge checks into the employee folder.

Curated generated samples are kept in `employees/demo_*` folders and can be used as public examples.

## Project Map

| Path | Purpose |
|------|---------|
| `src/onboarding_app/` | local Python server and package generator |
| `src/onboarding_app/web/` | HTML/CSS/JS interface |
| `config/` | domain defaults, document catalog, and instruction catalog |
| `templates/documents/` | sanitized public `.docx` and `.xlsx` templates |
| `templates/knowledge-checks/` | HTML knowledge checks |
| `examples/instructions/` | public adapted instruction fragments |
| `employees/` | synthetic demo packages and local generated output |

## Customize Data

Edit the catalogs in `config/` and the public templates in `templates/` to match your demo scenario:

- `config/defaults.yml`
- `config/document_catalog.yml`
- `config/instruction_catalog.yml`
- `templates/documents/`
- `templates/knowledge-checks/`

Keep real employee exports, internal source documents, secrets, and production onboarding packages out of git.

## Safety Notes

- `.eml` files are drafts and are not sent automatically.
- Access requests are tasks for responsible admins; the app does not create accounts or grant permissions.
- Passes, keys, parking, equipment, and inventory changes require manual confirmation.
- Knowledge checks and instruction assignments require review by training, safety, HR, IT, or other responsible owners.
- Sensitive access should stay in status `требует согласования` until approved.
- Demo data and public examples must remain synthetic and sanitized.

Русское резюме по безопасности: публичная версия использует только тестовые ресурсы и очищенные демонстрационные фрагменты. Доступы, пропуска, ключи, оборудование и инструктажи не считаются выданными без ручного подтверждения ответственных служб.

## Smoke Check

Start the app and generate one of the demo packages from the UI. Then verify that the output folder contains `00_input`, `01_summary`, `02_access`, `03_local_procedures`, `04_instructions`, `05_email`, and `Проверка.docx`.

## License

MIT. See [LICENSE](LICENSE).
