import logging
import asyncio
import httpx
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

    async def _download_direct_pdf(self, url: str) -> Optional[bytes]:
        """Try to download PDF directly if Content-Type matches."""
        try:
            async with httpx.AsyncClient() as client:
                # Use stream=True to peek at headers without downloading body yet
                async with client.stream("GET", url, follow_redirects=True) as resp:
                    resp.raise_for_status()
                    content_type = resp.headers.get("content-type", "").lower()
                    if "application/pdf" in content_type:
                        logger.info(f"Target is already a PDF ({content_type}). Downloading directly...")
                        content = await resp.aread()
                        return content
        except Exception as e:
            logger.warning(f"Failed to check/download direct PDF: {e}")
        return None

    async def generate_pdf(self, html_url: str) -> bytes:
        """
        Generate PDF from a URL.
        1. Check if URL is already a PDF -> Download directly.
        2. Else -> Render HTML with Playwright.
        """
        # 1. Direct PDF Check
        direct_pdf_bytes = await self._download_direct_pdf(html_url)
        if direct_pdf_bytes:
            # Upload to S3 (Mock) and return
            await self._upload_to_s3(direct_pdf_bytes, f"doc_downloaded_{asyncio.get_event_loop().time()}.pdf")
            return direct_pdf_bytes

        # 2. Playwright Render
        browser = await self._get_browser()
        context = await browser.new_context()
        page = await context.new_page()

        try:
            logger.info(f"Navigating to {html_url}")
            await page.goto(html_url, wait_until="networkidle")

            # Check for mermaid diagrams
            content = await page.content()
            if "mermaid" in content:
                logger.info("Mermaid diagrams detected, waiting for render...")
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
        await asyncio.sleep(0.01)

pdf_service = PDFService()
