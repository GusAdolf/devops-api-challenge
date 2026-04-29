from __future__ import annotations

import argparse
import uuid
from datetime import UTC, datetime, timedelta

import jwt


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a unique JWT for /DevOps")
    parser.add_argument("--secret", default="change-me-in-production")
    parser.add_argument("--subject", default="devops-client")
    parser.add_argument("--ttl", type=int, default=300)
    args = parser.parse_args()

    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": args.subject,
            "jti": str(uuid.uuid4()),
            "iat": now,
            "exp": now + timedelta(seconds=args.ttl),
        },
        args.secret,
        algorithm="HS256",
    )
    print(token)


if __name__ == "__main__":
    main()
