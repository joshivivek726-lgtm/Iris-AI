from backend.app import tools


def test_time_tool_triggers():
    result = tools.run_tools("What day is it today?")
    assert result is not None
    assert "current date" in result


def test_no_tool_for_normal_chat():
    assert tools.run_tools("Tell me a joke") is None


def test_weather_uses_city_from_message(monkeypatch):
    seen = {}

    def fake_weather(city):
        seen["city"] = city
        return "fake weather"

    monkeypatch.setattr(tools, "get_weather", fake_weather)
    assert tools.run_tools("What is the weather in Tampa?") == "fake weather"
    assert seen["city"] == "Tampa"


def test_weather_falls_back_to_default_city(monkeypatch):
    seen = {}
    monkeypatch.setattr(tools, "get_weather", lambda c: seen.setdefault("city", c))
    tools.run_tools("What is the weather like today?")
    assert seen["city"] == tools.DEFAULT_CITY


def test_search_failure_is_reported(monkeypatch):
    def boom(query):
        raise RuntimeError("network down")

    monkeypatch.setattr(tools, "web_search", boom)
    result = tools.run_tools("Search for the latest news about SpaceX")
    assert "failed" in result