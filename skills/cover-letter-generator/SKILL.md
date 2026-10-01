---
name: cover-letter-generator
description: Create truthful, personalized cover letters from a resume and job description, then apply blocking humanization, originality, paraphrasing, spelling, and grammar quality gates before delivery.
---

# Cover Letter Generator

## When to Use This Skill

Use this skill when the user wants to:
- Write a cover letter for a job application
- Create a personalized application letter
- Address specific job requirements in letter format
- Mentions: "cover letter", "application letter", "write cover letter", "letter for job"

Use AFTER analyzing job description to have clear talking points.

## Core Capabilities

- Generate personalized cover letters from resume + job description
- Match tone to company culture
- Address qualification gaps strategically
- Create compelling opening hooks
- Structure persuasive arguments for candidacy
- Maintain authenticity while selling effectively

## Cover Letter Philosophy

**The Problem:** Most cover letters are generic, boring, and add no value beyond the resume.

**The Solution:** A great cover letter should:
1. Show you've researched the company
2. Connect YOUR specific experience to THEIR specific needs by drawing concrete proof from authentic work logs (e.g. `What I worked.md`, project case studies)
3. Address the "why you, why now, why here" questions
4. Add personality and context a resume can't convey

### Core Safety & Domain Rules
- **Candidate Notice Period:** Contractual notice period is defined in `config/profile.json` under `invariants.notice_period_de` (*dreimonatige Kündigungsfrist zum Monatsende, im Einvernehmen gern auch kurzfristiger*). NEVER claim "ab sofort" or "sofort verfügbar".
- **Domain Prohibition:** Strictly NEVER mention or link to prohibited domains configured in `config/profile.json` under `candidate.prohibited_domains`. Because each resume is uniquely tailored per vacancy, directing employers to a generic resume URL presents the generic master resume, contradicting the customized application package. In header contact rows and closing paragraphs, use `candidate.links_url` and `candidate.email` from `config/profile.json`.

## Blocking Quality Pipeline

Run every stage in order. Do not deliver, export, or mark a letter ready until all stages pass.

### 1. Build an Evidence Ledger Before Drafting

- Extract the employer's top three needs as concepts, not reusable sentences.
- Map every proposed skill, metric, project, date, title, and company-specific statement to the resume, job description, official company source, or the private Work knowledge base.
- Cut unsupported claims. Do not repair a weak claim by making it vaguer while preserving an unverified implication.
- Keep names, technology versions, dates, and measurements exact through later rewriting passes.

### 2. Draft from Concepts Only

- Apply the weekly-blog-workflow's zero-plagiarism method: extract facts and concepts, discard source syntax, and write fresh sentences.
- Never paraphrase the job description, company website, a sample letter, or a previous application sentence by sentence.
- Quote no source language unless a short quotation is genuinely necessary and attributed. Cover letters normally need no quotations.

### 3. Humanize and Paraphrase Once

- Apply the authoritative **humanize** skill (`C:\Users\super\.agents\skills\humanize\SKILL.md` from `https://github.com/harshaneel/humanize.git`) to rewrite the complete first draft for natural human voice while preserving the evidence ledger exactly.
- Enforce the **7 Hard Rules**:
  1. *Em dashes:* 0 em dashes under 300 words.
  2. *Semicolons:* none unless in a comma-containing list.
  3. *Straight quotes and apostrophes only.*
  4. *Banned vocabulary:* delve, leverage, utilize, robust, comprehensive, streamline, furthermore, moreover, "it is important to note".
  5. *No negation framing:* "not just X", "not X, it's Y", "more X than Y". Say what the thing IS.
  6. *Output shape:* the letter text only (no meta preambles or diff explanations).
  7. *Sentence-length spread (Burstiness):* Range floor (longest sentence minus shortest >= 20 words) with at least one punchy <= 5-word fragment and fewer than half the sentences in the 10-to-20-word band.
- Apply the **9 Levers**: Perplexity injection (domain-native engineering vocabulary, e.g. "Webhooks abfeuern", "ans Rate-Limit treiben"), Burstiness, Hedge surgery, Structural flattening, Specificity insertion (exact numbers, named tools, concrete architecture), Voice and register, Discourse coherence, Punctuation normalization, and Stripping RLHF / "helpful assistant" cadence.
- Avoid German clichés such as: *hiermit bewerbe ich mich, mit großem Interesse habe ich, perfekte Besetzung, dynamisches Umfeld, meine Fähigkeiten gewinnbringend einsetzen,* and *mit meiner einzigartigen Kombination*.
- Never “humanize” by adding anecdotes, emotions, imperfections, slang, metrics, or company knowledge that the sources do not support.

### 4. Run the Originality Check

