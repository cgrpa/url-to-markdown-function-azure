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
    url = req.route_params.get('url', '')
    
    # Add query string if present in the original request
    query_params = dict(req.params)
    if query_params:
        query_string = '&'.join(f"{key}={value}" for key, value in query_params.items())
        url = f"{url}?{query_string}"
    
    logger.info("Received URL path: %s", url)
    if not url:
        return func.HttpResponse(
            body="Welcome to URL to Markdown API\nUsage: https://markdown.nimk.ir/convert/YOUR_URL",
            status_code=200,
            mimetype="text/plain"
        )

    # URL decoding and sanitization
    decoded_url = unquote(url).strip()
    logger.info("Decoded URL: %s", decoded_url)

    try:
        # Parse and validate URL
        parsed = urlparse(decoded_url)
        
        # If no scheme, add https://
        if not parsed.scheme:
            decoded_url = f"https://{decoded_url}"
            parsed = urlparse(decoded_url)
        
        # Basic validation
        if not parsed.netloc:
            return func.HttpResponse(
                body="Invalid URL: Missing domain",
                status_code=400
            )
        
        # Ensure scheme is http or https
        if parsed.scheme not in ('http', 'https'):
            return func.HttpResponse(
                body="Invalid URL: Only HTTP and HTTPS schemes are supported",
                status_code=400
            )
        
        final_url = parsed.geturl()
        logger.info("Final URL: %s", final_url)

        try:
            async def _convert() -> str:
                def _run():
                    instance = MarkItDown()
                    conversion_result = instance.convert(final_url)
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
    except Exception as e:
        return func.HttpResponse(
            body=f"URL processing failed: {str(e)}",
            status_code=400
        )

# Add a default route to handle the root URL
@app.route(route="", methods=["GET"])
async def root(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        body="Welcome to URL to Markdown API\nUsage: https://github.com/cgrpa/url-to-markdown-function-azure/blob/main/README.md",
        status_code=200,
        mimetype="text/plain"
    )