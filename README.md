# URL to Markdown API

A powerful FastAPI service that converts web content from URLs into clean, readable Markdown format. This service is built using the MarkItDown library and provides a simple HTTP API endpoint for converting various web content types.

## Features

- Convert web pages to clean Markdown
- Support for various content types including:
  - Web articles
  - YouTube videos
  - PDF documents
- Automatic URL protocol handling
- Clean error handling with appropriate HTTP status codes

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Start the server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoint

```
GET /{url}
```

The URL should be URL-encoded if it contains special characters.

### Example Use Cases

1. **Converting YouTube Videos**

   ```
   GET http://localhost:8000/www.youtube.com/watch?v=dQw4w9WgXcQ
   ```

   This will return the video title, description, and metadata in Markdown format.

2. **Converting PDF Documents**

   ```
   GET http://localhost:8000/https://pdfobject.com/pdf/sample.pdf
   ```

   This will convert the PDF content into readable Markdown text.

3. **Converting Web Articles**
   ```
   GET http://localhost:8000/https://dev.to/iw4p/scraping-tweets-without-twitter-api-and-free-5g9c
   ```
   This will convert the article content into clean Markdown format.

### Response Format

Successful response: Plain text Markdown content

```markdown
# Article Title

## Content

[Article content in Markdown format]
```

### Error Responses

- `400`: URL processing failed
- `415`: Unsupported URL format
- `500`: Internal server error

## Development

This project uses:

- FastAPI for the web framework
- MarkItDown for content conversion
- Python 3.12+

## License

MIT License
