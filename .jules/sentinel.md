## 2025-05-15 - [URL Parameter Injection & Information Leakage]
**Vulnerability:** URL query parameters were constructed using f-string interpolation in 'requests' calls, and internal exception details were leaked in API error responses.
**Learning:** Manual URL construction is prone to injection if inputs contain special characters like '&' or '='. FastAPI 'Exception' handling often defaults to being too verbose if not carefully controlled.
**Prevention:** Always use the 'params' argument in 'requests' to ensure proper encoding. Use generic error messages for client responses while logging the full exception internally.

## 2025-05-16 - [IPFS DoS via Memory Exhaustion & Hanging Connections]
**Vulnerability:** IPFS API calls lacked timeouts and loaded entire file contents into memory, creating risks for Denial of Service via resource exhaustion (OOM) or thread starvation.
**Learning:** `requests.post()` without a timeout can hang indefinitely. Loading large files via `response.content` pre-allocates memory for the whole file, which is unsafe for public-facing endpoints.
**Prevention:** Always use `timeout` in `requests` calls. Use `stream=True` and `iter_content()` for file data, and ensure `response.close()` is called (especially in error paths) when streaming.
