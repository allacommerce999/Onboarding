# Onboarding Agent

Onboarding Agent помогает HR, PeopleOps, руководителю команды или наставнику собрать onboarding-пакет для нового сотрудника рабочей группы корпоративных систем.

Контекст комплекта:

- 1С;
- Парус;
- Oracle;
- PostgreSQL;
- MySQL;
- Microsoft SQL Server;
- Cognos.

## Что генерирует агент

- onboarding-план до первого дня, на первый день, первую неделю и 30/60/90 дней;
- список доступов с владельцами, сроками и статусами;
- welcome-письмо новому сотруднику;
- пакет заявок на доступ к ИСР, базовым ресурсам, БД, серверам, Cognos и сервисным учетным записям;
- пакет первичных инструктажей и локальных процедур;
- открытые вопросы для HR, ОТ, ИБ, АХО и владельцев систем.

## Начать работу

Полный сценарий запуска и команда для чата находятся в:

- [`QUICKSTART.md`](QUICKSTART.md)

## Карта репозитория

| Файл или папка | Назначение |
|----------------|------------|
| `onboarding_agent_prompt.md` | основной prompt агента |
| `QUICKSTART.md` | полный быстрый старт и команда для чата |
| `templates/README.md` | навигация по шаблонам |
| `templates/core/employee_input_form.md` | форма входных данных |
| `templates/core/onboarding_package_template.md` | шаблон итогового onboarding-пакета |
| `templates/core/quality_checklist.md` | проверка полноты результата |
| `templates/access/workgroup_access_matrix.md` | матрица доступов рабочей группы |
| `templates/access/access_request_bundle_template.md` | шаблон пакета заявок |
| `templates/instructions/primary_instruction_matrix_template.md` | матрица инструктажей и локальных процедур |
| `templates/interactive/interactive_instruction_checklist.html` | интерактивный чек-лист процедур |
| `templates/knowledge-checks/knowledge_check_*.html` | HTML-проверки знаний после инструктажа |
| `templates/registers/instruction_register_template.xlsx` | книга учета инструктажей |
| `examples/` | примеры заполненных документов |
| `employees/` | onboarding-пакеты по конкретным ролям и сотрудникам |

## Prompt

Актуальная инструкция агента находится в:

- [`onboarding_agent_prompt.md`](onboarding_agent_prompt.md)

## Проверка результата

Для проверки готового пакета используйте:

- [`templates/core/quality_checklist.md`](templates/core/quality_checklist.md)
