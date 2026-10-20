"""Pre-condition: the Todo Manager answers on /categories.

When the service is down, the autouse `service_must_be_running` fixture in conftest.py makes this test
and every other category test FAIL with a clear message, they are never skipped.
"""
import pytest

from category_support import JSON, assert_content_type


@pytest.mark.documented
def test_todo_manager_answers_on_categories(api):
    response = api.get("/categories")

    assert response.status_code == 200
    assert_content_type(response, JSON)
