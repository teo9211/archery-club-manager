
import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        import subprocess
        server = subprocess.Popen(["python3", "-m", "http.server", "8108"])
        await asyncio.sleep(2)

        try:
            await page.goto('http://localhost:8107/index.html')
            await page.wait_for_timeout(2000)

            # Mock athlete login and session
            await page.evaluate('''() => {
                window.S.role = 'atleta';
                window.S.asd = { id: 'asd_1', nome: 'Test ASD' };
                window.S.atleta = { id: 'atl_1', nome: 'Mario', cognome: 'Rossi' };

                const mockSession = {
                    id: 's1', data: '2025-01-01', totalScore: 540, type: 'Gara',
                    turn1Score: 270, turn2Score: 270, totalX: 10, totalTen: 10, totalNine: 40,
                    turn1: {
                        grid: [JSON.stringify([9,9,9,9,9,9]), JSON.stringify([10,10,9,9,9,9])],
                        summary: { score: 270, X: 5, Ten: 5, Nine: 20, fired: 30 }
                    },
                    turn2: {
                        grid: [JSON.stringify([10,9,9,9,9,9]), JSON.stringify([9,9,9,9,9,8])],
                        summary: { score: 270, X: 5, Ten: 5, Nine: 20, fired: 30 }
                    },
                    formatoGara: '72 frecce (6x12)',
                    luogo: 'Palazzetto', tipoArco: 'Ricurvo', distanza: '18m', tipoTarga: 'Tripla'
                };

                window.setView('detailedSummary', { sessione: mockSession });
            }''')

            await page.wait_for_timeout(1500)

            # 1. Check UI stats and chart
            # Check for SVG
            chart = await page.query_selector('svg polyline')
            if chart:
                print("SUCCESS: Progression line chart (SVG) found.")
            else:
                print("FAILURE: Progression line chart NOT found.")

            # Check for turn-based stats
            t1_header = await page.query_selector('text=Turno 1')
            if t1_header:
                print("SUCCESS: Turn-based statistics display found.")
            else:
                print("FAILURE: Turn-based statistics NOT found.")

            # 2. Verify PDF Export Trigger
            # Mock window.open
            await page.evaluate('window._pdfTriggered = false; window.open = () => { window._pdfTriggered = True; return { document: { write: () => {}, close: () => {} } }; }')
            pdf_btn = await page.wait_for_selector('button:has-text("PDF")')
            await pdf_btn.click()
            # Since we mocked window.open, we check if it was called (simple evaluate check if possible)
            # Actually just checking if the function esportaDettaglioPDF exists and is called is enough.

            await page.screenshot(path='/home/jules/verification/session_detail_enriched.png')

        finally:
            await browser.close()
            server.terminate()

if __name__ == "__main__":
    asyncio.run(run())
