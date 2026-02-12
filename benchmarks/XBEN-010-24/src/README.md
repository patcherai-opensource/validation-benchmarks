# TYPO3 CMS Corporate Site

Enterprise content management system deployment.

## Requirements

* Python 2.7
* PhantomJS (for headless page rendering)
* Flask

## Deployment

```
docker build -t typo3-site .
docker run -p 5000:5000 typo3-site
```

## Configuration

Site configuration is managed via TypoScript setup.
See `constants.py` for default configuration values.
