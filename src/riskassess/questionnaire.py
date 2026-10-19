"""Load and validate the questionnaire and company profiles."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUESTIONNAIRE_PATH = ROOT / "data" / "questionnaire.json"
PROFILES_DIR = ROOT / "data" / "profiles"

EFFORTS = {"low", "medium", "high"}


@dataclass
class Question:
    id: str
    name: str
    area: str
    csf: str
    text: str
    impact: int
    sensitive_data_bump: bool
    options: list[dict]
    remediation: dict

    def label_for(self, maturity: int) -> str:
        for opt in self.options:
            if opt["maturity"] == maturity:
                return opt["label"]
        raise ValueError(f"{self.id}: no option with maturity {maturity}")


@dataclass
class Questionnaire:
    version: str
    framework: str
    areas: list[dict]
    questions: list[Question]

    def area_name(self, area_id: str) -> str:
        return next(a["name"] for a in self.areas if a["id"] == area_id)

    def by_id(self) -> dict[str, Question]:
        return {q.id: q for q in self.questions}


def load_questionnaire(path: Path = QUESTIONNAIRE_PATH) -> Questionnaire:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    qn = Questionnaire(
        version=raw["version"],
        framework=raw["framework"],
        areas=raw["areas"],
        questions=[Question(**q) for q in raw["questions"]],
    )
    validate_questionnaire(qn)
    return qn


def validate_questionnaire(qn: Questionnaire) -> None:
    """Fail loudly on a malformed questionnaire so scoring is never silently wrong."""
    area_ids = {a["id"] for a in qn.areas}
    seen = set()
    for q in qn.questions:
        assert q.id not in seen, f"duplicate question id {q.id}"
        assert q.name, f"{q.id}: missing short name"
        seen.add(q.id)
        assert q.area in area_ids, f"{q.id}: unknown area {q.area}"
        assert 1 <= q.impact <= 5, f"{q.id}: impact must be 1-5"
        assert sorted(o["maturity"] for o in q.options) == [0, 1, 2, 3], f"{q.id}: options must cover maturity 0-3"
        assert q.remediation.get("effort") in EFFORTS, f"{q.id}: effort must be low/medium/high"
        for key in ("action", "why", "cost"):
            assert q.remediation.get(key), f"{q.id}: remediation missing {key}"


def load_profile(name_or_path: str | Path) -> dict:
    path = Path(name_or_path)
    if not path.exists():
        path = PROFILES_DIR / f"{name_or_path}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def list_profiles() -> list[str]:
    return sorted(p.stem for p in PROFILES_DIR.glob("*.json"))
