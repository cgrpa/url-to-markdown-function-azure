from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from markitdown import MarkItDown, UnsupportedFormatException, FileConversionException
from urllib.parse import unquote
import asyncio
import logging

app = FastAPI(
    title="URL to Markdown API",
    description="API service to convert urls to markdown using MarkItDown",
    version="1.0.0",
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/healthz")
async def healthz():
    return Response(content="ok", media_type="text/plain")


@app.get("/{url:path}")
async def convert_url(url: str, request: Request):
    url = (
        request.url.path[1:]
        if not request.url.query
        else request.url.path[1:] + "?" + request.url.query
    )
    logger.info("Received URL path: %s", url)
    if url is None or url == "":
        return Response(
            content="Welcome to URL to Markdown API\nUsage: https://markdown.nimk.ir/YOUR_URL",
            media_type="text/plain",
        )

    decoded_url = unquote(url)
    logger.info("Decoded URL: %s", decoded_url)

    try:
        if not decoded_url.startswith(("http://", "https://")):
            if decoded_url.startswith("www."):
                decoded_url = "https://" + decoded_url
            else:
                decoded_url = "https://www." + decoded_url

        try:

            async def _convert() -> str:
                def _run():
                    instance = MarkItDown()
                    conversion_result = instance.convert(decoded_url)
                    return conversion_result.text_content

                return await asyncio.to_thread(_run)

            text_content = await asyncio.wait_for(_convert(), timeout=25)
            return Response(content=text_content, media_type="text/plain")
        except UnsupportedFormatException as e:
            raise HTTPException(
                status_code=415, detail=f"Unsupported URL format: {str(e)}"
            )
        except FileConversionException as e:
            raise HTTPException(
                status_code=400, detail=f"URL conversion failed: {str(e)}"
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504, detail="Conversion timed out. Please try again later."
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"URL processing failed: {str(e)}")
