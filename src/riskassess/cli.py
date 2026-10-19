"""Command line interface.

  riskassess list                          show the sample company profiles
  riskassess assess <profile> [--format md|html|json] [--out DIR]
                                           score a profile and write a report
  riskassess interview [--out FILE]        answer the questionnaire interactively
  riskassess validate [--n 1000]           run the scoring-model validation suite
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from .questionnaire import ROOT, list_profiles, load_profile, load_questionnaire
from .remediation import PHASES, build_plan
from .report import to_html, to_json, to_markdown
from .scoring import assess
from .summary import executive_summary
from .validate import run_validation

RENDERERS = {"md": to_markdown, "html": to_html, "json": to_json}


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def run_assessment(profile: dict, fmt: str, out_dir: Path, mode: str | None) -> Path:
    qn = load_questionnaire()
    a = assess(qn, profile)
    plan = build_plan(qn, a)
    summary, used = executive_summary(a, plan, mode=mode)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{slugify(a.company.get('name', 'company'))}.{fmt}"
    path.write_text(RENDERERS[fmt](a, plan, summary), encoding="utf-8")

    print(f"\n{a.company.get('name')}")
    print(f"  Overall maturity   {a.overall_maturity:g}%")
    print(f"  Risk index         {a.risk_index:g} / 100")
    print("  Ratings            " + ", ".join(f"{k} {v}" for k, v in a.rating_counts.items()))
    print(f"  Plan               {len(plan.items)} actions; risk index after quick wins "
          f"{plan.risk_index_after[PHASES[0]]:g}, after full plan {plan.risk_index_after[PHASES[2]]:g}")
    print(f"  Summary mode       {used}")
    print(f"  Report             {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}\n")
    return path


def interview() -> dict:
    qn = load_questionnaire()
    print("Cyber Risk Assessment questionnaire. Answer each question with a number.\n")
    company = {
        "name": input("Company name: ").strip() or "My Company",
        "industry": input("Industry: ").strip(),
        "employees": int(input("Number of employees: ").strip() or 0),
        "handles_sensitive_data": input("Does it store sensitive data (customer, health, payment)? [y/n]: ")
        .strip().lower().startswith("y"),
    }
    answers = {}
    for area in qn.areas:
        print(f"\n== {area['name']} ==")
        for q in [q for q in qn.questions if q.area == area["id"]]:
            print(f"\n{q.text}")
            opts = sorted(q.options, key=lambda o: -o["maturity"])
            for i, o in enumerate(opts, start=1):
                print(f"  {i}. {o['label']}")
            while True:
                choice = input("> ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(opts):
                    answers[q.id] = opts[int(choice) - 1]["maturity"]
                    break
                print(f"  Enter a number from 1 to {len(opts)}.")
    return {"company": company, "answers": answers}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="riskassess", description="AI Cyber Risk Assessment Assistant")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="list sample company profiles")

    p_assess = sub.add_parser("assess", help="score a profile and write a report")
    p_assess.add_argument("profile", help="profile name (see `list`) or path to a JSON file")
    p_assess.add_argument("--format", choices=list(RENDERERS), default="html")
    p_assess.add_argument("--out", default=str(ROOT / "reports"))
    p_assess.add_argument("--summary", choices=["template", "llm"], default=None)

    p_int = sub.add_parser("interview", help="answer the questionnaire interactively")
    p_int.add_argument("--out", default=str(ROOT / "data" / "profiles" / "my-company.json"))

    p_val = sub.add_parser("validate", help="validate the scoring model")
    p_val.add_argument("--n", type=int, default=1000)

    args = parser.parse_args(argv)

    if args.command == "list":
        for name in list_profiles():
            c = load_profile(name)["company"]
            print(f"  {name:<28} {c['name']} ({c['industry']}, {c['employees']} employees)")
    elif args.command == "assess":
        run_assessment(load_profile(args.profile), args.format, Path(args.out), args.summary)
    elif args.command == "interview":
        profile = interview()
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(profile, indent=2), encoding="utf-8")
        print(f"\nSaved answers to {out}")
        run_assessment(profile, "html", ROOT / "reports", None)
    elif args.command == "validate":
        r = run_validation(load_questionnaire(), n=args.n)
        print(f"\nScoring-model validation: {r['simulations']} simulated assessments\n")
        for name, c in r["checks"].items():
            print(f"  {name.replace('_', ' ').title():<18} {c['passed']}/{c['total']}  ({c['pct']}%)")
        po = r["profile_ordering"]
        print(f"  {'Profile ordering':<18} {'PASS' if po['passed'] else 'FAIL'}  "
              + ", ".join(f"{k}={v:g}" for k, v in po["risk_index"].items()))
        d = r["risk_index_distribution"]
        print(f"\n  Risk index across simulations: min {d['min']:g}, median {d['median']:g}, "
              f"max {d['max']:g}, stdev {d['stdev']:g}")
        print("  Biggest drivers of the risk index (|correlation| with area maturity):")
        for name, corr in r["area_drivers"]:
            print(f"    {name:<38} {corr}")
        out = ROOT / "validation" / "results.json"
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps(r, indent=2), encoding="utf-8")
        print(f"\n  Full results -> {out.relative_to(ROOT)}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
