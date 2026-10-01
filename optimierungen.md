1.  Optimierung des Skills (SKILL.md)

- Deep Research Step: Integriere einen optionalen Schritt zur Firmenrecherche. Bevor das Anschreiben erstellt wird, könnte der Agent die Vision, Mission oder aktuelle News des Unternehmens suchen, um "Culture Fit"-Elemente authentisch einzubauen.
- Validation Check: Füge einen Validierungsschritt hinzu, der nach der Generierung des Lebenslaufs prüft, ob alle data-lang-Attribute (Deutsch/Englisch) konsistent aktualisiert wurden, damit die Sprachumschalt-Funktion der HTML-Datei fehlerfrei bleibt.
- Automatisierte Ablage: Erweitere den Workflow um eine automatische Archivierung alter Versionen oder eine Verzeichnisstruktur nach Bewerbungsstatus (z. B. jobs/archive/rejected/ vs. jobs/active/).

2. Optimierung des Resume-Prompts (resume_prompt.md)

- Zweisprachige Konsistenz: Da dein Lebenslauf ein Sprach-Umschalt-Feature hat, sollte der Prompt explizit anweisen, sowohl den deutschen Text als auch die data-lang-en-Attribute zu aktualisieren. Aktuell besteht das Risiko, dass nur eine Sprache angepasst wird.
- Stärkere Quantifizierung: Fordere den Agenten auf, bei der STAR-Methode "Worst-Case-Szenarien" zu hypothetisieren, falls keine echten Zahlen vorliegen (z. B. "Reduzierung der Fehlerrate um X%"), damit du diese Platzhalter nur noch mit echten Daten füllen musst.
- Skill-Cluster: Weise den Agenten an, Skills nicht nur aufzulisten, sondern in "Expert", "Advanced" und "Familiar" zu kategorisieren, basierend auf der Häufigkeit der Nennung in deinen Projekten.

3. Optimierung des Anschreiben-Prompts (cover_letter_prompt.txt)

- Psychologische Trigger: Nutze Frameworks wie die AIDA-Formel (Attention, Interest, Desire, Action) oder das PAS-Modell (Problem, Agitation, Solution), um die Überzeugungskraft zu erhöhen.
- Tonalität-Profile: Definiere verschiedene Stile (z. B. "Startup-Locker", "Corporate-Professional", "Technisch-Fokussiert"), die je nach Unternehmensgröße und Branche gewählt werden können.
- Pain Point Hypothese: Weise den Agenten an, basierend auf der Teamgröße (z. B. "25 Mitarbeiter") spezifische Herausforderungen zu vermuten (z. B. "Generalist gesucht", "Skalierungsschmerzen"), und sich direkt als Lösung für diese zu positionieren.

4. Optimierung des Job-Search-Prompts (find_jobs_prompt.txt)

- Granulares Scoring: Verfeinere das Match-Score-System. Statt einer Gesamtzahl könnte eine Aufschlüsselung erfolgen (z. B. Tech-Stack: 5/5, Standort/Remote: 3/3, Gehalt: 2/2).
- Negativ-Filter: Ergänze explizite Ausschlusskriterien (z. B. "Keine Agenturen", "Kein PHP < 8.0", "Keine Jobs mit < 30 Tagen Urlaub"), um Rauschen in den Ergebnissen zu minimieren.
- Wettbewerbs-Analyse: Bitte den Agenten zu schätzen, wie hoch die Konkurrenz für diesen spezifischen Job basierend auf den Anforderungen ist.
