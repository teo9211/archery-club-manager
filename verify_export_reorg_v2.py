
import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        import subprocess
        server = subprocess.Popen(["python3", "-m", "http.server", "8090"])
        await asyncio.sleep(2)

        try:
            await page.goto('http://localhost:8090/index.html')
            await page.wait_for_selector('#main-view')

            # Mock athlete login
            await page.evaluate('''() => {
                window.S.role = 'atleta';
                window.S.asd = { id: 'asd_1', nome: 'Test ASD' };
                window.S.atleta = { id: 'atl_1', nome: 'Mario', cognome: 'Rossi' };
                window.S.sessioni = [];
                window.setView('atletaDati');
            }''')

            # Wait for content to render
            await page.wait_for_timeout(1500)

            # Use specific button selector if possible or wait for text
            report_btn = await page.wait_for_selector('button:has-text("Report")')
            agenda_btn = await page.wait_for_selector('button:has-text("Agenda")')

            if report_btn and agenda_btn:
                print("SUCCESS: Report and Agenda buttons found in session summary.")

                # Test Report Modal
                await report_btn.click()
                await page.wait_for_selector('#modal-title')
                modal_title = await page.inner_text('#modal-title')
                if "Opzioni Report" in modal_title:
                    print("SUCCESS: Report modal opened.")
                else:
                    print(f"FAILURE: Report modal title mismatch: {modal_title}")
                await page.click('text=Annulla')
                await page.wait_for_timeout(300)

                # Test Agenda Modal
                await agenda_btn.click()
                await page.wait_for_selector('#modal-title')
                modal_title = await page.inner_text('#modal-title')
                if "Opzioni Agenda" in modal_title:
                    print("SUCCESS: Agenda modal opened.")
                else:
                    print(f"FAILURE: Agenda modal title mismatch: {modal_title}")
                await page.click('text=Annulla')
            else:
                print("FAILURE: Report or Agenda buttons NOT found.")

        finally:
            await browser.close()
            server.terminate()

if __name__ == "__main__":
    asyncio.run(run())
