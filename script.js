const form = document.getElementById("uploadForm");
const fileInput = document.getElementById("resumeFile");
const resultDiv = document.getElementById("result");
const scoreEl = document.getElementById("score");
const skillsEl = document.getElementById("skills");
const summaryEl = document.getElementById("summary");
const suggestionsEl = document.getElementById("suggestions");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = fileInput.files[0];
  if (!file) return alert("Please choose a PDF resume.");

  const fd = new FormData();
  fd.append("resume", file);

  try {
    const res = await fetch("/analyze", { method: "POST", body: fd });
    if (!res.ok) {
      const err = await res.json().catch(()=>({error:"server error"}));
      return alert("Server error: " + (err.error || JSON.stringify(err)));
    }
    const data = await res.json();
    resultDiv.classList.remove("hidden");
    scoreEl.textContent = data.score;
    skillsEl.textContent = data.skills.join(", ") || "None detected";
    summaryEl.textContent = data.summary;
    suggestionsEl.innerHTML = data.suggestions.map(s => `<li>${s}</li>`).join("");
  } catch (err) {
    alert("Network or server error: " + err.message);
  }
});