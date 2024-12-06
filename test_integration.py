import asyncio
import pytest
from status_poller import (
    HeyGenTranslationClient, 
    TranslationFailedError, 
    TimeoutError
)
import subprocess
import time
import os
import signal

# Tests the translation flow
@pytest.mark.asyncio
async def test_translation_flow():
    # Start server process
    server = subprocess.Popen(["python", "server.py"])
    time.sleep(2)  # Wait for server to start
    
    try:
        client = HeyGenTranslationClient(base_url="http://localhost:8000")
        
        # Test successful flow (retry up to 3 times to handle random errors)
        success = False
        for _ in range(3):
            try:
                result = await client.get_translation_status(
                    job_id="test_success",
                    timeout=60
                )
                assert result["result"] == "completed"
                success = True
                break
            except TranslationFailedError:
                continue
        
        assert success, "Failed to get a successful completion after 3 attempts"
        
        # Test timeout
        with pytest.raises(TimeoutError):
            await client.get_translation_status(
                job_id="test_timeout",
                timeout=1  # Very short timeout to trigger error
            )
            
    finally:
        # Ensure server is properly terminated
        if os.name == 'nt':  # Windows
            os.kill(server.pid, signal.CTRL_C_EVENT)
        else:  # Unix/Linux/MacOS
            server.terminate()
        server.wait()

# Run the test
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

