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


uploader = st.file_uploader("Excel-Datei hochladen", type=["xlsx"], accept_multiple_files=False)


if uploader:
    try:
        raw_bytes = uploader.getvalue()
        df = read_excel_from_bytes(raw_bytes)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Konnte Datei nicht lesen: {exc}")
    else:
        resolver = _load_mapping()

        program_names = df[PROGRAM_COLUMN].astype(str).str.strip().dropna().unique()
        unknown_programs = resolver.unknown_programs(program_names, manual_assignments=None)

        st.subheader("Unbekannte Studiengänge")
        manual_assignments: dict[str, str] = {}
        if unknown_programs:
            st.info(
                "Bitte ordne unbekannte Studiengänge einem Fachbereich zu, damit die Datei "
                "bereinigt werden kann."
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

        if st.button("Bereinigen", type="primary"):
            result = process_dataframe(
                df, resolver, PipelineConfig(manual_assignments=manual_assignments or None)
            )

            _render_issues(result.errors, "Fehler")
            _render_issues(result.warnings, "Hinweise")

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
else:
    st.info("Bitte eine Excel-Datei (.xlsx) auswählen.")
