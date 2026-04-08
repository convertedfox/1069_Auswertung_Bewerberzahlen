from __future__ import annotations

STATUS_COLUMN = "Status"
ACCEPTED_COLUMN = "Akzeptiert"
REJECTION_COLUMN = "Absage"
NO_POTENTIAL_COLUMN = "kein Potential"
FACHBEREICH_COLUMN = "Fachbereich"
PROGRAM_COLUMN = "Formularfelder_Hauptfach_Prüfungsordnung"
PROGRAM_EXPORT_COLUMN = "Formularfelder_Studiengang_Export"
EMAIL_COLUMN = "Formularfelder_E-Mail_privat"

REQUIRED_COLUMNS = [
    "Bewerbungsnummer",
    STATUS_COLUMN,
    "BEW-Start",
    ACCEPTED_COLUMN,
    "Gesamtstatus",
    REJECTION_COLUMN,
    NO_POTENTIAL_COLUMN,
    FACHBEREICH_COLUMN,
    PROGRAM_COLUMN,
    PROGRAM_EXPORT_COLUMN,
    "Formularfelder_Anrede",
    "Formularfelder_Vorname",
    "Formularfelder_Name",
    "Formularfelder_Strasse_und_Hausnummer",
    "Formularfelder_Postleitzahl",
    "Formularfelder_Ort",
    "Formularfelder_Land",
    "Formularfelder_Telefon_mobil",
    EMAIL_COLUMN,
]

PII_COLUMNS = [
    "Formularfelder_Vorname",
    "Formularfelder_Name",
    "Formularfelder_Strasse_und_Hausnummer",
    "Formularfelder_Ort",
    "Formularfelder_Telefon_mobil",
    EMAIL_COLUMN,
]

FACHBEREICHE = ["Wirtschaft", "Sozialwesen", "Gesundheit", "Technik"]

DERIVED_STATUS_VALUES = {
    ACCEPTED_COLUMN: "Akzeptiert",
    REJECTION_COLUMN: "Absage",
    NO_POTENTIAL_COLUMN: "Kein Potential",
}
