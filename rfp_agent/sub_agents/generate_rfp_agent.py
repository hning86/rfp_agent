import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

load_dotenv()

model_name = os.environ.get("MODEL_NAME")

import tempfile
from google.cloud import storage
from pypdf import PdfReader
from google.adk.tools import FunctionTool
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from google.adk.tools.load_artifacts_tool import load_artifacts_tool
from google.adk.tools.agent_tool import AgentTool

project = os.environ.get("GOOGLE_CLOUD_PROJECT")
location = os.environ.get("DATA_STORE_LOCATION", "global")

# Datastore 1: GALE Internal Documents
raw_store_id = os.environ.get("INTERNAL_DOCS_DATA_STORE_ID")
if "/" in raw_store_id:
    data_store_id = raw_store_id
else:
    data_store_id = f"projects/{project}/locations/{location}/collections/default_collection/dataStores/{raw_store_id}"

# Datastore 2: Past RFP Responses (used by research_engine)
rfp_raw_store_id = os.environ.get("RFP_DATA_STORE_ID")
if "/" in rfp_raw_store_id:
    rfp_store_id = rfp_raw_store_id
else:
    rfp_store_id = f"projects/{project}/locations/{location}/collections/default_collection/dataStores/{rfp_raw_store_id}"

def read_gcs_document(gcs_uri: str) -> str:
    """
    Reads and extracts the text content of an RFP document (PDF or TXT/Markdown) from a Google Cloud Storage (GCS) URI.
    
    Args:
        gcs_uri: The GCS URI of the document (e.g., gs://bucket-name/path/to/rfp.pdf or gs://bucket-name/rfp.txt)
        
    Returns:
        The extracted text content of the document.
    """
    if not gcs_uri.startswith("gs://"):
        return "Error: GCS URI must start with gs://"
        
    try:
        path_parts = gcs_uri[5:].split("/", 1)
        if len(path_parts) < 2:
            return "Error: Invalid GCS URI format."
        bucket_name, blob_name = path_parts
        
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        suffix = ".pdf" if blob_name.lower().endswith(".pdf") else ".txt"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
            tmp_path = tmp_file.name
            blob.download_to_filename(tmp_path)
            
        try:
            if suffix == ".pdf":
                reader = PdfReader(tmp_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text if text.strip() else "Error: No extractable text found in the PDF."
            else:
                with open(tmp_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    except Exception as e:
        return f"Error reading document from GCS: {e}"

read_gcs_rfp_document = FunctionTool(func=read_gcs_document)

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/generate_rfp_agent_instruction.md")
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    generate_rfp_instruction = f.read()

rfp_knowledge_search_agent = Agent(
    name="rfp_knowledge_search_agent",
    model=Gemini(
        model=model_name,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Search GALE's past client RFP responses and research profiles to find parallel client campaigns and vertical methodologies.",
    instruction="You are a search assistant. Search the past RFP responses data store to answer the user's query exactly and accurately.",
    tools=[
        VertexAiSearchTool(
            data_store_id=rfp_store_id,
            max_results=3,
            bypass_multi_tools_limit=True,
        )
    ],
)

generate_rfp_agent = Agent(
    name="generate_rfp_agent",
    model=Gemini(
        model=model_name,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Generates an RFP response.",
    instruction=generate_rfp_instruction,
    tools=[
        VertexAiSearchTool(
            data_store_id=data_store_id,
            max_results=3,
            bypass_multi_tools_limit=True,
        ),
        AgentTool(rfp_knowledge_search_agent),
    ],
    output_key="rfp_response"
)