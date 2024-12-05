import aiohttp
import asyncio
import random

class TranslationError(Exception):
    pass

class TimeoutError(TranslationError):
    pass

class ApiError(TranslationError):
    pass

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

    def get_next_interval(self):
        # Calculate next interval with exponential backoff
        jitter = random.uniform(0, 1)
        self.current_interval = min(
            self.current_interval * self.backoff_factor + jitter,    # Add jitter to avoid thundering herd and distribute server load
            self.max_interval
        )
        return self.current_interval

    async def poll_status(self, job_id: str, timeout: int) -> dict:
        start_time = asyncio.get_event_loop().time()
        self.current_interval = self.initial_interval  # Reset interval at start
        self.total_elapsed_time = 0
        self.last_poll_time = start_time
        
        async with aiohttp.ClientSession() as session:
            while True:
                current_time = asyncio.get_event_loop().time()
                
                # Calculate time since last poll
                if self.last_poll_time:
                    time_since_last_poll = current_time - self.last_poll_time
                    self.total_elapsed_time += time_since_last_poll
                    print(f"Time since last poll: {time_since_last_poll:.2f}s | Total elapsed: {self.total_elapsed_time:.2f}s")
                
                self.last_poll_time = current_time

                # Check timeout
                if current_time - start_time > timeout:
                    raise TimeoutError("Status polling timed out")
                
                # GET request to check status
                async with session.get(f"{self.base_url}/status/{job_id}") as response:
                    if response.status != 200:
                        raise ApiError(f"API returned status {response.status}")
                    
                    data = await response.json()
                    status = data.get("result")
                    print(f"Status: {status}")
                    
                    if status == "completed":
                        return data
                    elif status == "error":
                        raise TranslationError("Translation failed")
                    
                    # Use exponential backoff for the wait interval
                    await asyncio.sleep(self.current_interval)
                    self.get_next_interval()

class HeyGenTranslationClient:
    def __init__(self, api_key="test_key", base_url="http://localhost:8000"):  # Default values for local testing
        self.api_key = api_key
        self.poller = TranslationStatusPoller(base_url)
        
    async def get_translation_status(self, job_id, timeout=300):
        return await self.poller.poll_status(job_id, timeout)
