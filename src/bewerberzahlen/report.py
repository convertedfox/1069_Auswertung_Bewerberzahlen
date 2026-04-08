from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

IssueLevel = Literal["error", "warning"]


@dataclass
class Issue:
    message: str
    level: IssueLevel
    rows: list[int] = field(default_factory=list)
    context: dict[str, Any] | None = None

    def with_rows(self, rows: list[int]) -> Issue:
        return Issue(message=self.message, level=self.level, rows=rows, context=self.context)


@dataclass
class ProcessingResult:
    cleaned: Any | None  # pandas.DataFrame or None
    warnings: list[Issue]
    errors: list[Issue]
    duplicates: Any  # pandas.DataFrame
    n_input: int = 0
    n_kept: int = 0
    n_duplicates: int = 0
    n_missing_program: int = 0
    n_unknown_program: int = 0

    @property
    def is_successful(self) -> bool:
        return not self.errors
