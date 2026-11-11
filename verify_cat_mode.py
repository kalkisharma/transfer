"""Headless check for the rotor report's Cat Mode.
Usage: python3 verify_cat_mode.py path/to/harrington_rotor_report.html [out_dir]
Needs: pip install playwright && playwright install chromium (or point executable_path at Chrome).
Checks: no console errors, every cat places (or is intentionally hidden), no horizontal overflow,
blade-walk frequency, and that on/off cycles leave the DOM byte-identical (spin paused)."""
import asyncio, sys, pathlib
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve()
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else '.')
URL = HTML.as_uri()

async def main():
    async with async_playwright() as p:
        chrome = next((c for c in ['/usr/bin/google-chrome', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'] if pathlib.Path(c).exists()), None)
        b = await p.chromium.launch(args=['--no-sandbox'], **({'executable_path': chrome} if chrome else {}))
        for (w, h, tag) in [(390, 844, 'mobile'), (1366, 768, 'laptop'), (1920, 1080, '1080p')]:
            pg = await b.new_page(viewport={'width': w, 'height': h})
            errs = []
            pg.on('console', lambda m: errs.append(m.text) if m.type in ('error', 'warning') else None)
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(URL); await pg.wait_for_timeout(500)
            await pg.evaluate("RotorReport.spinning && document.getElementById('spin-btn').click()")
            before = await pg.evaluate("document.body.innerHTML")
            await pg.evaluate("catMode.on()"); await pg.wait_for_timeout(300)
            await pg.evaluate("catMode.fire('cat13'); catMode.fire('cat02')"); await pg.wait_for_timeout(700)
            await pg.screenshot(path=str(OUT / f'cats_on_{tag}.png'), full_page=True)
            placed = await pg.evaluate("[...document.querySelectorAll('.cat-clip')].map(c => c.dataset.cat + (c.style.display === 'none' ? ':hidden' : ':ok'))")
            overflow = await pg.evaluate("document.documentElement.scrollWidth - innerWidth")
            await pg.evaluate("window.__bat=0; let was=false; setInterval(()=>{ const m=document.querySelector('[data-cat=cat10] .cat-mv'); const now=!!(m&&m.getAnimations().length); if(now&&!was) __bat++; was=now; },100)")
            await pg.wait_for_timeout(12000)
            bat = await pg.evaluate("__bat")
            for _ in range(4):
                await pg.evaluate("catMode.off(); catMode.on()"); await pg.wait_for_timeout(400)
            await pg.evaluate("catMode.off()")
            same = before == await pg.evaluate("document.body.innerHTML")
            dbg = await pg.evaluate("catMode._debug()")
            print(f"{tag}: placed={placed}\n  overflow_px={overflow} bat_walks_per_12s={bat} dom_identical_after_off={same} leftovers={dbg} errors={errs}")
            await pg.close()
        await b.close()

asyncio.run(main())
