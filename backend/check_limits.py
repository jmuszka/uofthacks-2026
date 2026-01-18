import os
import asyncio
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

async def check_groq():
    print("\n1. Checking GROQ...")
    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            max_retries=0
        )
        await llm.ainvoke("hi")
        print("✅ Groq OK")
    except Exception as e:
        print(f"❌ Groq FAILED: {e}")

async def main():
    await check_groq()

if __name__ == "__main__":
    asyncio.run(main())
