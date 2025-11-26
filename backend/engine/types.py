from typing import Annotated, Sequence, TypedDict, Union, List, Dict, Any
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """The state of the agent."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    agent_id: str
    thread_id: str
    tools_output: Dict[str, Any]  # Store tool outputs if needed separately
