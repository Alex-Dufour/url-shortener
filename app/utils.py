from hashlib import sha256
import string
from urllib.parse import urlparse, urlunparse, quote, unquote


ALPHABET = string.digits + string.ascii_letters


def b62_encode(num: int) -> str:
    if num == 0:
        return ALPHABET[0]
    base = len(ALPHABET)
    out = []
    n = num
    while n > 0:
        n, rem = divmod(n, base)
        out.append(ALPHABET[rem])
    return ''.join(reversed(out))


def canonicalize(raw_url: str) -> str:
    raw_url = raw_url.strip()
    if not raw_url:
        raise ValueError("Empty URL")

    parsed = urlparse(raw_url, allow_fragments=True)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("URL must include scheme and host, e.g. https://example.com")

    scheme = parsed.scheme.lower()

    segments = parsed.path.split('/')
    path = '/'.join(quote(unquote(seg), safe=":@!$&'()*+,;=-._~") for seg in segments)

    new = parsed._replace(
        scheme=scheme,
        netloc=parsed.netloc,
        path=path,
        params='',
        query=parsed.query,
        fragment='',
    )
    return urlunparse(new)

def slug_for_canonical(canon: str, len: int) -> str:
    digest = sha256(canon.encode("utf-8")).digest()
    num = int.from_bytes(digest, "big")
    full = b62_encode(num)
    return full[:len]