## 2025-05-15 - [IPFS Module Hardening]
**Vulnerability:** API endpoints in `apps/ipfs/routers/ipfs.py` were leaking internal exception details in error responses. Insecure URL construction was also found.
**Learning:** Returning f-string formatted URLs with unsanitized user input allows for URL manipulation. Plain exceptions in FastAPI return full details to the client if not caught and transformed.
**Prevention:** Always use generic error messages for the client while logging specific errors internally. Use `params` argument in `requests` for safe URL parameter handling. Use `secrets.compare_digest` for security-sensitive comparisons.
