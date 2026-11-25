#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
import time
from urllib.request import urlopen


SERVICES = ("gateway", "orders", "payments", "postgres", "redis")


def command(*args: str) -> str:
    result = subprocess.run(args, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def service_status(service: str) -> str:
    container_id = command("docker", "compose", "ps", "-q", service)
    if not container_id:
        return "missing"
    return command(
        "docker",
        "inspect",
        "--format",
        "{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}",
        container_id,
    )


def gateway_health() -> dict:
    with urlopen("http://127.0.0.1:8000/health", timeout=3) as response:
        return json.load(response)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the local SentinelOps foundation stack")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    deadline = time.monotonic() + args.timeout
    statuses = {}

    try:
        while time.monotonic() < deadline:
            statuses = {service: service_status(service) for service in SERVICES}
            if all(status == "healthy" for status in statuses.values()):
                health = gateway_health()
                if health.get("status") != "healthy":
                    raise RuntimeError(f"gateway reported {health}")
                print("Healthy SentinelOps stack: " + ", ".join(SERVICES))
                return 0
            time.sleep(2)
    except (OSError, subprocess.CalledProcessError, RuntimeError) as error:
        print(f"Stack verification failed: {error}", file=sys.stderr)
        return 1

    print(f"Stack did not become healthy within {args.timeout}s: {statuses}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