- Compare the draft against the saved job description, company-source text used for research, supplied templates, and prior cover letters when available.
- Run `scripts/check_cover_letter.py` with the draft and relevant source files.
- Block delivery when any source sentence of eight or more words is copied exactly, or when a contiguous source sequence of twelve or more normalized words appears in the draft, except unavoidable legal names, role titles, addresses, and technology names.
- Rewrite the flagged passage from the underlying concept, then rerun the check. Do not use synonym swapping to disguise a near-copy.
- Treat the result as a source-overlap check, not proof against every publication on the internet. Never claim “100% plagiarism-free” or invent a plagiarism percentage without a dedicated, authorized service.
- Do not upload private resumes, letters, or work notes to a public plagiarism service without explicit user authorization.

### 5. Run Spelling and Grammar QA

- Proofread the final-language version independently from the humanization pass. Check spelling, grammar, punctuation, agreement, articles, tense, capitalization, and missing or duplicated words.
- For German, additionally check case and gender agreement, verb position, compound nouns, umlauts and ß, comma placement, and consistent formal `Sie/Ihr/Ihnen` capitalization.
- For English, additionally check article use, subject-verb agreement, tense consistency, prepositions, and punctuation.
- Preserve intentional technical terms and company spellings. Do not “correct” product names or framework capitalization.
- Use a local grammar checker when one is available. If none is installed, perform two separate model passes: first spelling/grammar only, then read the text once for naturalness. Do not send the letter to an external checker without authorization.
- Apply corrections, then rerun the originality check because edits can reintroduce source phrasing.

### 6. Run the Final Integrity Gate

Require all of the following:

- Every factual statement remains traceable to the evidence ledger.
- No unsupported keyword, metric, employer initiative, recipient name, or motivation was introduced.
- No placeholder, editorial note, alternative opening, strategy note, or QA commentary remains inside the deliverable letter.
- The letter stays within the requested word limit and contains three or four short paragraphs.
- Humanization, source-overlap, spelling, grammar, and final naturalness checks all pass.
- Markdown and PDF contain the same substantive letter text.

When any check cannot run, report the limitation and keep the package out of a Ready to Submit state.

## The Perfect Cover Letter Structure

### Length & Format
- **Length:** 220-300 words by default (3-4 paragraphs), unless the user requests a different limit
- **Format:** Professional business letter style
- **Tone:** Confident but not arrogant, personalized but professional

### Structure Overview
```
[Your Contact Info]
[Date]
[Recipient Info]

Opening Paragraph: Hook + Position + Why This Company (2-3 sentences)

Body Paragraph 1: Your strongest qualification match (3-4 sentences)

Body Paragraph 2: Additional qualifications + address any gaps (3-4 sentences)

Closing Paragraph: Call to action + enthusiasm (2-3 sentences)

[Professional Sign-off]
```

## Opening Paragraph Strategies

The opening is critical - you have 5 seconds to grab attention.

### Hook Types (Choose One)

**1. Specific Company Knowledge**
```
"I was excited to see TechCorp's recent launch of your API marketplace - as a Product Manager who's spent 3 years building developer tools, I immediately saw how my experience could accelerate your platform growth."
```

**2. Mutual Connection**
```
"Sarah Chen on your engineering team mentioned you're looking for a PM to lead the payments initiative. Having worked with Sarah at [Previous Company] and led payment integrations at [Current Company], I'd love to discuss how I could contribute."
```

**3. Problem-Solver**
```
"Your job description mentions the challenge of aligning technical and business stakeholders - I've navigated this exact challenge, successfully launching 8 products by building shared roadmap visibility across engineering, sales, and executive teams."
```

**4. Impressive Achievement**
```
"Last year, I led a product that grew from 0 to 100K users in 6 months. I'm excited about the opportunity to bring that growth mindset to [Company]'s expanding product line."
```

**5. Industry Insight**
```
"The B2B payments space is at an inflection point, and [Company]'s approach to embedded finance positions you perfectly for the next wave. As someone who's been building in fintech for 5 years, I'd love to contribute to that growth."
```

### Opening Don'ts
- ❌ "I am writing to apply for..." (boring, obvious)
- ❌ "I am the perfect candidate..." (let them decide)
- ❌ "I saw your job posting on LinkedIn..." (generic)
- ❌ Starting with "I" (start with them or a hook)

## Body Paragraph Frameworks

### Body Paragraph 1: Direct Match

Connect your strongest experience to their top requirement.

**Formula:** [Their Need] + [Your Exact Experience] + [Specific Result]

```
Your focus on data-driven product decisions aligns perfectly with my approach. At [Company], I implemented a product analytics framework that increased feature adoption by 40% by identifying and prioritizing high-impact opportunities through A/B testing and user behavior analysis.
```

### Body Paragraph 2: Broader Value + Gap Handling

Show additional value and proactively address concerns.

**If you have gaps, address them:**
```
While my SQL experience is developing (currently completing DataCamp's SQL track), I bring strong analytical skills demonstrated through building Tableau dashboards that informed $2M in strategic decisions. I've consistently collaborated effectively with data teams and have a track record of quickly ramping on new tools.
```

