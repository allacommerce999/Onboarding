# Synthetic onboarding examples

Эта папка содержит синтетические документы для разработки onboarding-агента.

Все ФИО, организации, ресурсы, учетные записи, IP-адреса, владельцы и номера согласований искусственные. Примеры сохраняют только принципы структуры:

- заявка содержит адресата, отправителя, дату, основание, сотрудника, ресурсы, роли доступа и согласование;
- учетная запись пользователя строится как `surname + initials`;
- сервисная учетная запись строится как `svc_ + system + purpose`;
- серверные ресурсы именуются по принципу `тип-система-номер`;
- чувствительные доступы требуют отдельного согласования;
- пароли, токены и ключи не указываются.

## Структура

| Папка | Состав |
|-------|--------|
| `access/` | заявки на доступ, сопроводительное письмо, реестр доменных учетных записей |
| `onboarding-packages/` | полные synthetic onboarding-пакеты |
| `instruction-packages/` | пакеты первичных инструктажей для офисной и выездной роли |
| `instructions/` | краткие synthetic-примеры инструкций по ПВТР, ОТ, ПБ, первой помощи, ЛВС/ИБ и выездным работам |
| `local-procedures/` | парковка, ключи, пропуск, имущество |
| `demos/` | сценарии проверки интерактивных HTML-артефактов |

## Ключевые файлы

| Файл | Назначение |
|------|------------|
| `access/synthetic_access_request_ad_domain.md` | Пример заявки на домен, почту, мессенджер и базовые сетевые ресурсы |
| `access/synthetic_access_request_bundle_enterprise_systems.md` | Пример пакета заявок для рабочей группы 1С, Парус, БД и Cognos |
| `onboarding-packages/synthetic_onboarding_package_enterprise_systems.md` | Пример полного onboarding-пакета для инженера корпоративных систем |
| `instruction-packages/synthetic_primary_instruction_package_office_employee.md` | Пример пакета инструктажей для офисного ИТ-сотрудника |
| `instruction-packages/synthetic_primary_instruction_package_field_grid_worker.md` | Пример пакета инструктажей для выездной роли |
| `instructions/synthetic_instruction_pvtr.md` | Пример краткой инструкции по ПВТР |
| `instructions/synthetic_instruction_occupational_safety.md` | Пример краткой инструкции по охране труда |
| `instructions/synthetic_instruction_fire_safety.md` | Пример краткой инструкции по пожарной безопасности |
| `instructions/synthetic_instruction_first_aid.md` | Пример краткой инструкции по первой помощи |
| `instructions/synthetic_instruction_local_network_security.md` | Пример краткой инструкции по ЛВС и ИБ |
| `instructions/synthetic_instruction_field_safety.md` | Пример краткой инструкции для выездных работ |
| `local-procedures/synthetic_parking_access_list.md` | Пример обезличенного списка парковки |
| `local-procedures/synthetic_room_key_access_list.md` | Пример обезличенного списка доступа к ключам |
| `local-procedures/synthetic_building_pass_request.md` | Пример заявки на электронный пропуск |
| `local-procedures/synthetic_material_assets_inventory_entry.md` | Пример записи передачи имущества |
| `demos/synthetic_interactive_instruction_checklist_demo.md` | Сценарии проверки интерактивного чек-листа |

Персональные synthetic drafts по тестовым сотрудникам лежат в `../employees/`.

## Как использовать

1. Использовать файлы из `../templates/` как базовую форму.
2. Использовать файлы из тематических подпапок `examples/` как few-shot примеры для агента.
3. Не переносить реальные персональные данные, внутренние документы и маршруты доступа в генерируемые результаты.
4. Не добавлять названия закрытых ресурсов, реальные контакты и секреты.
5. Все неизвестные значения помечать как `требует уточнения`.
6. Профильные допуски помечать как `требует профильной проверки`.
