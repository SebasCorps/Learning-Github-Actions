import os
import json
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# ✅ Base URL from environment variable
BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:5000")


@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()

    # ✅ CI-safe Chrome flags
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # ✅ Use Chromium (self-hosted runner is arm64; Google Chrome has no linux-arm64 build)
    options.binary_location = "/usr/bin/chromium"

    # ✅ Use the system chromedriver (matches the arm64 Chromium package;
    # Google's Chrome-for-Testing feed has no linux-arm64 chromedriver)
    service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()


def test_homepage_loads(driver):
    driver.get(BASE_URL)
    body_text = driver.find_element(By.TAG_NAME, "body").text
    data = json.loads(body_text)
    assert data["message"] == "Welcome to Task Manager API"


def test_get_tasks(driver):
    driver.get(f"{BASE_URL}/tasks")
    body_text = driver.find_element(By.TAG_NAME, "body").text
    tasks = json.loads(body_text)
    assert isinstance(tasks, list)
    assert len(tasks) >= 2
    assert any(task["title"] == "Learn GitHub Actions" for task in tasks)


def test_add_task_via_api(driver):
    driver.get(BASE_URL)

    # ✅ Add task via JS fetch (app has no add-task form in the UI)
    driver.execute_script(
        """
        fetch('/tasks', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({title: 'Learn Selenium'})
        });
        """
    )
    time.sleep(1)

    driver.get(f"{BASE_URL}/tasks")
    body_text = driver.find_element(By.TAG_NAME, "body").text
    tasks = json.loads(body_text)

    assert any(task["title"] == "Learn Selenium" for task in tasks)


# ✅ Capture screenshot on failure
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver")
        if driver:
            os.makedirs("reports", exist_ok=True)
            driver.save_screenshot("reports/failure.png")
