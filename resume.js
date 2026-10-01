/**
 * WebResume Client Hydration & Dynamic Multi-Language Engine
 * Drives resume.html exclusively from config/profile.json or embedded #profile-data.
 * Automatically discovers all configured languages (en, de, or custom) and renders
 * the complete semantic resume structure.
 */

// Helper: Extract text for requested language with fallback to English, German, or first available
function getI18nText(field, lang) {
  if (field === null || field === undefined) return '';
  if (typeof field === 'string') return field;
  if (typeof field === 'number') return String(field);
  if (typeof field === 'object') {
    if (field[lang] !== undefined) return field[lang];
    if (field['en'] !== undefined) return field['en'];
    if (field['de'] !== undefined) return field['de'];
    const ignoreKeys = new Set(['supplemental', 'id', 'year', 'type', 'url', 'verify_url']);
    for (const k of Object.keys(field)) {
      if (!ignoreKeys.has(k) && typeof field[k] === 'string') {
        return field[k];
      }
    }
    const keys = Object.keys(field);
    if (keys.length > 0 && typeof field[keys[0]] === 'string') return field[keys[0]];
  }
  return '';
}

// Helper: Escape HTML attributes
function escapeHtmlAttr(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

// Detect all distinct language codes available in profile
function detectAvailableLanguages(profile) {
  const langs = new Set();
  const ignoreKeys = new Set(['supplemental', 'id', 'year', 'type', 'url', 'verify_url', 'heading_display']);

  if (profile.ui_labels) {
    Object.values(profile.ui_labels).forEach(obj => {
      if (obj && typeof obj === 'object') {
        Object.keys(obj).forEach(l => { if (!ignoreKeys.has(l)) langs.add(l); });
      }
    });
  }
  if (profile.candidate) {
    ['degree', 'subtitle', 'summary', 'title'].forEach(k => {
      const val = profile.candidate[k];
      if (val && typeof val === 'object') {
        Object.keys(val).forEach(l => { if (!ignoreKeys.has(l)) langs.add(l); });
      }
    });
  }
  if (profile.experience && Array.isArray(profile.experience)) {
    profile.experience.forEach(exp => {
      ['title', 'period', 'company'].forEach(k => {
        const val = exp[k];
        if (val && typeof val === 'object') {
          Object.keys(val).forEach(l => { if (!ignoreKeys.has(l)) langs.add(l); });
        }
      });
      (exp.bullets || []).forEach(b => {
        if (b && typeof b === 'object') {
          Object.keys(b).forEach(l => { if (!ignoreKeys.has(l)) langs.add(l); });
        }
      });
    });
  }
  if (profile.skills && Array.isArray(profile.skills)) {
    profile.skills.forEach(cat => {
      if (cat.heading && typeof cat.heading === 'object') {
        Object.keys(cat.heading).forEach(l => { if (!ignoreKeys.has(l)) langs.add(l); });
      }
      (cat.items || []).forEach(it => {
        if (it && typeof it === 'object') {
          Object.keys(it).forEach(l => { if (!ignoreKeys.has(l)) langs.add(l); });
        }
      });
    });
  }
  if (langs.size === 0) {
    langs.add('en');
    langs.add('de');
  }
  return Array.from(langs);
}

// Dynamic Language Switcher Rendering
function renderLanguageSwitcher(langs, activeLang) {
  const container = document.getElementById('language-switcher-container');
  if (!container) return;

  container.innerHTML = '';
  const group = document.createElement('div');
  group.className = 'flex flex-col space-y-1 bg-white dark:bg-stone-800 p-1.5 rounded-lg shadow-md border border-gray-200 dark:border-gray-700';

  langs.forEach(langCode => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = `px-2.5 py-1 text-xs font-bold rounded transition-colors uppercase ${
      langCode === activeLang
        ? 'bg-[#cc785c] text-white shadow-sm'
        : 'text-gray-600 hover:text-black hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-stone-700'
    }`;
    btn.textContent = langCode;
    btn.setAttribute('aria-label', `Switch language to ${langCode.toUpperCase()}`);
    btn.onclick = () => switchLanguage(langCode);
    group.appendChild(btn);
  });

  container.appendChild(group);
}

