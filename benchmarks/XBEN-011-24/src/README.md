# OpenFAQ

A lightweight FAQ and knowledge base management system.

## Features

- Browse and search FAQs by category
- Share FAQ entries with friends via email
- Export FAQ data in multiple formats (HTML, PDF, JSON)
- Multi-language support

## Requirements

- Python 2.7
- Flask
- PhantomJS (for PDF export functionality)

## Running

```
flask run
```

The service will be available on port 5000.

## API Endpoints

- `/` - Home page
- `/faq` - Browse all FAQs
- `/faq/<id>` - View specific FAQ
- `/send2friend` - Share FAQ with a friend
- `/export` - Export FAQ data
