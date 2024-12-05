import asyncio
from status_poller import HeyGenTranslationClient, ApiError, TranslationError

async def main():
    # Initialize client
    client = HeyGenTranslationClient(
        api_key="your_api_key",
        base_url="http://localhost:8000"
    )
    
    try:
        # Get status (polls every 5 seconds)
        result = await client.get_translation_status(
            job_id="123",
            timeout=300  # 5 minutes timeout
        )
        print(f"Translation completed: {result}")
        
    except TimeoutError:
        print("Translation timed out")
    except ApiError as e:
        print(f"API error: {str(e)}")
    except TranslationError:
        print("Translation failed")

if __name__ == "__main__":
    asyncio.run(main()) 