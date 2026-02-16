# DataSheet Format Toolkit

Interactive number format wizards for spreadsheet development.

## Requirements

* Python 2.7
* Flask
* PhantomJS (for format preview rendering)

## Running

```
pip install -r requirements.txt
python -m flask run --host=0.0.0.0 --port=5000
```

## Available Wizards

- **Numeric** - Basic number formatting with decimal places and thousands separators
- **Accounting** - Currency and accounting format patterns
- **Percent** - Percentage display formatting
- **Scientific** - Scientific notation formatting
