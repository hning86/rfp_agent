# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from dotenv import load_dotenv

load_dotenv()

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from .sub_agents.research_agent import research_agent
from .sub_agents.generate_rfp_agent import generate_rfp_agent
from .sub_agents.ppt_agent import ppt_agent

model_name = os.environ.get("MODEL_NAME")

from google.adk.tools.agent_tool import AgentTool

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=model_name,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Orchestrates the RFP response process sequentially.",
    instruction=r"""
    You are the Lead RFP Response Agent. Your goal is to guide the user through the RFP process.
    Execute these steps in order:
    1. Ask the user what is the name of the client.
    2. Pass the client name to 'research_agent' tool to perform deep internal and external research.
    3. Display the research findings returned by the 'research_agent' tool verbatim to the user in your response.
    4. Call the 'generate_rfp_agent' tool to generate the RFP response.
    5. Display the generated RFP response verbatim to the user.
    6. Call 'ppt_agent' tool to generate the PowerPoint presentation deck and display the success message and file path.
    """,
    tools=[
        AgentTool(research_agent),
        AgentTool(generate_rfp_agent),
        AgentTool(ppt_agent),
    ],
)

app_name = __package__.split(".")[-1] if __package__ else "rfp_agent"

app = App(
    root_agent=root_agent,
    name=app_name,
)
