import argparse
import csv
import os
import re
import sys
from collections import Counter


def parse_datastream(path: str) -> list[str]:
    """Return the ordered list of rule IDs the CIS L1 Server profile selects."""
    xml = open(path).read()
    m = re.search(
        r'<xccdf-1\.2:Profile\s+id="xccdf_org\.ssgproject\.content_profile_cis_level1_server"[^>]*>(.*?)</xccdf-1\.2:Profile>',
        xml, re.DOTALL,
    )
    if not m:
        sys.exit(f"CIS L1 Server profile not found in {path}")
    return re.findall(
        r'<xccdf-1\.2:select\s+idref="xccdf_org\.ssgproject\.content_rule_([^"]+)"\s+selected="true"',
        m.group(1),
    )


def parse_results(path: str) -> dict[str, str]:
    """Return {rule_id: status} for every rule the host was evaluated against."""
    xml = open(path).read()
    # Each rule-result is multi-line; result is a child element.
    pattern = re.compile(
        r'<rule-result[^>]*idref="xccdf_org\.ssgproject\.content_rule_([^"]+)"[^>]*>'
        r'.*?<result>([^<]+)</result>',
        re.DOTALL,
    )
    return {rid: status for rid, status in pattern.findall(xml)}


def index_role(role_dir: str) -> dict[str, list[str]]:
    """Build a keyword -> [file:line] index by scanning the role's tasks + defaults + templates."""
    index: dict[str, list[str]] = {}
    for root, _dirs, files in os.walk(role_dir):
        for fname in files:
            if not (fname.endswith(".yml") or fname.endswith(".j2")):
                continue
            fpath = os.path.join(root, fname)
            try:
                lines = open(fpath).read().splitlines()
            except Exception:
                continue
            for i, line in enumerate(lines, 1):
                key = line.lower()
                index.setdefault(fpath, []).append((i, key))
    return index


def role_mentions(rule_id: str, role_index: dict[str, list[tuple[int, str]]]) -> list[str]:
    """Look for the rule's distinctive keywords in the role files."""
    
    tokens = rule_id.split("_")
    candidates = set()
    
    candidates.add(rule_id.lower())

    for t in tokens:
        if len(t) >= 4:
            candidates.add(t.lower())
    # Multi-token compounds
    for i in range(len(tokens) - 1):
        candidates.add((tokens[i] + "_" + tokens[i + 1]).lower())

    hits: list[str] = []
    for fpath, lineidx in role_index.items():
        for line_no, content in lineidx:
            if any(c in content for c in candidates if len(c) >= 5):
                hits.append(f"{os.path.relpath(fpath)}:{line_no}")
                break  # one hit per file is enough
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datastream", required=True, help="Path to SSG datastream XML (vendor file)")
    ap.add_argument("--results", required=True, help="Path to OpenSCAP results XML for one host")
    ap.add_argument("--role", required=True, help="Path to roles/cis_hardening directory")
    ap.add_argument("--out", required=True, help="Output CSV path")
    args = ap.parse_args()

    print(f"[1/4] Reading vendor datastream: {args.datastream}")
    required = parse_datastream(args.datastream)
    print(f"      Vendor CIS L1 Server profile = {len(required)} rules")

    print(f"[2/4] Reading scan results: {args.results}")
    results = parse_results(args.results)
    print(f"      Host evaluated against {len(results)} rules")

    print(f"[3/4] Indexing role at: {args.role}")
    role_idx = index_role(args.role)
    print(f"      Indexed {len(role_idx)} files")

    print(f"[4/4] Cross-checking each vendor rule...\n")

    rows = []
    summary = Counter()
    role_hits_by_status = Counter()

    for rule in required:
        status = results.get(rule, "not_evaluated")
        hits = role_mentions(rule, role_idx)
        rows.append({
            "rule_id": rule,
            "status": status,
            "role_mentions": "; ".join(hits) if hits else "",
            "role_addresses": "yes" if hits else "no",
        })
        summary[status] += 1
        if hits:
            role_hits_by_status[status] += 1

    # Write CSV
    with open(args.out, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["rule_id", "status", "role_addresses", "role_mentions"])
        writer.writeheader()
        writer.writerows(rows)

    print("=== ALIGNMENT SUMMARY ===")
    print(f"Vendor rules in CIS L1 Server profile : {len(required)}")
    print(f"Rules evaluated on this host          : {len(results)}")
    print()
    print(f"Status breakdown (vendor rules vs this host):")
    for status in ("pass", "fail", "notapplicable", "notchecked", "informational", "error", "fixed", "unknown", "not_evaluated"):
        if summary.get(status):
            covered = role_hits_by_status.get(status, 0)
            print(f"  {status:18s} : {summary[status]:4d}   (role addresses {covered})")

    total_scored = summary["pass"] + summary["fail"]
    if total_scored:
        pct = 100.0 * summary["pass"] / total_scored
        print()
        print(f"Pass rate (pass / (pass+fail)): {summary['pass']}/{total_scored} = {pct:.1f}%")

    print()
    print(f"Failing rules with NO role mention (uncovered gaps):")
    uncovered = [r for r in rows if r["status"] == "fail" and not r["role_mentions"]]
    print(f"  Count: {len(uncovered)}")
    for r in uncovered[:25]:
        print(f"  - {r['rule_id']}")
    if len(uncovered) > 25:
        print(f"  ... ({len(uncovered) - 25} more in CSV)")

    print()
    print(f"Full alignment matrix saved: {args.out}")


if __name__ == "__main__":
    main()