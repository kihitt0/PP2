# Practice 5 – Python Regular Expressions

## Overview

This practice covers the `re` module in Python. The main project is a receipt parser that reads a real pharmacy receipt and extracts structured data using regular expressions.

## Files

| File | Description |
|---|---|
| `receipt_parser.py` | Main script – parses `raw.txt` using regex |
| `raw.txt` | Raw receipt data from EUROPHARMA pharmacy (Astana, Kazakhstan) |

## What the parser does

- Extracts all prices from the receipt
- Parses all 20 product names with quantity and unit price
- Detects prescription (`[RX]`) items
- Finds date, time, receipt number, and payment method
- Calculates and verifies the total against the receipt
- Splits the store address into parts
- Cleans up product names (collapses whitespace)
- Outputs everything as structured JSON

## Regex functions used

| Function | Purpose |
|---|---|
| `re.findall()` | Extract all price values |
| `re.search()` | Find date, time, total, VAT, payment method, receipt number |
| `re.match()` | Detect `[RX]` prescription lines |
| `re.split()` | Split address string |
| `re.sub()` | Clean whitespace in product names |

## How to run

```bash
python receipt_parser.py
```

Make sure `raw.txt` is in the same directory.

## Sample output

```
Receipt №: 2331180266
Date: 18.04.2019  Time: 11:13:58
Method: Банковская карта  Amount: 18,009.00
ИТОГО: 18,009.00
totals_match: true
Items: 20  (4 prescription)
```
