import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models import Gemini

load_dotenv()

model_name = os.environ.get("MODEL_NAME")

from google.adk.tools.load_artifacts_tool import load_artifacts_tool

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/generate_rfp_agent_instruction.md")
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    generate_rfp_instruction = f.read()

generate_rfp_agent = Agent(
    name="generate_rfp_agent",
    model=Gemini(model=model_name),
    description="Generates an RFP response.",
    instruction=generate_rfp_instruction,
    tools=[load_artifacts_tool],
    output_key="rfp_response"
)