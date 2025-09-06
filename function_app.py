import azure.functions as func
import logging
from markitdown import MarkItDown, UnsupportedFormatException, FileConversionException
from urllib.parse import unquote, urlparse
import asyncio

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route(route="healthz", methods=["GET"])
async def healthz(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        body="ok",
        status_code=200,
        mimetype="text/plain"
    )

@app.route(route="convert/{*url}", methods=["GET"])
async def convert_url(req: func.HttpRequest) -> func.HttpResponse:
    # Get URL from route parameter
    raw_url = req.route_params.get('url', '')
    logger.info("Raw URL from route params: %s", raw_url)
    
    if not raw_url:
        return func.HttpResponse(
            body="Welcome to URL to Markdown API\nUsage: https://markdown.nimk.ir/convert/YOUR_URL",
            status_code=200,
            mimetype="text/plain"
        )

    # URL decode but don't transform
    url_to_process = unquote(raw_url).strip()
    logger.info("URL to process: %s", url_to_process)
    
    # Basic URL validation
    try:
        parsed = urlparse(url_to_process)
        if not parsed.scheme or not parsed.netloc:
            return func.HttpResponse(
                body="Invalid URL: Must include protocol (http:// or https://) and domain",
                status_code=400
            )
        
        if parsed.scheme not in ('http', 'https'):
            return func.HttpResponse(
                body="Invalid URL: Only HTTP and HTTPS protocols are supported",
                status_code=400
            )
    except Exception as e:
        return func.HttpResponse(
            body=f"URL validation failed: {str(e)}",
            status_code=400
        )
    
    try:
        # Convert to markdown using the validated but unmodified URL
        async def _convert() -> str:
            def _run():
                instance = MarkItDown()
                conversion_result = instance.convert(url_to_process)
                return conversion_result.text_content

            return await asyncio.to_thread(_run)

        text_content = await asyncio.wait_for(_convert(), timeout=25)
        return func.HttpResponse(
            body=text_content,
            status_code=200,
            mimetype="text/plain"
        )
    except UnsupportedFormatException as e:
        return func.HttpResponse(
            body=f"Unsupported URL format: {str(e)}",
            status_code=415
        )
    except FileConversionException as e:
        return func.HttpResponse(
            body=f"URL conversion failed: {str(e)}",
            status_code=400
        )
    except asyncio.TimeoutError:
        return func.HttpResponse(
            body="Conversion timed out. Please try again later.",
            status_code=504
        )
    except Exception as e:
        return func.HttpResponse(
            body=f"Internal server error: {str(e)}",
            status_code=500
        )

# Add a default route to handle the root URL
@app.route(route="", methods=["GET"])
async def root(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        body="Welcome to URL to Markdown API\nUsage: https://github.com/cgrpa/url-to-markdown-function-azure/blob/main/README.md",
        status_code=200,
        mimetype="text/plain"
    )