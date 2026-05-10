"""Demo: three scripted triage cases (normal, critical, borderline)."""

from __future__ import annotations

import json

from orchestrator import triage


def main() -> None:
    cases: list[tuple[str, str]] = [
        (
            "normal_demo",
            "Mild sore throat for two days, no fever, drinking fluids fine, no breathing problems.",
        ),
        (
            "critical_demo",
            "Sudden crushing chest pain with pain into the left arm, clammy skin, and trouble catching breath for 20 minutes.",
        ),
        (
            "borderline_demo",
            "Fever 101°F for a day, bad headache, neck feels stiff, but awake and talking normally.",
        ),
    ]

    for case_id, symptoms in cases:
        print(f"\n=== Case: {case_id} ===")
        result = triage(symptoms, case_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
