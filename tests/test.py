import asyncio
import sys
import os

# Add project root directory to sys.path to allow importing rfp_agent
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../rfp_agent/.env"))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
from google.genai import types

# Import the root agent from the agent package
from rfp_agent.agent import root_agent

async def run_test_queries(queries: list[str]):
    """Runs a series of predefined queries sequentially against the root agent."""
    
    # Setup in-memory services
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    memory_service = InMemoryMemoryService()
    credential_service = InMemoryCredentialService()
    
    # Create the child session
    user_id = "test_user"
    app_name = "rfp_agent"
    session = await session_service.create_session(app_name=app_name, user_id=user_id)
    
    # Initialize the Runner
    runner = Runner(
        app_name=app_name,
        agent=root_agent,
        artifact_service=artifact_service,
        session_service=session_service,
        memory_service=memory_service,
        credential_service=credential_service,
    )
    
    print(f"--- Starting Agent Test Session (ID: {session.id}) ---")
    
    for query in queries:
        print(f"\n[user]: {query}")
        
        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=query)]
        )
        
        # Run the agent asynchronously
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=content
        ):
            if event.content and event.content.parts:
                author = event.author or "agent"
                text = "".join(part.text or "" for part in event.content.parts if not part.thought)
                if text.strip():
                    print(f"[{author}]: {text}")
                    
    print("\n--- Test Session Completed ---")
    await runner.close()

if __name__ == "__main__":
    # EDIT THIS ARRAY: Predefine your test queries here!
    TEST_INPUTS = [
        "Hello! I need help responding to an RFP.",
        "The prospect client is 'H&R Block'. Let's research them.",
        "Let's generate the RFP response document now.",
    ]
    
    asyncio.run(run_test_queries(TEST_INPUTS))
