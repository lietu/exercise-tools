import asyncio
import random
from pathlib import Path

from playwright.async_api import async_playwright, Page, TimeoutError
from rich import print
from typer import Typer

from settings import conf

HEADLESS = True
GARMIN_CONNECT_URL = "https://connect.garmin.com/modern/"

app = Typer()


async def wait():
    time = random.uniform(0.2, 3.0)
    await asyncio.sleep(time)


async def login(page: Page):
    await page.goto(GARMIN_CONNECT_URL)

    try:
        email = page.locator("input#email")
        password = page.locator("input#password")

        await email.fill(conf.GARMIN_USERNAME.get_secret_value())
        await password.fill(conf.GARMIN_PASSWORD.get_secret_value())
        await wait()

        await page.locator("button[type=submit]").click()
    except TimeoutError:
        return

    print("Logged in")

    await page.wait_for_url(GARMIN_CONNECT_URL)
    await wait()
    await wait()


async def open_activities(page: Page):
    print("Opening activities page")
    await wait()
    await page.goto(f"{GARMIN_CONNECT_URL.rstrip('/')}/activities")


async def export_activities(page: Page, target: str):
    print("Exporting activities")
    await wait()

    async with page.expect_download() as download_info:
        await page.locator("a.export-btn").click()

    download = await download_info.value
    tgt = (Path(".") / target).absolute()
    await download.save_as(tgt)
    print(f"Downloaded {tgt}")


async def run(playwright, target: str):
    print("Launching browser")
    browser = await playwright.firefox.launch(headless=HEADLESS)
    page = await browser.new_page()
    await login(page)
    await open_activities(page)
    await export_activities(page, target)


async def _main(target: str):
    async with async_playwright() as playwright:
        await run(playwright, target)


@app.command()
def download_garmin_activities(target: str = "Activities-latest.csv"):
    asyncio.run(_main(target))


if __name__ == "__main__":
    app()
