import re
import json

with open("raw.txt", encoding="utf-8") as f:
    text = f.read()

price_pattern = r"\d[\d ]*,\d{2}"
all_prices_raw = re.findall(price_pattern, text)

def parse_price(s):
    return float(s.replace(" ", "").replace(",", "."))

all_prices = [parse_price(p) for p in all_prices_raw]
print("=== re.findall() – all prices ===")
print(all_prices_raw[:10], "…")

date_pattern = r"(\d{2})\.(\d{2})\.(\d{4})\s(\d{2}:\d{2}:\d{2})"
match = re.search(date_pattern, text)
if match:
    day, month, year, time = match.groups()
    date_str = f"{day}.{month}.{year}"
    time_str = time
print("\n=== re.search() – date & time ===")
print(f"Date: {date_str}  Time: {time_str}")

receipt_match = re.search(r"Чек №(\d+)", text)
receipt_number = receipt_match.group(1) if receipt_match else "N/A"
print("\n=== re.search() – receipt number ===")
print(f"Receipt №: {receipt_number}")

payment_pattern = r"(Банковская карта|Наличные|Kaspi\s*Pay|QR)\s*:\s*([\d\s,]+)"
payment_match = re.search(payment_pattern, text, re.IGNORECASE)
if payment_match:
    payment_method = payment_match.group(1)
    payment_amount = parse_price(payment_match.group(2).strip())
else:
    payment_method = "Unknown"
    payment_amount = 0.0
print("\n=== re.search() – payment method ===")
print(f"Method: {payment_method}  Amount: {payment_amount:,.2f}")

total_match = re.search(r"ИТОГО:\s*([\d\s]+,\d{2})", text)
total = parse_price(total_match.group(1).strip()) if total_match else 0.0
print("\n=== re.search() – total ===")
print(f"ИТОГО: {total:,.2f}")

vat_match = re.search(r"НДС\s+\d+%:\s*([\d\s]*,\d{2})", text)
vat = parse_price(vat_match.group(1).strip()) if vat_match else 0.0
print("\n=== re.search() – VAT ===")
print(f"VAT 12%: {vat:,.2f}")

print("\n=== re.match() – RX items ===")
rx_items = []
for line in text.splitlines():
    if re.match(r"\[RX\]", line):
        rx_items.append(line.strip())
        print(line.strip())

lines = text.splitlines()
items = []
i = 0
item_num_re = re.compile(r"^(\d+)\.$")
qty_price_re = re.compile(r"([\d,]+)\s*x\s*([\d\s,]+)")

while i < len(lines):
    line = lines[i].strip()
    num_match = item_num_re.match(line)
    if num_match:
        num = int(num_match.group(1))
        name = lines[i + 1].strip() if i + 1 < len(lines) else ""
        qp_line = lines[i + 2].strip() if i + 2 < len(lines) else ""
        qp_match = qty_price_re.search(qp_line)
        if qp_match:
            qty = parse_price(qp_match.group(1))
            unit_price = parse_price(qp_match.group(2))
            subtotal = round(qty * unit_price, 2)
            items.append({
                "num": num,
                "name": name,
                "qty": qty,
                "unit_price": unit_price,
                "subtotal": subtotal,
                "is_rx": bool(re.match(r"\[RX\]", name)),
            })
    i += 1

addr_match = re.search(r"г\.\s*.+?(?=\nОператор)", text, re.DOTALL)
address_parts = []
if addr_match:
    raw_addr = addr_match.group(0).strip()
    address_parts = re.split(r",\s*", raw_addr)
print("\n=== re.split() – address parts ===")
print(address_parts)

for item in items:
    item["name"] = re.sub(r"\s+", " ", item["name"]).strip()
print("\n=== re.sub() – cleaned product names ===")
for item in items:
    print(f"  {item['num']:>2}. {item['name']}")

calculated_total = round(sum(item["subtotal"] for item in items), 2)

result = {
    "receipt_number": receipt_number,
    "date": date_str,
    "time": time_str,
    "store": "EUROPHARMA Астана",
    "payment_method": payment_method,
    "payment_amount": payment_amount,
    "vat_12pct": vat,
    "total_from_receipt": total,
    "calculated_total": calculated_total,
    "totals_match": abs(calculated_total - total) < 0.01,
    "items_count": len(items),
    "rx_items_count": sum(1 for it in items if it["is_rx"]),
    "items": items,
}

print("\n=== Structured JSON output ===")
print(json.dumps(result, ensure_ascii=False, indent=2))
