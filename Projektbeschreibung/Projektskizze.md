# Projektbeschreibung: Automatisierte Auswertung von Bewerberzahlen mit Streamlit

## Ziel des Projekts

Ziel ist es, eine Streamlit-basierte Python-Anwendung zu entwickeln, die die Auswertung von Bewerberzahlen einer Hochschule automatisiert.

Das Projekt wird in zwei Phasen unterteilt:

- **Phase 1:** Entwicklung eines Importeurs zur Datenaufbereitung  
- **Phase 2:** Aufbau einer Datenbasis und Durchführung historischer Auswertungen

---

## Architektur

- **Programmiersprache:** Python  
- **Frontend:** Streamlit  
- **Datenquelle:** Excel-Dateien  
- **Datenpfad (Entwicklung):** `data/development`

---

## Phase 1: Importeur und Datenbereinigung

### 1. Datenimport

- Die Anwendung liest Excel-Dateien ein über ein Uploadfeld
- eine typische Datei dazu liegt in `data/development`.
- Die Struktur der Datei entspricht dem typischen Format eingehender Bewerberdaten.

---

### 2. Dublettenprüfung

- Jede Zeile repräsentiert eine Bewerbung.
- Die **E-Mail-Adresse befindet sich in der letzten Spalte**.
- Eine Dublette liegt vor, wenn:
  - dieselbe E-Mail-Adresse mehrfach vorkommt  
  - **UND** es sich um denselben Studiengang handelt
- Ausnahme:
  - Gleiche E-Mail-Adresse bei **unterschiedlichen Studiengängen** → **keine Dublette**
- Wenn Dubletten vorliegen, soll der Benutzer wählen können, welche Duplette gelöscht werden soll.
---

### 3. Statusprüfung

- Der Status befindet sich in **Spalte B**.
- Es muss geprüft werden, ob Einträge in folgenden Spalten vorhanden sind:
  - Spalte D  -> ist ein Datumseintrag vorhanden, wird der Status in B auf "Akzeptiert" gesetzt
  - Spalte F  -> ist ein Datumseintrag vorhanden, wird der Status in B auf "Absage" gesetzt
  - Spalte G  -> ist eine "1" vorhanden, wird der Status in B auf "Kein Potential" gesetzt

---

### 4. Fachbereich-Zuordnung

- Der Fachbereich wird in **Spalte H** eingetragen.
- Der Studiengang steht in **Spalte I**.
- Jeder Studiengang muss genau einem der folgenden Fachbereiche zugeordnet werden:

  - Wirtschaft  
  - Sozialwesen  
  - Gesundheit  
  - Technik  

- Die Zuordnung erfolgt regelbasiert anhand des Studiengangs.
Wir sollten dazu ein JSON aufbauen, was alle Studiengänge vorhält.
#### Studiengangs-JSON:
Studiengang {
  aktueller Name,
  alter Name,
  Fachbereich
}
---

### 5. Bereinigung personenbezogener Daten
Die Spalten L, M, N, P, R, S sollen anschliessend gelöscht werden.
### 6. Rückgabe
Die so bereinigte und aufbereitete Datei soll als Download angeboten werden

## Phase 2: Historische Auswertungen

In der zweiten Phase wird auf den bereinigten Daten aufgebaut:
Diese Daten sollen dann zukünftig in eine Datenbank (vielleicht Supabase, vielleicht Airtable) abgespeichert werden unter Ergänzung eines Datumsstempels (siehe Dateiname), um einen Datenbestand aufzubauen.
- Aufbau einer **persistenten Datenbasis**
- Durchführung von **Zeitreihenanalysen**
- Ermöglichung von **historischen Vergleichen** (z. B. Bewerberzahlen pro Zeitraum, Studiengang, Fachbereich)

---

## Zielbild

Am Ende entsteht eine Streamlit-Anwendung, die:

- Rohdaten automatisiert bereinigt  
- konsistente Daten erzeugt  
- und darauf aufbauend aussagekräftige Auswertungen und Vergleiche ermöglicht
