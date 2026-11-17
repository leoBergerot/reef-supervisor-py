from fastapi import Request


def get_client_ip(request: Request) -> str:
    """Prefer Cloudflare's real client IP, then X-Forwarded-For, then socket peer."""
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()

    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()

    if request.client and request.client.host:
        return request.client.host

    return "unknown"
