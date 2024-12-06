# HeyGen Translation Status Client

A Python client library for polling HeyGen's video translation status with smart backoff strategies.

## Features

- Asynchronous status polling with exponential backoff
- Configurable timeout and polling intervals
- Jitter implementation to prevent thundering herd
- Detailed time tracking between polls
- Comprehensive error handling
- Clean async/await interface

## Installation

```bash
git clone https://github.com/jordanconklin/heygen_takehome
cd heygen_takehome
python -m venv venv
source venv/activate # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

## Implementation Details

### Exponential Backoff
- Starts with a 1-second interval
- Doubles after each attempt (with added jitter)
- Caps at 30 seconds maximum
- Includes random jitter to prevent thundering herd

### Time Tracking
- Monitors time between polls
- Tracks total elapsed time
- Provides detailed timing feedback

### Error Types
- `TimeoutError`: When polling exceeds timeout duration
- `ApiError`: For HTTP-related issues
- `TranslationError`: Base exception class for translation failures

## Quick Start

1. Start the mock server:
```bash
python server.py    # Starts the server, run in one terminal
```
2. In another terminal, run the example:
```bash
python example.py
```

## Development

The mock server simulates:
- Random job durations (15-30 seconds)
- 15% random error rate
- Realistic async behavior
