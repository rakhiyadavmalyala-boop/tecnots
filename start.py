"""One-command startup — launches all three services.

Usage: python start.py
"""

import subprocess
import sys
import time
import os


def main():
    """Start all three FastAPI services."""
    root = os.path.dirname(os.path.abspath(__file__))

    # Copy .env.example to .env if .env doesn't exist
    env_file = os.path.join(root, ".env")
    env_example = os.path.join(root, ".env.example")
    if not os.path.exists(env_file) and os.path.exists(env_example):
        import shutil
        shutil.copy(env_example, env_file)
        print("Created .env from .env.example — edit it to add your API key")

    services = [
        {
            "name": "Knowledge Brain",
            "module": "task1_knowledge_brain.main:app",
            "port": 8001,
        },
        {
            "name": "Inbox Agent",
            "module": "task2_inbox_agent.main:app",
            "port": 8002,
        },
        {
            "name": "Meeting to Scope",
            "module": "task3_meeting_scope.main:app",
            "port": 8003,
        },
    ]

    processes = []
    print("\n" + "=" * 50)
    print("AI Tech Consultant — Starting all services")
    print("=" * 50)

    for svc in services:
        print(f"\nStarting {svc['name']} on port {svc['port']}...")
        proc = subprocess.Popen(
            [
                sys.executable, "-m", "uvicorn",
                svc["module"],
                "--host", "0.0.0.0",
                "--port", str(svc["port"]),
                "--reload",
            ],
            cwd=root,
        )
        processes.append((svc["name"], proc))

    print("\n" + "=" * 50)
    print("All services started:")
    print(f"  Task 1 — Knowledge Brain:  http://localhost:8001")
    print(f"  Task 2 — Inbox Agent:      http://localhost:8002")
    print(f"  Task 3 — Meeting to Scope: http://localhost:8003")
    print(f"\nAPI docs:")
    print(f"  http://localhost:8001/docs")
    print(f"  http://localhost:8002/docs")
    print(f"  http://localhost:8003/docs")
    print("=" * 50)
    print("\nPress Ctrl+C to stop all services\n")

    try:
        while True:
            # Check if any process has died
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"\n⚠️  {name} exited with code {proc.returncode}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nShutting down all services...")
        for name, proc in processes:
            proc.terminate()
            print(f"  Stopped {name}")
        print("Done.")


if __name__ == "__main__":
    main()
