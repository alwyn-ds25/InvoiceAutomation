from psycopg2.extras import Json
from typing import Optional, Tuple

# To allow running this file directly for testing
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import AgentCard, ToolDefinition
from core.database import get_postgres_connection

class AgentRegistryService:
    """
    Handles the registration and discovery of agents in the network.
    This service now connects directly to the database, decoupling it from the DataStoreAgent.
    """

    def register_agent(self, agent_card: AgentCard) -> dict:
        """
        Registers an agent and its tools directly into the database.
        """
        print(f"Registering agent: {agent_card.agent_id}")
        conn = None
        try:
            conn = get_postgres_connection()
            with conn.cursor() as cur:
                # 1. Register the agent card
                cur.execute(
                    """
                    INSERT INTO agent_registry (agent_id, agent_card)
                    VALUES (%s, %s)
                    ON CONFLICT (agent_id) DO UPDATE SET
                        agent_card = EXCLUDED.agent_card,
                        last_heartbeat = NOW();
                    """,
                    (agent_card.agent_id, Json(agent_card.dict()))
                )

                # 2. Register each tool
                for tool in agent_card.tools:
                    cur.execute(
                        """
                        INSERT INTO agent_tools (agent_id, tool_id, capability, description, parameters)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (agent_id, tool_id) DO UPDATE SET
                            capability = EXCLUDED.capability,
                            description = EXCLUDED.description,
                            parameters = EXCLUDED.parameters;
                        """,
                        (agent_card.agent_id, tool.tool_id, tool.capability, tool.description, Json(tool.parameters or {}))
                    )
                conn.commit()
            print(f"Agent {agent_card.agent_id} and its tools registered successfully.")
            return {"status": "AGENT_FULLY_REGISTERED", "agent_id": agent_card.agent_id}
        except Exception as e:
            if conn: conn.rollback()
            print(f"Failed to register agent or tools: {e}")
            return {"status": "FAILED_REGISTRATION", "error": str(e)}
        finally:
            if conn: conn.close()

    def lookup_agent_by_capability(self, capability: str) -> Optional[Tuple[str, ToolDefinition]]:
        """
        Finds an agent that provides a specific capability.
        Returns the agent's ID and the specific tool that matches the capability.
        """
        conn = None
        try:
            conn = get_postgres_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT agent_id, tool_id, capability, description, parameters
                    FROM agent_tools
                    WHERE capability = %s
                    LIMIT 1;
                    """,
                    (capability,)
                )
                result = cur.fetchone()
                if result:
                    agent_id, tool_id, cap, desc, params = result
                    tool_def = ToolDefinition(tool_id=tool_id, capability=cap, description=desc, parameters=params)
                    return agent_id, tool_def
            return None
        except Exception as e:
            print(f"Error looking up agent by capability '{capability}': {e}")
            return None
        finally:
            if conn: conn.close()
