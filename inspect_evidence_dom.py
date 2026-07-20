from pathlib import Path
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Workflow run _ Khuong Nguyen Dang on MindPal _ MindPal.html"


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
    page.goto(SOURCE.as_uri(), wait_until="domcontentloaded")
    page.add_style_tag(
        content="*{animation:none!important;transition:none!important}"
        "html{scroll-behavior:auto!important}"
    )

    print("TITLE", page.title())
    print("BODY", page.evaluate("({w: document.body.scrollWidth, h: document.body.scrollHeight})"))

    steps = page.locator('[aria-label^="Step "]')
    print("STEPS", steps.count())
    for index in range(steps.count()):
        step = steps.nth(index)
        print(
            "STEP",
            index + 1,
            step.get_attribute("id"),
            step.get_attribute("aria-label"),
            step.bounding_box(),
            " ".join(step.inner_text().split())[:220],
        )

    probes = [
        "Session Attributes",
        "Content Brief",
        "Ran search_workspace_tools",
        "Ran Search News and Blog Articles",
        "Validation Error: Query must be at least 1 character(s)",
        "rateLimited",
        "Market Research Report: AI Workflow Automation for Small Businesses",
        "Distribution Pack",
        "Task 1: Create Facebook Post for AI Marketing Workflows",
        "Task 2: Create LinkedIn Post for AI Marketing Workflows",
        "Task 3: Create Newsletter for AI Marketing Workflows",
        "Social Media Copywriter",
        "Email Marketing Specialist",
    ]
    for text in probes:
        locator = page.get_by_text(text, exact=True)
        print("PROBE", repr(text), "COUNT", locator.count())
        for index in range(min(locator.count(), 5)):
            item = locator.nth(index)
            print(" ", index, item.evaluate("e => e.tagName"), item.bounding_box())

    browser.close()