**If no gaps, add more value:**
```
Beyond product management, I bring [relevant additional skill]. At [Company], this enabled me to [specific achievement]. I'm particularly drawn to [Company] because [specific reason showing research].
```

## Closing Paragraph

End with confidence and a clear call to action.

**Strong Closing Example:**
```
I'm excited about the opportunity to bring my [specific skill] experience to [Company]'s [specific initiative or product]. I'd welcome the chance to discuss how my background in [key area] could contribute to your team's goals. Thank you for considering my application.
```

**Elements of a Good Close:**
- Express genuine enthusiasm (for something specific)
- Reference a specific contribution you'd make
- Clear call to action (discuss, meet, etc.)
- Thank them

**Closing Don'ts:**
- ❌ "I look forward to hearing from you" (passive)
- ❌ "Please find my resume attached" (obvious)
- ❌ "I am available for an interview at your convenience" (desperate)

## Complete Cover Letter Template

```
[Your Name]
[Your Email] | [Your Phone] | [LinkedIn URL]
[City, State]

[Date]

[Hiring Manager Name, if known]
[Title]
[Company Name]
[Company Address]

Dear [Mr./Ms. Last Name / Hiring Manager],

[OPENING HOOK - 1-2 sentences grabbing attention with company knowledge, mutual connection, or impressive achievement]

[BRIDGE TO POSITION - 1 sentence stating the role and your interest]

[BODY 1 - 3-4 sentences connecting your strongest relevant experience to their primary requirement. Include specific metrics and results.]

[BODY 2 - 3-4 sentences adding additional value, addressing any gaps if needed, and demonstrating company research/culture fit]

[CLOSING - 2-3 sentences expressing enthusiasm, suggesting next steps, and thanking them]

Sincerely,
[Your Name]
```

## Industry-Specific Considerations

### Tech/Engineering
- Mention specific technologies
- Reference GitHub, portfolio, or technical projects
- Show you understand their tech stack

### Marketing/Creative
- Show creativity in the letter itself (within reason)
- Reference their campaigns or brand voice
- Include relevant metrics (engagement, conversion, etc.)

### Finance/Consulting
- More formal tone
- Lead with credentials/certifications
- Emphasize analytical rigor and results

### Startup vs. Enterprise
**Startup:** More casual, show scrappiness, emphasize growth mindset
**Enterprise:** More formal, emphasize process and scale experience

## Handling Common Scenarios

### When You Don't Know the Hiring Manager
```
Dear Hiring Manager,
OR
Dear [Department] Team,
OR
Dear [Company Name] Recruiting Team,
```
Avoid "To Whom It May Concern" (too impersonal)

### When You Have a Referral
Lead with it:
```
"[Name] on your [team] team suggested I reach out about the [Position] role. Having [connection to referrer], I was excited to learn about [Company]'s work in [area]."
```

### When You're Underqualified
Don't apologize. Instead, emphasize:
- Transferable skills
- Quick learning ability
- Genuine enthusiasm
- Related experience that compensates

### When You're Overqualified
Explain your motivation:
```
"After 10 years leading large teams, I'm energized by the opportunity to return to hands-on [function] work at a company where I can make direct impact on [specific area]."
```

### When Addressing Career Change
```
"While my background is in [Previous Field], I've been actively building [New Field] skills through [courses, projects, etc.]. My experience in [transferable skill] translates directly to [new role] through [specific connection]."
```

## Output Format

When generating a cover letter, provide:

```markdown
# COVER LETTER FOR [POSITION] AT [COMPANY]

## Analysis Summary
- Match Score: [From JD Analyzer]
- Key Strengths to Highlight: [List]
- Gaps to Address: [List or "None"]
- Company Research Notes: [Key facts to reference]

## Generated Cover Letter

[Full cover letter text]

---

## Alternative Openings

**Option 1 (Company Knowledge):**
[Alternative opening hook]

**Option 2 (Achievement-Led):**
[Alternative opening hook]

## Key Talking Points for Interview
- [Point 1 from the letter to expand on]
- [Point 2]
- [Point 3]
```

## Quality Checklist

Before delivering any cover letter:

1. ✅ Opens with a hook (not "I am writing to apply")
2. ✅ Mentions specific company knowledge
3. ✅ Connects experience directly to job requirements
4. ✅ Includes at least one specific metric/achievement
5. ✅ Addresses any obvious gaps (if applicable)
6. ✅ Has confident but not arrogant tone
7. ✅ Ends with clear call to action
8. ✅ Is within the requested limit (220-300 words by default, 3-4 paragraphs)
9. ✅ Contains no typos or grammatical errors
10. ✅ Would make you want to interview this person
11. ✅ Humanization pass completed without changing facts
12. ✅ Deterministic source-overlap check passed after the final rewrite
13. ✅ No banned AI filler, cover-letter clichés, placeholders, or template commentary remains
14. ✅ Final Markdown and PDF carry the same substantive text
