# File: build_paper_part3_multilingual.py
# Version: 1.3.1 | Release Date: 2026-11-17
# EN: Generates complete German and Russian Part III IMRaD manuscripts and exports them to Zenodo PDF preprints.
# DE: Erzeugt vollständige deutsche und russische IMRaD-Manuskripte (Teil III) und exportiert sie als PDF-Preprints.

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from export_preprint_pdf import convert_markdown_to_html, find_headless_browser


PAPER_DE = r'''<!-- File: docs/paper_part3_imrad_de.md -->
<!-- Version: 1.3.1 | Release Date: 2026-11-17 -->

# Temporale Ereignisgraphen und longitudinale episodische Gedächtnisse in zweistufigen neuro-symbolischen Agenten: Quellenübergreifende Entitätsauflösung und proaktive Multi-Horizont-Orchestrierung

* **English:** *Temporal Event Graphs and Longitudinal Episodic Memory in Dual-Tier Neuro-Symbolic Agents: Cross-Source Entity Resolution and Proactive Multi-Horizon Orchestration*
* **Русский:** *Темпоральные графы событий и продольная эпизодическая память в двухуровневых нейросимволических агентах: кросс-источниковая резолюция сущностей и проактивная многогоризонтная оркестрация*

**Autor:** Oleh Riabtsev  
**Institution:** Universität Vechta, Referat Forschung, Nachwuchsförderung und Transfer (RFNT), Vechta, Deutschland  
**ORCID:** 0009-0003-7848-6418  
**Datum:** 17. November 2026  
**Framework-Version:** PyCognition v1.3.0  
**Zugehöriges Software-Artefakt:** Grant Harvester v2.2.0 (`DOI: 10.5281/zenodo.24106395`)  
**Repository:** [https://github.com/MasterUaKi/pycognition](https://github.com/MasterUaKi/pycognition)  
**Lizenz:** Creative Commons Attribution 4.0 International (CC-BY-4.0)

---

## Zusammenfassung (Abstract)

Zweistufige neuro-symbolische Agenten erreichen eine hohe Laufzeiteffizienz und strukturelle Resilienz, indem sie deterministische prozedurale Fähigkeiten (**System 1**) mit deliberativer Reflexion durch Große Sprachmodelle (**System 2**) kombinieren. Im kontinuierlichen Betrieb über wiederkehrende Beobachtungszyklen in offenen Web-Umgebungen bleiben bestehende Architekturen jedoch **zustandslos über die Zeit und isoliert über verschiedene Quellen hinweg**: Jeder Crawl-Zyklus erzeugt eine unabhängige Momentaufnahme, die über fragile `(title, URI)`-Hashes indiziert wird. Infolgedessen fragmentieren mehrsprachige Übersetzungen, portalübergreifende Syndizierungen und URI-Migrationen identische reale Entitäten in Duplikatdatensätze, während longitudinale Zustandsübergänge — wie Fristverlängerungen, Ausschreibungsenden und saisonale Wiedereröffnungen — unerkannt bleiben.

In diesem Beitrag stellen wir **PyCognition v1.3.0** vor und erweitern unseren neuro-symbolischen Orchestrierungskern um einen **Bitemporalen Ereignisgraphen** (`TemporalEventGraph`), einen **Zweistufigen Neuro-Symbolischen Entitätsauflöser** (`NeuroSymbolicEntityResolver`) mit persistenter Alias-Kristallisation (`AliasMemoryStore`) sowie einen **Proaktiven Multi-Horizont-Aktionsplaner** (`ProactiveHorizonPlanner`). Grenzwertige Kandidatenpaare innerhalb einer lexikalisch-strukturellen Grauzone $[0.42, 0.90)$ werden einmalig durch System 2 entschieden und dauerhaft als positive Alias-Zuordnungen oder negative Ausschlusspaare kristallisiert, wodurch die Inferenzkosten wiederkehrender Entitätsauflösungen auf null sinken. Wir evaluieren PyCognition v1.3.0 auf dem neu eingeführten longitudinalen Benchmark **ChronoDrift-Entity-60** (60 Episoden über 6 zeitliche Schnappschüsse, 360 Ereignisse) sowie auf einem produktiven Multi-Portal-Fördermittelverzeichnis mit 1.230 Datensätzen (*Grant Harvester*). Die experimentellen Ergebnisse belegen einen paarweisen **$F_1$-Wert von 1,000 bei der Entitätsauflösung**, einen **Recall von 1,000 bei Lebenszyklusübergängen und Aktionsplanung**, eine **Reduktion der System-2-Auflösungsaufrufe um 81,5 %** auf dem Benchmark (10 gegenüber 54 Aufrufen) sowie eine **31,1-fache Beschleunigung der Gesamtlaufzeit** (von 674,7 s auf 21,7 s) bei **null System-2-LLM-Aufrufen** in warmen Synchronisationszyklen über 958 konsolidierte kanonische Entitäten.

**Schlüsselwörter:** Neuro-Symbolische KI, Bitemporale Ereignisgraphen, Entitätsauflösung, Episodisches Gedächtnis, Multi-Horizont-Planung, Selbstheilende Agenten, PyCognition.

---

## 1. Einleitung

Autonome Informationsagenten, die für ein kontinuierliches Domänen-Monitoring eingesetzt werden — etwa im Bereich der akademischen Forschungsförderung, der regulatorischen Überwachung oder der Synchronisation wissenschaftlicher Repositorien —, müssen nicht nur statische Webseiten verarbeiten, sondern **sich über die Zeit entwickelnde reale Entitäten** modellieren [1, 2]. In den vorangegangenen Phasen des Forschungsprogramms **PyCognition** (`v1.0.0` und `v1.2.0`) [12] haben wir zwei grundlegende Engpässe kognitiver Zwei-Prozess-Architekturen [3] gelöst:

1. **Berechnungsamortisation (Teil I, `v1.0.0`):** Kompilierung wiederkehrender algorithmischer Intentionen aus System-2-Inferenz in deterministische System-1-Python-Subroutinen im Sub-Millisekundenbereich mit einer marginalen Beschleunigung um den Faktor $11.326,7\times$.
2. **Strukturelle Resilienz (Teil II, `v1.2.0`):** Ablösung datenbasierter *toxischer Mikro-Kompensation* durch telemetriegesteuertes, AST-geprüftes Skill-Refactoring (`TelemetryEvaluator`, `SkillCapability`, `SkillCrystallizer`), wodurch Datenbankvergiftungen eliminiert und LLM-Aufrufe auf dem Benchmark `WebDrift-Fault-50` um 94,0 % reduziert wurden.

### 1.1 Grenzen zustandsloser Momentaufnahmen

Selbst mit selbstheilenden System-1-Skills leiden Agenten, die jeden Crawl-Zyklus über kryptografische Hashes von `(title, URI)` persistieren, im Langzeitbetrieb unter drei strukturellen Defiziten:

1. **Quellen- und sprachübergreifende Fragmentierung:** Deutsche und europäische Förderorganisationen veröffentlichen identische Ausschreibungen regelmäßig parallel auf Deutsch und Englisch unter unterschiedlichen Pfaden (z. B. *«Karl Schmidt-Rottluff Stipendium»* vs. *«Karl Schmidt-Rottluff Scholarship»*) oder syndizieren Programme sowohl auf eigenen Portalen als auch im EU Funding & Tenders Portal. Eine hashbasierte Deduplizierung spaltet dieselbe reale Entität in unverbundene Einzeleinträge auf.
2. **Blindheit gegenüber longitudinalen Zustandsänderungen:** Das Überschreiben von Datenbankzeilen in Folgezyklen löscht die zeitliche Historie. Wenn ein Fördergeber eine Einreichungsfrist verlängert (`DEADLINE_EXTENDED`), eine Ausschreibung schließt (`STATUS_EXPIRED`) oder eine saisonale Förderlinie erneut öffnet (`STATUS_REOPENED`), erzeugt eine zustandslose Datenhaltung keine strukturierten Übergangsereignisse.
3. **Reaktive statt proaktiver Ausführung:** Ohne explizite Zustandsübergänge müssen nachgelagerte Workflows (z. B. Übernahme in Forschungsinformationssysteme, Benachrichtigung von Forschenden oder gezielte Verifikations-Crawls) Rohtabellen abfragen, anstatt auf priorisierte Zeithorizont-Trigger zu reagieren.

### 1.2 Beiträge dieser Arbeit

Um neuro-symbolische Agenten mit einem longitudinalen episodischen Gedächtnis und proaktiver Handlungsfähigkeit auszustatten, führt PyCognition v1.3.0 vier Kernbeiträge ein:

1. **Bitemporaler Ereignisgraph (`TemporalEventGraph`):** Ein SQLite-gestützter Graph, der die reale Gültigkeitszeit (`valid_time`) von der Systemerfassungszeit (`transaction_time`) trennt und Entitäten als konsolidierte `EntityNode`-Instanzen modelliert, die über unveränderliche `StateTransitionEdge`-Deltas verknüpft sind.
2. **Zweistufige Neuro-Symbolische Entitätsauflösung (`NeuroSymbolicEntityResolver`):** Ein hybrider Matcher, der Token-Jaccard-, Zeichen-Bigramm-Dice-Ähnlichkeit und großgeschriebene institutionelle Akronym-Anker (`System 1`) mit einer einmaligen semantischen Arbitrierung durch `System 2` innerhalb einer kalibrierten Grauzone $[0.42, 0.90)$ verbindet und Entscheidungen dauerhaft im `AliasMemoryStore` kristallisiert.
3. **Proaktiver Multi-Horizont-Planer (`ProactiveHorizonPlanner`):** Ein regelbasierter Scheduler, der Graph-Übergänge in deduplizierte Aktionen über unmittelbare (`H1`, 0–24 Std.), taktische (`H2`, 1–14 Tage) und strategische (`H3`, 14+ Tage) Horizonte überführt.
4. **Offener Benchmark (`ChronoDrift-Entity-60`) & Produktivevaluation:** Empirische Evaluierung über 60 longitudinale Szenarien sowie auf einem realen Verzeichnis mit 1.230 Datensätzen (*Grant Harvester v2.2.0* [13]).

---

## 2. Verwandte Arbeiten

### 2.1 Episodisches Gedächtnis und temporale Wissensgraphen in LLM-Agenten

Langzeitgedächtnis-Architekturen für autonome Agenten — wie Generative Agents [4], MemGPT [5] und Zep [6] — verdeutlichen die Notwendigkeit, historische Beobachtungen jenseits flacher Kontextfenster strukturiert zu speichern. Temporale Wissensgraphen (TKGs) formalisieren sich verändernde Fakten als Quadrupel $(s, r, o, t)$ [7], während bitemporale Datenmodelle [8] zwischen dem Eintrittszeitpunkt eines Ereignisses in der realen Welt (`valid_time`) und dem Zeitpunkt der Systemerfassung (`transaction_time`) unterscheiden. PyCognition v1.3.0 adaptiert bitemporale Ereignismodellierung gezielt für Zwei-Prozess-Agenten: Anstatt für jeden historischen Zustand eine LLM-Zusammenfassung zu generieren, berechnen deterministische Übergangsregeln feldgenaue Deltas im Sub-Millisekundenbereich und delegieren ausschließlich mehrdeutige quellenübergreifende Identitätsfragen an System 2.

### 2.2 Neuro-Symbolische Entitätsauflösung

Entity Resolution (ER) basiert auf der probabilistischen Record-Linkage-Theorie [9] und kombiniert klassischerweise Blocking-Keys mit paarweisen Ähnlichkeitsmaßen oder feinjustierten Cross-Encodern [10]. Neuere LLM-basierte ER-Ansätze (z. B. Narayan et al. [11]) erzielen eine hohe Zero-Shot-Genauigkeit bei mehrsprachigen und verrauschten Textpaaren, verursachen jedoch bei wiederkehrenden Batch-Läufen $O(N^2)$ bzw. $O(N \cdot B)$ API-Aufrufe. Durch die Kopplung deterministischer Blocking-Anker (`_extract_acronyms`) mit einem persistenten Positiv-/Negativ-Entscheidungscache (`AliasMemoryStore`) amortisiert PyCognition semantische System-2-Urteile auf strikt **einen einzigen Aufruf pro neuem Alias-Paar** über die gesamte Betriebslebensdauer des Systems.

---

## 3. Methodik und Architektur (`pycognition.temporal`)

PyCognition v1.3.0 kapselt das longitudinale Gedächtnis und die Horizontplanung im Paket `src/pycognition/temporal/` über drei kohäsive Module: `graph.py`, `resolver.py` und `planner.py`.

```text
  [Erfasste Beobachtung o_t = (title, uri, deadline, attrs)]
                              |
                              v
  +-----------------------------------------------------------+
  | 1. NeuroSymbolicEntityResolver (temporal/resolver.py)     |
  |   • Tier 0: AliasMemoryStore-Lookup -> CACHE_HIT (0 LLM)  |
  |   • Tier 1: Lexikalischer + Akronym-Anker-Score s         |
  |       - s >= 0.90 -> SYSTEM1_LEXICAL (0 LLM)              |
  |       - s <  0.42 -> SYSTEM1_DISTINCT (0 LLM)             |
  |   • Tier 2: 0.42 <= s < 0.90 -> System-2-Semantik-Arbiter |
  |       - Kristallisiert positiven Alias oder Negativpaar   |
  +---------------------------+-------------------------------+
                              | canonical_id
                              v
  +-----------------------------------------------------------+
  | 2. TemporalEventGraph (temporal/graph.py)                 |
  |   • Биtemporales Tracking (valid_time, transaction_time)  |
  |   • Erzeugt StateTransitionEdge: CREATED, ALIAS_MERGED,   |
  |     DEADLINE_EXTENDED, STATUS_EXPIRING_SOON,              |
  |     STATUS_EXPIRED, STATUS_REOPENED                       |
  +---------------------------+-------------------------------+
                              | list[StateTransitionEdge]
                              v
  +-----------------------------------------------------------+
  | 3. ProactiveHorizonPlanner (temporal/planner.py)          |
  |   • H1_IMMEDIATE (0–24h): Dringende Frist-/Reopen-Alarme  |
  |   • H2_TACTICAL (1–14d): Metadaten-Konsolidierung & Sync  |
  |   • H3_STRATEGIC (14+d): Archivierung & System-Export     |
  +-----------------------------------------------------------+
```

### 3.1 Zweistufige Entitätsauflösung mit Alias-Kristallisation

Für eine eingehende Beobachtung $o_t$ mit Titel $T_a$, Frist $D_a$ und Förderorganisation $F_a$ normalisiert `NeuroSymbolicEntityResolver` zunächst $T_a$ mittels Unicode-NFKD-Diakritikbereinigung und Stoppwort-Filterung zu einer kanonischen Signatur $\sigma(T_a)$.

1. **Tier 0 — Kristallisierter Alias-Cache (`CACHE_HIT`):** Existiert $\sigma(T_a)$ bereits im `AliasMemoryStore`, wird die gespeicherte `canonical_id` sofort per $O(1)$-SQLite-Abfrage ohne LLM-Tokens zurückgegeben.
2. **Tier 1 — Hybrider lexikalischer und institutioneller Blocking-Score:** Für nicht gecachte Titel berechnet System 1 die Ähnlichkeit zu bestehenden Knoten-Aliasen $T_b$:
   $$S(a, b) = \min\Big(1.0,\; 0.55 \cdot J(W_a, W_b) + 0.45 \cdot \mathrm{Dice}(B_a, B_b) + \beta_{\mathrm{inst}}(a, b) + \beta_{\mathrm{dl}}(a, b)\Big)$$
   wobei $J$ die Token-Jaccard-Ähnlichkeit, $\mathrm{Dice}$ die Zeichen-Bigramm-Ähnlichkeit, $\beta_{\mathrm{inst}} = 0.14$ bei übereinstimmenden großgeschriebenen institutionellen Akronymen ($\ge 3$ Zeichen, z. B. `DFG`, `ERC`, `DAAD`, `BMBF`) oder normalisierten Förderernamen und $\beta_{\mathrm{dl}} = 0.08$ bei identischen ISO-8601-Fristdaten bezeichnet. Paare mit $S \ge 0.90$ werden deterministisch zusammengeführt (`SYSTEM1_LEXICAL`), während Paare mit $S < 0.42$ als eigenständige Entitäten registriert werden (`SYSTEM1_DISTINCT`).
3. **Tier 2 — Grauzonen-Arbitrierung durch System 2 (`SYSTEM2_SEMANTIC`):** Ausschließlich Kandidatenpaare mit $0.42 \le S(a, b) < 0.90$ (sofern nicht bereits in `negative_pairs` hinterlegt) werden an `semantic_arbiter` übergeben. Positive Entscheidungen verknüpfen $\sigma(T_a) \mapsto \mathrm{id}_{\mathrm{can}}$ (gespeichert als `canonical_id` in `alias_mappings`); negative Urteile persistieren $(\sigma(T_a), \sigma(T_b))$ in `negative_pairs`, sodass unterschiedliche Förderlinien derselben Organisation (z. B. *ERC Starting Grant* vs. *ERC Synergy Grant*) nie erneut angefragt werden.

### 3.2 Bitemporaler Ereignisgraph und Lebenszyklus-Zustandsautomat

`TemporalEventGraph` modelliert jede konsolidierte reale Entität als `EntityNode` in einem von acht kanonischen Zuständen: `NEW`, `ACTIVE`, `UPDATED`, `DEADLINE_EXTENDED`, `EXPIRING_SOON`, `EXPIRED`, `REOPENED` oder `ARCHIVED`.

Bei der Verarbeitung einer `EntityObservation(canonical_id, source_id, raw_uri, title, attributes, deadline_iso, valid_time, transaction_time)` berechnet der Graph feldgenaue Deltas und erzeugt eine unveränderliche Kante `StateTransitionEdge`:

* **Wiedereröffnung (`STATUS_REOPENED`):** Wird ausgelöst, wenn ein Knoten im Zustand `EXPIRED` oder `ARCHIVED` erneut mit einer in der Zukunft liegenden Frist ($D_{\mathrm{new}} > t_{\mathrm{valid}}$) beobachtet wird.
* **Fristverschiebungen (`DEADLINE_EXTENDED` / `DEADLINE_SHORTENED`):** Wird ausgelöst, wenn $D_{\mathrm{new}} > D_{\mathrm{old}}$ bzw. $D_{\mathrm{new}} < D_{\mathrm{old}}$ gilt.
* **Horizont-Schwellenwerte (`STATUS_EXPIRING_SOON` / `STATUS_EXPIRED`):** Wird entweder während der Erfassung oder autonom über `sweep_temporal_horizons(reference_time, expiring_window_days=14)` ausgelöst, sobald $0 \le D - t_{\mathrm{ref}} \le 14\;\mathrm{Tage}$ oder $D < t_{\mathrm{ref}}$ eintritt.
* **Quellenübergreifende Konsolidierung (`ALIAS_MERGED`):** Wird ausgelöst, wenn ein neu aufgelöster Alias oder eine sekundäre Portal-URI einem bestehenden kanonischen Knoten zugeordnet wird.

### 3.3 Proaktive Multi-Horizont-Aktionsplanung

`ProactiveHorizonPlanner` ordnet erzeugte `StateTransitionEdge`-Ereignisse deklarativen `TriggerPolicy`-Regeln über drei zeitliche Horizonte hinweg zu:

* **`H1_IMMEDIATE` (Kritisch/Hoch):** `STATUS_EXPIRING_SOON` $\to$ `DISPATCH_URGENT_ALERT`; `STATUS_REOPENED` $\to$ `DISPATCH_REOPENED_NOTICE`.
* **`H2_TACTICAL` (Hoch/Mittel):** `DEADLINE_EXTENDED` $\to$ `UPDATE_DEADLINE_RECORD`; `ALIAS_MERGED` $\to$ `CONSOLIDATE_CROSS_SOURCE_METADATA`; `CREATED` $\to$ `ENRICH_AND_INDEX_ENTITY`.
* **`H3_STRATEGIC` (Niedrig):** `STATUS_EXPIRED` $\to$ `ARCHIVE_EXPIRED_ENTITY`.

Entitätsspezifische Cooldown-Fenster (`cooldown_hours`) verhindern Benachrichtigungsstürme bei häufigen Abfragezyklen.

---

## 4. Experimentelle Evaluierung

### 4.1 Kontrollierter Longitudinal-Benchmark: `ChronoDrift-Entity-60`

Zur Evaluierung der longitudinalen Entitätsauflösung und Lebenszyklusverfolgung unter reproduzierbarer Zeitdynamik haben wir **ChronoDrift-Entity-60** (`benchmarks/chronodrift_entity_60.json`) entwickelt. Der Datensatz umfasst **60 quellenübergreifende Episoden** über **6 wöchentliche Zeitpunkte** ($t_1 \dots t_6$, insgesamt **360 Beobachtungsereignisse**), gleichmäßig aufgeteilt in sechs Szenarioklassen (jeweils 10 Episoden):

* **Klasse A (`A_CROSS_LINGUAL_ALIAS`, E01–E10):** Alternierende deutsche und englische Versionen identischer Förderprogramme von DFG, BMBF und DAAD.
* **Klasse B (`B_URI_MIGRATION_SYNDICATION`, E11–E20):** Portalübergreifende Syndizierung zwischen `erc.europa.eu` und `ec.europa.eu` inklusive einer URL-Migration zum Zeitpunkt $t_4$.
* **Klasse C (`C_DEADLINE_SHIFT`, E21–E30):** Sequenzielle Fristverlängerungen zu den Zeitpunkten $t_3$ und $t_5$.
* **Klasse D (`D_EXPIRATION_REOPENING`, E31–E40):** Fristablauf bei $t_3$ с последующей saisonaler Wiedereröffnung der Förderlinie bei $t_5$.
* **Klasse E (`E_URGENT_HORIZON_SWEEP`, E41–E50):** Eintritt in das 14-tägige kritische Zeitfenster bei $t_4$ und Ablauf bei $t_6$.
* **Klasse F (`F_HARD_NEGATIVE_HOMONYMS`, E51–E60):** Unterschiedliche Förderlinien derselben Organisation mit identischen Akronymen und Fristen (Test auf Resistenz gegen falsch-positive Zusammenführungen).

Wir haben vier Architekturen über alle 360 temporalen Beobachtungen verglichen:

1. **B1 (`Stateless_Hash`):** SHA-256-Deduplizierung über `(title, raw_uri)`.
2. **B2 (`Naive_Lexical`):** Deterministischer Ähnlichkeitsschwellenwert ($\ge 0.90$) ohne System-2-Arbitrierung und ohne Lebenszyklus-Tracking.
3. **B3 (`Uncached_LLM_ER`):** Paarweise LLM-Arbitrierung für Grauzonen-Kandidaten ohne persistenten Alias-Cache und ohne Horizontplanung.
4. **Unsere Architektur (`PyCognition_v1.3`):** Полная Integration aus `NeuroSymbolicEntityResolver` + `AliasMemoryStore` + `TemporalEventGraph` + `ProactiveHorizonPlanner`.

| Architektur | ER Precision | ER Recall | ER $F_1$ | Transition Recall | Action Recall | LLM-Aufrufe gesamt |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **B1: Stateless Hash (`title\|url`)** | 1,000 | 0,741 | 0,851 | 0,000 | 0,000 | 0 |
| **B2: Naive Lexical Only** | 1,000 | 0,889 | 0,941 | 0,000 | 0,000 | 0 |
| **B3: Uncached LLM ER** | 1,000 | 1,000 | 1,000 | 0,000 | 0,000 | 54 |
| **Unsere: PyCognition v1.3.0** | **1,000** | **1,000** | **1,000** | **1,000** | **1,000** | **10** |

**Zentrale Ergebnisse:**

* **Fehlerfreie quellenübergreifende Clusterbildung ohne Falsch-Fusionen:** PyCognition v1.3.0 erreichte **ER Precision = 1,000, ER Recall = 1,000, ER $F_1$ = 1,000**, führte sämtliche DE/EN-Paare (Klasse A) und migrierten URIs (Klasse B) zusammen und hielt alle 10 Hard-Negative-Homonympaare (Klasse F) strikt getrennt.
* **81,5 % Amortisation der System-2-Aufrufe zur Entitätsauflösung:** Gegenüber der ungecachten paarweisen LLM-Arbitrierung (`B3`, 54 Aufrufe) reduzierte der `AliasMemoryStore` die System-2-Aufrufe auf **10 Aufrufe** (strikt 1 Aufruf pro neuem zweisprachigem Paar in Klasse A; 0 Aufrufe in den Zyklen $t_3 \dots t_6$).
* **100 % Recall bei Lebenszyklusübergängen und Aktionsplanung:** Jede Fristverlängerung, Schließung, Wiedereröffnung und Schwellenwertüberschreitung wurde erfasst (`Transition Recall = 1,000`) und in die entsprechende Horizont-Aktion überführt (`Action Recall = 1,000`).

### 4.2 Produktiv-Fallstudie: *Grant Harvester v2.2.0* (1.230 Live-Portaldatensätze)

Wir haben `pycognition.temporal` in **Grant Harvester v2.2.0** [13] integriert und eine zweistufige Synchronisation по der produktiven 24-Portale-SQLite-Datenbank (`grants_vault.db`, **1.230 aktive Datensätze**) durchgeführt:

| Metrik | Kalter Synchronisationslauf (Lauf 1) | Warmer Synchronisationslauf (Lauf 2) | Verbesserung / Дельта |
| :--- | :---: | :---: | :---: |
| **Evaluierte Rohdatensätze im Vault** | 1.230 | 1.230 | Vollständige Abdeckung |
| **Konsolidierte kanonische Entitäten** | **958** | **958** | **-272 Duplikate (-22,1 % Redundanz)** |
| **System-2-ER-LLM-Aufrufe (`deepseek-chat`)** | 37 | **0** | **-100,0 % LLM-Tokenverbrauch** |
| **Gesamte Ausführungszeit (Wall-Clock)** | 674,7 s | **21,7 s** | **31,1x schneller (-96,8 % Latenz)** |

Während des ersten (kalten) Durchlaufs führte System 2 zweisprachige deutsch-englische Stipendienpaare präzise zusammen (z. B. *«Karl Schmidt-Rottluff Stipendium»* $\leftrightarrow$ *«Karl Schmidt-Rottluff Scholarship»*, *«Logo der Stiftung»* $\leftrightarrow$ *«Logo of the Foundation»*) sowie portalübergreifende Ausschreibungen (*«ERC Proof of Concept»* $\leftrightarrow$ *«Call for proposals for ERC Proof of Concept»*), während Hunderte eigenständiger Programm- und Personaleinträge derselben Institutionen korrekt getrennt blieben. Im anschließenden warmen Durchlauf löste der `AliasMemoryStore` alle 1.230 Datensätze in **21,7 Sekunden** bei **null LLM-Aufrufen** in die 958 kanonischen Entitäten auf.

---

## 5. Diskussion, Limitationen und Fazit

### 5.1 Vereinheitlichte dreistufige kognitive Amortisation

Über die Teile I bis III des PyCognition-Frameworks hinweg zeigt sich ein durchgängiges Architekturprinzip: **System-2-Inferenz darf niemals für wiederkehrende Ausführungspfade, wiederkehrende Selektorfehler oder wiederkehrende Entitätsvergleiche aufgewendet werden.** Durch die Kristallisation algorithmischer Pläne в prozedurale Skills (Teil I), von Selektorreparaturen in AST-geprüfte Module (Teil II) und von semantischen Äquivalenzurteilen in bitemporale Alias-Caches (Teil III) konvergieren die marginalen Inferenzkosten eines kontinuierlich arbeitenden neuro-symbolischen Agenten asymptotisch gegen null.

### 5.2 Limitationen

1. **Rauschpropagation aus der vorgelagerten Extraktion:** Как im Produktivexperiment beobachtet (wo vereinzelt Verzeichnislinks von Stiftungsmitarbeitenden in den Roh-Vault gelangten), arbeitet die Entitätsauflösung nachgelagert zur System-1-Extraktion. Eine Rückkopplung vom `ProactiveHorizonPlanner` an den `TelemetryEvaluator` zur Bereinigung verrauschter Unterpfade bildet einen vielversprechenden Ansatz für eine geschlossene Crawl-Optimierung.
2. **Transitive Cluster-Zusammenführung:** Während der `AliasMemoryStore` paarweise Äquivalenz- und Nicht-Äquivalenzentscheidungen speichert, erfordern mehrstufige transitive Alias-Ketten ($A \sim B$ und $B \sim C$) eine periodische Zusammenhangskomponenten-Bereinigung bei widersprüchlichen Negativbedingungen.

### 5.3 Fazit

Wir haben **PyCognition v1.3.0** vorgestellt und damit eine dreistufige neuro-symbolische Architektur vervollständigt, die prozedurale Fähigkeiten erlernt, strukturellen Extraktionsdrift selbstständig repariert und longitudinal über sich entwickelnde quellenübergreifende Entitäten schließt. Validiert auf `ChronoDrift-Entity-60` sowie im produktiven Monitoring von 24 академических Förderportalen eliminieren bitemporale Ereignisgraphen in Verbindung mit kristallisiertem Alias-Gedächtnis Duplikatfragmentierung und senken die wiederkehrenden Inferenzkosten der Entitätsauflösung auf null.

---

## Daten- und Code-Verfügbarkeit

Sämtlicher Quellcode, Benchmark-Generatoren, Datensätze und Reproduktionsskripte sind unter offenen Lizenzen öffentlich zugänglich:

* **PyCognition-Framework (`v1.3.0`, LGPL-3.0-or-later):** [https://github.com/MasterUaKi/pycognition](https://github.com/MasterUaKi/pycognition)
* **ChronoDrift-Entity-60 Datensatz & Evaluation:** `benchmarks/chronodrift_entity_60.json`, `benchmarks/generate_chronodrift_60.py` und `benchmarks/run_temporal_benchmark.py` im PyCognition-Repository.
* **Grant-Harvester-Produktivarchiv:** [https://doi.org/10.5281/zenodo.24106395](https://doi.org/10.5281/zenodo.24106395)

---

## Literaturverzeichnis

[1] S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao, "ReAct: Synergizing Reasoning and Acting in Language Models," in *Proc. 11th Int. Conf. Learning Representations (ICLR)*, Kigali, Rwanda, May 2023. Available: [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)

[2] G. Wang, Y. Xie, Y. Jiang, A. Mandlekar, C. Xiao, Y. Zhu, L. Fan, and A. Anandkumar, "Voyager: An Open-Ended Embodied Agent with Large Language Models," *Transactions on Machine Learning Research (TMLR)*, 2024. Available: [https://arxiv.org/abs/2305.16291](https://arxiv.org/abs/2305.16291)

[3] D. Kahneman, *Thinking, Fast and Slow*. New York, NY, USA: Farrar, Straus and Giroux, 2011.

[4] J. S. Park, J. O'Brien, C. J. Cai, M. R. Morris, P. Liang, and M. S. Bernstein, "Generative Agents: Interactive Simulacra of Human Behavior," in *Proc. 36th Annual ACM Symp. User Interface Software and Technology (UIST)*, San Francisco, CA, USA, Oct. 2023, Art. no. 2, pp. 1–22. doi: [10.1145/3586183.3606763](https://doi.org/10.1145/3586183.3606763).

[5] C. Packer, S. Wooders, K. Lin, V. Fang, S. G. Patil, I. Stoica, and J. E. Gonzalez, "MemGPT: Towards LLMs as Operating Systems," *arXiv preprint arXiv:2310.08560*, Oct. 2023. Available: [https://arxiv.org/abs/2310.08560](https://arxiv.org/abs/2310.08560)

[6] P. Rasmussen, P. Paliychuk, T. Beauvais, J. Ryan, and D. Chalef, "Zep: A Temporal Knowledge Graph Architecture for Agent Memory," *arXiv preprint arXiv:2501.13956*, Jan. 2025. Available: [https://arxiv.org/abs/2501.13956](https://arxiv.org/abs/2501.13956)

[7] B. Cai, Y. Xiang, L. Gao, H. Zhang, Y. Li, and J. Li, "Temporal Knowledge Graph Completion: A Survey," in *Proc. 32nd Int. Joint Conf. Artificial Intelligence (IJCAI)*, Macao, SAR, China, Aug. 2023, pp. 6545–6553. doi: [10.24963/ijcai.2023/734](https://doi.org/10.24963/ijcai.2023/734).

[8] R. T. Snodgrass and I. Ahn, "Temporal Databases," *IEEE Computer*, vol. 19, no. 9, pp. 35–42, Sep. 1986. doi: [10.1109/MC.1986.1663327](https://doi.org/10.1109/MC.1986.1663327).

[9] I. P. Fellegi and A. B. Sunter, "A Theory for Record Linkage," *Journal of the American Statistical Association*, vol. 64, no. 328, pp. 1183–1210, Dec. 1969. doi: [10.1080/01621459.1969.10501049](https://doi.org/10.1080/01621459.1969.10501049).

[10] Y. Li, J. Li, Y. Suhara, A. Doan, and W.-C. Tan, "Deep Entity Matching with Pre-Trained Language Models," *Proceedings of the VLDB Endowment*, vol. 14, no. 1, pp. 50–60, Sep. 2020. doi: [10.14778/3421424.3421431](https://doi.org/10.14778/3421424.3421431).

[11] A. Narayan, I. Chami, L. Orr, and C. Ré, "Can Foundation Models Wrangle Your Data?," *Proceedings of the VLDB Endowment*, vol. 16, no. 4, pp. 738–746, Dec. 2022. doi: [10.14778/3574245.3574258](https://doi.org/10.14778/3574245.3574258).

[12] O. Riabtsev, "PyCognition: Dual-Tier Neuro-Symbolic Cognitive Orchestration Framework with Telemetry-Driven Skill Refactoring and Bitemporal Event Graphs (v1.0.0–v1.3.0)," *GitHub Software Repository*, Nov. 2026. Available: [https://github.com/MasterUaKi/pycognition](https://github.com/MasterUaKi/pycognition)

[13] O. Riabtsev, "Grant Harvester: Autonomous Academic Funding Monitoring Framework with Cognitive Multi-Tier Reflection," *Zenodo Software Archive*, Nov. 2026. doi: [10.5281/zenodo.24106395](https://doi.org/10.5281/zenodo.24106395).
'''