// Main Render Function: Populates All Structural Slots
function renderResume(profile, lang) {
  document.documentElement.lang = lang;
  const cand = profile.candidate || {};
  const ui = profile.ui_labels || {};
  const availLangs = detectAvailableLanguages(profile);

  // Document Head & Title
  const candName = cand.name || 'Candidate';
  const roleTitle = getI18nText(cand.title, lang) || getI18nText(cand.subtitle, lang);
  document.title = `${candName} | ${roleTitle} — Resume`;

  const metaDesc = document.querySelector('meta[name="description"]');
  if (metaDesc) metaDesc.content = getI18nText(cand.summary, lang);

  // 1. Header
  const avatarEl = document.getElementById('candidate-avatar');
  if (avatarEl) {
    avatarEl.src = cand.avatar || './stefan-kramer-profile.webp';
    avatarEl.alt = candName;
  }

  const nameEl = document.getElementById('candidate-name');
  if (nameEl) nameEl.textContent = candName;

  const degEl = document.getElementById('candidate-degree');
  if (degEl) {
    degEl.textContent = getI18nText(cand.degree, lang);
    availLangs.forEach(l => {
      if (cand.degree && cand.degree[l]) degEl.setAttribute(`data-lang-${l}`, cand.degree[l]);
    });
  }

  const subEl = document.getElementById('candidate-subtitle');
  if (subEl) {
    subEl.textContent = getI18nText(cand.subtitle, lang);
    availLangs.forEach(l => {
      if (cand.subtitle && cand.subtitle[l]) subEl.setAttribute(`data-lang-${l}`, cand.subtitle[l]);
    });
  }

  const sumEl = document.getElementById('candidate-summary');
  if (sumEl) {
    sumEl.textContent = getI18nText(cand.summary, lang);
    availLangs.forEach(l => {
      if (cand.summary && cand.summary[l]) sumEl.setAttribute(`data-lang-${l}`, cand.summary[l]);
    });
  }

  // Contact Navigation
  const contactNav = document.getElementById('contact-nav');
  if (contactNav && cand.links) {
    contactNav.innerHTML = '';
    cand.links.forEach((link, idx) => {
      const a = document.createElement('a');
      a.className = 'contact-link font-medium text-[#a9583e] hover:underline dark:text-[#e8a55a]';
      a.href = link.url || '#';
      if (link.type !== 'email' && link.type !== 'phone') {
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
      }
      a.textContent = getI18nText(link.label, lang);
      contactNav.appendChild(a);

      if (idx < cand.links.length - 1) {
        const sep = document.createElement('span');
        sep.setAttribute('aria-hidden', 'true');
        sep.textContent = '·';
        contactNav.appendChild(sep);
      }
    });
  }

  // Header Buttons
  const dlBtn = document.getElementById('downloadPdf');
  if (dlBtn && ui.download_cv) {
    dlBtn.textContent = getI18nText(ui.download_cv, lang);
  }
  const liBtn = document.getElementById('linkedin-btn');
  if (liBtn) {
    if (ui.view_linkedin) liBtn.textContent = getI18nText(ui.view_linkedin, lang);
    const liLink = (cand.links || []).find(l => l.label && (l.label.en === 'LinkedIn' || l.label.de === 'LinkedIn'));
    if (liLink) liBtn.href = liLink.url;
  }

  // 2. Work Experience
  const expHeading = document.getElementById('heading-work-experience');
  if (expHeading && ui.work_experience) {
    expHeading.textContent = getI18nText(ui.work_experience, lang);
  }

  const expContainer = document.getElementById('experience-container');
  if (expContainer && profile.experience) {
    expContainer.innerHTML = '';
    profile.experience.forEach(role => {
      const roleDiv = document.createElement('div');
      if (role.id) roleDiv.id = role.id;
      roleDiv.className = 'mb-6';

      const h3 = document.createElement('h3');
      h3.className = 'font-bold';
      const titleSpan = document.createElement('span');
      titleSpan.textContent = getI18nText(role.title, lang);
      availLangs.forEach(l => {
        if (role.title && role.title[l]) titleSpan.setAttribute(`data-lang-${l}`, role.title[l]);
      });
      h3.appendChild(titleSpan);

      if (role.company) {
        const compText = document.createTextNode(` · ${getI18nText(role.company, lang)}`);
        h3.appendChild(compText);
      }
      roleDiv.appendChild(h3);

      const pDate = document.createElement('p');
      pDate.className = 'text-sm text-gray-600';
      const dateSpan = document.createElement('span');
      dateSpan.textContent = getI18nText(role.period, lang);
      availLangs.forEach(l => {
        if (role.period && role.period[l]) dateSpan.setAttribute(`data-lang-${l}`, role.period[l]);
      });
      pDate.appendChild(dateSpan);
      roleDiv.appendChild(pDate);

      const ul = document.createElement('ul');
      ul.className = 'list-disc ml-5 mt-2 text-sm';
      (role.bullets || []).forEach(b => {
        const li = document.createElement('li');
        if (b.supplemental) li.className = 'job-fair-supplemental';
        li.innerHTML = getI18nText(b, lang);
        availLangs.forEach(l => {
          if (b[l]) li.setAttribute(`data-lang-${l}`, b[l]);
        });
        ul.appendChild(li);
      });
      roleDiv.appendChild(ul);
      expContainer.appendChild(roleDiv);
    });
  }

  // 3. Technical Skills
  const skillsHeading = document.getElementById('heading-skills');
  if (skillsHeading && ui.technical_skills) {
    skillsHeading.textContent = getI18nText(ui.technical_skills, lang);
  }

  const skillsContainer = document.getElementById('skills-container');
  if (skillsContainer && profile.skills) {
    skillsContainer.innerHTML = '';
    profile.skills.forEach(cat => {
      const catDiv = document.createElement('div');
      if (cat.supplemental) catDiv.className = 'job-fair-supplemental';

      const h4 = document.createElement('h4');
      h4.className = 'font-semibold';
      h4.textContent = getI18nText(cat.heading, lang);
      availLangs.forEach(l => {
        if (cat.heading && cat.heading[l]) h4.setAttribute(`data-lang-${l}`, cat.heading[l]);
      });
      catDiv.appendChild(h4);

      const ul = document.createElement('ul');
      ul.className = 'list-disc ml-5';
      (cat.items || []).forEach(it => {
        const li = document.createElement('li');
        li.innerHTML = getI18nText(it, lang);
        availLangs.forEach(l => {
          if (it[l]) li.setAttribute(`data-lang-${l}`, it[l]);
        });
        ul.appendChild(li);
      });
      catDiv.appendChild(ul);
      skillsContainer.appendChild(catDiv);
    });
  }

  // 4. Education
  const eduHeading = document.getElementById('heading-education');
  if (eduHeading && ui.education) {
    eduHeading.textContent = getI18nText(ui.education, lang);
  }

  const eduContainer = document.getElementById('education-container');
  if (eduContainer && profile.education) {
    eduContainer.innerHTML = '';
    profile.education.forEach(deg => {
      const degDiv = document.createElement('div');
      degDiv.className = 'mb-3';

      const topFlex = document.createElement('div');
      topFlex.className = 'flex flex-wrap justify-between items-baseline';

      const pTitle = document.createElement('p');
      const strong = document.createElement('strong');
      const degSpan = document.createElement('span');
      degSpan.textContent = getI18nText(deg.degree, lang);
      availLangs.forEach(l => {
        if (deg.degree && deg.degree[l]) degSpan.setAttribute(`data-lang-${l}`, deg.degree[l]);
      });
      strong.appendChild(degSpan);
      pTitle.appendChild(strong);

      const instSpan = document.createElement('span');
      instSpan.className = 'text-sm font-medium text-gray-700 dark:text-gray-300';
      instSpan.textContent = ` · ${getI18nText(deg.institution, lang)}`;
      availLangs.forEach(l => {
        if (deg.institution && deg.institution[l]) instSpan.setAttribute(`data-lang-${l}`, `· ${deg.institution[l]}`);
      });
      pTitle.appendChild(instSpan);

      if (deg.grade) {
        const grSpan = document.createElement('span');
        grSpan.className = 'text-sm text-gray-600 dark:text-gray-400';
        grSpan.textContent = ` - ${getI18nText(deg.grade, lang)}`;
        availLangs.forEach(l => {
          if (deg.grade && deg.grade[l]) grSpan.setAttribute(`data-lang-${l}`, `- ${deg.grade[l]}`);
        });
        pTitle.appendChild(grSpan);
      }
      topFlex.appendChild(pTitle);

      const perSpan = document.createElement('span');
      perSpan.className = 'text-sm text-gray-600 dark:text-gray-400 font-medium';
      perSpan.textContent = getI18nText(deg.period, lang);
      availLangs.forEach(l => {
        if (deg.period && deg.period[l]) perSpan.setAttribute(`data-lang-${l}`, deg.period[l]);
      });
      topFlex.appendChild(perSpan);
      degDiv.appendChild(topFlex);

      if (deg.description) {
        const descP = document.createElement('p');
        descP.className = 'text-sm mt-1 text-gray-700 dark:text-gray-300';
        descP.textContent = getI18nText(deg.description, lang);
        availLangs.forEach(l => {
          if (deg.description && deg.description[l]) descP.setAttribute(`data-lang-${l}`, deg.description[l]);
        });
        degDiv.appendChild(descP);
      }
      eduContainer.appendChild(degDiv);
    });
  }

  // Academic Achievements
  const achHeading = document.getElementById('heading-academic-achievements');
  if (achHeading && ui.academic_achievements) {
    achHeading.textContent = getI18nText(ui.academic_achievements, lang);
  }
  const achContainer = document.getElementById('achievements-container');
  if (achContainer && profile.academic_achievements) {
    achContainer.innerHTML = '';
    profile.academic_achievements.forEach(item => {
      const li = document.createElement('li');
      li.textContent = getI18nText(item, lang);
      availLangs.forEach(l => {
        if (item[l]) li.setAttribute(`data-lang-${l}`, item[l]);
      });
      achContainer.appendChild(li);
    });
  }

  // Certifications
  const certHeading = document.getElementById('heading-certifications');
  if (certHeading && ui.certifications) {
    certHeading.textContent = getI18nText(ui.certifications, lang);
  }
  const certLink = document.getElementById('certifications-verify-link');
  if (certLink && profile.certifications) {
    certLink.href = profile.certifications.verify_url || '#';
    certLink.textContent = getI18nText(ui.verify_online, lang);
  }
  const certContainer = document.getElementById('certifications-container');
  if (certContainer && profile.certifications && profile.certifications.items) {
    certContainer.innerHTML = '';
    profile.certifications.items.forEach(c => {
      const li = document.createElement('li');
      const spanTitle = document.createElement('span');
      spanTitle.innerHTML = getI18nText(c.title, lang);
      availLangs.forEach(l => {
        if (c.title && c.title[l]) spanTitle.setAttribute(`data-lang-${l}`, c.title[l]);
      });
      li.appendChild(spanTitle);
      if (c.year) {
        const spanYr = document.createElement('span');
        spanYr.className = 'text-xs text-gray-500';
        spanYr.textContent = ` · ${c.year}`;
        li.appendChild(spanYr);
      }
      certContainer.appendChild(li);
    });
  }

  // 5. Languages
  const langHeading = document.getElementById('heading-languages');
  if (langHeading && ui.languages) {
    langHeading.textContent = getI18nText(ui.languages, lang);
  }
  const langContainer = document.getElementById('languages-container');
  if (langContainer && profile.languages) {
    langContainer.innerHTML = '';
    profile.languages.forEach(lItem => {
      const li = document.createElement('li');
      li.textContent = getI18nText(lItem, lang);
      availLangs.forEach(l => {
        if (lItem[l]) li.setAttribute(`data-lang-${l}`, lItem[l]);
      });
      langContainer.appendChild(li);
    });
  }

  // 6. Other Info & Hobbies
  const otherHeading = document.getElementById('heading-other-info');
  if (otherHeading && ui.other_info) {
    otherHeading.textContent = getI18nText(ui.other_info, lang);
  }
  const otherContainer = document.getElementById('other-info-container');
  if (otherContainer && profile.other_info) {
    otherContainer.innerHTML = '';
    profile.other_info.forEach(oItem => {
      const li = document.createElement('li');
      li.textContent = getI18nText(oItem, lang);
      availLangs.forEach(l => {
        if (oItem[l]) li.setAttribute(`data-lang-${l}`, oItem[l]);
      });
      otherContainer.appendChild(li);
    });
  }

  const hobHeading = document.getElementById('heading-hobbies');
  if (hobHeading && ui.hobbies) {
    hobHeading.textContent = getI18nText(ui.hobbies, lang);
  }
  const hobContainer = document.getElementById('hobbies-container');
  if (hobContainer && profile.hobbies) {
    hobContainer.innerHTML = '';
    profile.hobbies.forEach(hItem => {
      const li = document.createElement('li');
      li.textContent = getI18nText(hItem, lang);
      availLangs.forEach(l => {
        if (hItem[l]) li.setAttribute(`data-lang-${l}`, hItem[l]);
      });
      hobContainer.appendChild(li);
    });
  }

  // 7. Footer Print Signature
  const sigLink = document.getElementById('print-signature-link');
  if (sigLink) {
    const portfolioUrl = cand.portfolio_url || 'https://masrisystems.com';
    sigLink.href = portfolioUrl;
    sigLink.textContent = portfolioUrl;
  }

  // Render language switcher pills
  renderLanguageSwitcher(availLangs, lang);

  // Re-run Lucide SVG icon replacement
  if (window.lucide) {
    lucide.createIcons();
  }
}

