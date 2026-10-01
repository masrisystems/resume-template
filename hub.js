/**
 * Career Hub Interactive Client Logic
 * Handles 1-click clipboard copy, persona switching, ATS mode, action briefs, cover letters, and engine commands.
 * Zero external framework dependencies. Zero emojis.
 */

// Toast notification helper
function showToast(message) {
  let toast = document.getElementById('hub-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'hub-toast';
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 2500);
}

// 1-Click Clipboard Copy for Prompts
function copyPrompt(btn) {
  const card = btn.closest('.prompt-card');
  if (!card) return;
  
  const rawElement = card.querySelector('.prompt-raw');
  const textToCopy = rawElement ? rawElement.textContent.trim() : '';
  
  if (!textToCopy) return;

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(textToCopy).then(() => {
      const originalText = btn.innerHTML;
      btn.textContent = 'Copied!';
      showToast('Prompt copied to clipboard!');
      setTimeout(() => {
        btn.innerHTML = originalText;
        if (window.lucide) lucide.createIcons();
      }, 2000);
    }).catch(err => {
      console.error('Failed to copy text: ', err);
      showToast('Press Ctrl+C to copy');
    });
  } else {
    const textArea = document.createElement('textarea');
    textArea.value = textToCopy;
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
      showToast('Prompt copied to clipboard!');
    } catch (err) {
      showToast('Failed to copy');
    }
    document.body.removeChild(textArea);
  }
}

// 1-Click Clipboard Copy for CLI Engine Commands
function copyEngineCommand(btn) {
  const card = btn.closest('.engine-command-card');
  if (!card) return;

  const codeEl = card.querySelector('.engine-command-code');
  const textToCopy = codeEl ? codeEl.textContent.trim() : '';
  if (!textToCopy) return;

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(textToCopy).then(() => {
      const originalText = btn.innerHTML;
      btn.textContent = 'Copied!';
      showToast('Command copied to clipboard!');
      setTimeout(() => {
        btn.innerHTML = originalText;
      }, 2000);
    }).catch(err => {
      showToast('Press Ctrl+C to copy');
    });
  } else {
    const textArea = document.createElement('textarea');
    textArea.value = textToCopy;
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
      showToast('Command copied to clipboard!');
    } catch (err) {
      showToast('Failed to copy');
    }
    document.body.removeChild(textArea);
  }
}

// Pre-defined Archetype Data for Resume Preview
const ARCHETYPES = {
  engineering: {
    name: "Stefan Kramer",
    title_en: "Senior Systems & Mechanical Engineer (M.Sc.)",
    title_de: "Senior Entwicklungsingenieur Maschinenbau (M.Sc.)",
    file: "./resume.html",
    avatar: "./assets/profiles/stefan-kramer-profile.webp"
  },
  fullstack: {
    name: "Alex Morgan",
    title_en: "Senior Fullstack Engineer & AI Solutions Architect",
    title_de: "Senior Fullstack Entwickler & KI Lösungsarchitekt",
    file: "./jobs/roles/html/fullstack_laravel.html",
    avatar: "./assets/profiles/alex-morgan-profile.webp"
  },
  devops: {
    name: "Elena Becker",
    title_en: "Lead Cloud DevOps & Platform Architect",
    title_de: "Lead Cloud DevOps & Plattform Architektin",
    file: "./jobs/roles/html/ai_product_engineer.html",
    avatar: "./assets/profiles/alex-morgan-profile.webp"
  },
  designer: {
    name: "Julian Richter",
    title_en: "Staff Product Designer & Design Systems Lead",
    title_de: "Staff Product Designer & Design Systems Lead",
    file: "./jobs/roles/html/frontend_ui_architect.html",
    avatar: "./assets/profiles/alex-morgan-profile.webp"
  },
  finance: {
    name: "Clara Lindemann",
    title_en: "Senior Financial Controller & FP&A Lead",
    title_de: "Senior Financial Controllerin & FP&A Spezialistin",
    file: "./resume.html",
    avatar: "./assets/profiles/alex-morgan-profile.webp"
  }
};

// Persona Switcher for Live Resume
function switchPersona(personaKey) {
  const data = ARCHETYPES[personaKey];
  if (!data) return;

  const frame = document.getElementById('resumeFrame');
  const standaloneLink = document.getElementById('resume-standalone-link');

  if (frame && data.file) {
    frame.src = data.file;
  }
  if (standaloneLink && data.file) {
    standaloneLink.href = data.file;
  }

  // Update pill active states
  document.querySelectorAll('.persona-pills .btn-pill-sm').forEach(pill => {
    if (pill.dataset.persona === personaKey) {
      pill.classList.add('active');
    } else {
      pill.classList.remove('active');
    }
  });

  showToast(`Switched preview to ${data.name} (${personaKey})`);
}

// Print Resume Frame
function printResumeFrame() {
  const frame = document.getElementById('resumeFrame');
  if (frame && frame.contentWindow) {
    try {
      frame.contentWindow.focus();
      frame.contentWindow.print();
      return;
    } catch (e) {
      console.warn('Frame print cross-origin or restricted, falling back to open', e);
    }
  }
  window.open('./resume.html', '_blank');
}

// ATS Plain Text Mode Toggle
function toggleAtsMode() {
  const frame = document.getElementById('resumeFrame');
  const paper = document.getElementById('resume-paper');
  let isAts = false;

  if (frame && frame.contentDocument) {
    try {
      const doc = frame.contentDocument;
      const target = doc.getElementById('resumeContent') || doc.body;
      target.classList.toggle('ats-plain-mode');
      isAts = target.classList.contains('ats-plain-mode');
    } catch (e) {
      console.warn('Cannot access frame document', e);
    }
  }

  if (paper) {
    paper.classList.toggle('ats-plain-mode');
    if (!isAts) isAts = paper.classList.contains('ats-plain-mode');
  }

  showToast(isAts ? 'ATS plain-text preview active' : 'Standard visual layout active');
}

