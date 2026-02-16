"""
Pre-configured demo applications for the DataCanvas platform.
Each demo represents an ML model showcase with its own widgets.
"""

from widgets import (
    Widget,
    TextInput,
    TextArea,
    ImageDisplay,
    Label,
    NumberInput,
    Dropdown,
    Slider,
    FileUpload,
)


class DemoApp:
    """Represents a single demo application with a set of widgets."""

    def __init__(self, title: str, description: str, theme: str = "default"):
        self.title = title
        self.description = description
        self.theme = theme
        self.widgets: dict[int, Widget] = {}
        self.fn_registry: dict[int, callable] = {}
        self._fn_counter = 0

    def add_widget(self, widget: Widget) -> Widget:
        self.widgets[widget.widget_id] = widget
        return widget

    def register_fn(self, fn, inputs=None, outputs=None):
        self._fn_counter += 1
        self.fn_registry[self._fn_counter] = {
            "fn": fn,
            "inputs": inputs or [],
            "outputs": outputs or [],
        }
        return self._fn_counter

    def get_config(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "theme": self.theme,
            "components": [w.get_config() for w in self.widgets.values()],
            "dependencies": [
                {
                    "id": fn_id,
                    "inputs": [w.widget_id for w in entry["inputs"]],
                    "outputs": [w.widget_id for w in entry["outputs"]],
                }
                for fn_id, entry in self.fn_registry.items()
            ],
        }


def sentiment_classifier(text: str) -> dict:
    """Simple sentiment classification demo."""
    positive_words = {"good", "great", "excellent", "amazing", "wonderful", "love", "happy", "best", "fantastic"}
    negative_words = {"bad", "terrible", "horrible", "awful", "worst", "hate", "sad", "poor", "disappointing"}

    words = set(text.lower().split())
    pos = len(words & positive_words)
    neg = len(words & negative_words)
    total = pos + neg

    if total == 0:
        return {"label": "Neutral", "confidence": 0.5}
    score = pos / total
    if score > 0.5:
        return {"label": "Positive", "confidence": round(score, 3)}
    elif score < 0.5:
        return {"label": "Negative", "confidence": round(1 - score, 3)}
    return {"label": "Neutral", "confidence": 0.5}


def text_summarizer(text: str, max_sentences: int = 3) -> str:
    """Simple extractive text summarization."""
    sentences = [s.strip() for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
    if len(sentences) <= max_sentences:
        return text
    scored = []
    word_freq = {}
    for s in sentences:
        for w in s.lower().split():
            word_freq[w] = word_freq.get(w, 0) + 1
    for s in sentences:
        score = sum(word_freq.get(w.lower(), 0) for w in s.split())
        scored.append((score, s))
    scored.sort(reverse=True)
    selected = scored[:int(max_sentences)]
    return ". ".join(s for _, s in selected) + "."


def image_classifier_mock(image_path: str) -> dict:
    """Mock image classification."""
    return {
        "predictions": [
            {"label": "cat", "confidence": 0.82},
            {"label": "dog", "confidence": 0.11},
            {"label": "bird", "confidence": 0.04},
            {"label": "fish", "confidence": 0.02},
            {"label": "other", "confidence": 0.01},
        ]
    }


def build_sentiment_demo() -> DemoApp:
    demo = DemoApp(
        title="Sentiment Analyzer",
        description="Analyze the sentiment of any text using our NLP model.",
        theme="soft",
    )
    text_in = demo.add_widget(
        TextArea(
            value="",
            placeholder="Enter text to analyze...",
            label="Input Text",
            lines=5,
        )
    )
    result_label = demo.add_widget(Label(value="", label="Sentiment"))
    confidence = demo.add_widget(
        NumberInput(value=0, label="Confidence", minimum=0, maximum=1, step=0.001)
    )

    def analyze(text):
        result = sentiment_classifier(text)
        return result["label"], result["confidence"]

    demo.register_fn(analyze, inputs=[text_in], outputs=[result_label, confidence])
    return demo


def build_summarizer_demo() -> DemoApp:
    demo = DemoApp(
        title="Text Summarizer",
        description="Generate concise summaries of long text passages.",
        theme="monochrome",
    )
    text_in = demo.add_widget(
        TextArea(
            value="",
            placeholder="Paste your text here...",
            label="Original Text",
            lines=10,
        )
    )
    num_sentences = demo.add_widget(
        Slider(value=3, label="Max Sentences", minimum=1, maximum=10, step=1)
    )
    summary_out = demo.add_widget(
        TextArea(value="", label="Summary", lines=5)
    )

    def summarize(text, max_s):
        return text_summarizer(text, int(max_s))

    demo.register_fn(summarize, inputs=[text_in, num_sentences], outputs=[summary_out])
    return demo


def build_image_classifier_demo() -> DemoApp:
    demo = DemoApp(
        title="Image Classifier",
        description="Upload an image to classify its contents using our vision model.",
        theme="glass",
    )
    image_in = demo.add_widget(
        FileUpload(label="Upload Image", file_types=[".jpg", ".jpeg", ".png", ".webp"])
    )
    model_choice = demo.add_widget(
        Dropdown(
            choices=["ResNet-50", "EfficientNet-B0", "ViT-Base"],
            value="ResNet-50",
            label="Model",
        )
    )
    result_out = demo.add_widget(Label(value="", label="Classification Result"))
    return demo
