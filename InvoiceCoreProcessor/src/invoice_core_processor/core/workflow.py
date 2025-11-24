from langgraph.graph import StateGraph, END
from typing import Dict, Any
import os
import asyncio
from functools import lru_cache

from invoice_core_processor.core.models import InvoiceGraphState
from invoice_core_processor.core.agent_registry import AgentRegistryService
from invoice_core_processor.core.mcp_clients import MCPClient, IngestionGrpcClient

# --- Client Factories ---

@lru_cache()
def get_mcp_client() -> MCPClient:
    return MCPClient()

@lru_cache()
def get_ingestion_client() -> IngestionGrpcClient:
    return IngestionGrpcClient()

@lru_cache()
def get_agent_registry() -> AgentRegistryService:
    return AgentRegistryService()

# --- Graph Nodes ---

def ingestion_step(state: InvoiceGraphState) -> Dict[str, Any]:
    # ... (logic remains the same) ...
    ingestion_client = get_ingestion_client()
    result = asyncio.run(ingestion_client.ingest_file(state['user_id'], state['file_path']))
    if result.get('status') != 'SUCCESS':
        return {"status": "FAILED_INGESTION"}
    get_mcp_client().call_tool("com.invoice.datastore", "postgres/save_audit_step", invoice_id=result['invoice_id'], from_status="START", to_status="UPLOADED", meta={})
    return {'invoice_id': result['invoice_id'], 'file_path': result['storage_path'], 'status': 'UPLOADED'}

def ocr_step(state: InvoiceGraphState) -> Dict[str, Any]:
    # ... (logic remains the same) ...
    agent_id, tool = get_agent_registry().lookup_agent_by_capability("CAPABILITY_OCR")
    result = get_mcp_client().call_tool(agent_id, tool.tool_id, invoice_id=state['invoice_id'], file_path=state['file_path'], file_extension=os.path.splitext(state['file_path'])[1], user_id=state['user_id'])
    if result['status'] == 'FAILED_OCR':
        return {"status": "FAILED_OCR"}
    get_mcp_client().call_tool("com.invoice.datastore", "postgres/save_audit_step", invoice_id=state['invoice_id'], from_status="UPLOADED", to_status="OCR_DONE", meta={})
    return {'extracted_text': " ".join([p['text'] for p in result['pages']]), 'status': 'OCR_DONE', 'ocr_confidence': result['avg_confidence']}

def mapping_step(state: InvoiceGraphState) -> Dict[str, Any]:
    # ... (logic remains the same) ...
    agent_id, tool = get_agent_registry().lookup_agent_by_capability("CAPABILITY_MAPPING")
    result = get_mcp_client().call_tool(agent_id, tool.tool_id, extracted_text=state['extracted_text'], target_system=state['target_system'])
    if result['status'] == 'FAILED_MAPPING':
        return {"status": "FAILED_MAPPING"}
    get_mcp_client().call_tool("com.invoice.datastore", "postgres/save_audit_step", invoice_id=state['invoice_id'], from_status="OCR_DONE", to_status="MAPPED", meta={})
    return {'mapped_schema': result['mapped_schema'], 'status': 'MAPPED'}

def validation_step(state: InvoiceGraphState) -> Dict[str, Any]:
    # ... (logic remains the same) ...
    agent_id, tool = get_agent_registry().lookup_agent_by_capability("CAPABILITY_VALIDATION")
    result = get_mcp_client().call_tool(agent_id, tool.tool_id, mapped_schema=state['mapped_schema'], invoice_id=state['invoice_id'], ocr_confidence=state.get('ocr_confidence', 1.0))
    get_mcp_client().call_tool("com.invoice.datastore", "postgres/save_audit_step", invoice_id=state['invoice_id'], from_status="MAPPED", to_status=result['status'], meta={})
    return {
        'status': result['status'],
        'reliability_score': result['overall_score'],
        'validation_flags': [res['rule_id'] for res in result.get('validation_results', []) if res['status'] != 'PASS'],
        'validation_results': result.get('validation_results', [])
    }

