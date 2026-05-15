const form = document.querySelector("#onboarding-form");
const generateButton = document.querySelector("#generate");
const errorsBox = document.querySelector("#form-errors");
const resultBox = document.querySelector("#result");
const statusBox = document.querySelector("#status");
const accessList = document.querySelector("#access-list");
const equipmentList = document.querySelector("#equipment-list");
const instructionList = document.querySelector("#instruction-list");

const instructionTitles = {
  pvtr: "ПВТР",
  occupational_safety: "Охрана труда",
  fire_safety: "Пожарная безопасность",
  first_aid: "Первая помощь",
  information_security: "Информационная безопасность",
  electrical_safety: "Электробезопасность и работы с электрооборудованием",
  height_work: "Работы на высоте"
};

function createAccessRow(seed = {}) {
  const row = document.createElement("div");
  row.className = "row";
  row.innerHTML = `
    <label>Ресурс<input data-field="name" value="${escapeAttr(seed.name || "")}" placeholder="TEST-WIKI"></label>
    <label>Тип<input data-field="type" value="${escapeAttr(seed.type || "")}" placeholder="база знаний"></label>
    <label>Владелец<input data-field="owner" value="${escapeAttr(seed.owner || "")}" placeholder="IT Service Desk"></label>
    <label>Статус
      <select data-field="sensitivity">
        <option value="normal">Обычный</option>
        <option value="sensitive">Согласование</option>
        <option value="server">Сервер</option>
        <option value="database">БД</option>
      </select>
    </label>
    <button class="icon-button" type="button" title="Удалить строку">x</button>
  `;
  row.querySelector("[data-field='sensitivity']").value = seed.sensitivity || "normal";
  row.querySelector("button").addEventListener("click", () => {
    row.remove();
    validateForm();
  });
  accessList.append(row);
}

function createEquipmentRow(seed = {}) {
  const row = document.createElement("div");
  row.className = "row equipment-row";
  row.innerHTML = `
    <label>Наименование<input data-field="name" value="${escapeAttr(seed.name || "")}" placeholder="Ноутбук тестовый"></label>
    <label>Инв. номер<input data-field="inventory_number" value="${escapeAttr(seed.inventory_number || "")}" placeholder="TEST-ASSET-001"></label>
    <button class="icon-button" type="button" title="Удалить строку">x</button>
  `;
  row.querySelector("button").addEventListener("click", () => {
    row.remove();
    validateForm();
  });
  equipmentList.append(row);
}

function renderInstructions(items) {
  instructionList.innerHTML = "";
  const catalog = items.length ? items : Object.entries(instructionTitles).map(([id, title]) => ({ id, title }));
  catalog.forEach((item) => {
    const label = document.createElement("label");
    const defaultChecked = item.default !== "false";
    label.dataset.instruction = item.id;
    if (item.field_work === "true") label.dataset.fieldWork = "true";
    label.innerHTML = `<input type="checkbox" name="instruction" value="${escapeAttr(item.id)}" ${defaultChecked ? "checked" : ""}> ${escapeHtml(item.title)}`;
    instructionList.append(label);
  });
  syncFieldWorkInstructions();
}

function syncDependents() {
  document.querySelectorAll("[data-dependent]").forEach((node) => {
    const checkbox = form.elements[node.dataset.dependent];
    node.classList.toggle("is-hidden", checkbox && !checkbox.checked);
  });
  syncFieldWorkInstructions();
}

function syncFieldWorkInstructions() {
  if (!form.elements.work_format || !instructionList.children.length) return;
  const isFieldWork = form.elements.work_format.value.includes("выезд");
  instructionList.querySelectorAll("[data-field-work='true']").forEach((label) => {
    label.classList.toggle("field-work-suggested", isFieldWork);
    const checkbox = label.querySelector("input");
    if (isFieldWork && checkbox) checkbox.checked = true;
  });
}

function selectedDocuments() {
  return {
    resource_access: form.elements.doc_resource_access.checked,
    inventory_inclusion: form.elements.doc_inventory_inclusion.checked,
    building_pass: form.elements.doc_building_pass.checked,
    room_key: form.elements.doc_room_key.checked,
    parking: form.elements.doc_parking.checked,
    equipment_handover: form.elements.doc_equipment_handover.checked,
    welcome_email: form.elements.doc_welcome_email.checked,
    instructions: form.elements.doc_instructions.checked
  };
}

function collectRows(root) {
  return Array.from(root.querySelectorAll(".row"))
    .map((row) => {
      const item = {};
      row.querySelectorAll("[data-field]").forEach((field) => {
        item[field.dataset.field] = field.value.trim();
      });
      return item;
    })
    .filter((item) => Object.values(item).some(Boolean));
}

