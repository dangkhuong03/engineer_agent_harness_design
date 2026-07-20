from pathlib import Path
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "Reverse Engineer Agent Harness Design of PAL.html"
CHROME = (
    Path.home()
    / "AppData/Local/ms-playwright/chromium-1097/chrome-win/chrome.exe"
)


def main() -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            executable_path=str(CHROME),
            args=["--allow-file-access-from-files"],
        )
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto(REPORT.as_uri(), wait_until="load")
        page.wait_for_timeout(500)

        images = page.locator("figure.evidence-shot img")
        records = []
        for index in range(images.count()):
            records.append(
                images.nth(index).evaluate(
                    """img => ({
                      src: img.getAttribute("src"),
                      complete: img.complete,
                      naturalWidth: img.naturalWidth,
                      naturalHeight: img.naturalHeight
                    })"""
                )
            )

        missing = [
            item
            for item in records
            if not item["complete"] or item["naturalWidth"] == 0
        ]
        print(f"EVIDENCE IMAGES: {len(records)}")
        for item in records:
            print(
                f"  {item['src']} "
                f"{item['naturalWidth']}x{item['naturalHeight']}"
            )
        print(f"REMAINING PRE BLOCKS: {page.locator('pre').count()}")
        if missing:
            raise RuntimeError(f"Images failed to load: {missing}")
        browser.close()


if __name__ == "__main__":
    main()
