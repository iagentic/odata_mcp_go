"""
Multi-Agent System using OpenAI Agents SDK

Uses the SDK's handoff system for LLM-driven routing to appropriate agents.
"""

import logging
from openai import OpenAI
from agents import Agent, Runner, function_tool

from .clients import MCPClient

logger = logging.getLogger(__name__)

@function_tool
def query_opportunities(query: str) -> str:
    """Query opportunity data from SAP C4C"""
    return f"Querying opportunities: {query}"

@function_tool
def query_service_requests(query: str) -> str:
    """Query service request data from SAP C4C"""
    return f"Querying service requests: {query}"

def create_sales_agent() -> Agent:
    """Create sales agent for opportunity queries"""
    return Agent(
        name="sales_agent",
        instructions=(
            "You are a sales assistant that handles queries about opportunities, deals, "
            "and sales data. When users ask about opportunities, deals, sales pipeline, "
            "or revenue, use the query_opportunities tool to get the data and provide helpful responses."
        ),
        tools=[query_opportunities],
        handoff_description="A sales assistant that handles opportunity and deal queries"
    )

def create_service_agent() -> Agent:
    """Create service agent for service request queries"""
    return Agent(
        name="service_agent",
        instructions=(
            "You are a service assistant that handles queries about service requests, "
            "tickets, and support issues. When users ask about service requests, "
            "support tickets, incidents, or problems, use the query_service_requests tool to get the data and provide helpful responses."
        ),
        tools=[query_service_requests],
        handoff_description="A service assistant that handles service request and support queries"
    )

def create_orchestrator_agent() -> Agent:
    """Create orchestrator agent that routes queries using handoffs"""
    sales_agent = create_sales_agent()
    service_agent = create_service_agent()
    
    return Agent(
        name="orchestrator_agent",
        instructions=(
            "You are an intelligent assistant that routes user queries to the appropriate "
            "specialized agent. Analyze the user's query and hand off to the sales agent "
            "for opportunity/deal queries or the service agent for service request/support queries. "
            "Use natural language understanding to determine the best agent for each query."
        ),
        handoffs=[sales_agent, service_agent]
    )

async def process_query(query: str, openai_client: OpenAI, mcp_client: MCPClient):
    """Process a user query using the multi-agent system"""
    orchestrator = create_orchestrator_agent()
    
    result = await Runner.run(orchestrator, query)
    return result


