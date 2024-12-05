import aiohttp
import asyncio

class TranslationError(Exception):
    pass

class TimeoutError(TranslationError):
    pass

class ApiError(TranslationError):
    pass

class TranslationStatusPoller:
    def __init__(self, base_url="http://localhost:8000", interval=5):  # Default to localhost
        self.base_url = base_url
        self.interval = interval

    async def poll_status(self, job_id: str, timeout: int) -> dict:
        start_time = asyncio.get_event_loop().time()
        
        async with aiohttp.ClientSession() as session:
            while True:
                # Check timeout
                if asyncio.get_event_loop().time() - start_time > timeout:
                    raise TimeoutError("Status polling timed out")
                
                # Simple GET request
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
                    
                    # Simple fixed interval wait
                    await asyncio.sleep(self.interval)

class HeyGenTranslationClient:
    def __init__(self, api_key="test_key", base_url="http://localhost:8000"):  # Default values for local testing
        self.api_key = api_key
        self.poller = TranslationStatusPoller(base_url)
        
    async def get_translation_status(self, job_id, timeout=300):
        return await self.poller.poll_status(job_id, timeout)
