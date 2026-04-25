## 2025-05-15 - [URL Parameter Injection & Information Leakage]
**Vulnerability:** URL query parameters were constructed using f-string interpolation in 'requests' calls, and internal exception details were leaked in API error responses.
**Learning:** Manual URL construction is prone to injection if inputs contain special characters like '&' or '='. FastAPI 'Exception' handling often defaults to being too verbose if not carefully controlled.
**Prevention:** Always use the 'params' argument in 'requests' to ensure proper encoding. Use generic error messages for client responses while logging the full exception internally.

## 2025-05-16 - [DoS via Resource Exhaustion & Information Leakage]
**Vulnerability:** Missing timeouts and lack of streaming for large IPFS files caused potential DoS and OOM crashes. Sensitive block data was leaked to standard output via `print()`.
**Learning:** Internal service calls (like IPFS) can hang or return massive data, exhausting server resources if not constrained by timeouts and streaming. Debug prints in production routers can expose sensitive user data.
**Prevention:** Implement mandatory timeouts for all external requests. Use `stream=True` and `StreamingResponse` for file transfers, ensuring connections are closed via generators. Audit and remove `print()` statements in routers.
