# URL Shortener

## Quick start (Docker)

```bash
docker build -t url-shortener .
docker run --rm -p 8000:8000 -v $(pwd)/.data:/data url-shortener
```

## Example 

```bash
curl -s -X POST http://localhost:8000/shorten \
  -H 'content-type: application/json' \
  -d '{"url":"https://medium.com/equify-tech/the-three-fundamental-stages-of-an-engineering-career-54dac732fc74"}'
```
