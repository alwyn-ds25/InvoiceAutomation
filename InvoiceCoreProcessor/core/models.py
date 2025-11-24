from typing import List, Literal, Optional, Dict
from pydantic import BaseModel
from typing_extensions import TypedDict

# Status literals for the invoice processing workflow
Status = Literal[
    "UPLOADED",
    "OCR_DONE",
    "MAPPED",
    "VALIDATED_CLEAN",
    "VALIDATED_FLAGGED",
    "SYNCED_SUCCESS",
    "FAILED_INGESTION",
    "FAILED_OCR",
    "FAILED_MAPPING",
    "FAILED_SYNC",
]

# Target system literals
TargetSystem = Literal["TALLY", "ZOHO", "QUICKBOOKS"]

class InvoiceProcessingProtocol(BaseModel):
    """
    A Pydantic model representing the core data of an invoice being processed.
    This can be used for validation and data interchange, while the TypedDict
    state is used within the LangGraph workflow.
    """
    user_id: str
    file_path: str
    target_system: TargetSystem
    status: Status = "UPLOADED"

    invoice_id: Optional[str] = None
    extracted_text: Optional[str] = None
    mapped_schema: Optional[Dict] = None
    validation_flags: List[str] = []
    reliability_score: Optional[float] = None
    anomaly_details: Optional[List[Dict]] = None
    integration_payload_preview: Optional[Dict] = None

class InvoiceGraphState(TypedDict):
    """
    Represents the state of the invoice processing workflow in LangGraph.
    """
    # Fields from InvoiceProcessingProtocol
    user_id: str
    file_path: str
    target_system: TargetSystem
    status: Status

    invoice_id: Optional[str]
    extracted_text: Optional[str]
    mapped_schema: Optional[Dict]
    validation_flags: List[str]
    reliability_score: Optional[float]
    anomaly_details: Optional[List[Dict]]
    integration_payload_preview: Optional[Dict]

    # Additional fields for LangGraph orchestration
    current_step: str
    history: List[Dict]

# Models for Agent Registry
class ToolDefinition(BaseModel):
    """
    Defines a single tool (capability) exposed by an agent.
    """
    tool_id: str
    capability: str
    description: str
    parameters: Optional[Dict] = None

class AgentCard(BaseModel):
    """
    Represents an agent's registration card, describing its identity and capabilities.
    """
    agent_id: str
    description: str
    tools: List[ToolDefinition]
