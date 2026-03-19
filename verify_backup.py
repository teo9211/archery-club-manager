import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Carica la pagina (index.html locale)
        await page.goto('http://localhost:8080/index.html')

        # Aspetta che l'app si carichi
        await page.wait_for_timeout(2000)

        # Mocking S and authentication to reach settings
        # We need to be logged in as an athlete to see the settings
        await page.evaluate('''() => {
            window.S.role = 'atleta';
            window.S.asd = { id: 'test_asd', nome: 'Test ASD' };
            window.S.atleta = { id: 'test_atleta', nome: 'Mario', cognome: 'Rossi' };
            window.setView('impostazioni');
        }''')

        await page.wait_for_timeout(1000)

        # Check if Backup & Ripristino section is present
        backup_title = await page.query_selector('text=Backup & Ripristino')
        if backup_title:
            print("SUCCESS: Backup & Ripristino section found in settings.")
        else:
            print("FAILURE: Backup & Ripristino section NOT found in settings.")

        backup_btn = await page.query_selector('text=Scarica Backup Completo')
        if backup_btn:
            print("SUCCESS: 'Scarica Backup Completo' button found.")
        else:
            print("FAILURE: 'Scarica Backup Completo' button NOT found.")

        restore_btn = await page.query_selector('text=Ripristina Dati')
        if restore_btn:
            print("SUCCESS: 'Ripristina Dati' button found.")
        else:
            print("FAILURE: 'Ripristina Dati' button NOT found.")

        await page.screenshot(path='settings_backup_verify.png')
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
