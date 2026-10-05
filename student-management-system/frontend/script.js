const API_URL = "http://127.0.0.1:5000/api/students";

const form = document.getElementById("studentForm");
const tableBody = document.getElementById("studentTableBody");
const submitBtn = document.getElementById("submitBtn");
const cancelBtn = document.getElementById("cancelBtn");
const formTitle = document.getElementById("formTitle");
const searchInput = document.getElementById("searchInput");
const notification = document.getElementById("notification");

const FIELDS = ["name", "email", "phone", "age", "gender", "course", "address"];

let allStudents = [];   // used for the dashboard (always the full list)
let notificationTimer;
let searchTimer;

/* ---------- Helpers ---------- */
function showNotification(message, type = "success") {
  notification.textContent = message;
  notification.className = `notification ${type}`;
  clearTimeout(notificationTimer);
  notificationTimer = setTimeout(() => notification.classList.add("hidden"), 3500);
}

// Prevents HTML injection (XSS) when inserting text into the table
function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value ?? "";
  return div.innerHTML;
}

function setFieldError(field, message) {
  document.getElementById(`${field}Error`).textContent = message;
  document.getElementById(field).classList.toggle("invalid", Boolean(message));
}

function clearErrors() {
  FIELDS.forEach((field) => setFieldError(field, ""));
}

function getFormData() {
  return {
    name: document.getElementById("name").value.trim(),
    email: document.getElementById("email").value.trim(),
    phone: document.getElementById("phone").value.trim(),
    age: document.getElementById("age").value.trim(),
    gender: document.getElementById("gender").value,
    course: document.getElementById("course").value.trim(),
    address: document.getElementById("address").value.trim(),
  };
}

/* ---------- Frontend validation (mirrors the backend rules) ---------- */
function validateForm(data) {
  const errors = {};

  if (!data.name) errors.name = "Name is required";
  else if (data.name.length < 3) errors.name = "Name must be at least 3 characters";
  else if (!/^[A-Za-z][A-Za-z .'-]*$/.test(data.name)) errors.name = "Name can contain only letters and spaces";

  if (!data.email) errors.email = "Email is required";
  else if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(data.email)) errors.email = "Please enter a valid email";

  if (!data.phone) errors.phone = "Phone number is required";
  else if (!/^[6-9]\d{9}$/.test(data.phone)) errors.phone = "Phone number must contain 10 digits (starting with 6-9)";

  if (data.age === "") errors.age = "Age is required";
  else if (!/^\d+$/.test(data.age) || Number(data.age) < 16 || Number(data.age) > 100)
    errors.age = "Age must be between 16 and 100";

  if (!data.gender) errors.gender = "Gender is required";
  if (!data.course) errors.course = "Course is required";

  if (data.address && (data.address.length < 5 || data.address.length > 255))
    errors.address = "Address must be between 5 and 255 characters";

  return errors;
}

function showErrors(errors) {
  clearErrors();
  Object.entries(errors).forEach(([field, message]) => setFieldError(field, message));
}

/* ---------- API ---------- */
async function apiRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    const result = await response.json();
    return { ok: response.ok, status: response.status, ...result };
  } catch (err) {
    return { ok: false, success: false, message: "Cannot connect to the server. Is the backend running?" };
  }
}

/* ---------- Read ---------- */
async function loadStudents() {
  tableBody.innerHTML = `<tr class="loading-row"><td colspan="9">Loading...</td></tr>`;
  const result = await apiRequest(API_URL);
  if (!result.ok) {
    tableBody.innerHTML = `<tr class="empty-row"><td colspan="9">Failed to load students.</td></tr>`;
    showNotification(result.message, "error");
    return;
  }
  allStudents = result.data;
  renderTable(allStudents);
  updateDashboard(allStudents);
}

async function searchStudents(query) {
  if (!query.trim()) return loadStudents();
  const result = await apiRequest(`${API_URL}/search?q=${encodeURIComponent(query)}`);
  if (!result.ok) return showNotification(result.message, "error");
  renderTable(result.data); // dashboard stays based on all students
}

