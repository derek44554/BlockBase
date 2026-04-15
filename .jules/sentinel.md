## 2025-05-15 - [IPFS API Security Enhancements]
**Vulnerability:**
1. Potential URL manipulation via f-string interpolation for IPFS CID parameters.
2. Timing attacks on password verification using standard equality operator.
3. Information leakage through detailed exception messages in error responses.

**Learning:**
The application interactively calls an internal IPFS API. Using string formatting for these URLs can lead to unexpected behavior or injection if input isn't strictly validated. Standard string comparison is vulnerable to timing attacks. Detailed error messages are helpful for debugging but risky in production as they reveal internal state.

**Prevention:**
Always use the `params` argument in `requests` for query parameters to ensure proper encoding and separation. Use `secrets.compare_digest` for security-sensitive comparisons. Log detailed errors internally but return generic messages to the client.
