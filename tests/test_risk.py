from core.risk import score_url
def test_score_caps():
    assert score_url([{"weight":90},{"weight":20}])["score"]==100
def test_levels():
    assert score_url([])["level"]=="informational"
    assert score_url([{"weight":40}])["level"]=="medium"
