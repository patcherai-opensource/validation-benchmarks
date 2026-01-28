# PhpSheet Sample Applications

Demo site for PhpSheet library - a PHP spreadsheet reading/writing library.

## Running the Demo

Requirements:
* Python with Flask
* PhantomJS for JavaScript execution tests

```
pip install Flask
python app.py
```

## Sample Applications

The `/samples` directory contains demonstration applications:

- **Engineering/Convert-Online.php** - Interactive unit conversion tool
- Various chart creation samples
- Basic spreadsheet manipulation examples

## API Endpoints

- `/api/units` - List unit categories
- `/api/units/<category>` - List units in a category

## Security Notes

This is a demonstration site. For production use, please refer to the official PhpSheet documentation for security best practices.
