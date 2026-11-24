from reports.generator import ReportGenerator
def test_reports(tmp_path):
    r=ReportGenerator(tmp_path)
    assert r.json_report("sample",{"ok":True}).endswith("sample.json")
    assert r.html_report("sample",{"ok":True}).endswith("sample.html")
