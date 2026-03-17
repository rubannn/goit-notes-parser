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

            # открыть страницу логина
            page.goto(self.cfg.PAGE)

            page.fill('input[name="email"]', self.cfg.USER)
            page.fill('input[name="password"]', self.cfg.PASS)

            page.click('button[type="submit"]')

            page.wait_for_timeout(3000)
            print("Successfully logged in...")

            page.goto(self.cfg.TARGET_PAGE)
            page.wait_for_load_state("load")
            page.wait_for_timeout(3000)

            print("Opened target page")

            page.wait_for_selector("ul[open] li", timeout=10000)
            items_data = []

            items = page.locator('ul[open] > li > div[data-testid^="NavigationList__ListItemContent"]')
            count = items.count()
            print('~~~~ ', count)

            for i in range(count - 1, -1, -1):
                li_div = items.nth(i)

                second_div = li_div.locator("div")
                # print(f"{i} {second_div.count()=}")
                if second_div.count() != 2:
                    continue

                title = second_div.nth(1).inner_text().strip()

                items_data.append({
                    "title": title,
                    "link": ''
                })

                # кнопка раскрытия списка (если есть)
                btn = li_div.locator('button[data-testid^="NavigationList__ListItemIcon"]')
                if btn.count() == 0:
                    continue
                print("Processing:", title)
                btn.click()
                page.wait_for_timeout(1000)

                # if btn.count() == 0:
                #     continue

                # print("Processing:", title)

                # old_url = page.url

                # btn.click()

                # # ждать смену URL (SPA)
                # page.wait_for_url(lambda url: url != old_url, timeout=5000)

                # link = page.url



                # page.go_back()
                # page.wait_for_load_state("load")            # создать папку output если её нет

            items_data.reverse()
            os.makedirs("output", exist_ok=True)
            # сохранить JSON
            with open("output/list.json", "w", encoding="utf-8") as f:
                json.dump(items_data, f, ensure_ascii=False, indent=2)

            print("Saved to output/list.json")

            page.pause()


if __name__ == "__main__":
    app_cfg = Config()
    scraper = GoITScraper(app_cfg)
    scraper.run()
