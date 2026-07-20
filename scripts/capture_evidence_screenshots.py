from pathlib import Path
from playwright.sync_api import Locator, Page, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Workflow run _ Khuong Nguyen Dang on MindPal _ MindPal.html"
OUTPUT = ROOT / "evidence_screenshots"
CHROME = (
    Path.home()
    / "AppData/Local/ms-playwright/chromium-1097/chrome-win/chrome.exe"
)


def screenshot_element(locator: Locator, name: str) -> None:
    locator.scroll_into_view_if_needed()
    locator.screenshot(path=str(OUTPUT / name), animations="disabled")
    print(f"CREATED {name}")


def screenshot_clip(page: Page, box: dict, name: str) -> None:
    clip = {
        "x": max(0, box["x"]),
        "y": max(0, box["y"]),
        "width": min(box["width"], 1580),
        "height": min(box["height"], 15000),
    }
    page.screenshot(path=str(OUTPUT / name), clip=clip, animations="disabled")
    print(f"CREATED {name}")


def nearest_open_panel(locator: Locator) -> Locator:
    return locator.locator("xpath=ancestor::div[@data-open='true'][1]")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            executable_path=str(CHROME),
            args=["--allow-file-access-from-files"],
        )
        context = browser.new_context(
            java_script_enabled=False,
            viewport={"width": 1600, "height": 1000},
            device_scale_factor=1,
        )
        page = context.new_page()
        page.goto(SOURCE.as_uri(), wait_until="load")
        page.wait_for_timeout(300)

        # Run identity, manual trigger label and completion status.
        page.screenshot(
            path=str(OUTPUT / "run_header_manual_completed.png"),
            clip={"x": 0, "y": 0, "width": 1600, "height": 135},
            animations="disabled",
        )
        print("CREATED run_header_manual_completed.png")

        # Human-input node and required/optional fields.
        content_heading = page.get_by_text("Content Brief", exact=True).first
        content_panel = nearest_open_panel(content_heading)
        screenshot_element(content_panel, "content_brief_fields.png")

        # Tool-call sequence at the top of the market-research output.
        market_section = page.get_by_text(
            "SaaS Market Researcher", exact=True
        ).locator("xpath=ancestor::section[1]")
        market_box = market_section.bounding_box()
        screenshot_clip(
            page,
            {
                "x": market_box["x"],
                "y": market_box["y"],
                "width": market_box["width"],
                "height": 330,
            },
            "market_tool_sequence.png",
        )

        # The raw validation/rate-limit payloads only exist in serialized source
        # and do not materialize as rendered DOM elements in headless Chromium.
        # They intentionally remain raw code evidence in the report.

        # Final market report immediately after the two failed tool invocations.
        report_heading = page.get_by_text(
            "Market Research Report: AI Workflow Automation for Small Businesses",
            exact=True,
        )
        report_heading.scroll_into_view_if_needed()
        report_box = report_heading.bounding_box()
        report_scroll_y = page.evaluate("window.scrollY")
        report_document_height = page.evaluate("document.documentElement.scrollHeight")
        report_document_y = report_scroll_y + report_box["y"]
        report_height = min(
            760,
            max(1, report_document_height - report_document_y + 10),
        )
        screenshot_clip(
            page,
            {
                "x": max(0, report_box["x"] - 14),
                "y": max(0, report_document_y - 10),
                "width": 650,
                "height": report_height,
            },
            "market_report_after_tool_errors.png",
        )

        # Orchestrator worker tasks: task prompt, assigned specialist and output.
        task_names = [
            (
                "Task 1: Create Facebook Post for AI Marketing Workflows",
                "orchestrator_task_1_facebook.png",
            ),
            (
                "Task 2: Create LinkedIn Post for AI Marketing Workflows",
                "orchestrator_task_2_linkedin.png",
            ),
            (
                "Task 3: Create Newsletter for AI Marketing Workflows",
                "orchestrator_task_3_newsletter.png",
            ),
        ]
        for label, filename in task_names:
            task_heading = page.get_by_text(label, exact=True)
            task_heading.scroll_into_view_if_needed()
            task_box = task_heading.bounding_box()
            scroll_y = page.evaluate("window.scrollY")
            document_height = page.evaluate("document.documentElement.scrollHeight")
            document_y = scroll_y + task_box["y"]
            capture_height = min(980, max(1, document_height - document_y + 18))
            print(
                f"TASK CROP {filename}: y={document_y} "
                f"height={capture_height} document={document_height}"
            )
            screenshot_clip(
                page,
                {
                    "x": max(0, task_box["x"] - 55),
                    "y": max(0, document_y - 18),
                    "width": 620,
                    "height": capture_height,
                },
                filename,
            )

        browser.close()


if __name__ == "__main__":
    main()