function collectPayload() {
  const selectedInstructions = Array.from(form.querySelectorAll("input[name='instruction']:checked")).map((item) => item.value);
  return {
    employee: {
      full_name: form.elements.full_name.value.trim(),
      position: form.elements.position.value.trim(),
      department: form.elements.department.value.trim(),
      start_date: form.elements.start_date.value,
      work_format: form.elements.work_format.value,
      manager: form.elements.manager.value.trim(),
      hr_contact: form.elements.hr_contact.value.trim(),
      buddy: form.elements.buddy.value.trim(),
      city: form.elements.city.value.trim(),
      phone: form.elements.phone.value.trim()
    },
    accounts: {
      known_email: form.elements.known_email.value.trim(),
      email_domain: form.elements.email_domain.value.trim(),
      sender_email: form.elements.sender_email.value.trim()
    },
    documents: selectedDocuments(),
    access_requests: collectRows(accessList),
    local_procedures: {
      office_address: form.elements.office_address.value.trim(),
      room: form.elements.room.value.trim(),
      parking_space: form.elements.parking_space.value.trim(),
      car_number: form.elements.car_number.value.trim(),
      equipment: collectRows(equipmentList)
    },
    instructions: {
      mode: form.elements.instruction_mode.value,
      selected: selectedInstructions
    },
    generation: {
      package_mode: form.elements.package_mode.value
    },
    open_questions: []
  };
}

function validateForm() {
  syncDependents();
  const requiredMissing = Array.from(form.querySelectorAll("[required]")).filter((field) => !field.value.trim());
  const docs = selectedDocuments();
  const noDocuments = !Object.values(docs).some(Boolean);
  const messages = [];
  if (requiredMissing.length) messages.push("Заполните обязательные поля.");
  if (noDocuments) messages.push("Выберите хотя бы один тип документов.");
  generateButton.disabled = Boolean(messages.length);
  errorsBox.textContent = messages.join(" ");
}

async function submitForm(event) {
  event.preventDefault();
  validateForm();
  if (generateButton.disabled) return;
  statusBox.textContent = "Генерация";
  statusBox.className = "status status-muted";
  resultBox.hidden = true;
  generateButton.disabled = true;
  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(collectPayload())
    });
    const result = await response.json();
    if (!response.ok || !result.ok) {
      throw new Error((result.errors || ["Ошибка генерации"]).join(" "));
    }
    renderResult(result);
    statusBox.textContent = "Готово";
    statusBox.className = "status status-ok";
  } catch (error) {
    errorsBox.textContent = error.message;
    statusBox.textContent = "Ошибка";
    statusBox.className = "status status-error";
  } finally {
    validateForm();
  }
}

function renderResult(result) {
  const files = result.created_files.map((file) => `<li><code>${escapeHtml(file)}</code></li>`).join("");
  const questions = result.open_questions.length
    ? result.open_questions.map((item) => `<li>${escapeHtml(item)}</li>`).join("")
    : "<li>Нет открытых вопросов</li>";
  resultBox.innerHTML = `
    <h2>Пакет создан</h2>
    <p><code>${escapeHtml(result.relative_package_dir)}</code></p>
    <h3>Файлы</h3>
    <ul>${files}</ul>
    <h3>Открытые вопросы</h3>
    <ul>${questions}</ul>
  `;
  resultBox.hidden = false;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function escapeAttr(value) {
  return escapeHtml(value).replaceAll("'", "&#39;");
}

async function init() {
  try {
    const response = await fetch("/api/defaults");
    const data = await response.json();
    if (data.defaults) {
      form.elements.email_domain.value = data.defaults.email_domain || form.elements.email_domain.value;
      form.elements.sender_email.value = data.defaults.sender_email || form.elements.sender_email.value;
      form.elements.instruction_mode.value = data.defaults.default_instruction_mode || "linked";
    }
    renderInstructions(data.instructions || []);
  } catch {
    renderInstructions([]);
  }
  createAccessRow({ name: "TEST-DOMAIN account", type: "доменная учетная запись", owner: "IT Service Desk" });
  createAccessRow({ name: "TEST-MAIL", type: "корпоративная почта", owner: "IT Service Desk" });
  createEquipmentRow({ name: "Ноутбук тестовый", inventory_number: "TEST-ASSET-001" });
  validateForm();
}

document.querySelector("#add-access").addEventListener("click", () => createAccessRow());
document.querySelector("#add-equipment").addEventListener("click", () => createEquipmentRow());
form.addEventListener("input", validateForm);
form.addEventListener("change", validateForm);
form.addEventListener("submit", submitForm);
init();
