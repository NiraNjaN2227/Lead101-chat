import asyncio
import httpx
import time

BASE_URL = "http://127.0.0.1:8000"

async def test_endpoint(client, text, student_id="STU20260001", session_id="test_sess"):
    start = time.time()
    try:
        response = await client.post(
            f"{BASE_URL}/api/v1/chat",
            json={
                "user_message": text,
                "student_id": student_id,
                "session_id": session_id
            }
        )
        latency = time.time() - start
        print(f"\nExample Input: '{text}'")
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Latency: {latency:.4f}s")
            print(f"Response: {data['reply'][:200]}...") # Truncate check
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Request Failed: {e}")

async def main():
    print("Waiting for server to start...")
    await asyncio.sleep(5) 
    
    async with httpx.AsyncClient() as client:
        # 1. Health
        try:
            r = await client.get(f"{BASE_URL}/api/v1/health")
            print(f"Health Check: {r.status_code} {r.json()}")
        except Exception as e:
            print(f"Health Check Failed: {e}")
            return

        # 2. Tier 1 (Context: Fees)
        await test_endpoint(client, "What are my fees?")
        
        # 3. Tier 2 (Context: General Admission)
        await test_endpoint(client, "How do I apply?")
        
        # 4. Tier 3 (LLM Fallback)
        # Note: This might fail if OpenAI key is invalid, but we'll see the error handling.
        await test_endpoint(client, "Can you analyze my academic performance and tell me if I am doing well?")

if __name__ == "__main__":
    asyncio.run(main())
