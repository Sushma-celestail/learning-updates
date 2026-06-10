from __future__ import annotations

import argparse
from collections import Counter

from corrective_rag.config import Settings
from corrective_rag.corpus import load_eval_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed a Langfuse dataset from local JSONL data.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and summarize without calling Langfuse.")
    parser.add_argument("--dataset-name", default=None)
    args = parser.parse_args()

    settings = Settings.from_env()
    dataset_name = args.dataset_name or settings.langfuse_dataset_name
    items = load_eval_dataset(settings.eval_dataset_path)
    validate_dataset(items)

    if args.dry_run:
        print(f"Validated {len(items)} items for Langfuse dataset '{dataset_name}'.")
        print(f"Metadata distribution: {dict(Counter(item.get('metadata', {}).get('category', 'uncategorized') for item in items))}")
        return

    try:
        from langfuse import Langfuse
    except ImportError as exc:
        raise SystemExit(
            "Install the observability extras first: pip install -e .[observability]"
        ) from exc

    client = Langfuse()
    client.create_dataset(name=dataset_name, metadata={"use_case": "corrective-rag-observability"})
    for item in items:
        client.create_dataset_item(
            dataset_name=dataset_name,
            input=item["input"],
            expected_output=item["expected_answer"],
            metadata=item.get("metadata", {}),
        )
    client.flush()
    print(f"Seeded {len(items)} Langfuse dataset items into '{dataset_name}'.")


def validate_dataset(items: list[dict]) -> None:
    if len(items) < 30:
        raise ValueError(f"Expected at least 30 dataset items, found {len(items)}.")
    required = {"input", "expected_answer"}
    for index, item in enumerate(items, start=1):
        missing = required.difference(item)
        if missing:
            raise ValueError(f"Dataset item {index} is missing {sorted(missing)}.")


if __name__ == "__main__":
    main()
