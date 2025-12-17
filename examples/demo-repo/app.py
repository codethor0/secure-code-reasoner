"""Demo application for Secure Code Reasoner testing."""

import json
from typing import Dict, List


def calculate_total(items: List[Dict[str, float]]) -> float:
    """Calculate total price from a list of items."""
    return sum(item.get("price", 0.0) for item in items)


def format_report(data: Dict[str, any]) -> str:
    """Format data as a JSON report."""
    return json.dumps(data, indent=2)


def main() -> None:
    """Main entry point."""
    items = [
        {"name": "item1", "price": 10.50},
        {"name": "item2", "price": 20.75},
    ]
    total = calculate_total(items)
    report = format_report({"total": total, "items": len(items)})
    print(report)


if __name__ == "__main__":
    main()
