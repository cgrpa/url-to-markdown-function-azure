from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from markitdown import MarkItDown, UnsupportedFormatException, FileConversionException

app = FastAPI(
    title="URL to Markdown API",
    description="API service to convert urls to markdown using MarkItDown",
    version="1.0.0",
)

md = MarkItDown()


@app.get("/{url:path}")
async def convert_url(url: str):
    try:
        # Normalize URL format
        if not url.startswith(("http://", "https://")):
            if url.startswith("www."):
                url = "https://" + url
            else:
                url = "https://www." + url

        try:
            result = md.convert(url)
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


@app.get("/")
async def root():
    return {"message": "Welcome to URL to Markdown API"}
