"""Safe portfolio demo: normalize fictional vendor pricing input."""
import argparse
import csv
from collections import defaultdict
from pathlib import Path

REQUIRED = {"vendor", "sku", "price", "updated_at"}


def transform(rows):
    latest = {}
    exceptions = []
    for i, row in enumerate(rows, start=2):
        vendor = row.get("vendor", "").strip()
        sku = row.get("sku", "").strip().upper()
        try:
            price = round(float(row.get("price", "")), 2)
            if not vendor or not sku or price <= 0:
                raise ValueError("missing vendor/SKU or nonpositive price")
            date = row.get("updated_at", "").strip()
            if not date or len(date) != 10 or date[4] != '-' or date[7] != '-':
                raise ValueError("invalid ISO date")
            key = (vendor, sku)
            record = {"vendor": vendor, "sku": sku, "price": f"{price:.2f}", "updated_at": date}
            if key not in latest or date >= latest[key]["updated_at"]:
                latest[key] = record
        except (TypeError, ValueError) as exc:
            exceptions.append({"row": i, "reason": str(exc), "vendor": vendor, "sku": sku})
    return sorted(latest.values(), key=lambda x:(x['vendor'], x['sku'])), exceptions


def run(source, output, exceptions_file):
    with open(source, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing headers: {sorted(missing)}")
        clean, errors = transform(reader)
    for path, fields, rows in [(output, ['vendor','sku','price','updated_at'], clean), (exceptions_file,['row','reason','vendor','sku'],errors)]:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f, fieldnames=fields)
            writer.writeheader();writer.writerows(rows)
    print(f"Exported {len(clean)} prices; {len(errors)} exceptions")

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--exceptions',required=True)
    args=parser.parse_args()
    run(args.input,args.output,args.exceptions)
