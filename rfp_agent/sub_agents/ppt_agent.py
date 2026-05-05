import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models import Gemini

load_dotenv()

model_name = os.environ.get("MODEL_NAME")

ppt_agent = Agent(
    name="ppt_agent",
    model=Gemini(model=model_name),
    description="Generates a PowerPoint presentation deck based on the final RFP response.",
    instruction="Stub implementation for generating PowerPoint presentations. Details will be implemented later.",
)