// Global active profile cache
let currentProfileData = null;

// Switch active language and update DOM
function switchLanguage(targetLang) {
  const available = detectAvailableLanguages(currentProfileData || {});
  let nextLang = targetLang;
  if (!nextLang) {
    const cur = document.documentElement.lang || 'en';
    const curIdx = available.indexOf(cur);
    nextLang = available[(curIdx + 1) % available.length];
  }

  localStorage.setItem('lang', nextLang);
  if (currentProfileData) {
    renderResume(currentProfileData, nextLang);
  }
}

// Download CV PDF Handler
function downloadPdfHandler() {
  const resumeElement = document.getElementById('resumeContent');
  const noPrintElements = document.querySelectorAll('.no-print');

  document.body.classList.add('pdf-export-active');
  resumeElement.classList.add('pdf-export-active');
  noPrintElements.forEach(el => {
    el.dataset.originalDisplay = el.style.display;
    el.style.display = 'none';
  });

  const resumeRect = resumeElement.getBoundingClientRect();
  const linkElements = Array.from(resumeElement.querySelectorAll('a[href]')).filter(a => {
    return !a.closest('.no-print') && a.offsetParent !== null;
  });

  const linkAnnotations = [];
  linkElements.forEach(a => {
    const rects = a.getClientRects();
    if (rects && rects.length > 0) {
      for (let i = 0; i < rects.length; i++) {
        const r = rects[i];
        if (r.width > 0 && r.height > 0) {
          linkAnnotations.push({
            href: a.href,
            left: r.left - resumeRect.left,
            top: r.top - resumeRect.top,
            width: r.width,
            height: r.height,
          });
        }
      }
    }
  });

  html2canvas(resumeElement, {
    scale: 2,
    useCORS: true,
    backgroundColor: window.getComputedStyle(document.body).getPropertyValue('background-color'),
    ignoreElements: element => element.classList && element.classList.contains('no-print'),
  }).then(canvas => {
    const imgData = canvas.toDataURL('image/jpeg', 0.90);
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF({ orientation: 'portrait', unit: 'pt', format: 'a4' });

    const imgProps = pdf.getImageProperties(imgData);
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = pdf.internal.pageSize.getHeight();
    const bottomMargin = 10;
    const usablePdfPageHeight = pdfHeight - bottomMargin;
    const imgHeightInPdf = (imgProps.height * pdfWidth) / imgProps.width;

    let heightLeft = imgHeightInPdf;
    let position = 0;

    pdf.addImage(imgData, 'JPEG', 0, position, pdfWidth, imgHeightInPdf, undefined, 'FAST');
    heightLeft -= usablePdfPageHeight;

    while (heightLeft > 0) {
      position = heightLeft - imgHeightInPdf;
      pdf.addPage();
      pdf.addImage(imgData, 'JPEG', 0, position, pdfWidth, imgHeightInPdf, undefined, 'FAST');
      heightLeft -= usablePdfPageHeight;
    }

    const numPages = pdf.getNumberOfPages();
    linkAnnotations.forEach(annot => {
      const x = (annot.left / resumeRect.width) * pdfWidth;
      const w = (annot.width / resumeRect.width) * pdfWidth;
      const yTotal = (annot.top / resumeRect.height) * imgHeightInPdf;
      const h = (annot.height / resumeRect.height) * imgHeightInPdf;

      const pageIndex = Math.floor(yTotal / usablePdfPageHeight);
      const targetPage = pageIndex + 1;
      const yOnPage = yTotal - (pageIndex * usablePdfPageHeight);

      if (targetPage <= numPages) {
        pdf.setPage(targetPage);
        pdf.link(x, yOnPage, w, h, { url: annot.href });
      }
    });

    const candName = (currentProfileData && currentProfileData.candidate && currentProfileData.candidate.name) || 'Stefan-Kramer';
    const cleanName = candName.replace(/\s+/g, '-');
    pdf.save(`CV-${cleanName}.pdf`);
  }).catch(err => {
    console.error('Error generating PDF:', err);
  }).finally(() => {
    noPrintElements.forEach(el => {
      el.style.display = el.dataset.originalDisplay || '';
    });
    document.body.classList.remove('pdf-export-active');
    resumeElement.classList.remove('pdf-export-active');
  });
}

