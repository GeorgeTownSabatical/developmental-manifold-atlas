async function loadJson(paths) {
  for (const path of paths) {
    const response = await fetch(path);
    if (response.ok) return response.json();
  }
  throw new Error(`Unable to load ${paths.join(" or ")}`);
}

function dashboardPaths(file) {
  const inDocsFolder = window.location.pathname.includes("/docs/");
  return inDocsFolder ? [`../dashboards/${file}`, `dashboards/${file}`] : [`dashboards/${file}`, `../dashboards/${file}`];
}

function metric(label, value) {
  return `<article class="metric"><span>${label}</span><strong>${value}</strong></article>`;
}

function listObject(obj) {
  const entries = Object.entries(obj || {});
  if (!entries.length) return "<p>No records yet.</p>";
  return `<ul class="data-list">${entries
    .map(([key, value]) => `<li><span>${key}</span><strong>${value}</strong></li>`)
    .join("")}</ul>`;
}

Promise.all([loadJson(dashboardPaths("summary.json")), loadJson(dashboardPaths("data_quality.json"))])
  .then(([summary, quality]) => {
    document.querySelector("#summary").innerHTML = [
      metric("Datasets", summary.dataset_count),
      metric("Hypotheses", summary.hypothesis_count),
      metric("Organisms", summary.organism_count),
      metric("Measurements", summary.measurement_record_count),
      metric("Quality A-C", Object.entries(summary.quality_grades || {}).reduce((sum, [grade, count]) => (["A", "B", "C"].includes(grade) ? sum + count : sum), 0)),
    ].join("");
    document.querySelector("#coverage").innerHTML = listObject(summary.species_counts);
    document.querySelector("#hypothesis-status").innerHTML = listObject(summary.evidence_grades || summary.hypothesis_status);
    document.querySelector("#quality-grades").innerHTML = listObject(quality.quality_grades || summary.quality_grades);
  })
  .catch((error) => {
    document.querySelector("#summary").innerHTML = `<article class="metric"><span>Dashboard</span><strong>Offline</strong></article>`;
    console.error(error);
  });
