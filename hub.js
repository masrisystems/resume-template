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
  fullstack: {
    name: "Alex Morgan",
    title_en: "Senior Fullstack Engineer & AI Solutions Architect",
    title_de: "Senior Fullstack Entwickler & KI Lösungsarchitekt",
    avatar: "alex-morgan-profile.webp"
  },
  devops: {
    name: "Elena Becker",
    title_en: "Lead Cloud DevOps & Platform Architect",
    title_de: "Lead Cloud DevOps & Plattform Architektin",
    avatar: "alex-morgan-profile.webp"
  },
  designer: {
    name: "Julian Richter",
    title_en: "Staff Product Designer & Design Systems Lead",
    title_de: "Staff Product Designer & Design Systems Lead",
    avatar: "alex-morgan-profile.webp"
  },
  finance: {
    name: "Clara Lindemann",
    title_en: "Senior Financial Controller & FP&A Lead",
    title_de: "Senior Financial Controllerin & FP&A Spezialistin",
    avatar: "alex-morgan-profile.webp"
  },
  engineering: {
    name: "Stefan Kramer",
    title_en: "Senior Systems & Mechanical Engineer (M.Sc.)",
    title_de: "Senior Entwicklungsingenieur Maschinenbau (M.Sc.)",
    avatar: "stefan-kramer-profile.webp"
  }
};

// Persona Switcher
function switchPersona(personaKey) {
  const data = ARCHETYPES[personaKey];
  if (!data) return;

  // Update name in header
  const nameEl = document.querySelector('#header h1');
  if (nameEl) nameEl.textContent = data.name;

  // Update subtitle
  const titleEl = document.querySelector('#header h2');
  if (titleEl) {
    titleEl.setAttribute('data-lang-en', data.title_en);
    titleEl.setAttribute('data-lang-de', data.title_de);
    const currentLang = document.documentElement.lang || 'en';
    titleEl.textContent = currentLang === 'de' ? data.title_de : data.title_en;
  }

  // Update avatar
  const avatarEl = document.querySelector('#header img');
  if (avatarEl && data.avatar) {
    avatarEl.src = data.avatar;
    avatarEl.alt = data.name;
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

// ATS Plain Text Mode Toggle
function toggleAtsMode() {
  const paper = document.getElementById('resume-paper');
  if (!paper) return;
  paper.classList.toggle('ats-plain-mode');
  const isAts = paper.classList.contains('ats-plain-mode');
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
