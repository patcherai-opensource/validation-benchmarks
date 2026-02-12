# PhpSpreadsheet Sample Server

A lightweight Python server that hosts interactive sample scripts for the PhpSpreadsheet library, including Number Format Wizards, Chart samples, and Reader demos.

## Requirements

- Python 2.7+
- Flask
- PhantomJS (for server-side rendering validation)

## Running

```
pip install -r requirements.txt
python -m flask run --host=0.0.0.0 --port=5000
```

## Samples

- **Number Format Wizards**: Accounting, Currency, Date, Scientific
- **Charts**: Area, Bar
- **Readers**: XLSX, CSV
