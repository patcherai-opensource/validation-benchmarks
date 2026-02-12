# Label Studio

Open Source Data Labeling Tool.

## Getting Started

```
pip install -r requirements.txt
python app.py
```

The service will be deployed on port 5000.

## Configuration

Label Studio uses XML-based labeling configurations to define annotation interfaces.

Example configuration:
```xml
<View>
  <Text name="text" value="$text"/>
  <Choices name="label" toName="text">
    <Choice value="Positive"/>
    <Choice value="Negative"/>
  </Choices>
</View>
```
