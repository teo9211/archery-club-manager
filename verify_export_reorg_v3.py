
import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        import subprocess
        server = subprocess.Popen(["python3", "-m", "http.server", "8091"])
        await asyncio.sleep(2)

        try:
            await page.goto('http://localhost:8091/index.html')
            await page.wait_for_selector('#main-view')

            # Mock athlete login AND dependencies
            await page.evaluate('''() => {
                window.S.role = 'atleta';
                window.S.asd = { id: 'asd_1', nome: 'Test ASD' };
                window.S.atleta = { id: 'atl_1', nome: 'Mario', cognome: 'Rossi' };
                window.S.sessioni = [];

                // Mock Firestore dependency
                window.loadAtletaSessioni = async () => [];

                window.setView('atletaDati');
            }''')

            # Wait for content to render
            await page.wait_for_timeout(1000)

            # Check for Report button
            report_btn = await page.wait_for_selector('button:has-text("Report")')
            if report_btn:
                print("SUCCESS: Report button found.")
                await report_btn.click()
                await page.wait_for_selector('#modal-title')
                print(f"SUCCESS: Modal opened: {await page.inner_text('#modal-title')}")
            else:
                print("FAILURE: Report button NOT found.")

        finally:
            await browser.close()
            server.terminate()

if __name__ == "__main__":
    asyncio.run(run())
