## 2025-05-22 - API Information Leakage in IPFS Router
**Vulnerability:** API endpoints in `apps/ipfs/routers/ipfs.py` were found leaking internal exception details (e.g., `f"上传失败: {exc}"`) in error responses.
**Learning:** Returning raw exception messages to the user can expose sensitive internal system details like file paths or database schemas.
**Prevention:** Always log the detailed exception server-side and return generic, non-informative error messages to the client.

## 2025-05-22 - Timing Attack Vulnerability in Password Comparison
**Vulnerability:** Direct string comparison (`password != ipfs_password`) was used for password validation in `apps/ipfs/routers/ipfs.py`.
**Learning:** Non-constant-time comparison allows attackers to potentially deduce the password by measuring response times.
**Prevention:** Use `secrets.compare_digest` for all sensitive comparisons (passwords, tokens, etc.).

## 2025-05-22 - Insecure URL Construction in IPFS API Calls
**Vulnerability:** IPFS API URLs were constructed using f-strings for query parameters (e.g., `f"{ipfs_api}/cat?arg={cid}"`).
**Learning:** Manual URL construction is error-prone and can lead to malformed URLs or potential injection if parameters aren't properly encoded.
**Prevention:** Use the `params` argument in the `requests` library to ensure safe and automatic URL encoding of query parameters.
