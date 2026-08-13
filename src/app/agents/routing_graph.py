from typing import Literal

from langgraph.graph import END, START, StateGraph

from src.app.agents.state import AgentState


def inspect_request(state: AgentState) -> dict:

    last_message = state["messages"][-1]["content"]

    needs_tool = "order" in last_message.lower()

    return {
        "needs_tool": needs_tool
    }


def choose_route(
    state: AgentState,
) -> Literal["tool_node", "answer_node"]:

    if state["needs_tool"]:
        return "tool_node"

    return "answer_node"


def tool_node(state: AgentState) -> dict:

    return {
        "result": "The TOOL path was selected."
    }


def answer_node(state: AgentState) -> dict:

    return {
        "result": "The DIRECT ANSWER path was selected."
    }


builder = StateGraph(AgentState)

builder.add_node(
    "inspect_request",
    inspect_request,
)

builder.add_node(
    "tool_node",
    tool_node,
)

builder.add_node(
    "answer_node",
    answer_node,
)


builder.add_edge(
    START,
    "inspect_request",
)


builder.add_conditional_edges(
    "inspect_request",
    choose_route,
)


builder.add_edge(
    "tool_node",
    END,
)

builder.add_edge(
    "answer_node",
    END,
)


routing_graph = builder.compile()