import logging
import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page

logger = logging.getLogger(__name__)

class PDFService:
    _browser: Optional[Browser] = None
    _playwright = None

    async def _get_browser(self) -> Browser:
        """Singleton pattern for Playwright Browser."""
        if not self._browser:
            logger.info("Launching Playwright Browser...")
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=True)
        return self._browser

    async def close(self):
        """Cleanup browser resources."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def generate_pdf(self, html_url: str) -> bytes:
        """
        Generate PDF from a URL.
        - Wails for network idle.
        - Waits for mermaid diagrams if detected.
        - Injects print CSS.
        """
        browser = await self._get_browser()
        # Create a new context per request (isolated cookies/storage)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            logger.info(f"Navigating to {html_url}")
            await page.goto(html_url, wait_until="networkidle")

            # Check for mermaid diagrams and wait for them to render
            # Assuming mermaid diagrams have class 'mermaid' and we wait for the svg to appear inside?
            # Or just wait for the element to exist.
            # Simple heuristic: if 'mermaid' appears in content, wait a bit or wait for selector.
            content = await page.content()
            if "mermaid" in content:
                logger.info("Mermaid diagrams detected, waiting for render...")
                # Wait for at least one svg inside a mermaid div, or just a fixed delay if selector is unknown
                try:
                    await page.wait_for_selector(".mermaid svg", timeout=5000) 
                except Exception:
                    logger.warning("Timed out waiting for .mermaid svg, proceeding...")

            # Inject Print CSS
            await page.add_style_tag(content="""
                @page { margin: 20px; size: A4; }
                body { -webkit-print-color-adjust: exact; }
            """)

            # Generate PDF
            pdf_bytes = await page.pdf(format="A4", print_background=True)
            logger.info(f"PDF generated: {len(pdf_bytes)} bytes")

            # Upload to S3 (Mock)
            await self._upload_to_s3(pdf_bytes, f"doc_{asyncio.get_event_loop().time()}.pdf")

            return pdf_bytes

        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
        finally:
            await page.close()
            await context.close()

    async def _upload_to_s3(self, file_bytes: bytes, key: str):
        """Mock S3 Upload"""
        logger.info(f"MOCK UPLOAD to S3 bucket 'babuai-docs': {key}")
        # async with self.s3_client.put_object(...)
        await asyncio.sleep(0.01)

pdf_service = PDFService()
