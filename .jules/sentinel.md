## 2025-05-15 - [URL Parameter Injection & Information Leakage]
**Vulnerability:** URL query parameters were constructed using f-string interpolation in 'requests' calls, and internal exception details were leaked in API error responses.
**Learning:** Manual URL construction is prone to injection if inputs contain special characters like '&' or '='. FastAPI 'Exception' handling often defaults to being too verbose if not carefully controlled.
**Prevention:** Always use the 'params' argument in 'requests' to ensure proper encoding. Use generic error messages for client responses while logging the full exception internally.

## 2025-05-20 - [DoS via Memory Exhaustion & Missing Timeouts]
**Vulnerability:** IPFS file retrieval loaded entire files into memory before chunking, risking OOM crashes. Missing timeouts on external requests could hang worker processes indefinitely.
**Learning:** External service integrations (like IPFS) must be treated as untrusted regarding response size and latency. Buffering unknown response sizes is a direct path to Denial of Service.
**Prevention:** Use `stream=True` and generators/StreamingResponse for all file-related operations. Enforce strict timeouts on all outbound `requests` calls.
