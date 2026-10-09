import google.generativeai as genai
import asyncio

async def test():
    try:
        genai.configure(api_key="AQ.Ab8RN6I8SxtqQZbn2Ywg53aWRK4J9NkYO_16fuLKIiQa8ZKTTA")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print("Error:", str(e))

asyncio.run(test())
