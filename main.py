import os
# import time
import json
from playwright.sync_api import sync_playwright


class Config:
    USER = os.environ.get("LGN", "")
    PASS = os.environ.get("PSW", "")
    PAGE = os.environ.get("PAGE", "")
    TARGET_PAGE = os.environ.get("TARGET_PAGE", "")


class GoITScraper:
    def __init__(self, config: Config):
        self.cfg = config

    def run(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(viewport={"width": 1600, "height": 900})
            page = context.new_page()

            page.goto(self.cfg.PAGE)

            page.fill('input[name="email"]', self.cfg.USER)
            page.fill('input[name="password"]', self.cfg.PASS)

            page.click('button[type="submit"]')

            # просто подождать
            page.wait_for_timeout(3000)

            print("Successfully logged in...")

            page.goto(self.cfg.TARGET_PAGE)

            page.wait_for_load_state("load")

            print("Opened target page")
            page.wait_for_timeout(5000)

            items = page.evaluate(
                """
                () => {
                    return Array.from(document.querySelectorAll('ul[open] li')).map(li => {
                        const btnEl = li.querySelector('button');
                        if (!btnEl) return null;
                        
                        const title = li.querySelector('.next-vhhssk')?.innerText.trim() || '';
                        const btn = li.querySelector('button')?.outerHTML.split('>')[0] + '>' || '';

                        return {title: title, btn: btn};
                    });
                }
                """
            )

            # создать папку output если её нет
            os.makedirs("output", exist_ok=True)

            # сохранить json
            with open("output/list.json", "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)

            print("Saved to output/list.json")

            page.pause()


if __name__ == "__main__":
    app_cfg = Config()
    scraper = GoITScraper(app_cfg)
    scraper.run()
