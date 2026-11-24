# Lab Assignment 1 – Is the Service Up, Slow or Down?

## Overview

This project contains a simple health monitoring system built with Python, FastAPI, and HTTPX.

The monitor checks three running services every two seconds and reports whether each service is UP, SLOW, or DOWN.

## Project Structure

```text
ASS/
├── .gitignore
├── requirements.txt
└── lab1-assignment/
    ├── service.py
    ├── monitor.py
    └── README.md
```

## Requirements

- Python 3.10 or newer
- FastAPI
- Uvicorn
- HTTPX

Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Services

Open three separate terminals and run one service in each terminal.

**Service 1 – Port 8001**

```bash
python -m uvicorn service:app --app-dir lab1-assignment --host 127.0.0.1 --port 8001
```

**Service 2 – Port 8002**

```bash
python -m uvicorn service:app --app-dir lab1-assignment --host 127.0.0.1 --port 8002
```

**Service 3 – Port 8003**

```bash
python -m uvicorn service:app --app-dir lab1-assignment --host 127.0.0.1 --port 8003
```

Each service provides a `/health` endpoint that returns its status and uptime.

## Running the Monitor

Open another terminal and run:

```bash
python lab1-assignment/monitor.py
```

The monitor checks all three services every two seconds and displays their status and response time.

## Monitor Configuration

The monitor uses the following settings:

| Setting                   |                  Value |
| ------------------------- | ---------------------: |
| Check interval            |              2 seconds |
| Request timeout           |            1.5 seconds |
| Slow response threshold   |                 500 ms |
| Failed checks before DOWN | 3 consecutive failures |
| Number of services        |                      3 |

Service 3 includes a delay of 0.8 seconds to simulate a slow service.

## Test Results

The following output was collected during the actual test. Service 1 was stopped during the monitoring process and restarted later.

```text
Starting Service Health Monitor...
Round 001 | Service 1: UP (82.0 ms) | Service 2: UP (81.6 ms) | Service 3: SLOW (881.8 ms)
Round 002 | Service 1: UP (10.4 ms) | Service 2: UP (10.2 ms) | Service 3: SLOW (811.2 ms)
Round 003 | Service 1: UP (10.9 ms) | Service 2: UP (10.7 ms) | Service 3: SLOW (820.2 ms)
Round 004 | Service 1: UP (9.9 ms) | Service 2: UP (20.4 ms) | Service 3: SLOW (811.0 ms)
Round 005 | Service 1: UP (18.0 ms) | Service 2: UP (17.8 ms) | Service 3: SLOW (818.9 ms)
Round 006 | Service 1: UP (11.2 ms) | Service 2: UP (11.2 ms) | Service 3: SLOW (810.2 ms)
Round 007 | Service 1: UP (10.7 ms) | Service 2: UP (10.7 ms) | Service 3: SLOW (811.0 ms)
Round 008 | Service 1: UP (10.7 ms) | Service 2: UP (10.6 ms) | Service 3: SLOW (810.9 ms)
Round 009 | Service 1: WAITING (1/3) | Service 2: UP (21.4 ms) | Service3: SLOW (822.2 ms)
Round 010 | Service 1: WAITING (2/3) | Service 2: UP (19.9 ms) | Service3: SLOW (810.2 ms)
Round 011 | Service 1: DOWN | Service 2: UP (20.5 ms) | Service 3: SLOW (810.6 ms)
Round 012 | Service 1: DOWN | Service 2: UP (10.1 ms) | Service 3: SLOW (820.3 ms)
Round 013 | Service 1: DOWN | Service 2: UP (10.1 ms) | Service 3: SLOW (819.9 ms)
Round 014 | Service 1: DOWN | Service 2: UP (9.9 ms) | Service 3: SLOW (820.4 ms)
Round 015 | Service 1: DOWN | Service 2: UP (19.4 ms) | Service 3: SLOW (810.5 ms)
Round 016 | Service 1: DOWN | Service 2: UP (20.3 ms) | Service 3: SLOW (821.1 ms)
Round 017 | Service 1: DOWN | Service 2: UP (19.7 ms) | Service 3: SLOW (820.7 ms)
Round 018 | Service 1: DOWN | Service 2: UP (20.8 ms) | Service 3: SLOW (821.3 ms)
Round 019 | Service 1: DOWN | Service 2: UP (40.2 ms) | Service 3: SLOW (830.9 ms)
Round 020 | Service 1: DOWN | Service 2: UP (9.5 ms) | Service 3: SLOW (811.0 ms)
Round 021 | Service 1: DOWN | Service 2: UP (20.4 ms) | Service 3: SLOW (820.9 ms)
Round 022 | Service 1: DOWN | Service 2: UP (19.8 ms) | Service 3: SLOW (810.8 ms)
Round 023 | Service 1: DOWN | Service 2: UP (10.5 ms) | Service 3: SLOW (821.1 ms)
Round 024 | Service 1: DOWN | Service 2: UP (20.6 ms) | Service 3: SLOW (820.8 ms)
Round 025 | Service 1: UP (47.9 ms) | Service 2: UP (10.3 ms) | Service 3: SLOW (825.2 ms)
Round 026 | Service 1: UP (19.7 ms) | Service 2: UP (9.7 ms) | Service 3: SLOW (810.4 ms)
Round 027 | Service 1: UP (20.9 ms) | Service 2: UP (10.2 ms) | Service 3: SLOW (821.9 ms)
Round 028 | Service 1: UP (11.1 ms) | Service 2: UP (10.5 ms) | Service 3: SLOW (811.8 ms)
Round 029 | Service 1: UP (11.0 ms) | Service 2: UP (10.5 ms) | Service 3: SLOW (821.8 ms)
Round 030 | Service 1: UP (10.0 ms) | Service 2: UP (20.2 ms) | Service 3: SLOW (810.9 ms)
Round 031 | Service 1: UP (10.0 ms) | Service 2: UP (19.6 ms) | Service 3: SLOW (810.7 ms)
Round 032 | Service 1: UP (10.9 ms) | Service 2: UP (11.2 ms) | Service 3: SLOW (812.0 ms)
Round 033 | Service 1: UP (29.3 ms) | Service 2: UP (30.0 ms) | Service 3: SLOW (810.3 ms)
Round 034 | Service 1: UP (20.1 ms) | Service 2: UP (9.4 ms) | Service 3: SLOW (810.1 ms)
Round 035 | Service 1: UP (24.5 ms) | Service 2: UP (14.2 ms) | Service 3: SLOW (819.9 ms)

Monitor stopped.
```

## Explanation of the Results

### 1. Normal operation

At the beginning, Service 1 and Service 2 responded successfully and were reported as `UP`.

Service 3 was consistently reported as `SLOW` because its response time was around 810–880 ms. This is above the 500 ms threshold.

### 2. Stopping and restarting a service

During the test, Service 1 was stopped manually.

The monitor did not report it as DOWN immediately. Instead:

- First failed check: `WAITING (1/3)`
- Second failed check: `WAITING (2/3)`
- Third failed check: `DOWN`

Service 1 remained DOWN while it was unavailable. After restarting it, the monitor detected the successful response and changed its status back to UP in Round 025.

## Improving the DOWN Detection

The monitor was improved by counting consecutive failed checks for each service.

A service is only marked as DOWN after three consecutive failures
