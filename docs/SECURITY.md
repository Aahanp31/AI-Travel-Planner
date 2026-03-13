# Security

## Measures

| Layer | Implementation | Details |
|-------|---------------|---------|
| **CORS** | Whitelist-only | Only configured `FRONTEND_URLS` allowed; no wildcard origins |
| **JWT Authentication** | 1-hour token expiry | Rejects weak/default secret keys at startup (`JWT_SECRET_KEY` validation) |
| **Password Hashing** | Werkzeug `generate_password_hash` / `check_password_hash` | Bcrypt-level security with automatic salting |
| **Google OAuth 2.0** | Server-side token verification | Uses `google-auth` library to verify tokens against Google's servers |
| **Database Security** | Connection pooling with pre-ping, keepalive, SSL support | No raw SQL exposure; parameterized queries via SQLAlchemy ORM |
| **Secret Scanning** | `security_audit.py` script | Scans entire codebase for accidentally committed API keys, passwords, and credentials |
| **Centralized API Config** | Single `api.ts` config file | Environment-based URLs, no hardcoded endpoints |
| **Input Validation** | Server-side checks on all endpoints | Required field validation, email/username uniqueness, trip ownership verification |

## Secret Scanning

Run the audit script before committing:

```bash
cd backend && python scripts/security_audit.py
```

Patterns detected: Google API keys (`AIza...`), AWS access keys (`AKIA...`), database URLs with credentials, JWT secrets, auth tokens, private keys, and generic passwords.

The script also validates `.gitignore` completeness and checks `.env.example` for accidentally committed real values.

## Environment Variables

Never commit `.env` files. The `.gitignore` already excludes them. Use `.env.example` as a template and share that instead.
