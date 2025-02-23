from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from markitdown import MarkItDown, UnsupportedFormatException, FileConversionException
from urllib.parse import unquote

app = FastAPI(
    title="URL to Markdown API",
    description="API service to convert urls to markdown using MarkItDown",
    version="1.0.0",
)

md = MarkItDown()


@app.get("/{url:path}")
async def convert_url(url, request: Request):
    url = (
        request.url.path[1:]
        if not request.url.query
        else request.url.path[1:] + "?" + request.url.query
    )
    print(f"Received URL: {url}")
    if url is None or url == "":
        return Response(
            content="Welcome to URL to Markdown API\nUsage: https://markdown.nimk.ir/YOUR_URL",
            media_type="text/plain",
        )

    decoded_url = unquote(url)
    print(f"Full URL received: {decoded_url}")

    try:
        if not decoded_url.startswith(("http://", "https://")):
            if decoded_url.startswith("www."):
                decoded_url = "https://" + decoded_url
            else:
                decoded_url = "https://www." + decoded_url

        try:
            result = md.convert(decoded_url)
            return Response(content=result.text_content, media_type="text/plain")
        except UnsupportedFormatException as e:
            raise HTTPException(
                status_code=415, detail=f"Unsupported URL format: {str(e)}"
            )
        except FileConversionException as e:
            raise HTTPException(
                status_code=400, detail=f"URL conversion failed: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"URL processing failed: {str(e)}")
