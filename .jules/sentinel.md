## 2025-05-22 - [IPFS API Security Hardening]
**Vulnerability:** Several security risks were identified in the IPFS-related components:
1. Timing Attack: Standard string comparison was used for password verification in `apps/ipfs/routers/ipfs.py`.
2. Parameter Injection/SSRF: URL query parameters were constructed using f-string interpolation instead of the `params` argument in the `requests` library.
3. Information Leakage: Internal Python exception details were returned to the user in API error responses.

**Learning:** This codebase's IPFS integration relied on string manipulation for URL construction and direct password comparison, which are common but dangerous patterns. The lack of standardized error handling across routers led to internal detail leakage.

**Prevention:**
1. Always use `secrets.compare_digest` for sensitive comparisons (passwords, tokens).
2. Use the `params` argument in `requests` calls to ensure proper URL encoding and prevent injection.
3. Catch generic exceptions in API endpoints and return sanitized, user-friendly error messages while logging the actual error internally.
