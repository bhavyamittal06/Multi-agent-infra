const form = document.getElementById("triage-form");
const submitBtn = document.getElementById("submit-btn");
const statusBox = document.getElementById("status");
const resultPanel = document.getElementById("result-panel");

const caseIdValue = document.getElementById("case-id-value");
const routingNote = document.getElementById("routing-note");
const recommendation = document.getElementById("recommendation");
const severityBadge = document.getElementById("severity-badge");
const patientAssessment = document.getElementById("patient-assessment");
const doctorConsult = document.getElementById("doctor-consult");
const auditLog = document.getElementById("audit-log");

function setStatus(message, isError = false) {
  statusBox.classList.remove("hidden");
  statusBox.textContent = message;
  statusBox.style.borderColor = isError ? "rgba(255, 98, 122, 0.7)" : "";
}

function clearStatus() {
  statusBox.classList.add("hidden");
  statusBox.textContent = "";
  statusBox.style.borderColor = "";
}

function setSeverityBadge(severity) {
  severityBadge.className = "badge";
  const s = (severity || "unknown").toLowerCase();
  severityBadge.textContent = s;
  if (s === "normal" || s === "borderline" || s === "critical") {
    severityBadge.classList.add(s);
  }
}

function renderJson(node, data) {
  if (!data) {
    node.textContent = "Not applicable for this case.";
    return;
  }
  node.textContent = JSON.stringify(data, null, 2);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearStatus();
  resultPanel.classList.add("hidden");

  const formData = new FormData(form);
  const payload = {
    case_id: formData.get("case_id")?.toString().trim() || null,
    symptoms: formData.get("symptoms")?.toString().trim() || "",
  };

  if (payload.symptoms.length < 10) {
    setStatus("Please enter more detailed symptoms (at least 10 characters).", true);
    return;
  }

  submitBtn.disabled = true;
  setStatus("Running patient and doctor agents...");

  try {
    const response = await fetch("/api/triage", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Request failed");
    }

    caseIdValue.textContent = data.case_id || "-";
    routingNote.textContent = data.routing_note || "-";
    recommendation.textContent = data.recommendation || "-";
    setSeverityBadge(data.severity);
    renderJson(patientAssessment, data.patient_assessment);
    renderJson(doctorConsult, data.doctor_consult);

    auditLog.innerHTML = "";
    (data.audit_log || []).forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      auditLog.appendChild(li);
    });

    resultPanel.classList.remove("hidden");
    setStatus("Agent collaboration completed successfully.");
  } catch (error) {
    const msg = error instanceof Error ? error.message : "Unknown error";
    setStatus(`Failed to run triage: ${msg}`, true);
  } finally {
    submitBtn.disabled = false;
  }
});
