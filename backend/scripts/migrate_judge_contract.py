#!/usr/bin/env python3
"""
Migration: Enforce judge contract — function_metadata as single source of truth.
- For each problem with function_metadata: regenerate starter_code_* and driver_code_* from metadata.
- For each problem without function_metadata but with title in registry: set metadata from registry and regenerate.
Run from repo root: python -m backend.scripts.migrate_judge_contract [--dry-run] [--mongo-url URL]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from pymongo import MongoClient
from starter_template_generator import generate_starter_and_driver
from problem_metadata_registry import get_metadata
from models import ProblemFunctionMetadata


def run(dry_run: bool, mongo_url: str):
    client = MongoClient(mongo_url)
    db = client.get_database(os.environ.get("DB_NAME", "ifelse_db"))
    coll = db.problems
    updated = 0
    skipped = 0
    errors = []

    for problem in coll.find({}, {"_id": 1, "id": 1, "title": 1, "function_metadata": 1}):
        pid = problem.get("id") or problem.get("_id")
        title = (problem.get("title") or "").strip()
        meta_raw = problem.get("function_metadata")

        metadata = None
        input_spec = None

        if meta_raw and isinstance(meta_raw, dict):
            try:
                metadata = ProblemFunctionMetadata(**meta_raw)
                input_spec = [{"name": p.name, "type": p.type} for p in (metadata.parameters or [])]
            except Exception as e:
                errors.append((pid, title, f"function_metadata parse: {e}"))
                skipped += 1
                continue
        else:
            entry = get_metadata(title)
            if entry is not None:
                metadata, input_spec = entry
                if not input_spec and metadata.parameters:
                    input_spec = [{"name": p.name, "type": p.type} for p in metadata.parameters]
            else:
                skipped += 1
                continue

        if not metadata:
            skipped += 1
            continue

        try:
            generated = generate_starter_and_driver(metadata, input_spec)
        except Exception as e:
            errors.append((pid, title, str(e)))
            skipped += 1
            continue

        update = {}
        for k, v in generated.items():
            if v:
                update[k] = v
        if not update:
            skipped += 1
            continue

        if not meta_raw and metadata:
            update["function_metadata"] = metadata.model_dump()

        if dry_run:
            print(f"[dry-run] would update {pid} ({title}): {list(update.keys())}")
            updated += 1
            continue

        result = coll.update_one(
            {"id": pid},
            {"$set": update},
        )
        if result.modified_count or result.matched_count:
            updated += 1
            print(f"Updated {pid} ({title})")

    print(f"\nDone. Updated: {updated}, Skipped: {skipped}")
    if errors:
        print("Errors:")
        for pid, title, err in errors:
            print(f"  {pid} ({title}): {err}")
    return 0 if not errors else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Only print what would be updated")
    ap.add_argument("--mongo-url", default=os.environ.get("MONGO_URL", "mongodb://localhost:27017"), help="MongoDB URL")
    args = ap.parse_args()
    return run(args.dry_run, args.mongo_url)


if __name__ == "__main__":
    sys.exit(main())