function renderTable(students) {
  if (students.length === 0) {
    tableBody.innerHTML = `<tr class="empty-row"><td colspan="9">No students found.</td></tr>`;
    return;
  }
  tableBody.innerHTML = students
    .map(
      (s) => `
    <tr>
      <td>${s.id}</td>
      <td>${escapeHtml(s.name)}</td>
      <td>${escapeHtml(s.email)}</td>
      <td>${escapeHtml(s.phone)}</td>
      <td>${s.age}</td>
      <td>${escapeHtml(s.gender)}</td>
      <td>${escapeHtml(s.course)}</td>
      <td>${escapeHtml(s.address) || "-"}</td>
      <td class="actions">
        <button class="btn btn-edit" onclick="editStudent(${s.id})">Edit</button>
        <button class="btn btn-delete" onclick="deleteStudent(${s.id})">Delete</button>
      </td>
    </tr>`
    )
    .join("");
}

function updateDashboard(students) {
  document.getElementById("statTotal").textContent = students.length;
  document.getElementById("statMale").textContent = students.filter((s) => s.gender === "Male").length;
  document.getElementById("statFemale").textContent = students.filter((s) => s.gender === "Female").length;
  const uniqueCourses = new Set(students.map((s) => s.course.trim().toLowerCase()));
  document.getElementById("statCourses").textContent = uniqueCourses.size;
}

/* ---------- Create & Update ---------- */
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = getFormData();
  const errors = validateForm(data);
  showErrors(errors);
  if (Object.keys(errors).length > 0) return;

  const studentId = document.getElementById("studentId").value;
  const isEditing = Boolean(studentId);

  submitBtn.disabled = true;
  submitBtn.textContent = isEditing ? "Updating..." : "Adding...";

  const result = await apiRequest(isEditing ? `${API_URL}/${studentId}` : API_URL, {
    method: isEditing ? "PUT" : "POST",
    body: JSON.stringify(data),
  });

  submitBtn.disabled = false;

  if (result.success) {
    showNotification(result.message, "success");
    resetForm();
    searchInput.value = "";
    loadStudents();
  } else {
    submitBtn.textContent = isEditing ? "Update Student" : "Add Student";
    if (result.errors) showErrors(result.errors); // show backend errors beside fields
    showNotification(result.message, "error");
  }
});

/* ---------- Edit ---------- */
async function editStudent(id) {
  const result = await apiRequest(`${API_URL}/${id}`);
  if (!result.success) return showNotification(result.message, "error");

  const s = result.data;
  document.getElementById("studentId").value = s.id;
  FIELDS.forEach((field) => (document.getElementById(field).value = s[field] ?? ""));

  clearErrors();
  formTitle.textContent = "Edit Student";
  submitBtn.textContent = "Update Student";
  cancelBtn.classList.remove("hidden");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetForm() {
  form.reset();
  document.getElementById("studentId").value = "";
  clearErrors();
  formTitle.textContent = "Add New Student";
  submitBtn.textContent = "Add Student";
  cancelBtn.classList.add("hidden");
}

cancelBtn.addEventListener("click", resetForm);

/* ---------- Delete ---------- */
async function deleteStudent(id) {
  if (!confirm("Are you sure you want to delete this student?")) return;

  const result = await apiRequest(`${API_URL}/${id}`, { method: "DELETE" });
  if (result.success) {
    showNotification(result.message, "success");
    if (document.getElementById("studentId").value === String(id)) resetForm();
    searchInput.value = "";
    loadStudents();
  } else {
    showNotification(result.message, "error");
  }
}

/* ---------- Search (debounced: waits 300ms after typing stops) ---------- */
searchInput.addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => searchStudents(searchInput.value), 300);
});

/* ---------- Init ---------- */
document.addEventListener("DOMContentLoaded", loadStudents);
