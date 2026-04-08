from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import pandas as pd

from .constants import (
    ACCEPTED_COLUMN,
    DERIVED_STATUS_VALUES,
    EMAIL_COLUMN,
    FACHBEREICH_COLUMN,
    NO_POTENTIAL_COLUMN,
    PII_COLUMNS,
    PROGRAM_COLUMN,
    REJECTION_COLUMN,
    REQUIRED_COLUMNS,
    STATUS_COLUMN,
)
from .mapping import ProgramResolver
from .report import Issue, ProcessingResult


@dataclass
class PipelineConfig:
    manual_assignments: dict[str, str] | None = None


def process_dataframe(
    df: pd.DataFrame, resolver: ProgramResolver, config: PipelineConfig | None = None
) -> ProcessingResult:
    cfg = config or PipelineConfig()
    working = df.copy()
    working["__row_number"] = range(2, len(working) + 2)
    warnings: list[Issue] = []
    errors: list[Issue] = []

    missing = _missing_columns(working.columns)
    if missing:
        errors.append(
            Issue(
                message=f"Erforderliche Spalten fehlen: {', '.join(sorted(missing))}", level="error"
            )
        )
        return ProcessingResult(
            cleaned=None, warnings=warnings, errors=errors, duplicates=pd.DataFrame()
        )

    _normalize_columns(working)

    duplicates, working = _deduplicate(working)
    if not duplicates.empty:
        warnings.append(
            Issue(
                message=(
                    "Dubletten gefunden (gleiche E-Mail + Studiengang); "
                    "nur der erste Eintrag wurde behalten."
                ),
                level="warning",
                rows=duplicates["__row_number"].astype(int).tolist(),
                context={"anzahl": len(duplicates)},
            )
        )

    status_errors = _apply_status_rules(working)
    if status_errors:
        errors.append(
            Issue(
                message="Status-Spalten (D/F/G) sind mehrfach gefüllt; bitte bereinigen.",
                level="error",
                rows=status_errors,
            )
        )

    mapping_errors = _apply_fachbereich_mapping(working, resolver, cfg.manual_assignments)
    if mapping_errors:
        for program, rows in sorted(mapping_errors.items()):
            errors.append(
                Issue(
                    message=f"Unbekannter Studiengang: {program}",
                    level="error",
                    rows=rows,
                )
            )

    cleaned: pd.DataFrame | None = None
    if not errors:
        cleaned = _finalize_output(working)

    duplicates = _sanitize_output(duplicates)

    return ProcessingResult(
        cleaned=cleaned, warnings=warnings, errors=errors, duplicates=duplicates
    )


def _missing_columns(columns: Iterable[str]) -> set[str]:
    return {col for col in REQUIRED_COLUMNS if col not in columns}


def _normalize_columns(df: pd.DataFrame) -> None:
    df[EMAIL_COLUMN] = df[EMAIL_COLUMN].astype(str).str.strip().str.lower()
    df[PROGRAM_COLUMN] = df[PROGRAM_COLUMN].astype(str).str.strip()
    df[STATUS_COLUMN] = df[STATUS_COLUMN].fillna("").astype(str)


def _deduplicate(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df["__program_key"] = df[PROGRAM_COLUMN]
    df["__email_key"] = df[EMAIL_COLUMN]
    duplicate_mask = df.duplicated(subset=["__program_key", "__email_key"], keep="first")
    duplicates = df.loc[duplicate_mask].copy()
    deduped = df.loc[~duplicate_mask].copy()
    return duplicates, deduped


def _has_value(value: object) -> bool:
    value_any: Any = value
    if pd.isna(value_any):
        return False
    if isinstance(value, str) and not value.strip():
        return False
    return True


def _apply_status_rules(df: pd.DataFrame) -> list[int]:
    error_rows: list[int] = []
    for idx, row in df.iterrows():
        row_number = int(row["__row_number"])
        filled = []
        if _has_value(row[ACCEPTED_COLUMN]):
            filled.append(DERIVED_STATUS_VALUES[ACCEPTED_COLUMN])
        if _has_value(row[REJECTION_COLUMN]):
            filled.append(DERIVED_STATUS_VALUES[REJECTION_COLUMN])
        if _has_value(row[NO_POTENTIAL_COLUMN]) and str(row[NO_POTENTIAL_COLUMN]).strip() != "0":
            filled.append(DERIVED_STATUS_VALUES[NO_POTENTIAL_COLUMN])

        if len(filled) > 1:
            error_rows.append(row_number)
            continue
        if len(filled) == 1:
            df.at[idx, STATUS_COLUMN] = filled[0]
    return error_rows


def _apply_fachbereich_mapping(
    df: pd.DataFrame, resolver: ProgramResolver, manual_assignments: dict[str, str] | None
) -> dict[str, list[int]]:
    errors: dict[str, list[int]] = {}
    for idx, row in df.iterrows():
        program_name = str(row[PROGRAM_COLUMN])
        row_number = int(row["__row_number"])
        fachbereich, _ = resolver.resolve(program_name, manual_assignments)
        if fachbereich:
            df.at[idx, FACHBEREICH_COLUMN] = fachbereich
        else:
            errors.setdefault(program_name, []).append(row_number)
    return errors


def _finalize_output(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = _remove_pii(df)
    return _drop_internal_columns(df)


def _sanitize_output(df: pd.DataFrame) -> pd.DataFrame:
    df = _remove_pii(df.copy())
    return _drop_internal_columns(df)


def _remove_pii(df: pd.DataFrame) -> pd.DataFrame:
    df.drop(columns=[col for col in PII_COLUMNS if col in df.columns], inplace=True)
    return df


def _drop_internal_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=[c for c in df.columns if c.startswith("__")], errors="ignore")
