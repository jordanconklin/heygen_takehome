import asyncio
from status_poller import (
    HeyGenTranslationClient, 
    ApiError, 
    TimeoutError, 
    TranslationFailedError,
    InvalidJobIdError
)

async def main():
    # Initialize client
    client = HeyGenTranslationClient(
        api_key="your_api_key",
        base_url="http://localhost:8000"
    )
    
    try:
        # Get translation status
        result = await client.get_translation_status(
            job_id="123",
            timeout=300
        )
        print(f"Translation completed: {result}")
        
    # Handle errors
    except TimeoutError as e:
        print(f"Error: {e.message}")
        print(f"Details: Timeout was {e.details['timeout']}s")
    except ApiError as e:
        print(f"Error: {e.message}")
        print(f"Details: {e.details}")
    except TranslationFailedError as e:
        print(f"Error: {e.message}")
        print(f"Details: Job ID {e.details['job_id']} failed")
    except InvalidJobIdError as e:
        print(f"Error: {e.message}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

# Run the main function
if __name__ == "__main__":
    asyncio.run(main()) 