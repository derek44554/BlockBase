## 2025-05-23 - [IPFS URL Parameter Injection & Info Leakage]
**Vulnerability:** User-controlled CIDs were directly interpolated into IPFS API query strings, and internal exceptions were leaked in upload error responses.
**Learning:** Common pattern in this repo is using f-strings for URL construction, which is vulnerable to parameter injection. Error handling was also inconsistent.
**Prevention:** Always use the `params` argument in `requests` calls for query parameters. Use generic error messages for 500 status codes in production-facing endpoints.
