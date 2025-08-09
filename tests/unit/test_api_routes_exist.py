from importlib import reload


def test_favorites_and_recipes_routes_present(monkeypatch):
    # Ensure INTERNAL_API_TOKEN for import-time checks if any
    monkeypatch.setenv("INTERNAL_API_TOKEN", "z" * 40)

    from services.api.bot import main as api_main
    reload(api_main)

    app = api_main.app
    paths = {(route.path, tuple(sorted(route.methods or []))) for route in app.routes}

    expected = {
        ("/favorites/save", None),
        ("/favorites/list", None),
        ("/favorites/{favorite_id}", None),
        ("/recipes/save", None),
        ("/recipes/list", None),
        ("/recipes/{recipe_id}", None),
    }

    present_paths = {p for p, _ in paths}
    for p, _ in list(expected):
        assert p in present_paths, f"Route missing: {p}"