// Action Brief Data Across Multiple Domains
const BRIEFS = {
  fullstack: {
    title: "Morning Action Brief · 2026-09-26 (Production Run)",
    target: "Daily Job Discovery & Application Preparation (Target: 2 qualifying roles scoring >= 9.0/10)",
    result: "2 complete, fully verified application packages generated, validated, and exported to print-ready HTML and high-fidelity PDF.",
    pkg1: {
      company: "energy & meteo systems GmbH (Priority 1 · Oldenburg Local)",
      role: "Fullstack Softwareentwickler / Software Engineer (w/m/d)",
      location: "Oskar-Homt-Str. 1, 26131 Oldenburg · Priority 1 Local Commute (~2,5 km, 5-7 min)",
      score: "9.8 / 10",
      justification: "Hervorragender lokaler Oldenburger Match für Python, TypeScript, Java (B.Sc. Informatik Äquivalenz), REST APIs, relationales Datenbankdesign (PostgreSQL/MySQL), Redis & RabbitMQ Message Queues und Docker Containerisierung im Bereich SaaS für erneuerbare Energien.",
      keywords: "Python, TypeScript, Java, REST APIs, PostgreSQL",
      gap: "Große verteilte Kafka-Cluster im Produktiveinsatz (durch RabbitMQ, Redis Queues und asynchrone Ereignisverarbeitung nahtlos überbrückt).",
      salary: "46.500 € – 74.000 € (kununu Ø 59.900 € brutto/Jahr für Softwareentwickler). Zielvergütung: 52.500 € brutto/Jahr.",
      apply: "jobs@energymeteo.de · Ansprechpartnerin: Frau Alexandra Jobst",
      assets: ["energy_meteo_systems.html", "energy_meteo_systems.pdf", "2026-09-26_energy_meteo_systems.html", "2026-09-26_energy_meteo_systems.pdf", "energy_meteo_systems.txt"],
      qa: "222 Wörter (DIN-5008 < 300) · 0 Gedankenstriche · 0 Semikolons · Burstiness-Spannweite = 28 Wörter · 0 8-Wort Überlappung · Invariante 52.500 € brutto/Jahr · 3 Monate Kündigungsfrist"
    },
    pkg2: {
      company: "LEONEX Internet GmbH (Priority 2 · 100% Remote Deutschland)",
      role: "Shopware Developer (all genders) · LEONEX Internet GmbH (MAI Group)",
      location: "Technologiepark 6, 33100 Paderborn / 100% Remote Deutschland (Mobiles Arbeiten deutschlandweit)",
      score: "9.9 / 10",
      justification: "Direkter Treffer für individuelle Shopware 6 Plugin-Entwicklung (DAL, Flow Builder, CLI), PHP 8+, Symfony, Vue 3, Twig Storefronts, ERP- und PIM-Anbindungen (Pimcore) sowie asynchrone Redis Job Queues.",
      keywords: "Shopware 6, PHP 8+, Symfony, MySQL, Vue.js",
      gap: "Spezifische Shopware 4 Legacy-Migrationsskripte (durch fundiertes Verständnis der Shopware 6 DAL sofort adaptierbar).",
      salary: "55.000 € – 68.000 € (Markt- und Agentur-Benchmark für Shopware 6 & PHP Entwickler). Zielvergütung: 52.500 € brutto/Jahr.",
      apply: "Portal Apply & jobs@leonex.de · Ansprechpartner: Recruiting Team LEONEX",
      assets: ["leonex.html", "leonex.pdf", "2026-09-26_leonex.html", "2026-09-26_leonex.pdf", "leonex.txt"],
      qa: "242 Wörter (DIN-5008 < 300) · 0 Gedankenstriche · 0 Semikolons · Burstiness-Spannweite = 31 Wörter · 0 8-Wort Überlappung · Invariante 52.500 € brutto/Jahr · 3 Monate Kündigungsfrist"
    },
    checklist: {
      availability: "3 Monate zum Monatsende (im Einvernehmen gern auch kurzfristiger durch Aufhebungsvereinbarung). Frühester regulärer Starttermin: 01.01.2027.",
      salary: "52.500 € brutto / Jahr (52.500 Euro)",
      uploads: "Anschreiben-PDF + Lebenslauf-PDF + ZAB Zeugnisbewertung (B.Sc. Informatik Gleichwertigkeit)"
    },
    maintenance: "No master-resume change recommended today. Netto-Änderung Sektionen: 0 · Netto-Änderung Bullets: 0 · Wortanzahl-Delta: 0. Master index.html bleibt unberührt und geschützt."
  },
  devops: {
    title: "Morning Action Brief · 2026-09-28 (Cloud DevOps Archetype)",
    target: "Daily Job Discovery & Application Preparation (Target: 2 qualifying roles scoring >= 9.0/10)",
    result: "2 complete, fully verified application packages generated, validated, and exported to print-ready HTML and high-fidelity PDF.",
    pkg1: {
      company: "Scalable Capital GmbH (Priority 1 · München Hybrid)",
      role: "Senior Cloud Platform & Infrastructure Engineer (m/w/d)",
      location: "Seitzstraße 8e, 80538 München / Hybrid (2 Tage Office)",
      score: "9.7 / 10",
      justification: "Präziser Match für Multi-Region Kubernetes Cluster (EKS), Terraform IaC, AWS Cloud Architekturen, Prometheus & Grafana Observability und Zero-Trust Microsegmentation.",
      keywords: "Kubernetes, Terraform, AWS, Prometheus, Docker",
      gap: "Spezifische Erfahrung mit AWS EKS Pod Identity Associations (durch IAM OIDC Rollenwissen trivial adaptierbar).",
      salary: "72.000 € – 88.000 € (kununu Benchmark für Platform Engineers bei FinTech Scale-ups). Zielvergütung: 68.000 € brutto/Jahr.",
      apply: "careers@scalable.capital · Talent Acquisition Team",
      assets: ["scalable_capital.html", "scalable_capital.pdf", "2026-09-28_scalable_capital.html", "2026-09-28_scalable_capital.pdf", "scalable_capital.txt"],
      qa: "235 Wörter (DIN-5008 < 300) · 0 Gedankenstriche · 0 Semikolons · Burstiness-Spannweite = 26 Wörter · 0 8-Wort Überlappung · Invariante 68.000 € brutto/Jahr · 3 Monate Kündigungsfrist"
    },
    pkg2: {
      company: "Personio SE & Co. KG (Priority 2 · 100% Remote Deutschland)",
      role: "Site Reliability Engineer / SRE (all genders)",
      location: "Rundfunkplatz 4, 80335 München / 100% Remote Deutschland",
      score: "9.8 / 10",
      justification: "Exzellente Übereinstimmung für GitOps (ArgoCD), automated Canary Rollouts, Datadog Distributed Tracing, Golang/Python Automation und SLO/Error-Budget Monitoring.",
      keywords: "ArgoCD, GitOps, Datadog, Golang, CI/CD Pipelines",
      gap: "Multi-Account AWS Control Tower Enterprise Landing Zones.",
      salary: "75.000 € – 92.000 € (kununu Personio SRE Benchmark). Zielvergütung: 68.000 € brutto/Jahr.",
      apply: "Personio Careers Portal · Engineering Recruiting Team",
      assets: ["personio.html", "personio.pdf", "2026-09-28_personio.html", "2026-09-28_personio.pdf", "personio.txt"],
      qa: "248 Wörter (DIN-5008 < 300) · 0 Gedankenstriche · 0 Semikolons · Burstiness-Spannweite = 29 Wörter · 0 8-Wort Überlappung · Invariante 68.000 € brutto/Jahr · 3 Monate Kündigungsfrist"
    },
    checklist: {
      availability: "3 Monate zum Monatsende (im Einvernehmen gern auch kurzfristiger).",
      salary: "68.000 € brutto / Jahr (68.000 Euro)",
      uploads: "Anschreiben-PDF + Lebenslauf-PDF + CKA/AWS Zertifikate"
    },
    maintenance: "No master-resume change recommended today. 0 Section Delta, 0 Bullet Growth. Master index.html remains strictly preserved."
  },
  designer: {
    title: "Morning Action Brief · 2026-09-29 (Product Design Archetype)",
    target: "Daily Job Discovery & Application Preparation (Target: 2 qualifying roles scoring >= 9.0/10)",
    result: "2 complete, fully verified application packages generated, validated, and exported to print-ready HTML and high-fidelity PDF.",
    pkg1: {
      company: "Jimdo GmbH (Priority 1 · Hamburg / Hybrid)",
      role: "Senior UI/UX & Design Systems Designer (f/m/d)",
      location: "Stresemannstraße 375, 22761 Hamburg / Hybrid (Flex-Office)",
      score: "9.9 / 10",
      justification: "Perfekte Kongruenz für Multi-Brand Figma Design Systems, Design Tokens (Style Dictionary), Barrierefreiheit (WCAG 2.1 AA), interaktive Prototypen und quantitative Nutzerforschung.",
      keywords: "Figma Design, Design Tokens, User Testing, WCAG AA, Prototyping",
      gap: "Framer Motion Code-Export (durch fundierte CSS3 Grid/Flexbox Kenntnisse und Storybook Erfahrung unmittelbar überbrückt).",
      salary: "60.000 € – 75.000 € (kununu Jimdo Design Benchmark). Zielvergütung: 62.000 € brutto/Jahr.",
      apply: "jobs@jimdo.com · Design Operations Team",
      assets: ["jimdo.html", "jimdo.pdf", "2026-09-29_jimdo.html", "2026-09-29_jimdo.pdf", "jimdo.txt"],
      qa: "218 Wörter (DIN-5008 < 300) · 0 Gedankenstriche · 0 Semikolons · Burstiness-Spannweite = 25 Wörter · 0 8-Wort Überlappung · Invariante 62.000 € brutto/Jahr · 3 Monate Kündigungsfrist"
    },
    pkg2: {
      company: "Celonis SE (Priority 2 · 100% Remote Deutschland)",
      role: "Senior Product Experience Designer (all genders)",
      location: "Theresienstraße 6, 80333 München / 100% Remote Deutschland",
      score: "9.6 / 10",
      justification: "Starke Übereinstimmung für komplexe B2B SaaS Enterprise Dashboards, Datenvisualisierung, Micro-Interactions und Usability Testing in agilen Scrum Squads.",
      keywords: "Figma, B2B SaaS, User Journey Mapping, Data Visualization, Design Sprint",
      gap: "Spezielles Process Mining Visualisierungs-Framework.",
      salary: "65.000 € – 80.000 € (kununu Celonis Product Design). Zielvergütung: 62.000 € brutto/Jahr.",
      apply: "Celonis Careers Portal · People Team",
      assets: ["celonis.html", "celonis.pdf", "2026-09-29_celonis.html", "2026-09-29_celonis.pdf", "celonis.txt"],
      qa: "230 Wörter (DIN-5008 < 300) · 0 Gedankenstriche · 0 Semikolons · Burstiness-Spannweite = 27 Wörter · 0 8-Wort Überlappung · Invariante 62.000 € brutto/Jahr · 3 Monate Kündigungsfrist"
    },
    checklist: {
      availability: "3 Monate zum Monatsende (im Einvernehmen gern auch kurzfristiger).",
      salary: "62.000 € brutto / Jahr (62.000 Euro)",
      uploads: "Anschreiben-PDF + Lebenslauf-PDF + Case Study Portfolio Link"
    },
    maintenance: "No master-resume change recommended today. Zero bloat budget verified."
  },
  engineering: {
    title: "Morning Action Brief · 2026-09-30 (Renewable Energy Systems Archetype)",
    target: "Daily Job Discovery & Application Preparation (Target: 2 qualifying roles scoring >= 9.0/10)",
    result: "2 complete, fully verified application packages generated, validated, and exported to print-ready HTML and high-fidelity PDF.",
    pkg1: {
      company: "EnBW Energie Baden-Württemberg AG (Priority 1 · Stuttgart)",
      role: "Senior Entwicklungsingenieur Großbatteriespeicher / BESS (w/m/d)",
      location: "Durlacher Allee 93, 76131 Karlsruhe / Stuttgart Region",
      score: "9.8 / 10",
      justification: "Hervorragender Match für Batteriespeichersysteme (BESS), thermische Simulation (CFD / Ansys Fluent), CAD Konstruktion (SolidWorks / Inventor) und Netzanschlussrichtlinien (VDE-AR-N 4110/4120).",
      keywords: "BESS, SolidWorks, CFD Simulation, Thermisches Management, VDE",
      gap: "Spezifische Container-Level Brandschutz-Zulassung nach UL 9540A (theoretisch fundiert, Zulassungsbegleitung in Vorprojekt nachgewiesen).",
      salary: "68.000 € – 84.000 € (Tarifvertrag Versorgungsbetriebe TV-V / kununu EnBW). Zielvergütung: 72.000 € brutto/Jahr.",
      apply: "karriere@enbw.com · Recruiting Center Stuttgart",
      assets: ["enbw.html", "enbw.pdf", "2026-09-30_enbw.html", "2026-09-30_enbw.pdf", "enbw.txt"],
      qa: "238 Wörter (DIN-5008 < 300) · 0 Gedankenstriche · 0 Semikolons · Burstiness-Spannweite = 29 Wörter · 0 8-Wort Überlappung · Invariante 72.000 € brutto/Jahr · 3 Monate Kündigungsfrist"
    },
    pkg2: {
      company: "Siemens Energy Global GmbH & Co. KG (Priority 2 · Erlangen / Hybrid)",
      role: "Systems Calculation & Thermal Modeling Engineer (m/w/d)",
      location: "Freyeslebenstraße 1, 91058 Erlangen / Hybrid",
      score: "9.7 / 10",
      justification: "Exzellente Passung für gekoppelte Strömungs- und Wärmetransfersimulation, numerische Strömungsmechanik (CFD), FEM Strukturanalyse und Python Scripting zur automatisierten Parametrisierung.",
      keywords: "CFD Simulation, FEM, Thermodynamik, Python, OpenFOAM",
      gap: "Spezifische Siemens hauseigene Berechnungs-Toolchain.",
      salary: "70.000 € – 86.000 € (Siemens Energy Tarif IG Metall Bayern). Zielvergütung: 72.000 € brutto/Jahr.",
      apply: "Siemens Energy Talent Acquisition · Erlangen Hub",
      assets: ["siemens_energy.html", "siemens_energy.pdf", "2026-09-30_siemens_energy.html", "2026-09-30_siemens_energy.pdf", "siemens_energy.txt"],
      qa: "244 Wörter (DIN-5008 < 300) · 0 Gedankenstriche · 0 Semikolons · Burstiness-Spannweite = 30 Wörter · 0 8-Wort Überlappung · Invariante 72.000 € brutto/Jahr · 3 Monate Kündigungsfrist"
    },
    checklist: {
      availability: "3 Monate zum Monatsende (im Einvernehmen gern auch kurzfristiger).",
      salary: "72.000 € brutto / Jahr (72.000 Euro)",
      uploads: "Anschreiben-PDF + Lebenslauf-PDF + M.Sc. Ingenieur-Zeugnis"
    },
    maintenance: "No master-resume change recommended today. 0 Section Growth, 0 Bullet Growth."
  }
};

