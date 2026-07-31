"""
pipeline.py
-----------
Orchestrates the full pipeline end-to-end:

    mine_source.py -> generate.py -> dedup.py -> quality_check.py -> final CSV

Because dedup and quality-check both drop a small number of rows, this
script loops: generate, dedup, quality-check, and if the surviving count
is below config.TOTAL_TARGET, generate an extra top-up batch (with a
fresh random seed offset) and repeat, until exactly TOTAL_TARGET rows
are produced (or MAX_ROUNDS is hit, in which case it ships what it has
and says so honestly).

Final output: config.FINAL_CSV, with ONLY the columns PSA_ID, Domain,
English -- ready for the translation step.
"""

import json
import random

import config
import dedup
import generate
import mine_source
import quality_check

MAX_ROUNDS = 6


def top_up_round(round_num: int, needed_per_subcat: dict) -> list:
    """Generate extra candidate rows for sub-categories that are short,
    using a different random seed each round so it doesn't just
    regenerate the same rejected candidates."""
    random.seed(1000 + round_num)
    authorities_by_domain = generate.load_authorities()
    extra_rows = []

    for domain, subcats in config.TAXONOMY.items():
        prefix = config.DOMAIN_PREFIX[domain]
        authorities = authorities_by_domain.get(domain) or ["Government of Kenya"]
        for subcat in subcats:
            need = needed_per_subcat.get((domain, subcat), 0)
            if need <= 0:
                continue
            # generate a bit extra to absorb the next dedup/QC pass
            rows = generate.generate_for_subcategory(
                domain, subcat, authorities, need + max(20, need // 4)
            )
            for text in rows:
                extra_rows.append(
                    {
                        "PSA_ID": "TMP",  # renumbered later
                        "Domain": domain,
                        "English": text,
                        "_subcategory": subcat,
                    }
                )
    return extra_rows


def renumber(rows: list) -> list:
    counters = {domain: 1 for domain in config.TAXONOMY}
    out = []
    for r in rows:
        prefix = config.DOMAIN_PREFIX[r["Domain"]]
        psa_id = f"{prefix}_{counters[r['Domain']]:05d}"
        counters[r["Domain"]] += 1
        out.append({"PSA_ID": psa_id, "Domain": r["Domain"], "English": r["English"],
                     "_subcategory": r.get("_subcategory", "")})
    return out


def counts_per_subcat(rows: list) -> dict:
    counts = {}
    for r in rows:
        key = (r["Domain"], r.get("_subcategory", ""))
        counts[key] = counts.get(key, 0) + 1
    return counts


def main():
    print("=" * 60)
    print("STEP 1: Mining source CSV for authorities/phrases")
    print("=" * 60)
    mine_source.main()

    print("\n" + "=" * 60)
    print("STEP 2: Generating synthetic PSAs")
    print("=" * 60)
    generate.main()

    all_rows = json.loads((config.DATA_DIR / "generated_raw.json").read_text())

    for round_num in range(1, MAX_ROUNDS + 1):
        print("\n" + "=" * 60)
        print(f"STEP 3+4 (round {round_num}): Dedup + quality check")
        print("=" * 60)

        (config.DATA_DIR / "generated_raw.json").write_text(json.dumps(all_rows, indent=2))

        rows = dedup.dedup_exact(all_rows)
        rows = dedup.dedup_near(rows)
        print(f"After dedup: {len(rows)}")

        (config.DATA_DIR / "deduped.json").write_text(json.dumps(rows, indent=2))
        quality_check.main()
        rows = json.loads((config.DATA_DIR / "quality_checked.json").read_text())
        print(f"After quality check: {len(rows)}")

        if len(rows) >= config.TOTAL_TARGET:
            rows = dedup.dedup_exact(rows)  # quality_check's text cleanup can rarely
            # collide two previously-distinct rows (e.g. same fix applied to both)
            if len(rows) >= config.TOTAL_TARGET:
                rows = rows[: config.TOTAL_TARGET]
                print(f"Target of {config.TOTAL_TARGET} reached.")
                break
            print(f"Post-cleanup dedup dropped below target ({len(rows)}); topping up again...")

        shortfall = config.TOTAL_TARGET - len(rows)
        print(f"Shortfall of {shortfall} rows -- generating a top-up batch...")

        have = counts_per_subcat(rows)
        target_per_subcat = config.PER_SUBCATEGORY_TARGET
        needed = {}
        for domain, subcats in config.TAXONOMY.items():
            for subcat in subcats:
                key = (domain, subcat)
                short = target_per_subcat - have.get(key, 0)
                if short > 0:
                    needed[key] = short

        extra = top_up_round(round_num, needed)
        all_rows = rows + extra

    # Final renumbering and column selection
    rows = renumber(rows)
    final_rows = [{"PSA_ID": r["PSA_ID"], "Domain": r["Domain"], "English": r["English"]} for r in rows]

    import pandas as pd

    df = pd.DataFrame(final_rows, columns=["PSA_ID", "Domain", "English"])
    df.to_csv(config.FINAL_CSV, index=False, encoding="utf-8")

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"Final row count: {len(df)}")
    print(f"Final CSV: {config.FINAL_CSV}")
    print(df["Domain"].value_counts())


if __name__ == "__main__":
    main()
