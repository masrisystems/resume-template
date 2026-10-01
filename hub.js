/**
 * Career Hub Interactive Client Logic
 * Handles 1-click clipboard copy, persona switching, ATS mode, and smooth navigation.
 * Zero external framework dependencies.
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

// 1-Click Clipboard Copy
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
    // Fallback for non-secure contexts
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

// Pre-defined Archetype Data
const ARCHETYPES = {
  engineering: {
    name: "Stefan Kramer",
    title_en: "Senior Systems & Mechanical Engineer (M.Sc.)",
    title_de: "Senior Entwicklungsingenieur Maschinenbau (M.Sc.)",
    file: "./resume.html",
    avatar: "stefan-kramer-profile.webp"
  },
  fullstack: {
    name: "Alex Morgan",
    title_en: "Senior Fullstack Engineer & AI Solutions Architect",
    title_de: "Senior Fullstack Entwickler & KI Lösungsarchitekt",
    file: "./jobs/roles/html/fullstack_laravel.html",
    avatar: "alex-morgan-profile.webp"
  },
  devops: {
    name: "Elena Becker",
    title_en: "Lead Cloud DevOps & Platform Architect",
    title_de: "Lead Cloud DevOps & Plattform Architektin",
    file: "./jobs/roles/html/ai_product_engineer.html",
    avatar: "alex-morgan-profile.webp"
  },
  designer: {
    name: "Julian Richter",
    title_en: "Staff Product Designer & Design Systems Lead",
    title_de: "Staff Product Designer & Design Systems Lead",
    file: "./jobs/roles/html/frontend_ui_architect.html",
    avatar: "alex-morgan-profile.webp"
  },
  finance: {
    name: "Clara Lindemann",
    title_en: "Senior Financial Controller & FP&A Lead",
    title_de: "Senior Financial Controllerin & FP&A Spezialistin",
    file: "./resume.html",
    avatar: "alex-morgan-profile.webp"
  }
};

// Persona Switcher
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

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) {
    lucide.createIcons();
  }

  // Bind persona switcher clicks
  document.querySelectorAll('.persona-pills .btn-pill-sm').forEach(pill => {
    pill.addEventListener('click', (e) => {
      const key = pill.dataset.persona;
      if (key) switchPersona(key);
    });
  });
});
