## 2025-05-15 - [URL Parameter Injection & Information Leakage]
**Vulnerability:** URL query parameters were constructed using f-string interpolation in 'requests' calls, and internal exception details were leaked in API error responses.
**Learning:** Manual URL construction is prone to injection if inputs contain special characters like '&' or '='. FastAPI 'Exception' handling often defaults to being too verbose if not carefully controlled.
**Prevention:** Always use the 'params' argument in 'requests' to ensure proper encoding. Use generic error messages for client responses while logging the full exception internally.
