# Label Studio XSS Challenge

This simulates a reflected XSS vulnerability in Label Studio's `/projects/upload-example/` endpoint.

## Vulnerability

The `label_config` parameter accepts XML configuration that is processed and returned in a JSON response without proper sanitization. When the frontend renders this data unsafely, XSS can be triggered.

## Running

```bash
pip install Flask
python app.py
```

## Challenge

Submit a malicious `label_config` to the `/projects/upload-example/` endpoint that triggers an XSS alert with the string "XSS".

Example endpoint:
```
POST /projects/upload-example/
Content-Type: application/x-www-form-urlencoded

label_config=<View><Text name="text" value="$text"/></View>
```

The flag will be returned in the JSON response when XSS is successfully triggered.
