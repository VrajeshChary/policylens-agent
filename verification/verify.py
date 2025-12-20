from playwright.sync_api import sync_playwright

def verify_frontend():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("http://localhost:8000")

            # Use specific locator
            assert page.get_by_role("heading", name="Intelligent PolicyLens Insights").is_visible()

            page.screenshot(path="verification/landing_page.png")
            print("Landing page screenshot taken.")

        except Exception as e:
            print(f"Verification failed: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_frontend()
