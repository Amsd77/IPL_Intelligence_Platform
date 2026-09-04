from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    """Severity level for a data-quality issue."""

    ERROR = "ERROR"
    WARNING = "WARNING"


@dataclass(frozen=True)
class DataQualityIssue:
    """Represents one data-quality issue."""

    rule_id: str
    field: str
    message: str
    severity: Severity


@dataclass
class DataQualityResult:
    """Result produced by the data-quality engine."""

    issues: list[DataQualityIssue] = field(
        default_factory=list
    )

    @property
    def errors(self) -> list[DataQualityIssue]:
        """Return all ERROR-level issues."""

        return [
            issue
            for issue in self.issues
            if issue.severity == Severity.ERROR
        ]

    @property
    def warnings(self) -> list[DataQualityIssue]:
        """Return all WARNING-level issues."""

        return [
            issue
            for issue in self.issues
            if issue.severity == Severity.WARNING
        ]

    @property
    def is_valid(self) -> bool:
        """Return True when no ERROR-level issues exist."""

        return len(self.errors) == 0

    def add_error(
        self,
        rule_id: str,
        field: str,
        message: str,
    ) -> None:
        """Add an ERROR-level issue."""

        self.issues.append(
            DataQualityIssue(
                rule_id=rule_id,
                field=field,
                message=message,
                severity=Severity.ERROR,
            )
        )

    def add_warning(
        self,
        rule_id: str,
        field: str,
        message: str,
    ) -> None:
        """Add a WARNING-level issue."""

        self.issues.append(
            DataQualityIssue(
                rule_id=rule_id,
                field=field,
                message=message,
                severity=Severity.WARNING,
            )
        )