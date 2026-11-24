

import time
from concurrent.futures import ThreadPoolExecutor

import httpx


# Configuration
SERVICES = {
    "Service 1": "http://127.0.0.1:8001/health",
    "Service 2": "http://127.0.0.1:8002/health",
    "Service 3": "http://127.0.0.1:8003/health?delay=0.8",
}

INTERVAL_SECONDS = 2
TIMEOUT_SECONDS = 1.5
SLOW_THRESHOLD_MS = 500
FAILED_CHECKS_LIMIT = 3


def check_service(url):

    start = time.perf_counter()

    try:
        response = httpx.get(url, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()

        elapsed_ms = (time.perf_counter() - start) * 1000

        return {
            "success": True,
            "response_time": elapsed_ms,
        }

    except httpx.RequestError:
        elapsed_ms = (time.perf_counter() - start) * 1000

        return {
            "success": False,
            "response_time": elapsed_ms,
        }

    except httpx.HTTPStatusError:
        elapsed_ms = (time.perf_counter() - start) * 1000

        return {
            "success": False,
            "response_time": elapsed_ms,
        }


def main():
    failed_checks = {
        name: 0 for name in SERVICES
    }

    round_number = 0
    next_round = time.monotonic()

    print("Starting Service Health Monitor...")
   

    try:
        with ThreadPoolExecutor(
            max_workers=len(SERVICES)
        ) as executor:

            while True:
                round_number += 1

                futures = {
                    name: executor.submit(
                        check_service, url
                    )
                    for name, url in SERVICES.items()
                }

                results = {
                    name: future.result()
                    for name, future in futures.items()
                }

                output = []

                for name, result in results.items():

                    if result["success"]:
                        failed_checks[name] = 0

                        response_time = result["response_time"]

                        if response_time > SLOW_THRESHOLD_MS:
                            state = "SLOW"
                        else:
                            state = "UP"

                        output.append(
                            f"{name}: {state} "
                            f"({response_time:.1f} ms)"
                        )

                    else:
                        failed_checks[name] += 1

                        failures = failed_checks[name]

                        if failures >= FAILED_CHECKS_LIMIT:
                            state = "DOWN"
                        else:
                            state = (
                                f"WAITING "
                                f"({failures}/{FAILED_CHECKS_LIMIT})"
                            )

                        output.append(
                            f"{name}: {state}"
                        )

                print(
                    f"Round {round_number:03d} | "
                    + " | ".join(output),
                    flush=True,
                )

                next_round += INTERVAL_SECONDS
                sleep_time = next_round - time.monotonic()

                if sleep_time > 0:
                    time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nMonitor stopped.")


if __name__ == "__main__":
    main()
