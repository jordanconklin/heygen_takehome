

class TranslationError(Exception):
    pass

class TimeoutError(TranslationError):
    pass

class ApiError(TranslationError):
    pass

class TranslationStatusPoller:
    #Initialize poller with initial, max, and current interval to perform smart polling on a translation job
    def __init__(self, base_url, initial_interval=1, max_interval=30):
        self.base_url = base_url
        self.initial_interval = initial_interval
        self.max_interval = max_interval
        self.current_interval = initial_interval

    # Get the next interval based on the current interval and the max interval using exponential backoff
    def get_next_interval(self, current_interval):
    # Exponential backoff with max limit
        next_interval = min(current_interval * 2, self.max_interval)
        return next_interval


class HeyGenTranslationClient:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.poller = TranslationStatusPoller(base_url)
        
    async def get_translation_status(self, job_id, timeout=300):
        # Implementation with timeout and smart polling
        pass