PAPER_RU = r'''<!-- File: docs/paper_part3_imrad_ru.md -->
<!-- Version: 1.3.1 | Release Date: 2026-11-17 -->

# Темпоральные графы событий и продольная эпизодическая память в двухуровневых нейросимволических агентах: кросс-источниковая резолюция сущностей и проактивная многогоризонтная оркестрация

* **English:** *Temporal Event Graphs and Longitudinal Episodic Memory in Dual-Tier Neuro-Symbolic Agents: Cross-Source Entity Resolution and Proactive Multi-Horizon Orchestration*
* **Deutsch:** *Temporale Ereignisgraphen und longitudinale episodische Gedächtnisse in zweistufigen neuro-symbolischen Agenten: Quellenübergreifende Entitätsauflösung und proaktive Multi-Horizont-Orchestrierung*

**Автор:** Олег Рябцев (Oleh Riabtsev)  
**Аффилиация:** Университет Фехты, Отдел исследований, поддержки молодых учёных и трансфера технологий (Universität Vechta, Referat Forschung, Nachwuchsförderung und Transfer — RFNT), Фехта, Германия  
**ORCID:** 0009-0003-7848-6418  
**Дата:** 17 ноября 2026 г.  
**Версия фреймворка:** PyCognition v1.3.0  
**Связанный программный артефакт:** Grant Harvester v2.2.0 (`DOI: 10.5281/zenodo.24106395`)  
**Репозиторий:** [https://github.com/MasterUaKi/pycognition](https://github.com/MasterUaKi/pycognition)  
**Лицензия:** Creative Commons Attribution 4.0 International (CC-BY-4.0)

---

## Аннотация (Abstract)

Двухуровневые нейросимволические агенты обеспечивают высокую вычислительную эффективность и структурную устойчивость за счёт сочетания детерминированных процедурных навыков (**Система 1**) и делиберативной рефлексии больших языковых моделей (**Система 2**). Однако при непрерывной работе в повторяющихся циклах наблюдения в открытых веб-средах существующие архитектуры остаются **лишёнными темпорального состояния и изолированными между источниками**: каждый цикл обхода формирует независимый снимок, индексируемый хрупкими криптографическими хешами от пары `(title, URI)`. В результате многоязычные переводы, кросс-портальная синдикация и миграция URI фрагментируют идентичные объекты реального мира в дублирующиеся записи, тогда как продольные переходы состояний — продление дедлайнов, закрытие конкурсов и сезонное переоткрытие программ — остаются незамеченными.

В настоящей работе мы представляем **PyCognition v1.3.0** — расширение нашего нейросимволического ядра оркестрации, включающее **Битемпоральный граф событий** (`TemporalEventGraph`), **Двухуровневый нейросимволический резолвер сущностей** (`NeuroSymbolicEntityResolver`) с постоянной кристаллизацией алиасов (`AliasMemoryStore`) и **Проактивный многогоризонтный планировщик действий** (`ProactiveHorizonPlanner`). Пограничные пары кандидатов, попадающие в лексико-структурную «серую зону» $[0.42, 0.90)$, однократно рассматриваются Системой 2 и навсегда кристаллизуются в кэш положительных соответствий или негативных исключений, сводя к нулю стоимость повторной резолюции сущностей. Мы оцениваем PyCognition v1.3.0 на новом продольном бенчмарке **ChronoDrift-Entity-60** (60 эпизодов на 6 временных срезах, 360 событий) и на живом мультипортальном репозитории академического финансирования из 1 230 записей (*Grant Harvester*). Экспериментальные результаты демонстрируют **попарную точность резолюции сущностей $F_1 = 1.000$**, **полноту детекции переходов жизненного цикла и планирования действий $1.000$**, **снижение числа вызовов Системы 2 на 81,5 %** на бенчмарке (10 против 54 вызовов) и **ускорение синхронизации в 31,1 раза** (с 674,7 с до 21,7 с) при **нулевом расходе вызовов LLM Системы 2** в тёплых производственных циклах по 958 консолидированным каноническим сущностям.

**Ключевые слова:** нейросимволический ИИ, битемпоральные графы событий, резолюция сущностей, эпизодическая память, многогоризонтное планирование, самовосстанавливающиеся агенты, PyCognition.

---

## 1. Введение

Автономные интеллектуальные агенты, развёрнутые для непрерывного мониторинга предметных областей — таких как отслеживание грантового финансирования, нормативных изменений и синхронизация научных репозиториев, — должны рассуждать не просто над статическими веб-страницами, а над **эволюционирующими во времени сущностями реального мира** [1, 2]. На предыдущих этапах исследовательской программы **PyCognition** (`v1.0.0` и `v1.2.0`) [12] были решены два фундаментальных узких места двухпроцессных когнитивных архитектур [3]:

1. **Вычислительная амортизация (Часть I, `v1.0.0`):** JIT-компиляция повторяющихся алгоритмических намерений из рассуждений Системы 2 в детерминированные Python-подпрограммы Системы 1 субмиллисекундного уровня с маржинальным ускорением в $11\,326,7\times$.
2. **Структурная устойчивость (Часть II, `v1.2.0`):** Замена *токсичной микрокомпенсации* на уровне отдельных записей телеметрически управляемым рефакторингом навыков с AST-аудитом безопасности (`TelemetryEvaluator`, `SkillCapability`, `SkillCrystallizer`), что устранило загрязнение баз данных и сократило количество вызовов LLM на 94,0 % на бенчмарке `WebDrift-Fault-50`.

### 1.1 Ограничения сбора данных в виде беспамятных снимков

Даже при наличии самовосстанавливающихся навыков Системы 1 агенты, фиксирующие каждый цикл обхода через криптографические хеши от `(title, URI)`, сталкиваются в продольной эксплуатации с тремя структурными патологиями:

1. **Кросс-источниковая и кросс-языковая фрагментация:** Немецкие и европейские научные фонды регулярно публикуют идентичные конкурсы на немецком и английском языках по разным URL-путям (например, *«Karl Schmidt-Rottluff Stipendium»* и *«Karl Schmidt-Rottluff Scholarship»*) либо синдицируют программы одновременно на сайтах агентств и на портале EU Funding & Tenders. Дедупликация по хешу расщепляет единую сущность реального мира на несколько несвязанных записей.
2. **Слепота к продольным изменениям состояния:** Перезапись строк базы данных в последующих циклах стирает темпоральную историю. Когда фонд продлевает срок подачи заявок (`DEADLINE_EXTENDED`), закрывает приём (`STATUS_EXPIRED`) или повторно открывает сезонную программу (`STATUS_REOPENED`), хранилище без темпорального графа не формирует структурированных событий перехода.
3. **Реактивность вместо проактивной оркестрации:** Без явных переходов состояний смежные контуры (например, загрузка в институциональный репозиторий CRIS, оповещение исследователей или точечная верификация порталов) вынуждены опрашивать сырые таблицы вместо реакции на приоритизированные триггеры временных горизонтов.

### 1.2 Вклад работы

Для наделения нейросимволических агентов продольной эпизодической памятью и проактивной агентностью в PyCognition v1.3.0 реализованы четыре ключевых компонента:

1. **Битемпоральный граф событий (`TemporalEventGraph`):** Графовое хранилище на базе SQLite, разделяющее время действительности факта в реальном мире (`valid_time`) и время фиксации в системе (`transaction_time`), представляющее объекты как консолидированные узлы `EntityNode`, связанные неизменяемыми рёбрами переходов `StateTransitionEdge`.
2. **Двухуровневая нейросимволическая резолюция сущностей (`NeuroSymbolicEntityResolver`):** Гибридный алгоритм сопоставления, объединяющий токеновый коэффициент Жаккара, биграммный коэффициент Дайса и блокирующие якоря институциональных акронимов (`Система 1`) с однократной семантической арбитрацией `Системы 2` в калиброванной серой зоне $[0.42, 0.90)$ и постоянной кристаллизацией решений в `AliasMemoryStore`.
3. **Проактивный многогоризонтный планировщик (`ProactiveHorizonPlanner`):** Планировщик на базе декларативных политик, преобразующий переходы графа в дедуплицированные действия по трём временным горизонтам: немедленному (`H1`, 0–24 ч), тактическому (`H2`, 1–14 дней) и стратегическому (`H3`, 14+ дней).
4. **Открытый бенчмарк (`ChronoDrift-Entity-60`) и производственная валидация:** Эмпирическая оценка на 60 продольных сценариях и живом репозитории из 1 230 записей (*Grant Harvester v2.2.0* [13]).

---

## 2. Обзор смежных исследований

### 2.1 Эпизодическая память и темпоральные графы знаний в LLM-агентах

Архитектуры долговременной памяти автономных агентов — такие как Generative Agents [4], MemGPT [5] и Zep [6] — демонстрируют необходимость структурирования исторических наблюдений за пределами плоского контекстного окна. Темпоральные графы знаний (TKG) формализуют изменяющиеся факты в виде четвёрок $(s, r, o, t)$ [7], а битемпоральные модели данных [8] разграничивают момент наступления события во внешней среде (`valid_time`) и момент его регистрации в базе (`transaction_time`). PyCognition v1.3.0 адаптирует битемпоральное моделирование событий специально для двухпроцессных агентов: вместо вызова LLM для пересказа каждого состояния детерминированные правила переходов вычисляют пополевые дельты за доли миллисекунды, передавая Системе 2 исключительно неоднозначные случаи кросс-источниковой идентификации.

### 2.2 Нейросимволическая резолюция сущностей

Резолюция сущностей (Entity Resolution, ER) опирается на вероятностную теорию связывания записей [9] и традиционно сочетает блокирующие ключи с попарной оценкой сходства или дообученными кросс-энкодерами [10]. Современные подходы на базе LLM (например, Narayan et al. [11]) обеспечивают высокую точность без дообучения на мультиязычных и зашумлённых парах, но требуют $O(N^2)$ или $O(N \cdot B)$ обращений к API при повторяющихся пакетных прогонах. Сочетая детерминированные блокирующие якоря (`_extract_acronyms`) с постоянным кэшем положительных и отрицательных вердиктов (`AliasMemoryStore`), PyCognition амортизирует семантические суждения Системы 2 строго до **одного вызова на каждую новую пару алиасов** за весь жизненный цикл системы.

---

## 3. Методология и архитектура (`pycognition.temporal`)

В PyCognition v1.3.0 подсистема продольной памяти и планирования инкапсулирована в пакете `src/pycognition/temporal/` в виде трёх согласованных модулей: `graph.py`, `resolver.py` и `planner.py`.

```text
  [Наблюдение o_t = (title, uri, deadline, attrs)]
                              |
                              v
  +-----------------------------------------------------------+
  | 1. NeuroSymbolicEntityResolver (temporal/resolver.py)     |
  |   • Уровень 0: поиск в AliasMemoryStore -> CACHE_HIT (0)  |
  |   • Уровень 1: лексический + акронимный скор s            |
  |       - s >= 0.90 -> SYSTEM1_LEXICAL (0 вызовов LLM)      |
  |       - s <  0.42 -> SYSTEM1_DISTINCT (0 вызовов LLM)     |
  |   • Уровень 2: 0.42 <= s < 0.90 -> Арбитр Системы 2       |
  |       - Кристаллизация алиаса или негативной пары         |
  +---------------------------+-------------------------------+
                              | canonical_id
                              v
  +-----------------------------------------------------------+
  | 2. TemporalEventGraph (temporal/graph.py)                 |
  |   • Битемпоральный учёт (valid_time, transaction_time)    |
  |   • Рёбра переходов StateTransitionEdge: CREATED,         |
  |     ALIAS_MERGED, DEADLINE_EXTENDED, STATUS_EXPIRING_SOON,|
  |     STATUS_EXPIRED, STATUS_REOPENED                       |
  +---------------------------+-------------------------------+
                              | list[StateTransitionEdge]
                              v
  +-----------------------------------------------------------+
  | 3. ProactiveHorizonPlanner (temporal/planner.py)          |
  |   • H1_IMMEDIATE (0–24ч): срочные дедлайны и открытия     |
  |   • H2_TACTICAL (1–14д): консолидация метаданных и синк   |
  |   • H3_STRATEGIC (14+д): архивация и экспорт в CRIS/DMS   |
  +-----------------------------------------------------------+
```

### 3.1 Двухуровневая резолюция сущностей с кристаллизацией алиасов

Для входящего наблюдения $o_t$ с заголовком $T_a$, сроком подачи $D_a$ и финансирующей организацией $F_a$ модуль `NeuroSymbolicEntityResolver` сначала нормализует $T_a$ с помощью Unicode-NFKD-свёртки диакритических знаков и удаления стоп-слов в каноническую сигнатуру $\sigma(T_a)$.

1. **Уровень 0 — Кристаллизованный кэш алиасов (`CACHE_HIT`):** Если $\sigma(T_a)$ присутствует в `AliasMemoryStore`, сохранённый идентификатор `canonical_id` возвращается немедленно за $O(1)$ через запрос к SQLite без затрат токенов LLM.
2. **Уровень 1 — Гибридная лексическая и институциональная оценка:** Для новых заголовков Система 1 вычисляет сходство с известными алиасами $T_b$ существующих узлов:
   $$S(a, b) = \min\Big(1.0,\; 0.55 \cdot J(W_a, W_b) + 0.45 \cdot \mathrm{Dice}(B_a, B_b) + \beta_{\mathrm{inst}}(a, b) + \beta_{\mathrm{dl}}(a, b)\Big)$$
   где $J$ — коэффициент Жаккара по множествам токенов, $\mathrm{Dice}$ — коэффициент Дайса по символьным биграммам, $\beta_{\mathrm{inst}} = 0.14$ при совпадении институциональных акронимов в верхнем регистре ($\ge 3$ символов, например `DFG`, `ERC`, `DAAD`, `BMBF`) или нормализованных названий фондов, а $\beta_{\mathrm{dl}} = 0.08$ при совпадении даты дедлайна ISO-8601. Пары с $S \ge 0.90$ объединяются детерминированно (`SYSTEM1_LEXICAL`), тогда как пары с $S < 0.42$ регистрируются как самостоятельные сущности (`SYSTEM1_DISTINCT`).
3. **Уровень 2 — Арбитрация серой зоны Системой 2 (`SYSTEM2_SEMANTIC`):** Только пары, удовлетворяющие условию $0.42 \le S(a, b) < 0.90$ (и не зафиксированные ранее в таблице `negative_pairs`), передаются в `semantic_arbiter`. Положительные вердикты связывают $\sigma(T_a) \mapsto \mathrm{id}_{\mathrm{can}}$ (сохраняется как `canonical_id` в `alias_mappings`); отрицательные вердикты фиксируют пару $(\sigma(T_a), \sigma(T_b))$ в `negative_pairs`, благодаря чему различные конкурсные треки одного фонда (например, *ERC Starting Grant* и *ERC Synergy Grant*) никогда не отправляются на повторную проверку.

### 3.2 Битемпоральный граф событий и конечный автомат жизненного цикла

`TemporalEventGraph` представляет каждую консолидированную сущность реального мира в виде узла `EntityNode`, находящегося в одном из восьми канонических состояний: `NEW`, `ACTIVE`, `UPDATED`, `DEADLINE_EXTENDED`, `EXPIRING_SOON`, `EXPIRED`, `REOPENED` или `ARCHIVED`.

При поступлении наблюдения `EntityObservation(canonical_id, source_id, raw_uri, title, attributes, deadline_iso, valid_time, transaction_time)` граф вычисляет пополевые дельты и порождает неизменяемое ребро перехода `StateTransitionEdge`:

* **Повторное открытие (`STATUS_REOPENED`):** Генерируется, когда узел в состоянии `EXPIRED` или `ARCHIVED` повторно наблюдается с будущим сроком подачи ($D_{\mathrm{new}} > t_{\mathrm{valid}}$).
* **Сдвиги сроков подачи (`DEADLINE_EXTENDED` / `DEADLINE_SHORTENED`):** Генерируются при $D_{\mathrm{new}} > D_{\mathrm{old}}$ или $D_{\mathrm{new}} < D_{\mathrm{old}}$.
* **Пороги временных горизонтов (`STATUS_EXPIRING_SOON` / `STATUS_EXPIRED`):** Генерируются либо в момент приёма наблюдения, либо автономно методом `sweep_temporal_horizons(reference_time, expiring_window_days=14)` при выполнении $0 \le D - t_{\mathrm{ref}} \le 14\;\mathrm{дней}$ или $D < t_{\mathrm{ref}}$.
* **Кросс-источниковая консолидация (`ALIAS_MERGED`):** Генерируется при прикреплении нового алиаса или вторичного URI портала к существующему каноническому узлу.

### 3.3 Проактивное многогоризонтное планирование действий

`ProactiveHorizonPlanner` сопоставляет порождённые рёбра `StateTransitionEdge` с декларативными правилами `TriggerPolicy`, распределёнными по трём временным горизонтам:

* **`H1_IMMEDIATE` (Критический/Высокий приоритет):** `STATUS_EXPIRING_SOON` $\to$ `DISPATCH_URGENT_ALERT`; `STATUS_REOPENED` $\to$ `DISPATCH_REOPENED_NOTICE`.
* **`H2_TACTICAL` (Высокий/Средний приоритет):** `DEADLINE_EXTENDED` $\to$ `UPDATE_DEADLINE_RECORD`; `ALIAS_MERGED` $\to$ `CONSOLIDATE_CROSS_SOURCE_METADATA`; `CREATED` $\to$ `ENRICH_AND_INDEX_ENTITY`.
* **`H3_STRATEGIC` (Низкий приоритет):** `STATUS_EXPIRED` $\to$ `ARCHIVE_EXPIRED_ENTITY`.

Индивидуальные окна задержки (`cooldown_hours`) для каждой сущности предотвращают дублирование уведомлений при частых циклах опроса.

---

## 4. Экспериментальная оценка

### 4.1 Контролируемый продольный бенчмарк: `ChronoDrift-Entity-60`

Для оценки продольной резолюции и отслеживания жизненного цикла при воспроизводимой временной динамике был сформирован бенчмарк **ChronoDrift-Entity-60** (`benchmarks/chronodrift_entity_60.json`), включающий **60 мультипортальных эпизодов** на **6 еженедельных временных срезах** ($t_1 \dots t_6$, всего **360 событий**), равномерно распределённых по шести классам сценариев (по 10 эпизодов в каждом):

* **Класс A (`A_CROSS_LINGUAL_ALIAS`, E01–E10):** Чередующиеся немецкие и английские версии идентичных программ финансирования DFG, BMBF и DAAD.
* **Класс B (`B_URI_MIGRATION_SYNDICATION`, E11–E20):** Кросс-портальная синдикация между `erc.europa.eu` и `ec.europa.eu` в сочетании со сменой URL на шаге $t_4$.
* **Класс C (`C_DEADLINE_SHIFT`, E21–E30):** Последовательные продления сроков подачи заявок на срезах $t_3$ и $t_5$.
* **Класс D (`D_EXPIRATION_REOPENING`, E31–E40):** Истечение срока на $t_3$ с последующим сезонным переоткрытием конкурса на $t_5$.
* **Класс E (`E_URGENT_HORIZON_SWEEP`, E41–E50):** Вход в 14-дневный критический горизонт на $t_4$ и закрытие на $t_6$.
* **Класс F (`F_HARD_NEGATIVE_HOMONYMS`, E51–E60):** Различные конкурсные треки одного фонда с общими акронимами и одинаковыми дедлайнами (проверка устойчивости к ложным слияниям).

На всех 360 темпоральных наблюдениях сравнивались четыре архитектуры:

1. **B1 (`Stateless_Hash`):** Дедупликация по SHA-256 от пары `(title, raw_uri)`.
2. **B2 (`Naive_Lexical`):** Детерминированный порог сходства ($\ge 0.90$) без арбитрации Системы 2 и без графа состояний.
3. **B3 (`Uncached_LLM_ER`):** Попарная LLM-арбитрация кандидатов серой зоны без постоянного кэширования алиасов и планировщика горизонтов.
4. **Наша архитектура (`PyCognition_v1.3`):** Полная связка `NeuroSymbolicEntityResolver` + `AliasMemoryStore` + `TemporalEventGraph` + `ProactiveHorizonPlanner`.

| Архитектура | ER Precision | ER Recall | ER $F_1$ | Transition Recall | Action Recall | Всего вызовов LLM |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **B1: Stateless Hash (`title\|url`)** | 1,000 | 0,741 | 0,851 | 0,000 | 0,000 | 0 |
| **B2: Naive Lexical Only** | 1,000 | 0,889 | 0,941 | 0,000 | 0,000 | 0 |
| **B3: Uncached LLM ER** | 1,000 | 1,000 | 1,000 | 0,000 | 0,000 | 54 |
| **Наша: PyCognition v1.3.0** | **1,000** | **1,000** | **1,000** | **1,000** | **1,000** | **10** |

**Ключевые выводы:**

* **Безошибочная кросс-источниковая кластеризация без ложных слияний:** PyCognition v1.3.0 показал **ER Precision = 1,000, ER Recall = 1,000, ER $F_1$ = 1,000**, объединив все двуязычные пары DE/EN (Класс A) и мигрировавшие URI (Класс B), но сохранив строгую раздельность всех 10 пар-однофамильцев (Класс F).
* **Амортизация вызовов LLM на 81,5 %:** По сравнению с некэшированной попарной арбитрацией (`B3`, 54 вызова) хранилище `AliasMemoryStore` сократило число обращений к Системе 2 до **10 вызовов** (ровно по 1 вызову на каждую новую двуязычную пару в Классе A; 0 вызовов на срезах $t_3 \dots t_6$).
* **100 % полнота отслеживания жизненного цикла и планирования:** Все продления дедлайнов, закрытия, переоткрытия и входы в срочный горизонт были зафиксированы (`Transition Recall = 1,000`) и преобразованы в целевые действия (`Action Recall = 1,000`).

### 4.2 Производственная валидация: *Grant Harvester v2.2.0* (1 230 живых записей)

Мы интегрировали `pycognition.temporal` в систему **Grant Harvester v2.2.0** [13] и выполнили двухпроходную синхронизацию по живой базе 24 порталов (`grants_vault.db`, **1 230 активных записей**):

| Метрика | Холодный проход синхронизации (Прогон 1) | Тёплый проход синхронизации (Прогон 2) | Улучшение / Дельта |
| :--- | :---: | :---: | :---: |
| **Обработано записей в хранилище** | 1 230 | 1 230 | Полный охват репозитория |
| **Консолидировано канонических сущностей** | **958** | **958** | **-272 дубля (-22,1 % избыточности)** |
| **Вызовы LLM Системы 2 (`deepseek-chat`)** | 37 | **0** | **-100,0 % расхода токенов LLM** |
| **Общее время выполнения (Wall-Clock)** | 674,7 с | **21,7 с** | **Ускорение в 31,1 раза (-96,8 % задержки)** |

На первом (холодном) проходе Система 2 корректно объединила немецко-английские пары стипендиальных программ (например, *«Karl Schmidt-Rottluff Stipendium»* $\leftrightarrow$ *«Karl Schmidt-Rottluff Scholarship»*, *«Logo der Stiftung»* $\leftrightarrow$ *«Logo of the Foundation»*) и кросс-портальные анонсы (*«ERC Proof of Concept»* $\leftrightarrow$ *«Call for proposals for ERC Proof of Concept»*), отклонив при этом сотни различных программных и кадровых записей одних и тех же организаций. На последующем тёплом проходе `AliasMemoryStore` сопоставил все 1 230 записей с 958 каноническими сущностями за **21,7 секунды** при **нулевом количестве вызовов LLM**.

---

## 5. Обсуждение, ограничения и заключение

### 5.1 Единая трёхуровневая когнитивная амортизация

Во всех трёх частях исследовательской программы PyCognition прослеживается единый архитектурный принцип: **рассуждения Системы 2 никогда не должны расходоваться повторно на повторяющиеся траектории вычислений, повторяющиеся сбои селекторов или повторяющиеся сравнения сущностей.** Благодаря кристаллизации алгоритмических планов в процедурные навыки (Часть I), исправлений селекторов в AST-проверенные модули (Часть II) и семантических вердиктов эквивалентности в битемпоральный кэш алиасов (Часть III) предельные затраты на инференс непрерывно работающего нейросимволического агента асимптотически стремятся к нулю.

### 5.2 Ограничения

1. **Распространение шума из вышестоящего слоя извлечения:** Как показал производственный эксперимент (где ссылки на страницы сотрудников одного из фондов попали в сырой свод записей), резолюция сущностей работает поверх выходов Системы 1. Обратная связь от `ProactiveHorizonPlanner` к `TelemetryEvaluator` для отсечения зашумлённых подпутей представляет собой перспективное направление замкнутой оптимизации обхода.
2. **Транзитивное слияние кластеров:** Хотя `AliasMemoryStore` кэширует попарные решения об эквивалентности и различии, масштабные многозвенные цепочки алиасов ($A \sim B$ и $B \sim C$) требуют периодической согласованности компонент связности при возникновении конфликтующих негативных ограничений.

### 5.3 Заключение

Мы представили **PyCognition v1.3.0** — завершающий этап трёхуровневой нейросимволической архитектуры, способной синтезировать процедурные навыки, устранять структурный дрейф извлечения данных и вести продольный учёт эволюционирующих кросс-источниковых сущностей. Валидация на бенчмарке `ChronoDrift-Entity-60` и в промышленном мониторинге 24 академических порталов подтвердила, что битемпоральные графы событий в сочетании с кристаллизованной памятью алиасов устраняют дублирование данных и сводят к нулю стоимость повторной резолюции сущностей.

---

## Доступность данных и программного кода

Весь исходный код, генераторы бенчмарков, наборы данных и скрипты воспроизведения находятся в открытом доступе под свободными лицензиями:

* **Фреймворк PyCognition (`v1.3.0`, LGPL-3.0-or-later):** [https://github.com/MasterUaKi/pycognition](https://github.com/MasterUaKi/pycognition)
* **Датасет и стенд ChronoDrift-Entity-60:** `benchmarks/chronodrift_entity_60.json`, `benchmarks/generate_chronodrift_60.py` и `benchmarks/run_temporal_benchmark.py` в репозитории PyCognition.
* **Производственный архив Grant Harvester:** [https://doi.org/10.5281/zenodo.24106395](https://doi.org/10.5281/zenodo.24106395)

---

## Список литературы

[1] S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao, "ReAct: Synergizing Reasoning and Acting in Language Models," in *Proc. 11th Int. Conf. Learning Representations (ICLR)*, Kigali, Rwanda, May 2023. Available: [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)

[2] G. Wang, Y. Xie, Y. Jiang, A. Mandlekar, C. Xiao, Y. Zhu, L. Fan, and A. Anandkumar, "Voyager: An Open-Ended Embodied Agent with Large Language Models," *Transactions on Machine Learning Research (TMLR)*, 2024. Available: [https://arxiv.org/abs/2305.16291](https://arxiv.org/abs/2305.16291)

[3] D. Kahneman, *Thinking, Fast and Slow*. New York, NY, USA: Farrar, Straus and Giroux, 2011.

[4] J. S. Park, J. O'Brien, C. J. Cai, M. R. Morris, P. Liang, and M. S. Bernstein, "Generative Agents: Interactive Simulacra of Human Behavior," in *Proc. 36th Annual ACM Symp. User Interface Software and Technology (UIST)*, San Francisco, CA, USA, Oct. 2023, Art. no. 2, pp. 1–22. doi: [10.1145/3586183.3606763](https://doi.org/10.1145/3586183.3606763).

[5] C. Packer, S. Wooders, K. Lin, V. Fang, S. G. Patil, I. Stoica, and J. E. Gonzalez, "MemGPT: Towards LLMs as Operating Systems," *arXiv preprint arXiv:2310.08560*, Oct. 2023. Available: [https://arxiv.org/abs/2310.08560](https://arxiv.org/abs/2310.08560)

[6] P. Rasmussen, P. Paliychuk, T. Beauvais, J. Ryan, and D. Chalef, "Zep: A Temporal Knowledge Graph Architecture for Agent Memory," *arXiv preprint arXiv:2501.13956*, Jan. 2025. Available: [https://arxiv.org/abs/2501.13956](https://arxiv.org/abs/2501.13956)

[7] B. Cai, Y. Xiang, L. Gao, H. Zhang, Y. Li, and J. Li, "Temporal Knowledge Graph Completion: A Survey," in *Proc. 32nd Int. Joint Conf. Artificial Intelligence (IJCAI)*, Macao, SAR, China, Aug. 2023, pp. 6545–6553. doi: [10.24963/ijcai.2023/734](https://doi.org/10.24963/ijcai.2023/734).

[8] R. T. Snodgrass and I. Ahn, "Temporal Databases," *IEEE Computer*, vol. 19, no. 9, pp. 35–42, Sep. 1986. doi: [10.1109/MC.1986.1663327](https://doi.org/10.1109/MC.1986.1663327).

[9] I. P. Fellegi and A. B. Sunter, "A Theory for Record Linkage," *Journal of the American Statistical Association*, vol. 64, no. 328, pp. 1183–1210, Dec. 1969. doi: [10.1080/01621459.1969.10501049](https://doi.org/10.1080/01621459.1969.10501049).

[10] Y. Li, J. Li, Y. Suhara, A. Doan, and W.-C. Tan, "Deep Entity Matching with Pre-Trained Language Models," *Proceedings of the VLDB Endowment*, vol. 14, no. 1, pp. 50–60, Sep. 2020. doi: [10.14778/3421424.3421431](https://doi.org/10.14778/3421424.3421431).

[11] A. Narayan, I. Chami, L. Orr, and C. Ré, "Can Foundation Models Wrangle Your Data?," *Proceedings of the VLDB Endowment*, vol. 16, no. 4, pp. 738–746, Dec. 2022. doi: [10.14778/3574245.3574258](https://doi.org/10.14778/3574245.3574258).

[12] O. Riabtsev, "PyCognition: Dual-Tier Neuro-Symbolic Cognitive Orchestration Framework with Telemetry-Driven Skill Refactoring and Bitemporal Event Graphs (v1.0.0–v1.3.0)," *GitHub Software Repository*, Nov. 2026. Available: [https://github.com/MasterUaKi/pycognition](https://github.com/MasterUaKi/pycognition)

[13] O. Riabtsev, "Grant Harvester: Autonomous Academic Funding Monitoring Framework with Cognitive Multi-Tier Reflection," *Zenodo Software Archive*, Nov. 2026. doi: [10.5281/zenodo.24106395](https://doi.org/10.5281/zenodo.24106395).
'''


