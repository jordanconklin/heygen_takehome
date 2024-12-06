import aiohttp
import asyncio
import random

class TranslationError(Exception):
    """Base exception class for translation-related errors"""
    def __init__(self, message, details=None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class TimeoutError(TranslationError):
    """Raised when polling exceeds the specified timeout duration"""
    def __init__(self, timeout_seconds, elapsed_time):
        message = f"Translation status polling timed out after {elapsed_time:.1f}s (timeout: {timeout_seconds}s)"
        super().__init__(message, {"timeout": timeout_seconds, "elapsed": elapsed_time})

class ApiError(TranslationError):
    """Raised when the API returns an unexpected status code"""
    def __init__(self, status_code, response_text=None):
        message = f"API request failed with status {status_code}"
        if response_text:
            message += f": {response_text}"
        super().__init__(message, {"status_code": status_code, "response": response_text})

class TranslationFailedError(TranslationError):
    """Raised when the translation process fails on the server side"""
    def __init__(self, job_id):
        message = f"Translation failed for job_id: {job_id}"
        super().__init__(message, {"job_id": job_id})

class InvalidJobIdError(TranslationError):
    """Raised when the provided job_id is invalid"""
    def __init__(self, job_id):
        message = f"Invalid job_id provided: {job_id}"
        super().__init__(message, {"job_id": job_id})

# Polls the HeyGen server for the status of a translation job
class TranslationStatusPoller:
    def __init__(self, base_url="http://localhost:8000", 
                 initial_interval=1,    # Start with 1 second
                 max_interval=30,       # Max wait of 30 seconds
                 backoff_factor=2):     # Double the interval each time
        self.base_url = base_url
        self.initial_interval = initial_interval
        self.max_interval = max_interval
        self.backoff_factor = backoff_factor
        self.current_interval = initial_interval
        self.last_poll_time = None
        self.total_elapsed_time = 0

    # Calculates the next interval with exponential backoff and jitter
    def get_next_interval(self):
        jitter = random.uniform(0, 1)   # Add randomness to avoid thundering herd
        self.current_interval = min(
            self.current_interval * self.backoff_factor + jitter,    # Add jitter to avoid thundering herd and distribute server load
            self.max_interval
        )
        return self.current_interval

    # Polls the HeyGen server for the status of a translation job
    async def poll_status(self, job_id: str, timeout: int) -> dict:
        if not job_id or not isinstance(job_id, str):
            raise InvalidJobIdError(job_id)

        # Timing variables initialized
        start_time = asyncio.get_event_loop().time()
        self.current_interval = self.initial_interval
        self.total_elapsed_time = 0
        self.last_poll_time = start_time
        
        # Polls the HeyGen server until the job is completed, fails, or times out
        async with aiohttp.ClientSession() as session:
            while True:
                current_time = asyncio.get_event_loop().time()
                elapsed = current_time - start_time
                
                # Print timing information
                if self.last_poll_time:
                    time_since_last_poll = current_time - self.last_poll_time
                    self.total_elapsed_time += time_since_last_poll
                    print(f"Time since last poll: {time_since_last_poll:.2f}s | Total elapsed: {self.total_elapsed_time:.2f}s")
                
                self.last_poll_time = current_time

                # Check for timeout
                if elapsed > timeout:
                    raise TimeoutError(timeout, elapsed)
                
                # GET request to check status
                try:
                    async with session.get(f"{self.base_url}/status/{job_id}") as response:
                        if response.status == 404:
                            raise InvalidJobIdError(job_id)
                        elif response.status != 200:
                            response_text = await response.text()
                            raise ApiError(response.status, response_text)
                        
                        # Parse the response
                        data = await response.json()
                        status = data.get("result")
                        print(f"Status: {status}")
                        
                        # Return the data if the job is completed
                        if status == "completed":
                            return data
                        elif status == "error":
                            raise TranslationFailedError(job_id)
                        
                        # Wait for the next interval
                        await asyncio.sleep(self.current_interval)
                        self.get_next_interval()
                
                # Handle network errors
                except aiohttp.ClientError as e:
                    raise ApiError(0, f"Network error: {str(e)}")

# Client for interacting with the HeyGen translation service
class HeyGenTranslationClient:
    def __init__(self, api_key="test_key", base_url="http://localhost:8000"):  # Default values for local testing
        self.api_key = api_key
        self.poller = TranslationStatusPoller(base_url)
        
    # Polls the HeyGen server for the status of a translation job
    async def get_translation_status(self, job_id, timeout=300):
        return await self.poller.poll_status(job_id, timeout)
