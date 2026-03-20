
import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        import subprocess
        server = subprocess.Popen(["python3", "-m", "http.server", "8092"])
        await asyncio.sleep(2)

        try:
            await page.goto('http://localhost:8092/index.html')
            # Wait for any potential initial redirects to settle
            await page.wait_for_timeout(2000)

            # Force set the state and call renderAtletaDati directly
            await page.evaluate('''() => {
                window.S.role = 'atleta';
                window.S.asd = { id: 'asd_1', nome: 'Test ASD' };
                window.S.atleta = { id: 'atl_1', nome: 'Mario', cognome: 'Rossi' };
                window.S.sessioni = [];
                window.loadAtletaSessioni = async () => [];
                window.renderAtletaDati();
            }''')

            await page.wait_for_timeout(500)

            # Use query_selector instead of wait_for_selector to check immediately
            report_btn = await page.query_selector('button:has-text("Report")')
            agenda_btn = await page.query_selector('button:has-text("Agenda")')

            if report_btn and agenda_btn:
                print("SUCCESS: Report and Agenda buttons verified.")
                await report_btn.click()
                await page.wait_for_timeout(300)
                title = await page.inner_text('#modal-title')
                print(f"Modal title: {title}")
            else:
                # Debug: print main-view content
                content = await page.inner_html('#main-view')
                print(f"FAILURE: Buttons not found. content preview: {content[:100]}...")

        finally:
            await browser.close()
            server.terminate()

if __name__ == "__main__":
    asyncio.run(run())
