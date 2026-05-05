import os
from google.adk.cli.fast_api import get_fast_api_app

from pydantic import BaseModel

# Determine the directory containing agents
# In this project, the rfp_agent package is under the project root.
# So agents_dir should be the parent of rfp_agent.
agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))

app = get_fast_api_app(
    agents_dir=agents_dir,
    web=True,
)

class FeedbackRequest(BaseModel):
    score: int
    user_id: str
    session_id: str
    text: str

@app.post("/feedback")
async def collect_feedback(feedback: FeedbackRequest):
    return {"status": "success", "message": "Feedback received"}