def integration_step(state: InvoiceGraphState) -> Dict[str, Any]:
    # ... (logic remains the same) ...
    agent_id, tool = get_agent_registry().lookup_agent_by_capability("CAPABILITY_INTEGRATION")
    result = get_mcp_client().call_tool(agent_id, tool.tool_id, invoice_id=state['invoice_id'], target_system=state['target_system'], mapped_schema=state['mapped_schema'], reliability_score=state['reliability_score'])
    integration_status = result.get('status', 'FAILED_SYNC')
    get_mcp_client().call_tool("com.invoice.datastore", "postgres/save_audit_step", invoice_id=state['invoice_id'], from_status="VALIDATED", to_status=integration_status, meta={})
    return {'status': integration_status, 'integration_status': integration_status}

def get_validation_status(validation_results: list) -> str:
    if not validation_results:
        return "PASS"
    if any(r.get("status") == "FAIL" for r in validation_results):
        return "FAIL"
    if any(r.get("status") == "WARN" for r in validation_results):
        return "REVIEW"
    return "PASS"


def summary_step(state: InvoiceGraphState) -> Dict[str, Any]:
    """
    Generates a summary of the invoice processing workflow.
    """
    agent_id, tool = get_agent_registry().lookup_agent_by_capability("CAPABILITY_SUMMARY")
    # We need to construct the invoice_data object from the current state
    validation_status = get_validation_status(state.get("validation_results", []))
    invoice_data = {
        "invoice": state.get("mapped_schema", {}),
        "validation": {
            "status": validation_status,
            "overall_score": state.get("reliability_score"),
            "rules": state.get("validation_results", [])
        },
        "integration": {
            "target_system": state.get("target_system"),
            "status": state.get("integration_status")
        },
        "review": {
            "required": "FLAGGED" in state.get("status", "")
        }
    }
    result = get_mcp_client().call_tool(agent_id, tool.tool_id, invoice_data=invoice_data)
    get_mcp_client().call_tool("com.invoice.datastore", "postgres/save_audit_step", invoice_id=state['invoice_id'], from_status=state['status'], to_status="SUMMARY_GENERATED", meta={})
    return {"summary": result, "status": "SUMMARY_GENERATED"}

def decide_next_step(state: InvoiceGraphState) -> str:
    # ... (logic remains the same) ...
    if 'FAILED' in state['status']: return "error_handler"
    status_map = {
        'UPLOADED': 'ocr',
        'OCR_DONE': 'mapping',
        'MAPPED': 'validation',
        'VALIDATED_CLEAN': 'integration',
        'VALIDATED_FLAGGED': 'integration',
        'SYNCED_SUCCESS': 'summary',
        'SYNCED_FAILED': 'summary'
    }
    return status_map.get(state['status'], END)

def error_handler_node(state: InvoiceGraphState):
    # ... (logic remains the same) ...
    return state

def build_workflow_graph():
    # ... (logic remains the same) ...
    workflow = StateGraph(InvoiceGraphState)
    workflow.add_node("ingestion", ingestion_step)
    workflow.add_node("ocr", ocr_step)
    workflow.add_node("mapping", mapping_step)
    workflow.add_node("validation", validation_step)
    workflow.add_node("integration", integration_step)
    workflow.add_node("summary", summary_step)
    workflow.add_node("error_handler", error_handler_node)

    workflow.set_entry_point("ingestion")

    workflow.add_conditional_edges("ingestion", decide_next_step, {"ocr": "ocr", "error_handler": "error_handler", END: END})
    workflow.add_conditional_edges("ocr", decide_next_step, {"mapping": "mapping", "error_handler": "error_handler", END: END})
    workflow.add_conditional_edges("mapping", decide_next_step, {"validation": "validation", "error_handler": "error_handler", END: END})
    workflow.add_conditional_edges("validation", decide_next_step, {"integration": "integration", "error_handler": "error_handler", END: END})
    workflow.add_conditional_edges("integration", decide_next_step, {"summary": "summary", "error_handler": "error_handler", END: END})

    workflow.add_edge("summary", END)
    workflow.add_edge("error_handler", END)

    return workflow.compile()
