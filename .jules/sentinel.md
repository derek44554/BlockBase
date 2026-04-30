## 2025-05-15 - [URL Parameter Injection & Information Leakage]
**Vulnerability:** URL query parameters were constructed using f-string interpolation in 'requests' calls, and internal exception details were leaked in API error responses.
**Learning:** Manual URL construction is prone to injection if inputs contain special characters like '&' or '='. FastAPI 'Exception' handling often defaults to being too verbose if not carefully controlled.
**Prevention:** Always use the 'params' argument in 'requests' to ensure proper encoding. Use generic error messages for client responses while logging the full exception internally.

## 2025-05-20 - [OOM DoS via Large File Retrieval]
**Vulnerability:** IPFS file retrieval endpoints were loading entire files into memory and had no timeouts, leading to potential OOM crashes and resource exhaustion.
**Learning:** Default 'requests' behavior is synchronous and non-timeout, which is dangerous for large data streams. 'StreamingResponse' must be used with a generator and 'try...finally' to ensure proper resource cleanup.
**Prevention:** Always use 'stream=True', 'timeout', and 'response.close()' when handling external file streams. Use 'iter_content' to process data in chunks.
