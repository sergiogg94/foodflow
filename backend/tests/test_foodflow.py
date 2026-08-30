"""FoodFlow backend test suite (NB-3).

Recreates the 29-test suite documented in
`docs/tests/implementation-t1-t10.md` (AC-1..AC-6, requirements edge cases,
ADR-1/ADR-4 error cases) and adds tests for the two review-fix behaviors:
whitespace-only recipe names are rejected (NB-1) and duplicate recipe adds to
a plan are silently deduplicated (NB-2 / ADR-5).

Run from the repository root: `python -m pytest backend/tests`.
"""

from sqlalchemy import text


def create_recipe(client, name, ingredients=None):
    resp = client.post(
        "/recipes", json={"name": name, "ingredients": ingredients or []}
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def create_plan(client, name):
    resp = client.post("/plans", json={"name": name})
    assert resp.status_code == 201, resp.text
    return resp.json()


# --- Acceptance criteria (AC-1..AC-6) -------------------------------------


def test_ac1_create_list_read(client):
    recipe = create_recipe(
        client, "Pasta Carbonara", ["pasta", "eggs", "bacon", "cheese"]
    )
    rid = recipe["id"]
    listing = client.get("/recipes").json()
    match = [r for r in listing if r["id"] == rid]
    assert len(match) == 1
    assert match[0]["name"] == "Pasta Carbonara"
    assert match[0]["ingredient_count"] == 4
    read = client.get(f"/recipes/{rid}").json()
    assert read["name"] == "Pasta Carbonara"
    assert read["ingredients"] == ["pasta", "eggs", "bacon", "cheese"]


def test_ac1_update(client):
    recipe = create_recipe(
        client, "Pasta Carbonara", ["pasta", "eggs", "bacon", "cheese"]
    )
    rid = recipe["id"]
    resp = client.patch(f"/recipes/{rid}", json={"name": "Carbonara"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Carbonara"
    assert resp.json()["ingredients"] == ["pasta", "eggs", "bacon", "cheese"]
    resp = client.patch(f"/recipes/{rid}", json={"ingredients": ["pasta", "cream"]})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Carbonara"
    assert resp.json()["ingredients"] == ["pasta", "cream"]


def test_ac1_delete(client):
    recipe = create_recipe(client, "Pasta Carbonara", ["pasta"])
    rid = recipe["id"]
    resp = client.delete(f"/recipes/{rid}")
    assert resp.status_code == 204
    assert client.get(f"/recipes/{rid}").status_code == 404


def test_ac2_shopping_list_dedup(client):
    pasta = create_recipe(
        client, "Pasta Carbonara", ["pasta", "eggs", "bacon", "cheese"]
    )
    salad = create_recipe(client, "Caesar Salad", ["lettuce", "cheese", "croutons"])
    plan = create_plan(client, "This week")
    client.patch(f"/plans/{plan['id']}", json={"add_meals": [pasta["id"], salad["id"]]})
    resp = client.post("/shopping-list", json={"plan_ids": [plan["id"]]})
    assert resp.status_code == 200
    assert resp.json()["ingredients"] == [
        "bacon",
        "cheese",
        "croutons",
        "eggs",
        "lettuce",
        "pasta",
    ]


def test_ac3_multiple_plans_history(client):
    pasta = create_recipe(client, "Pasta Carbonara", ["pasta"])
    salad = create_recipe(client, "Caesar Salad", ["lettuce"])
    week1 = create_plan(client, "This week")
    client.patch(f"/plans/{week1['id']}", json={"add_meals": [pasta["id"]]})
    week2 = create_plan(client, "Next week")
    client.patch(f"/plans/{week2['id']}", json={"add_meals": [salad["id"]]})
    plans = client.get("/plans").json()
    assert {p["name"] for p in plans} == {"This week", "Next week"}
    week1_read = client.get(f"/plans/{week1['id']}").json()
    assert [m["recipe_id"] for m in week1_read["meals"]] == [pasta["id"]]


def test_ac4_no_ingredients_tag(client):
    rice = create_recipe(client, "Plain Rice", [])
    plan = create_plan(client, "Week")
    client.patch(f"/plans/{plan['id']}", json={"add_meals": [rice["id"]]})
    plan_read = client.get(f"/plans/{plan['id']}").json()
    meal = plan_read["meals"][0]
    assert meal["recipe_id"] == rice["id"]
    assert meal["ingredient_count"] == 0
    resp = client.post("/shopping-list", json={"plan_ids": [plan["id"]]})
    assert resp.json()["ingredients"] == []


def test_ac5_concurrent_last_change_wins(client):
    recipe = create_recipe(client, "Recipe", ["a"])
    rid = recipe["id"]
    client.patch(f"/recipes/{rid}", json={"name": "Edited by A"})
    client.patch(f"/recipes/{rid}", json={"name": "Edited by B"})
    read = client.get(f"/recipes/{rid}").json()
    assert read["name"] == "Edited by B"
    assert read["ingredients"] == ["a"]


def test_ac6_plan_edit_cascades(client):
    pasta = create_recipe(
        client, "Pasta Carbonara", ["pasta", "eggs", "bacon", "cheese"]
    )
    salad = create_recipe(client, "Caesar Salad", ["lettuce", "cheese", "croutons"])
    plan = create_plan(client, "Week")
    client.patch(f"/plans/{plan['id']}", json={"add_meals": [pasta["id"], salad["id"]]})
    resp = client.patch(
        f"/plans/{plan['id']}", json={"remove_meal_ids": [salad["id"]]}
    )
    assert resp.status_code == 200
    shopping = client.post("/shopping-list", json={"plan_ids": [plan["id"]]}).json()
    assert "lettuce" not in shopping["ingredients"]
    assert "croutons" not in shopping["ingredients"]
    assert client.get(f"/recipes/{salad['id']}").status_code == 200


# --- Requirements edge cases ----------------------------------------------


def test_edge_empty_recipe_base(client):
    assert client.get("/recipes").json() == []
    plan = create_plan(client, "Empty week")
    assert client.get(f"/plans/{plan['id']}").json()["meals"] == []
    resp = client.post("/shopping-list", json={"plan_ids": [plan["id"]]})
    assert resp.json()["ingredients"] == []


def test_edge_recipe_no_ingredients(client):
    recipe = create_recipe(client, "Plain Rice", [])
    assert recipe["ingredients"] == []
    listing = client.get("/recipes").json()
    assert listing[0]["ingredient_count"] == 0


def test_edge_duplicate_ingredient_names(client):
    recipe = create_recipe(client, "Cheesy", ["cheese", "cheese"])
    assert recipe["ingredients"] == ["cheese", "cheese"]
    plan = create_plan(client, "Week")
    client.patch(f"/plans/{plan['id']}", json={"add_meals": [recipe["id"]]})
    shopping = client.post("/shopping-list", json={"plan_ids": [plan["id"]]}).json()
    assert shopping["ingredients"] == ["cheese"]


def test_edge_plan_with_no_meals(client):
    plan = create_plan(client, "Empty")
    assert client.get(f"/plans/{plan['id']}").json()["meals"] == []
    resp = client.post("/shopping-list", json={"plan_ids": [plan["id"]]})
    assert resp.json()["ingredients"] == []


def test_edge_shopping_list_multiple_plans(client):
    pasta = create_recipe(client, "Pasta Carbonara", ["pasta", "cheese"])
    salad = create_recipe(client, "Caesar Salad", ["lettuce", "cheese"])
    p1 = create_plan(client, "Week 1")
    p2 = create_plan(client, "Week 2")
    client.patch(f"/plans/{p1['id']}", json={"add_meals": [pasta["id"]]})
    client.patch(f"/plans/{p2['id']}", json={"add_meals": [salad["id"]]})
    shopping = client.post(
        "/shopping-list", json={"plan_ids": [p1["id"], p2["id"]]}
    ).json()
    assert shopping["ingredients"] == ["cheese", "lettuce", "pasta"]


def test_edge_edit_recipe_in_plan(client):
    recipe = create_recipe(client, "Pasta", ["pasta"])
    plan = create_plan(client, "Week")
    client.patch(f"/plans/{plan['id']}", json={"add_meals": [recipe["id"]]})
    client.patch(f"/recipes/{recipe['id']}", json={"ingredients": ["pasta", "garlic"]})
    shopping = client.post("/shopping-list", json={"plan_ids": [plan["id"]]}).json()
    assert shopping["ingredients"] == ["garlic", "pasta"]


def test_edge_delete_recipe_in_plan(client):
    recipe = create_recipe(client, "Pasta", ["pasta"])
    plan = create_plan(client, "Week")
    client.patch(f"/plans/{plan['id']}", json={"add_meals": [recipe["id"]]})
    client.delete(f"/recipes/{recipe['id']}")
    plan_read = client.get(f"/plans/{plan['id']}").json()
    assert plan_read["meals"] == []
    resp = client.post("/shopping-list", json={"plan_ids": [plan["id"]]})
    assert resp.json()["ingredients"] == []


def test_edge_concurrent_recipe_edits(client):
    recipe = create_recipe(client, "Recipe", ["a"])
    rid = recipe["id"]
    client.patch(f"/recipes/{rid}", json={"name": "A", "ingredients": ["a", "b"]})
    client.patch(f"/recipes/{rid}", json={"name": "B", "ingredients": ["a", "c"]})
    read = client.get(f"/recipes/{rid}").json()
    assert read["name"] == "B"
    assert read["ingredients"] == ["a", "c"]


def test_edge_concurrent_plan_edits(client):
    r1 = create_recipe(client, "Pasta", ["pasta"])
    r2 = create_recipe(client, "Salad", ["lettuce"])
    plan = create_plan(client, "Week")
    pid = plan["id"]
    client.patch(f"/plans/{pid}", json={"add_meals": [r1["id"]]})
    client.patch(f"/plans/{pid}", json={"add_meals": [r2["id"]]})
    plan_read = client.get(f"/plans/{pid}").json()
    assert {m["recipe_id"] for m in plan_read["meals"]} == {r1["id"], r2["id"]}


# --- ADR error cases (404 / 422) ------------------------------------------


def test_404_recipe_not_found(client):
    assert client.get("/recipes/999").status_code == 404
    assert client.patch("/recipes/999", json={"name": "X"}).status_code == 404
    assert client.delete("/recipes/999").status_code == 404


def test_404_plan_not_found(client):
    assert client.get("/plans/999").status_code == 404
    assert client.patch("/plans/999", json={"name": "X"}).status_code == 404
    assert client.delete("/plans/999").status_code == 404


def test_404_plan_in_shopping_list(client):
    resp = client.post("/shopping-list", json={"plan_ids": [999]})
    assert resp.status_code == 404


def test_404_add_meal_recipe_not_found(client):
    plan = create_plan(client, "Week")
    resp = client.patch(f"/plans/{plan['id']}", json={"add_meals": [999]})
    assert resp.status_code == 404
    assert "999" in resp.json()["detail"]


def test_validation_empty_recipe_name(client):
    resp = client.post("/recipes", json={"name": "", "ingredients": []})
    assert resp.status_code == 422
    resp = client.patch("/recipes/1", json={"name": ""})
    assert resp.status_code == 422


def test_validation_empty_plan_name(client):
    resp = client.post("/plans", json={"name": ""})
    assert resp.status_code == 422
    resp = client.patch("/plans/1", json={"name": ""})
    assert resp.status_code == 422


# --- ADR-1 schema and ADR-4 pragmas ---------------------------------------


def test_four_table_schema(client):
    # The client fixture re-imports app.db against the isolated temp DB, so
    # import it here (not at module level) to get the per-test engine.
    from app import db

    with db.engine.connect() as conn:
        tables = set(
            conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            ).scalars()
        )
    assert {"recipes", "recipe_ingredients", "plans", "plan_meals"} <= tables


def test_wal_and_busy_timeout_pragmas(client):
    # Same as test_four_table_schema: import app.db inside the test so the
    # engine is bound to the per-test isolated DB, not the collection-time one.
    from app import db

    with db.engine.connect() as conn:
        journal_mode = conn.execute(text("PRAGMA journal_mode")).scalar()
        busy_timeout = conn.execute(text("PRAGMA busy_timeout")).scalar()
        foreign_keys = conn.execute(text("PRAGMA foreign_keys")).scalar()
    assert str(journal_mode).lower() == "wal"
    assert busy_timeout == 5000
    assert foreign_keys == 1


# --- Developer-flagged behaviors ------------------------------------------


def test_remove_meal_ids_uses_recipe_ids(client):
    r1 = create_recipe(client, "Pasta", ["pasta"])
    r2 = create_recipe(client, "Salad", ["lettuce"])
    plan = create_plan(client, "Week")
    client.patch(f"/plans/{plan['id']}", json={"add_meals": [r1["id"], r2["id"]]})
    resp = client.patch(f"/plans/{plan['id']}", json={"remove_meal_ids": [r1["id"]]})
    assert resp.status_code == 200
    assert [m["recipe_id"] for m in resp.json()["meals"]] == [r2["id"]]


def test_remove_meal_ids_removes_single_meal(client):
    # ADR-5: a recipe appears at most once per plan, so removing a recipe id
    # removes that single meal; the recipe can still exist in other plans.
    recipe = create_recipe(client, "Pasta", ["pasta"])
    plan = create_plan(client, "Week")
    other_plan = create_plan(client, "Next week")
    client.patch(
        f"/plans/{plan['id']}", json={"add_meals": [recipe["id"], recipe["id"]]}
    )
    plan_read = client.get(f"/plans/{plan['id']}").json()
    assert len(plan_read["meals"]) == 1
    client.patch(
        f"/plans/{other_plan['id']}", json={"add_meals": [recipe["id"]]}
    )
    resp = client.patch(f"/plans/{plan['id']}", json={"remove_meal_ids": [recipe["id"]]})
    assert resp.status_code == 200
    assert resp.json()["meals"] == []
    other_read = client.get(f"/plans/{other_plan['id']}").json()
    assert [m["recipe_id"] for m in other_read["meals"]] == [recipe["id"]]


def test_shopping_list_sorted_alphabetically(client):
    recipe = create_recipe(client, "Mixed", ["zucchini", "apple", "mango"])
    plan = create_plan(client, "Week")
    client.patch(f"/plans/{plan['id']}", json={"add_meals": [recipe["id"]]})
    shopping = client.post("/shopping-list", json={"plan_ids": [plan["id"]]}).json()
    assert shopping["ingredients"] == ["apple", "mango", "zucchini"]


# --- Additional coverage from the test report scope -----------------------


def test_recipe_name_substring_filter(client):
    create_recipe(client, "Pasta Carbonara", ["pasta"])
    create_recipe(client, "Caesar Salad", ["lettuce"])
    listing = client.get("/recipes", params={"filter": "pasta"}).json()
    assert [r["name"] for r in listing] == ["Pasta Carbonara"]


def test_plan_delete(client):
    plan = create_plan(client, "Week")
    assert client.delete(f"/plans/{plan['id']}").status_code == 204
    assert client.get(f"/plans/{plan['id']}").status_code == 404


# --- New behaviors from the review fixes ----------------------------------


def test_validation_whitespace_recipe_name(client):
    # NB-1: whitespace-only recipe names are rejected with 422 on create...
    resp = client.post("/recipes", json={"name": "   ", "ingredients": []})
    assert resp.status_code == 422
    # ...and on update, while the stored name is preserved.
    recipe = create_recipe(client, "Pasta", ["pasta"])
    resp = client.patch(f"/recipes/{recipe['id']}", json={"name": "\t\n "})
    assert resp.status_code == 422
    read = client.get(f"/recipes/{recipe['id']}").json()
    assert read["name"] == "Pasta"


def test_add_meal_deduplicates_existing_recipe(client):
    # NB-2 / ADR-5: adding a recipe already in the plan is silently skipped.
    recipe = create_recipe(client, "Pasta", ["pasta"])
    plan = create_plan(client, "Week")
    resp = client.patch(f"/plans/{plan['id']}", json={"add_meals": [recipe["id"]]})
    assert resp.status_code == 200
    assert [m["recipe_id"] for m in resp.json()["meals"]] == [recipe["id"]]
    # Adding the same recipe again alongside a new one appends only the new one.
    other = create_recipe(client, "Salad", ["lettuce"])
    resp = client.patch(
        f"/plans/{plan['id']}", json={"add_meals": [recipe["id"], other["id"]]}
    )
    assert resp.status_code == 200
    assert [m["recipe_id"] for m in resp.json()["meals"]] == [
        recipe["id"],
        other["id"],
    ]
    # Duplicates within a single add_meals list are also deduped.
    resp = client.patch(
        f"/plans/{plan['id']}", json={"add_meals": [other["id"], other["id"]]}
    )
    assert resp.status_code == 200
    assert [m["recipe_id"] for m in resp.json()["meals"]] == [
        recipe["id"],
        other["id"],
    ]