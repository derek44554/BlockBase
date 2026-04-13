## 2025-05-15 - [Information Leakage in API Responses]
**Vulnerability:** Raw exception messages were returned to the user in the `upload_file` endpoint.
**Learning:** Returning `f"上传失败: {exc}"` in a FastAPI `HTTPException` can leak sensitive internal state if the exception contains stack traces, database details, or file paths.
**Prevention:** Always catch broad exceptions and return a generic error message to the client. Log the specific exception details on the server for internal debugging.