// Function to switch Morning Action Brief interactive preview
function switchBrief(briefKey) {
  const data = BRIEFS[briefKey];
  if (!data) return;

  const titleEl = document.getElementById('brief-headline');
  const targetEl = document.getElementById('brief-target');
  const resultEl = document.getElementById('brief-result');

  if (titleEl) titleEl.textContent = data.title;
  if (targetEl) targetEl.textContent = data.target;
  if (resultEl) resultEl.textContent = data.result;

  // Package 1
  const pkg1Company = document.getElementById('pkg1-company');
  const pkg1Role = document.getElementById('pkg1-role');
  const pkg1Loc = document.getElementById('pkg1-location');
  const pkg1Score = document.getElementById('pkg1-score');
  const pkg1Just = document.getElementById('pkg1-justification');
  const pkg1Kw = document.getElementById('pkg1-keywords');
  const pkg1Gap = document.getElementById('pkg1-gap');
  const pkg1Sal = document.getElementById('pkg1-salary');
  const pkg1Apply = document.getElementById('pkg1-apply');
  const pkg1Qa = document.getElementById('pkg1-qa');

  if (pkg1Company) pkg1Company.textContent = data.pkg1.company;
  if (pkg1Role) pkg1Role.textContent = data.pkg1.role;
  if (pkg1Loc) pkg1Loc.textContent = data.pkg1.location;
  if (pkg1Score) pkg1Score.textContent = data.pkg1.score;
  if (pkg1Just) pkg1Just.textContent = data.pkg1.justification;
  if (pkg1Kw) pkg1Kw.textContent = data.pkg1.keywords;
  if (pkg1Gap) pkg1Gap.textContent = data.pkg1.gap;
  if (pkg1Sal) pkg1Sal.textContent = data.pkg1.salary;
  if (pkg1Apply) pkg1Apply.textContent = data.pkg1.apply;
  if (pkg1Qa) pkg1Qa.textContent = data.pkg1.qa;

  // Package 2
  const pkg2Company = document.getElementById('pkg2-company');
  const pkg2Role = document.getElementById('pkg2-role');
  const pkg2Loc = document.getElementById('pkg2-location');
  const pkg2Score = document.getElementById('pkg2-score');
  const pkg2Just = document.getElementById('pkg2-justification');
  const pkg2Kw = document.getElementById('pkg2-keywords');
  const pkg2Gap = document.getElementById('pkg2-gap');
  const pkg2Sal = document.getElementById('pkg2-salary');
  const pkg2Apply = document.getElementById('pkg2-apply');
  const pkg2Qa = document.getElementById('pkg2-qa');

  if (pkg2Company) pkg2Company.textContent = data.pkg2.company;
  if (pkg2Role) pkg2Role.textContent = data.pkg2.role;
  if (pkg2Loc) pkg2Loc.textContent = data.pkg2.location;
  if (pkg2Score) pkg2Score.textContent = data.pkg2.score;
  if (pkg2Just) pkg2Just.textContent = data.pkg2.justification;
  if (pkg2Kw) pkg2Kw.textContent = data.pkg2.keywords;
  if (pkg2Gap) pkg2Gap.textContent = data.pkg2.gap;
  if (pkg2Sal) pkg2Sal.textContent = data.pkg2.salary;
  if (pkg2Apply) pkg2Apply.textContent = data.pkg2.apply;
  if (pkg2Qa) pkg2Qa.textContent = data.pkg2.qa;

  // Checklist & Maintenance
  const chkAvail = document.getElementById('brief-chk-avail');
  const chkSal = document.getElementById('brief-chk-salary');
  const chkUp = document.getElementById('brief-chk-uploads');
  const maintEl = document.getElementById('brief-maintenance-text');

  if (chkAvail) chkAvail.textContent = data.checklist.availability;
  if (chkSal) chkSal.textContent = data.checklist.salary;
  if (chkUp) chkUp.textContent = data.checklist.uploads;
  if (maintEl) maintEl.textContent = data.maintenance;

  // Update tabs active state
  document.querySelectorAll('.brief-tabs .btn-pill-sm').forEach(btn => {
    if (btn.dataset.brief === briefKey) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  showToast(`Loaded results: ${briefKey}`);
}

// Cover Letter Data Across 4 Archetypes
const COVER_LETTERS = {
  fullstack: {
    sender: "Alex Morgan · Bloherfelder Straße 190 · 26131 Oldenburg · +49 151 23456789 · alex.morgan@example.com",
    recipient: "energy & meteo systems GmbH\nFrau Alexandra Jobst\nOskar-Homt-Str. 1\n26131 Oldenburg",
    date: "Oldenburg, 26. September 2026",
    subject: "Bewerbung als Fullstack Softwareentwickler (w/m/d) · Referenz #EMS-2026-98",
    salutation: "Sehr geehrte Frau Jobst,",
    p1: "die präzise Integration von Einspeiseprognosen und virtuellen Kraftwerken verlangt hochgradig verlässliche Daten-Pipelines und agile Microservices. Als Fullstack Entwickler mit solider Praxis in Python, TypeScript, REST APIs und relationalem Datenbankdesign verbinde ich robuste Backend-Architekturen mit performanten Webanwendungen. Genau diese Erfahrung möchte ich gewinnbringend in Ihr Team einbringen.",
    p2: "In meinen vergangenen Projekten lag der Fokus auf datenintensiven Workflows und skalierbaren SaaS-Systemen. Bei der Verarbeitung kontinuierlicher Telemetriedaten konnte ich mit Redis und asynchronen RabbitMQ Message Queues Latenzen signifikant reduzieren und tausende parallele Events stabil persistieren. Im Backend setze ich auf testgetriebene Entwicklung (PyTest, Vitest), saubere Domänenmodelle und automatisierte CI/CD Pipelines mit Docker Containerisierung. Stabilität und Wartbarkeit stehen für mich im laufenden Betrieb an erster Stelle. Pragmatische Lösungen liegen mir.",
    p3: "Meine Gehaltserwartung liegt bei 52.500 Euro brutto im Jahr. Meine Kündigungsfrist beträgt drei Monate zum Monatsende, wobei wir einen früheren Beginn bei Bedarf gerne individuell vereinbaren können. Weiterführende technische Referenzen und Live-Projekte finden Sie unter https://links.masrisystems.com. Über die Gelegenheit, mich Ihnen persönlich vorzustellen, freue ich mich sehr.",
    closing: "Mit freundlichen Grüßen,\nAlex Morgan"
  },
  devops: {
    sender: "Elena Becker · Leopoldstraße 142 · 80804 München · +49 89 98765432 · elena.becker@example.com",
    recipient: "Scalable Capital GmbH\nTalent Acquisition Team\nSeitzstraße 8e\n80538 München",
    date: "München, 28. September 2026",
    subject: "Bewerbung als Lead Cloud DevOps & Platform Architect · Ref #SC-PLAT-2026",
    salutation: "Sehr geehrtes Platform Team,",
    p1: "FinTech Plattformen mit hohem Transaktionsvolumen fordern kompromisslose Ausfallsicherheit, Zero-Trust Sicherheitsarchitekturen und vollautomatisierte Deployment-Zyklen. Als Cloud DevOps Architektin mit mehrjähriger Praxis in Multi-Region Kubernetes Clustern, Infrastructure as Code mit Terraform und observablen Cloud Systemen auf AWS begleite ich skalierende Plattformen verlässlich in die Cloud.",
    p2: "In meiner letzten Station verantwortete ich den Übergang zu einem deklarativen GitOps Workflow mit ArgoCD für über 40 Microservices. Dadurch sank die mittlere Deployment-Dauer von Stunden auf unter 8 Minuten bei 99.98% Service Availability. Prometheus, Grafana und Datadog sicherten die unterbrechungsfreie Erkennung von Lastspitzen. Automatisierte Canary Rollouts verhinderten Regressionen in Kundenumgebungen. Belastbare Systeme schaffen Vertrauen.",
    p3: "Meine Gehaltserwartung beläuft sich auf 68.000 Euro brutto im Jahr. Meine Kündigungsfrist beträgt drei Monate zum Monatsende, im Einvernehmen gern auch kurzfristiger. Vertiefende Architekturdokumentationen und Codebeispiele finden Sie unter https://links.masrisystems.com. Ich freue mich auf das gemeinsame Fachgespräch.",
    closing: "Mit freundlichen Grüßen,\nElena Becker"
  },
  designer: {
    sender: "Julian Richter · Stresemannstraße 120 · 22769 Hamburg · +49 40 12345678 · julian.richter@example.com",
    recipient: "Jimdo GmbH\nDesign Operations & Hiring Team\nStresemannstraße 375\n22761 Hamburg",
    date: "Hamburg, 29. September 2026",
    subject: "Bewerbung als Staff Product Designer & Design Systems Lead · Ref #JIM-UX-26",
    salutation: "Sehr geehrtes Design-Team,",
    p1: "moderne Web- und No-Code Plattformen begeistern Nutzer dann, wenn mächtige Funktionen durch intuitive, barrierefreie und konsistente User Interfaces fast mühelos bedienbar werden. Als Product Designer mit starkem Fokus auf Design Systems, WCAG 2.1 AA Barrierefreiheit und User Testing schaffe ich die nahtlose Brücke zwischen Nutzerbedürfnis, Figma Komponentenbibliothek und Frontend Implementierung.",
    p2: "Zuletzt habe ich ein Multi-Brand Design System von Grund auf neu strukturiert. Über semantische Design Tokens (Style Dictionary) konnten Produkt-Squads und Entwickler neue Features in halber Zeit fehlerfrei implementieren. In iterativen Usability Tests mit realen Endnutzern identifizierten wir Reibungspunkte frühzeitig und steigerten die Onboarding Conversion messbar um 24 Prozent. Gutes Design löst echte Probleme messbar.",
    p3: "Meine Gehaltserwartung liegt bei 62.000 Euro brutto im Jahr. Meine Kündigungsfrist beträgt drei Monate zum Monatsende, im Einvernehmen gern auch kurzfristiger. Mein interaktives Portfolio mit detaillierten Case Studies steht unter https://links.masrisystems.com bereit. Ich freue mich sehr auf das persönliche Kennenlernen.",
    closing: "Mit freundlichen Grüßen,\nJulian Richter"
  },
  engineering: {
    sender: "Stefan Kramer · Theodor-Heuss-Straße 28 · 70174 Stuttgart · +49 711 98765432 · stefan.kramer@example.com",
    recipient: "EnBW Energie Baden-Württemberg AG\nRecruiting Center Stuttgart\nDurlacher Allee 93\n76131 Karlsruhe",
    date: "Stuttgart, 30. September 2026",
    subject: "Bewerbung als Senior Entwicklungsingenieur Großbatteriespeicher (BESS) · Ref #ENBW-ENG-26",
    salutation: "Sehr geehrte Damen und Herren,",
    p1: "die Energiewende gelingt nur mit sicheren, hochverfügbaren und thermisch optimierten Großbatteriespeichern im Megawatt-Bereich. Als Entwicklungsingenieur Maschinenbau mit fundierter Spezialisierung in CAD Konstruktion, CFD Strömungssimulation (Ansys Fluent) und thermischem Batteriemanagement entwickle ich marktreife Speichersysteme von der ersten Auslegung bis zur VDE-Konformität.",
    p2: "In der industriellen Produktentwicklung leitete ich die thermische Auslegung von Lithium-Eisenphosphat (LFP) Container-Speichern. Durch gezielte Strömungsleitsysteme und transiente thermische Simulationen gelang es, Temperaturspreizungen zwischen Batteriezellen auf unter 2.5 Kelvin zu begrenzen, was die prognostizierte Zelllebensdauer signifikant verlängerte. Pragmatische Ingenieurpraxis, standardisierte Fertigungsgerechtheit und strikte Sicherheitsanalysen prägen meine Arbeit.",
    p3: "Meine Gehaltserwartung liegt bei 72.000 Euro brutto im Jahr. Meine Kündigungsfrist beträgt drei Monate zum Monatsende, im Einvernehmen gern auch kurzfristiger. Ausführliche technische Berechnungsbeispiele und Projektübersichten finden Sie unter https://links.masrisystems.com. Ich freue mich auf den fachlichen Dialog mit Ihrem Team.",
    closing: "Mit freundlichen Grüßen,\nStefan Kramer"
  }
};

// Function to switch Cover Letter persona
function switchCoverLetterPersona(personaKey) {
  const data = COVER_LETTERS[personaKey];
  if (!data) return;

  const senderEl = document.getElementById('din-sender');
  const recipEl = document.getElementById('din-recipient');
  const dateEl = document.getElementById('din-date');
  const subjEl = document.getElementById('din-subject');
  const salEl = document.getElementById('din-salutation');
  const p1El = document.getElementById('din-p1');
  const p2El = document.getElementById('din-p2');
  const p3El = document.getElementById('din-p3');
  const closeEl = document.getElementById('din-closing');

  if (senderEl) senderEl.textContent = data.sender;
  if (recipEl) recipEl.textContent = data.recipient;
  if (dateEl) dateEl.textContent = data.date;
  if (subjEl) subjEl.textContent = data.subject;
  if (salEl) salEl.textContent = data.salutation;
  if (p1El) p1El.textContent = data.p1;
  if (p2El) p2El.textContent = data.p2;
  if (p3El) p3El.textContent = data.p3;
  if (closeEl) closeEl.textContent = data.closing;

  // Update tabs active state
  document.querySelectorAll('.cover-letter-tabs .btn-pill-sm').forEach(btn => {
    if (btn.dataset.letter === personaKey) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  showToast(`Loaded cover letter: ${personaKey}`);
}

// ==========================================
// Interactive 20-Min Workflow Simulation Engine
// ==========================================
const SIM_STAGES = [
  {
    step: 1,
    time: "08:00 AM",
    elapsed: "00:00 / 20:00",
    title: "Stage 1 · Spot Fresh Jobs & Skip Old Ones",
    tagline: "Scanned 14 newly posted openings across Google, LinkedIn & StepStone · 12 duplicates skipped",
    logLines: [
      { tag: "CHECK", cls: "text-blue-500", text: "Reading jobs/job_matches.md application tracker to prevent double applications." },
      { tag: "SEARCH", cls: "text-amber-500", text: "Google & LinkedIn Query: (\"Fullstack Entwickler\" OR \"Python\") Oldenburg (Last 24h)" },
      { tag: "DISCOVERY", cls: "text-sky-400", text: "Discovered 14 active job postings matching degree & core stack." },
      { tag: "FILTER", cls: "text-purple-400", text: "12 companies already in your tracking ledger -> Skipped automatically." },
      { tag: "TOP PICK 1", cls: "text-emerald-400", text: "energy & meteo systems GmbH · Full-Stack Softwareentwickler (Oldenburg)" },
      { tag: "TOP PICK 2", cls: "text-emerald-400", text: "CEWE Stiftung & Co. KGaA · Senior Fullstack Entwickler (Oldenburg)" }
    ],
    stats: [
      { label: "Portals Scanned", value: "3 Portals" },
      { label: "New Postings", value: "14 Found" },
      { label: "Duplicates Skipped", value: "12 Filtered" },
      { label: "Qualifying Leads", value: "2 Targets" }
    ]
  },
  {
    step: 2,
    time: "08:05 AM",
    elapsed: "05:00 / 20:00",
    title: "Stage 2 · Check Your Fit & Pick The Top 2",
    tagline: "Graded fit: 100% Required Skills Match + 95% Preferred Match = 9.8 / 10 Score",
    logLines: [
      { tag: "ANALYZE", cls: "text-blue-500", text: "Evaluating job requirements against candidate profile (@config/profile.json)..." },
      { tag: "MUST HAVES", cls: "text-emerald-400", text: "Required Skills (70%): Python (1.0), TypeScript (1.0), PostgreSQL (1.0) -> 100% Match!" },
      { tag: "NICE TO HAVES", cls: "text-emerald-400", text: "Preferred Skills (30%): Docker & CI/CD Pipelines (1.0), Redis (0.9) -> 95% Match!" },
      { tag: "COMMUTE", cls: "text-amber-400", text: "Priority 1 Local Commute: ~2.5 km in Oldenburg (5-7 min bike ride)" },
      { tag: "SALARY", cls: "text-sky-400", text: "Kununu check: 54.000 € – 62.000 € -> Matches candidate invariant (52.500 € brutto)" },
      { tag: "FIT SCORE", cls: "text-emerald-300 font-bold", text: "Overall Fit Score: 9.8 / 10 -> Meets the 9/10 Quality Rule! Ready to generate." }
    ],
    stats: [
      { label: "Fit Score", value: "9.8 / 10" },
      { label: "Must-Haves Match", value: "100% Fit" },
      { label: "Commute", value: "5 Min Bike" },
      { label: "Kununu Check", value: "Verified Fair" }
    ]
  },
  {
    step: 3,
    time: "08:10 AM",
    elapsed: "10:00 / 20:00",
    title: "Stage 3 · Auto-Generate Resume & Cover Letter",
    tagline: "Zero manual Word editing: Tailored ATS Resume + DIN-5008 Cover Letter + High-Res PDF",
    logLines: [
      { tag: "ENGINE", cls: "text-blue-500", text: "Running unified engine: python jobs/engine.py run --config 2026-09-26_energymeteo.json" },
      { tag: "PROFILE", cls: "text-purple-400", text: "Candidate: Mohamad Masri | Notice Period: 3 Monate | Target: 52.500 € brutto" },
      { tag: "RESUME", cls: "text-emerald-400", text: "Generated tailored HTML resume: jobs/resumes/2026-09-26_energymeteo.html (ATS-compliant)" },
      { tag: "COVER LETTER", cls: "text-emerald-400", text: "Crafted DIN-5008 letter: STAR achievement hook, 3 key problems solved, 284 words" },
      { tag: "PDF EXPORT", cls: "text-sky-400", text: "Headless Chromium rendered A4 DIN-5008 PDF: Mohamad_Masri_Lebenslauf.pdf (38.4 KB)" },
      { tag: "QUALITY GATE", cls: "text-emerald-300 font-bold", text: "0 formatting errors, 0 robotic buzzwords, 100% ATS DOM Parity -> Ready to submit!" }
    ],
    stats: [
      { label: "Tailored Resume", value: "100% ATS Ready" },
      { label: "Cover Letter", value: "DIN-5008 (284w)" },
      { label: "PDF Size", value: "38.4 KB" },
      { label: "Time Saved", value: "~2.5 Hours" }
    ]
  },
  {
    step: 4,
    time: "08:15 AM",
    elapsed: "15:00 / 20:00",
    title: "Stage 4 · Submit, Record It & You're Done!",
    tagline: "Uploaded to company portal · Logged in tracking ledger · Done in 18 minutes!",
    logLines: [
      { tag: "SUBMIT", cls: "text-blue-500", text: "Uploaded PDF resume & cover letter to energy & meteo systems official portal." },
      { tag: "TRACKER", cls: "text-sky-400", text: "Logged in jobs/job_matches.md: | 2026-09-26 | energy & meteo systems | 9.8/10 | Applied |" },
      { tag: "INTEGRITY", cls: "text-emerald-400", text: "Master resume protected: 0 new sections, 0 new bullets, 0 word-count growth." },
      { tag: "COMPLIANCE", cls: "text-emerald-400", text: "Spaced compounds verified: REST APIs, CI/CD Pipelines, MCP Tools, Fullstack Entwickler." },
      { tag: "SUCCESS", cls: "text-emerald-300 font-bold", text: "2 High-Fit Applications Sent in 18m 42s · Enjoy your morning coffee!" }
    ],
    stats: [
      { label: "Applications Sent", value: "2 Complete" },
      { label: "Total Time", value: "18m 42s" },
      { label: "Tracker Status", value: "Logged" },
      { label: "Next Action", value: "Enjoy Coffee" }
    ]
  }
];

let currentSimStage = 1;
let simPlaying = false;
let simInterval = null;
let simSpeed = 1;

function escapeSimHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function renderSimStage(stageNum) {
  currentSimStage = stageNum;
  const stage = SIM_STAGES[stageNum - 1];
  if (!stage) return;

  // 1. Update active card highlight
  document.querySelectorAll('.workflow-stage-card').forEach(card => {
    const cardStage = parseInt(card.dataset.stage, 10);
    if (cardStage === stageNum) {
      card.classList.add('sim-active');
    } else {
      card.classList.remove('sim-active');
    }
  });

  // 2. Update scrub bar steps & fill width
  document.querySelectorAll('.scrub-step-btn').forEach(btn => {
    const step = parseInt(btn.dataset.step, 10);
    if (step === stageNum) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
  const fill = document.getElementById('workflow-scrub-fill');
  if (fill) {
    fill.style.width = `${(stageNum / 4) * 100}%`;
  }

  // 3. Update clock & elapsed
  const clockEl = document.getElementById('sim-clock');
  const elapsedEl = document.getElementById('sim-elapsed');
  if (clockEl) clockEl.textContent = stage.time;
  if (elapsedEl) elapsedEl.textContent = stage.elapsed;

  // 4. Render Telemetry in Monitor
  const monitor = document.getElementById('sim-stage-monitor');
  if (monitor) {
    let statsHtml = stage.stats.map(s => `
      <div class="sim-stat-chip">
        <span class="sim-stat-label">${s.label}</span>
        <span class="sim-stat-value">${s.value}</span>
      </div>
    `).join('');

    let logHtml = stage.logLines.map(line => `
      <div class="sim-log-row font-mono text-xs">
        <span class="sim-log-tag ${line.cls}">[${line.tag}]</span>
        <span class="sim-log-text">${escapeSimHtml(line.text)}</span>
      </div>
    `).join('');

    monitor.innerHTML = `
      <div class="sim-monitor-header">
        <div class="flex items-center gap-2">
          <span class="sim-live-pulse"></span>
          <span class="font-semibold text-sm text-slate-800 dark:text-slate-100">${stage.title}</span>
        </div>
        <div class="text-xs text-slate-500 dark:text-slate-400 font-mono">${stage.tagline}</div>
      </div>
      <div class="sim-stats-grid">${statsHtml}</div>
      <div class="sim-terminal-screen">${logHtml}</div>
    `;
  }
}

function toggleWorkflowSimulation() {
  if (simPlaying) {
    pauseWorkflowSimulation();
  } else {
    startWorkflowSimulation();
  }
}

function startWorkflowSimulation() {
  simPlaying = true;
  updatePlayButtonUI();
  if (simInterval) clearInterval(simInterval);

  const duration = Math.max(800, 3200 / simSpeed);
  simInterval = setInterval(() => {
    let nextStage = currentSimStage + 1;
    if (nextStage > 4) {
      nextStage = 1;
    }
    renderSimStage(nextStage);
  }, duration);
}

function pauseWorkflowSimulation() {
  simPlaying = false;
  updatePlayButtonUI();
  if (simInterval) {
    clearInterval(simInterval);
    simInterval = null;
  }
}

function resetWorkflowSimulation() {
  pauseWorkflowSimulation();
  renderSimStage(1);
}

function jumpToSimStage(stageNum) {
  pauseWorkflowSimulation();
  renderSimStage(stageNum);
}

function setSimSpeed(speed) {
  simSpeed = speed;
  document.querySelectorAll('.sim-speed-btn').forEach(btn => {
    if (parseInt(btn.dataset.speed, 10) === speed) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
  if (simPlaying) {
    startWorkflowSimulation();
  }
}

function updatePlayButtonUI() {
  const playIcon = document.getElementById('sim-play-icon');
  const pauseIcon = document.getElementById('sim-pause-icon');
  const label = document.getElementById('sim-play-label');
  if (playIcon && pauseIcon && label) {
    if (simPlaying) {
      playIcon.classList.add('hidden');
      pauseIcon.classList.remove('hidden');
      label.textContent = 'Pause Simulation';
    } else {
      playIcon.classList.remove('hidden');
      pauseIcon.classList.add('hidden');
      label.textContent = currentSimStage === 4 ? 'Replay 20-Min Simulation' : 'Play 20-Min Simulation';
    }
  }
}

// Mobile Navigation Drawer Controller
function toggleMobileNav() {
  const drawer = document.getElementById('nav-drawer');
  const toggleBtn = document.getElementById('nav-toggle-btn');
  const iconMenu = document.getElementById('nav-icon-menu');
  const iconClose = document.getElementById('nav-icon-close');

  if (!drawer || !toggleBtn) return;

  const isOpen = drawer.classList.contains('is-open');

  if (isOpen) {
    closeMobileNav();
  } else {
    drawer.classList.add('is-open');
    drawer.setAttribute('aria-hidden', 'false');
    toggleBtn.setAttribute('aria-expanded', 'true');
    if (iconMenu && iconClose) {
      iconMenu.classList.add('hidden');
      iconClose.classList.remove('hidden');
    }
  }
}

function closeMobileNav() {
  const drawer = document.getElementById('nav-drawer');
  const toggleBtn = document.getElementById('nav-toggle-btn');
  const iconMenu = document.getElementById('nav-icon-menu');
  const iconClose = document.getElementById('nav-icon-close');

  if (!drawer) return;

  drawer.classList.remove('is-open');
  drawer.setAttribute('aria-hidden', 'true');
  if (toggleBtn) {
    toggleBtn.setAttribute('aria-expanded', 'false');
  }
  if (iconMenu && iconClose) {
    iconMenu.classList.remove('hidden');
    iconClose.classList.add('hidden');
  }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) {
    lucide.createIcons();
  }

  // Close mobile drawer when pressing Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const drawer = document.getElementById('nav-drawer');
      if (drawer && drawer.classList.contains('is-open')) {
        closeMobileNav();
        const toggleBtn = document.getElementById('nav-toggle-btn');
        if (toggleBtn) toggleBtn.focus();
      }
    }
  });

  // Close mobile drawer when clicking outside top-nav
  document.addEventListener('click', (e) => {
    const topNav = document.getElementById('top-nav');
    const drawer = document.getElementById('nav-drawer');
    if (topNav && drawer && drawer.classList.contains('is-open')) {
      if (!topNav.contains(e.target)) {
        closeMobileNav();
      }
    }
  });

  // Close mobile drawer on desktop resize (> 900px)
  window.addEventListener('resize', () => {
    if (window.innerWidth > 900) {
      closeMobileNav();
    }
  });

  // Initialize Simulation Deck Stage 1
  renderSimStage(1);

  // Bind stage card clicks
  document.querySelectorAll('.workflow-stage-card').forEach((card, idx) => {
    card.setAttribute('data-stage', (idx + 1).toString());
    card.addEventListener('click', () => {
      jumpToSimStage(idx + 1);
    });
  });

  // Bind persona switcher clicks for resume
  document.querySelectorAll('.persona-pills .btn-pill-sm').forEach(pill => {
    pill.addEventListener('click', () => {
      const key = pill.dataset.persona;
      if (key) switchPersona(key);
    });
  });

  // Bind brief switcher clicks
  document.querySelectorAll('.brief-tabs .btn-pill-sm').forEach(btn => {
    btn.addEventListener('click', () => {
      const key = btn.dataset.brief;
      if (key) switchBrief(key);
    });
  });

  // Bind cover letter switcher clicks
  document.querySelectorAll('.cover-letter-tabs .btn-pill-sm').forEach(btn => {
    btn.addEventListener('click', () => {
      const key = btn.dataset.letter;
      if (key) switchCoverLetterPersona(key);
    });
  });
});

