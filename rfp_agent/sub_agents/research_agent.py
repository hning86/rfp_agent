import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models import Gemini

load_dotenv()

model_name = os.environ.get("MODEL_NAME")

from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool

project = os.environ.get("GOOGLE_CLOUD_PROJECT")
raw_store_id = os.environ.get("DATA_STORE_ID")
location = os.environ.get("DATA_STORE_LOCATION")

if "/" in raw_store_id:
    data_store_id = raw_store_id
else:
    data_store_id = f"projects/{project}/locations/{location}/collections/default_collection/dataStores/{raw_store_id}"

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/research_agent_instruction.md")
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    research_instruction = f.read()

research_agent = Agent(
    name="research_agent",
    model=Gemini(model=model_name),
    description="Performs internal and external research on a prospect client.",
    instruction=research_instruction,
    tools=[
        VertexAiSearchTool(
            data_store_id=data_store_id,
            max_results=3,
            bypass_multi_tools_limit=True,
        ),
        GoogleSearchTool(bypass_multi_tools_limit=True),
    ],
    output_key="research_results",
)
