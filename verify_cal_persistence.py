
import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        import subprocess
        server = subprocess.Popen(["python3", "-m", "http.server", "8105"])
        await asyncio.sleep(2)

        try:
            await page.goto('http://localhost:8105/index.html')
            await page.wait_for_timeout(2000)

            # Mock athlete login and session for detail view
            await page.evaluate('''() => {
                window.S.role = 'atleta';
                window.S.asd = { id: 'asd_1', nome: 'Test ASD' };
                window.S.atleta = { id: 'atl_1', nome: 'Mario', cognome: 'Rossi' };
                window.S.sessioni = [
                    { id: 's1', data: '2025-01-01', totalScore: 500, type: 'Gara', archerId: 'atl_1' }
                ];
                window.loadAtletaSessioni = async () => {};
                window.setView('atletaCalendario');
            }''')

            await page.wait_for_timeout(1000)

            # 1. Change month (click Prec twice to go back 2 months)
            await page.click('text=Prec.')
            await page.wait_for_timeout(300)
            await page.click('text=Prec.')
            await page.wait_for_timeout(300)

            month_before = await page.inner_text('#cal-title')
            print(f"Month before navigation: {month_before}")

            # 2. Open session detail (mocking selection of session s1)
            await page.evaluate('window.setView("detailedSummary", {sessionId: "s1"})')
            await page.wait_for_timeout(1000)

            # 3. Go back
            await page.evaluate('window._navGoBack()')
            await page.wait_for_timeout(1000)

            month_after = await page.inner_text('#cal-title')
            print(f"Month after returning: {month_after}")

            if month_before == month_after:
                print("SUCCESS: Calendar state preserved.")
            else:
                print(f"FAILURE: Month changed. Before: {month_before}, After: {month_after}")

            await page.screenshot(path='/home/jules/verification/cal_persistence_verify.png')

        finally:
            await browser.close()
            server.terminate()

if __name__ == "__main__":
    asyncio.run(run())
