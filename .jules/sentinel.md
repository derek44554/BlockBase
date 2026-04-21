## 2025-05-15 - [IPFS Security Hardening]
**Vulnerability:** URL manipulation via parameter injection, internal exception leakage, and timing attack risk in IPFS endpoints.
**Learning:** Manual URL concatenation for query parameters allows attackers to inject extra parameters or malformed data if inputs aren't sanitized. Returning raw exception strings to users can expose sensitive internal system details.
**Prevention:** Always use the `params` argument in `requests` calls for automatic encoding. Use `secrets.compare_digest` for security-critical string comparisons. Mask internal exceptions with generic error messages in API responses.
