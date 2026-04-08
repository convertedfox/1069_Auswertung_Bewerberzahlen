from __future__ import annotations

from datetime import date
from pathlib import Path

import streamlit as st

from bewerberzahlen import (
    FACHBEREICHE,
    Issue,
    PipelineConfig,
    ProgramResolver,
    dataframe_to_excel_bytes,
    process_dataframe,
    read_excel_from_bytes,
)
from bewerberzahlen.constants import PROGRAM_COLUMN

MAPPING_PATH = Path(__file__).resolve().parent / "data" / "mapping" / "studiengaenge.json"

st.set_page_config(page_title="Bewerberzahlen bereinigen", layout="wide")
st.title("Bewerberzahlen bereinigen")
st.markdown(
    "Bereinigt Bewerber-Excel-Dateien: Dubletten filtern, Status ableiten, Fachbereiche "
    "zuordnen und personenbezogene Spalten entfernen."
)


@st.cache_data(show_spinner=False)
def _load_mapping() -> ProgramResolver:
    return ProgramResolver.from_file(MAPPING_PATH)


def _render_issues(issues: list[Issue], title: str) -> None:
    if not issues:
        return
    expander = st.expander(f"{title} ({len(issues)})", expanded=True)
    with expander:
        for issue in issues:
            rows = f" (Zeilen: {', '.join(map(str, issue.rows))})" if issue.rows else ""
            expander.markdown(f"**{issue.message}**{rows}")


st.info("Maximale Upload-Größe: 20 MB", icon="ℹ️")

with st.form("bereinigung_form"):
    uploader = st.file_uploader("Excel-Datei hochladen", type=["xlsx"], accept_multiple_files=False)
    submit = st.form_submit_button("Bereinigen", type="primary")

if submit:
    if not uploader:
        st.error("Bitte eine Excel-Datei auswählen.")
    elif uploader.size and uploader.size > 20 * 1024 * 1024:
        st.error("Datei ist größer als 20 MB und wird nicht verarbeitet.")
    else:
        try:
            raw_bytes = uploader.getvalue()
            df = read_excel_from_bytes(raw_bytes)
        except Exception as exc:  # noqa: BLE001
            st.error(f"Konnte Datei nicht lesen: {exc}")
        else:
            resolver = _load_mapping()

            program_names = df[PROGRAM_COLUMN].astype(str).str.strip().dropna().unique()
            unknown_programs = resolver.unknown_programs(program_names, manual_assignments=None)

            manual_assignments: dict[str, str] = {}
            if unknown_programs:
                st.warning(
                    "Unbekannte Studiengänge gefunden. Bitte Fachbereich zuordnen, damit die Datei "
                    "bereinigt werden kann.",
                    icon="⚠️",
                )
                for program in sorted(unknown_programs):
                    selection = st.selectbox(
                        f'Fachbereich für "{program}"',
                        options=[""] + FACHBEREICHE,
                        key=f"fachbereich_{program}",
                    )
                    if selection:
                        manual_assignments[program.strip()] = selection
            else:
                st.success("Alle Studiengänge sind im Mapping hinterlegt.")

            result = process_dataframe(
                df, resolver, PipelineConfig(manual_assignments=manual_assignments or None)
            )

            _render_issues(result.errors, "Fehler")
            _render_issues(result.warnings, "Hinweise")

            # Statusbanner
            if result.errors:
                st.error(
                    "Verarbeitung fehlgeschlagen. "
                    f"Eingelesen: {result.n_input}, "
                    f"unbekannte Studiengänge: {result.n_unknown_program}",
                )
            else:
                st.success(
                    "Bereit: "
                    f"Eingelesen: {result.n_input}, behalten: {result.n_kept}, "
                    f"Dubletten: {result.n_duplicates}, fehlender Studiengang ignoriert: "
                    f"{result.n_missing_program}, unbekannte Studiengänge: "
                    f"{result.n_unknown_program}",
                )

            if result.cleaned is None:
                st.error("Bereinigung nicht möglich, bitte Fehler beheben.")
            else:
                today = date.today().strftime("%Y%m%d")
                base_name = Path(uploader.name).stem
                cleaned_bytes = dataframe_to_excel_bytes(result.cleaned)
                st.download_button(
                    "Bereinigte Datei herunterladen",
                    data=cleaned_bytes,
                    file_name=f"cleaned_{base_name}_{today}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                )

                if not result.duplicates.empty:
                    duplicates_bytes = dataframe_to_excel_bytes(result.duplicates)
                    st.download_button(
                        "Dubletten-Liste herunterladen",
                        data=duplicates_bytes,
                        file_name=f"duplicates_{base_name}_{today}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
