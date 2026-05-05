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

async def run_test_queries():
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
    
    # 1. Write some mock RFP content to a text file and upload it as an artifact
    rfp_content = """
    REQUEST FOR PROPOSAL (RFP)
    Client: H&R Block
    Project: 2027 Digital Marketing & Performance Campaign
    Requirements:
    - Develop a comprehensive performance marketing strategy.
    - Drive user acquisition through targeted social media ads.
    - Leverage data-driven insights to optimize campaign performance.
    """
    
    part = types.Part.from_text(text=rfp_content)
    
    # Save the artifact to the artifact service
    await artifact_service.save_artifact(
        app_name=app_name,
        user_id=user_id,
        session_id=session.id,
        filename="rfp_document.txt",
        artifact=part
    )
    
    # Initialize the Runner
    runner = Runner(
        app_name=app_name,
        agent=root_agent,
        artifact_service=artifact_service,
        session_service=session_service,
        memory_service=memory_service,
        credential_service=credential_service,
    )
    
    print(f"--- Starting Agent Test Session with Uploaded RFP (ID: {session.id}) ---")
    
    queries = [
        "Hello! I need help responding to an RFP.",
        "The client is 'H&R Block'. Let's research them.",
        "Let's generate the RFP response document now. I have uploaded the RFP document as rfp_document.txt.",
        "Yes, please generate the PowerPoint presentation deck now.",
    ]
    
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
    asyncio.run(run_test_queries())
