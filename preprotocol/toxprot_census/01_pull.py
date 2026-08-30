#!/usr/bin/env python3
"""
01_pull.py — Download all Swiss-Prot toxin entries (KW-0800) from UniProt.

No model data is touched here. This script is model-blind.

Outputs (data/):
  raw_toxprot.jsonl       — one JSON object per entry (raw API responses)
  raw_toxprot_meta.json   — pull provenance (query, timestamp, count)

The raw file is the permanent record. All downstream scripts derive from it.
Do not re-pull mid-census.
"""

import json, time, sys, datetime, requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import DATA_DIR, UNIPROT_QUERY, UNIPROT_FIELDS, UNIPROT_PAGE_SIZE

BASE_URL = "https://rest.uniprot.org/uniprotkb/search"


def _next_link(headers: dict) -> str | None:
    """Extract the rel="next" URL from UniProt's RFC 8288 Link header.

    Do not split on commas because the URL contains a comma-separated
    fields parameter.
    """
    import re

    link = headers.get("Link", "")
    match = re.search(r'<([^>]+)>\s*;\s*rel="next"', link)
    return match.group(1) if match else None


def pull() -> int:
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    out_path  = Path(DATA_DIR) / "raw_toxprot.jsonl"
    meta_path = Path(DATA_DIR) / "raw_toxprot_meta.json"

    if out_path.exists():
        print(f"WARNING: {out_path} already exists. Delete it to re-pull.")
        sys.exit(1)

    params = {
        "query":  UNIPROT_QUERY,
        "fields": ",".join(UNIPROT_FIELDS),
        "format": "json",
        "size":   UNIPROT_PAGE_SIZE,
    }

    total_api, entries, page = "?", [], 0
    url = BASE_URL

    print(f"Query : {UNIPROT_QUERY}")
    print(f"Fields: {len(UNIPROT_FIELDS)} fields")

    while url:
        resp = requests.get(
            url,
            params=params if page == 0 else None,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()

        batch = data.get("results", [])
        entries.extend(batch)

        if page == 0:
            total_api = resp.headers.get("X-Total-Results", "?")
            print(f"API reports {total_api} total entries")

        print(f"  Page {page + 1:>4}: {len(batch):>5} entries  "
              f"(cumulative {len(entries):>6})", flush=True)

        url    = _next_link(resp.headers)
        params = None   # subsequent pages use the full URL from Link header
        page  += 1

        if url:
            time.sleep(0.4)   # be a polite client

    # ── write JSONL ──────────────────────────────────────────────────────────
    with open(out_path, "w") as fh:
        for entry in entries:
            fh.write(json.dumps(entry) + "\n")

    meta = {
        "query":           UNIPROT_QUERY,
        "fields":          UNIPROT_FIELDS,
        "pulled_at_utc":   datetime.datetime.utcnow().isoformat() + "Z",
        "api_total":       total_api,
        "entries_written": len(entries),
        "page_size":       UNIPROT_PAGE_SIZE,
        "output_file":     str(out_path),
    }
    with open(meta_path, "w") as fh:
        json.dump(meta, fh, indent=2)

    print(f"\nWrote {len(entries)} entries → {out_path}")
    print(f"Provenance → {meta_path}")
    return len(entries)


if __name__ == "__main__":
    pull()