def verify_manuscript(content: str, label: str) -> None:
    math_blocks = re.findall(r"\$\$.*?\$\$|\$[^$\n]+\$", content, re.DOTALL)
    for block in math_blocks:
        assert r"\text{" not in block, f"[{label}] Forbidden \\text in math block: {block}"
        assert r"\_" not in block, f"[{label}] Forbidden escaped underscore in math block: {block}"
    assert "10000000" not in content, f"[{label}] Placeholder DOI detected"


def render_localized_pdf(
    md_text: str,
    output_pdf: Path,
    lang_code: str,
    banner_left: str,
    doc_title: str,
) -> None:
    html_doc = convert_markdown_to_html(md_text)
    html_doc = html_doc.replace('<html lang="en">', f'<html lang="{lang_code}">', 1)
    html_doc = html_doc.replace(
        "<title>PyCognition v1.3.0 — Preprint</title>",
        f"<title>{doc_title}</title>",
        1,
    )
    html_doc = html_doc.replace(
        "<strong>PyCognition Research Series — Part III</strong> | Preprint (CC-BY-4.0)",
        banner_left,
        1,
    )

    temp_html = output_pdf.with_suffix(".preprint.html")
    temp_html.write_text(html_doc, encoding="utf-8")

    try:
        browser_bin = find_headless_browser()
        cmd = [
            browser_bin,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            "--virtual-time-budget=5000",
            f"--print-to-pdf={output_pdf.resolve()}",
            temp_html.resolve().as_uri(),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0 or not output_pdf.exists():
            raise RuntimeError(f"PDF export failed for {output_pdf}: {res.stderr}")
    finally:
        if temp_html.exists():
            temp_html.unlink()


def main() -> None:
    repo_root = Path(__file__).resolve().parent
    docs_dir = repo_root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    variants = [
        (
            "DE",
            "de",
            PAPER_DE.strip() + "\n",
            docs_dir / "paper_part3_imrad_de.md",
            docs_dir / "paper_part3_imrad_de.pdf",
            "<strong>PyCognition-Forschungsreihe — Teil III</strong> | Preprint (CC-BY-4.0)",
            "PyCognition v1.3.0 — Preprint (Deutsch)",
        ),
        (
            "RU",
            "ru",
            PAPER_RU.strip() + "\n",
            docs_dir / "paper_part3_imrad_ru.md",
            docs_dir / "paper_part3_imrad_ru.pdf",
            "<strong>Исследовательская серия PyCognition — Часть III</strong> | Препринт (CC-BY-4.0)",
            "PyCognition v1.3.0 — Препринт (Русский)",
        ),
    ]

    for label, lang_code, content, md_path, pdf_path, banner_left, doc_title in variants:
        verify_manuscript(content, label)
        md_path.write_text(content, encoding="utf-8")
        print(f"[{label}] Markdown saved: {md_path} ({len(content)} bytes, {len(content.splitlines())} lines)")

        render_localized_pdf(
            md_text=content,
            output_pdf=pdf_path,
            lang_code=lang_code,
            banner_left=banner_left,
            doc_title=doc_title,
        )
        size_kb = pdf_path.stat().st_size / 1024.0
        print(f"[{label}] PDF exported:   {pdf_path} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()