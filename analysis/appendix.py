"""Write the report appendix material straight from the code, so the paper cannot drift from what ran.

uv run python -m analysis.appendix > paper/appendix_scripts.md
"""

from __future__ import annotations

from sting.scripts import CONDITIONS, OFFER_HOURS, SCRIPTS, schedule


def main() -> None:
    print("# Appendix: planted-seller scripts\n")
    print(
        f"Messages are written in hours {', '.join(map(str, OFFER_HOURS))} and read one hour later. "
        "Even seeds use wording A and odd seeds use wording B. The planted seller asks $96 every hour "
        "in every condition and never replies.\n"
    )
    print("| Condition | Wording | Hour written | Message |")
    print("|---|---|---|---|")
    for cond in CONDITIONS:
        for wording in sorted(SCRIPTS[cond]):
            sch = schedule(cond, wording, 96)
            if not sch:
                print(f"| {cond} | {wording} | none | (no messages) |")
            for hour, text in sch.items():
                print(f"| {cond} | {wording} | {hour} | {text} |")


if __name__ == "__main__":
    main()
