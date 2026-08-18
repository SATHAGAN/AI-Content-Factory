from app.services.research.source_extract import extract_text_from_html


def test_html_extractor_removes_scripts_and_tags():
    html="""
    <html><head><style>.x{}</style></head>
    <body><h1>Hello</h1><script>alert('x')</script>
    <p>World</p></body></html>
    """
    text=extract_text_from_html(html)
    assert "Hello" in text
    assert "World" in text
    assert "alert" not in text
