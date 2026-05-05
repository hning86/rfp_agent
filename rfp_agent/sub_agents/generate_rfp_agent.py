import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models import Gemini

load_dotenv()

model_name = os.environ.get("MODEL_NAME")

from google.adk.tools.load_artifacts_tool import load_artifacts_tool
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool

project = os.environ.get("GOOGLE_CLOUD_PROJECT")
location = os.environ.get("DATA_STORE_LOCATION", "global")
raw_store_id = os.environ.get("INTERNAL_DOCS_DATA_STORE_ID")

if "/" in raw_store_id:
    data_store_id = raw_store_id
else:
    data_store_id = f"projects/{project}/locations/{location}/collections/default_collection/dataStores/{raw_store_id}"

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/generate_rfp_agent_instruction.md")
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    generate_rfp_instruction = f.read()

generate_rfp_agent = Agent(
    name="generate_rfp_agent",
    model=Gemini(model=model_name),
    description="Generates an RFP response.",
    instruction=generate_rfp_instruction,
    tools=[
        load_artifacts_tool,
        VertexAiSearchTool(
            data_store_id=data_store_id,
            max_results=3,
            bypass_multi_tools_limit=True,
        )
    ],
    output_key="rfp_response"
)