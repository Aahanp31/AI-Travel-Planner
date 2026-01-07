#!/usr/bin/env python3
"""
Secret Generator for AI Travel Planner
=======================================
Generates cryptographically secure secrets for production deployment.

Usage:
    python generate_secrets.py
"""

import secrets
import string

def generate_jwt_secret(length=64):
    """Generate a strong JWT secret key"""
    return secrets.token_urlsafe(length)

def generate_api_key(length=32):
    """Generate a random API key"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    print("=" * 70)
    print("🔐 AI Travel Planner - Secret Generator")
    print("=" * 70)
    print()
    print("⚠️  IMPORTANT: Keep these secrets secure!")
    print("   - Never commit them to git")
    print("   - Store them in environment variables")
    print("   - Rotate them if they are ever exposed")
    print()
    print("-" * 70)

    # Generate JWT secret
    jwt_secret = generate_jwt_secret()
    print("\n🔑 JWT Secret Key (for backend/.env):")
    print(f"   JWT_SECRET_KEY={jwt_secret}")

    # Generate share token secret
    share_secret = generate_api_key(32)
    print(f"\n🔗 Share Token Secret (optional, for backend/.env):")
    print(f"   SHARE_TOKEN_SECRET={share_secret}")

    print("\n" + "-" * 70)
    print("\n📝 Next Steps:")
    print("   1. Copy the JWT_SECRET_KEY to your backend/.env file")
    print("   2. Get new API keys:")
    print("      - Gemini AI: https://aistudio.google.com/app/apikey")
    print("      - reCAPTCHA: https://www.google.com/recaptcha/admin")
    print("      - Google OAuth: https://console.cloud.google.com/apis/credentials")
    print("      - News API: https://newsdata.io/")
    print("   3. Update all keys in backend/.env")
    print("   4. Never commit .env files to git!")
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