// Dark / Light Theme Toggle
function setTheme(theme) {
  const htmlElement = document.documentElement;
  if (theme === 'dark') {
    htmlElement.classList.add('dark');
    if (document.body) document.body.classList.add('dark');
    localStorage.setItem('theme', 'dark');
  } else {
    htmlElement.classList.remove('dark');
    if (document.body) document.body.classList.remove('dark');
    localStorage.setItem('theme', 'light');
  }
}

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  // Theme initialization
  const storedTheme = localStorage.getItem('theme');
  if (storedTheme) {
    setTheme(storedTheme);
  } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    setTheme('dark');
  } else {
    setTheme('light');
  }

  const themeToggleBtn = document.getElementById('theme-toggle');
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const isDark = document.documentElement.classList.contains('dark');
      setTheme(isDark ? 'light' : 'dark');
    });
  }

  // Load Profile Data: 1. Fetch live profile.json (if on server); 2. Fallback to embedded script
  const embeddedScript = document.getElementById('profile-data');
  if (embeddedScript && embeddedScript.textContent.trim()) {
    try {
      currentProfileData = JSON.parse(embeddedScript.textContent);
    } catch (e) {
      console.warn('Failed to parse embedded #profile-data JSON', e);
    }
  }

  // Check URL param or localStorage for language
  const urlParams = new URLSearchParams(window.location.search);
  const initialLang = urlParams.get('lang') || localStorage.getItem('lang') || 'en';

  // Attempt live fetch if served via HTTP/HTTPS, fallback to embedded
  if (window.location.protocol.startsWith('http')) {
    const fetchPath = window.location.pathname.includes('/jobs/') ? '../../../config/profile.json' : './config/profile.json';
    fetch(fetchPath)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => {
        currentProfileData = data;
        renderResume(currentProfileData, initialLang);
      })
      .catch(err => {
        console.info('Using embedded profile data (live fetch unavailable):', err.message);
        if (currentProfileData) {
          renderResume(currentProfileData, initialLang);
        }
      });
  } else if (currentProfileData) {
    renderResume(currentProfileData, initialLang);
  }
});
