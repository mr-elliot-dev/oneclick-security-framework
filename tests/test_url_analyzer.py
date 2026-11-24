import pytest
from modules.url_analyzer import URLAnalyzer
def test_reject_invalid_schemes():
    with pytest.raises(ValueError): URLAnalyzer().analyze("file:///etc/passwd")
def test_credential_url_rejected():
    with pytest.raises(ValueError): URLAnalyzer().analyze("https://user:pw@example.com")
def test_http_flagged():
    result=URLAnalyzer().analyze("http://example.org")
    assert "unencrypted_http" in [x["name"] for x in result["indicators"]]
