import uuid
import asyncio
import logging
from typing import Dict, Any, List, Optional, Annotated, TypedDict
from datetime import datetime
import operator

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.prebuilt import ToolNode
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = "__end__"
    MemorySaver = None
    ToolNode = None

from services.agent_service import AgentService
from services.langfuse_integration import LangfuseIntegration
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class WorkflowState(TypedDict):
    """The state of the workflow that gets passed between nodes"""
    messages: Annotated[List[Dict[str, Any]], operator.add]  # Accumulate messages
    context: Dict[str, Any]  # Workflow context/variables
    input_data: Dict[str, Any]  # Original input
    current_step: str  # Current step ID
    completed_steps: List[str]  # List of completed step IDs
    failed_steps: List[str]  # List of failed step IDs
    step_results: Dict[str, Any]  # Results from each step
    error: Optional[str]  # Error message if any
    metadata: Dict[str, Any]  # Additional metadata


class LangGraphWorkflowService:
    """
    Service to convert visual workflow definitions into LangGraph state machines.
    Maps workflow nodes to LangGraph nodes and edges.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.agent_service = AgentService(db)
        self.langfuse = LangfuseIntegration()
        
        if not LANGGRAPH_AVAILABLE:
            logger.warning("LangGraph not installed. Install with: pip install langgraph")
    
    def _validate_workflow(self, steps: List[Dict[str, Any]], dependencies: Dict[str, List[str]]) -> tuple[bool, Optional[str]]:
        """
        Validate workflow structure for circular dependencies and missing steps.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not steps:
            return False, "No steps defined in workflow"
        
        step_ids = {step["id"] for step in steps}
        
        # Check for missing step references in dependencies
        for step_id, deps in dependencies.items():
            if step_id not in step_ids:
                return False, f"Dependency references non-existent step: {step_id}"
            for dep in deps:
                if dep not in step_ids:
                    return False, f"Step '{step_id}' depends on non-existent step: {dep}"
        
        # Check for circular dependencies using topological sort approach
        visited = set()
        rec_stack = set()
        
        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            # Get nodes that this node depends on
            node_deps = dependencies.get(node, [])
            for dep in node_deps:
                if dep not in visited:
                    if has_cycle(dep):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        # Check for cycles starting from each node
        for step in steps:
            step_id = step["id"]
            if step_id not in visited:
                if has_cycle(step_id):
                    return False, f"Circular dependency detected involving step: {step_id}"
        
        return True, None
    
    def create_langgraph_from_workflow(self, workflow_definition: Dict[str, Any]) -> Optional[StateGraph]:
        """
        Convert a visual workflow definition to a LangGraph StateGraph.
        
        Args:
            workflow_definition: Workflow definition with steps, dependencies, conditions
            
        Returns:
            StateGraph instance or None if LangGraph not available
        """
        if not LANGGRAPH_AVAILABLE:
            logger.error("Cannot create LangGraph - library not installed")
            return None
        
        # Create state graph
        workflow = StateGraph(WorkflowState)
        
        steps = workflow_definition.get("steps", [])
        dependencies = workflow_definition.get("dependencies", {}) or {}
        conditions = workflow_definition.get("conditions", {}) or {}
        
        # Validate workflow structure
        is_valid, error_msg = self._validate_workflow(steps, dependencies)
        if not is_valid:
            logger.error(f"Workflow validation failed: {error_msg}")
            raise ValueError(f"Invalid workflow structure: {error_msg}")
        
        # Create a mapping of step_id to step definition
        step_map = {step["id"]: step for step in steps}
        
        # Add nodes to the graph
        for step in steps:
            step_id = step["id"]
            node_type = step.get("type", "action")
            
            # Create the node function based on type
            node_func = self._create_node_function(step, step_map)
            workflow.add_node(step_id, node_func)
        
        # Determine the entry point (start node or first node without dependencies)
        entry_point = self._find_entry_point(steps, dependencies)
        if entry_point:
            workflow.set_entry_point(entry_point)
        
        # Add edges based on dependencies and conditions
        for step in steps:
            step_id = step["id"]
            
            # Check if this step has conditional routing
            if step_id in conditions:
                # Add conditional edges
                self._add_conditional_edges(workflow, step_id, conditions[step_id], step_map)
            else:
                # Add regular edges based on dependencies
                next_steps = self._find_next_steps(step_id, dependencies, steps)
                
                if not next_steps:
                    # No next steps, end the workflow
                    workflow.add_edge(step_id, END)
                elif len(next_steps) == 1:
                    # Single next step
                    workflow.add_edge(step_id, next_steps[0])
                else:
                    # Multiple next steps - need conditional routing
                    # For now, we'll use the first one (can be enhanced)
                    workflow.add_edge(step_id, next_steps[0])
        
        return workflow
    
    def _create_node_function(self, step: Dict[str, Any], step_map: Dict[str, Dict[str, Any]]):
        """
        Create a LangGraph node function for a workflow step.
        Each node function takes state and returns updated state.
        """
        step_id = step["id"]
        node_type = step.get("type", "action")
        
        async def node_function(state: WorkflowState) -> WorkflowState:
            """
            Execute the workflow step and update state.
            """
            logger.info(f"Executing LangGraph node: {step_id} (type: {node_type})")
            
            try:
                # Update current step
                state["current_step"] = step_id
                
                # Execute based on node type
                if node_type == "start":
                    result = await self._execute_start_node(step, state)
                elif node_type == "agent":
                    result = await self._execute_agent_node(step, state)
                elif node_type == "condition":
                    result = await self._execute_condition_node(step, state)
                elif node_type == "loop":
                    result = await self._execute_loop_node(step, state)
                elif node_type == "action":
                    result = await self._execute_action_node(step, state)
                elif node_type == "error_handler":
                    result = await self._execute_error_handler_node(step, state)
                elif node_type == "end":
                    result = await self._execute_end_node(step, state)
                else:
                    result = {"output": f"Unknown node type: {node_type}"}
                
                # Update state with results
                state["step_results"][step_id] = result
                state["completed_steps"].append(step_id)
                
                # Add result to context for next steps
                if "output" in result:
                    state["context"][step_id] = result["output"]
                
                # Add message to history
                state["messages"].append({
                    "step_id": step_id,
                    "type": node_type,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                return state
                
            except Exception as e:
                logger.error(f"Error in LangGraph node {step_id}: {str(e)}")
                state["failed_steps"].append(step_id)
                state["error"] = str(e)
                state["step_results"][step_id] = {"error": str(e)}
                return state
        
        return node_function
    
    async def _execute_start_node(self, step: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute start node - initialize workflow"""
        return {
            "output": "Workflow started",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_agent_node(self, step: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute agent node - call AI agent"""
        # Get agent_id from step data or directly from step
        agent_id = step.get("agent_id")
        if not agent_id and "data" in step:
            agent_id = step["data"].get("agent_id")
        
        if not agent_id:
            logger.error(f"No agent_id found in step: {step}")
            return {"error": "No agent_id specified in step configuration"}
        
        logger.info(f"Executing agent node with agent_id: {agent_id}")
        
        # Prepare agent input from state
        agent_input = self._prepare_agent_input(step, state)
        
        logger.info(f"Agent input prepared: {agent_input}")
        
        # Execute agent
        try:
            # Convert agent_input dict to string for agent service
            if isinstance(agent_input, dict):
                # Check for common input fields
                input_text = (
                    agent_input.get("query") or 
                    agent_input.get("input") or 
                    agent_input.get("text") or 
                    agent_input.get("message") or
                    str(agent_input)
                )
            else:
                input_text = str(agent_input)
            
            logger.info(f"Calling agent with input: {input_text[:100]}...")
            
            result = await self.agent_service.execute_agent(
                agent_id=agent_id,
                input_text=input_text
            )
            logger.info(f"Agent execution completed successfully")
            return {"output": result, "agent_id": agent_id, "input": input_text}
        except Exception as e:
            logger.error(f"Agent execution failed: {str(e)}")
            return {"error": str(e), "agent_id": agent_id}
    
    async def _execute_condition_node(self, step: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute condition node - evaluate condition"""
        condition = step.get("condition", {})
        
        # Evaluate condition against state
        result = self._evaluate_condition(condition, state)
        
        return {
            "output": result,
            "condition_met": result
        }
    
    async def _execute_loop_node(self, step: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute loop node - iterate over collection"""
        loop_config = step.get("loop_config", {})
        collection_path = loop_config.get("collection")
        max_iterations = loop_config.get("max_iterations", 100)
        
        # Get collection from state
        collection = self._get_from_state(collection_path, state)
        
        if not isinstance(collection, (list, tuple)):
            return {"error": "Loop collection is not iterable"}
        
        results = []
        for idx, item in enumerate(collection[:max_iterations]):
            # Add item to context for loop body
            state["context"]["loop_item"] = item
            state["context"]["loop_index"] = idx
            results.append(item)
        
        return {
            "output": results,
            "iterations": len(results)
        }
    
    async def _execute_action_node(self, step: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute action node - perform custom action"""
        action_type = step.get("action_type", "custom")
        action_config = step.get("action_config", {})
        
        # Execute based on action type
        if action_type == "http_request":
            return await self._execute_http_request(action_config, state)
        elif action_type == "transform":
            return await self._execute_transform(action_config, state)
        elif action_type == "wait":
            return await self._execute_wait(action_config, state)
        else:
            return {"output": f"Action {action_type} executed"}
    
    async def _execute_error_handler_node(self, step: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute error handler node"""
        error = state.get("error")
        return {
            "output": f"Handled error: {error}",
            "error_handled": True
        }
    
    async def _execute_end_node(self, step: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute end node - finalize workflow"""
        return {
            "output": "Workflow completed",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_http_request(self, config: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute HTTP request action"""
        import aiohttp
        
        url = self._interpolate_variables(config.get("url", ""), state)
        method = config.get("method", "GET").upper()
        headers = config.get("headers", {})
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, headers=headers) as response:
                    data = await response.json()
                    return {"output": data, "status_code": response.status}
        except Exception as e:
            return {"error": str(e)}
    
    async def _execute_transform(self, config: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute data transformation"""
        expression = config.get("expression", "")
        result = self._interpolate_variables(expression, state)
        return {"output": result}
    
    async def _execute_wait(self, config: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute wait/delay"""
        duration = config.get("duration", 1)  # seconds
        await asyncio.sleep(duration)
        return {"output": f"Waited {duration} seconds"}
    
    def _prepare_agent_input(self, step: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Prepare input for agent from state"""
        input_mapping = step.get("input_mapping")
        
        if input_mapping:
            agent_input = {}
            for target_key, source_path in input_mapping.items():
                value = self._get_from_state(source_path, state)
                if value is not None:
                    agent_input[target_key] = value
            return agent_input
        else:
            # Use original input data
            return state["input_data"]
    
    def _get_from_state(self, path: str, state: WorkflowState) -> Any:
        """Get value from state using dot notation path"""
        if not path:
            return None
        
        # Handle special paths
        if path.startswith("$"):
            path = path[1:]  # Remove $
        
        parts = path.split(".")
        current = state
        
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        
        return current
    
    def _interpolate_variables(self, text: str, state: WorkflowState) -> str:
        """Interpolate variables in text using {{ }} syntax"""
        import re
        
        def replace_var(match):
            var_path = match.group(1).strip()
            value = self._get_from_state(var_path, state)
            return str(value) if value is not None else ""
        
        return re.sub(r'\{\{\s*(.+?)\s*\}\}', replace_var, text)
    
    def _evaluate_condition(self, condition: Dict[str, Any], state: WorkflowState) -> bool:
        """Evaluate a condition against state"""
        if not condition:
            return True
        
        operator_type = condition.get("operator", "equals")
        left = self._get_from_state(condition.get("left", ""), state)
        right = condition.get("right")
        
        if operator_type == "equals":
            return left == right
        elif operator_type == "not_equals":
            return left != right
        elif operator_type == "greater_than":
            return left > right
        elif operator_type == "less_than":
            return left < right
        elif operator_type == "contains":
            return right in left if left else False
        else:
            return True
    
    def _find_entry_point(self, steps: List[Dict[str, Any]], dependencies: Dict[str, List[str]]) -> Optional[str]:
        """Find the entry point (start node or node with no dependencies)"""
        # First try to find a start node
        for step in steps:
            if step.get("type") == "start":
                return step["id"]
        
        # Otherwise find node with no dependencies (not in dependencies dict as a key)
        for step in steps:
            step_id = step["id"]
            # A node has no dependencies if it's not a key in the dependencies dict
            if step_id not in dependencies:
                return step_id
        
        # Return first step as fallback
        return steps[0]["id"] if steps else None
    
    def _find_next_steps(self, step_id: str, dependencies: Dict[str, List[str]], steps: List[Dict[str, Any]]) -> List[str]:
        """Find steps that depend on the given step"""
        next_steps = []
        for next_step_id, deps in dependencies.items():
            if step_id in deps:
                next_steps.append(next_step_id)
        return next_steps
    
    def _add_conditional_edges(self, workflow: StateGraph, step_id: str, condition_config: Dict[str, Any], step_map: Dict[str, Dict[str, Any]]):
        """Add conditional edges based on condition evaluation"""
        
        def route_condition(state: WorkflowState) -> str:
            """Routing function for conditional edges"""
            step_result = state["step_results"].get(step_id, {})
            condition_met = step_result.get("condition_met", False)
            
            if condition_met:
                return condition_config.get("true_branch", END)
            else:
                return condition_config.get("false_branch", END)
        
        # Add conditional edge
        true_branch = condition_config.get("true_branch")
        false_branch = condition_config.get("false_branch")
        
        branches = {}
        if true_branch and true_branch in step_map:
            branches[true_branch] = true_branch
        if false_branch and false_branch in step_map:
            branches[false_branch] = false_branch
        
        if branches:
            workflow.add_conditional_edges(step_id, route_condition, branches)
        else:
            workflow.add_edge(step_id, END)
    
    async def execute_langgraph_workflow(
        self,
        workflow_definition: Dict[str, Any],
        input_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        workflow_name: str = "LangGraph Workflow"
    ) -> Dict[str, Any]:
        """
        Execute a workflow using LangGraph with monitoring.
        
        Args:
            workflow_definition: Visual workflow definition
            input_data: Input data for the workflow
            config: Optional configuration (e.g., checkpointer, recursion_limit)
            workflow_name: Name of the workflow for tracing
            
        Returns:
            Final workflow state
        """
        if not LANGGRAPH_AVAILABLE:
            raise Exception("LangGraph not installed. Install with: pip install langgraph")
        
        execution_id = str(uuid.uuid4())
        workflow_id = workflow_definition.get("workflow_id", "unknown")
        
        # Start Langfuse trace
        trace = None
        try:
            trace = self.langfuse.trace_workflow_execution(
                workflow_id=workflow_id,
                execution_id=execution_id,
                metadata={
                    "workflow_name": workflow_name,
                    "engine": "langgraph",
                    "input_data": input_data
                }
            )
        except Exception as e:
            logger.warning(f"Could not create Langfuse trace: {e}")
        
        try:
            logger.info(f"Starting LangGraph workflow execution: {execution_id}")
            
            # Create LangGraph from workflow definition
            graph = self.create_langgraph_from_workflow(workflow_definition)
            
            if not graph:
                raise Exception("Failed to create LangGraph")
            
            # Set up checkpointer for state persistence
            checkpointer = MemorySaver()
            
            # Compile the graph
            app = graph.compile(checkpointer=checkpointer)
            
            # Initialize state
            initial_state: WorkflowState = {
                "messages": [],
                "context": {},
                "input_data": input_data,
                "current_step": "",
                "completed_steps": [],
                "failed_steps": [],
                "step_results": {},
                "error": None,
                "metadata": {
                    "started_at": datetime.utcnow().isoformat(),
                    "workflow_id": workflow_definition.get("workflow_id"),
                    "execution_id": execution_id,
                    "trace_id": trace.id if trace else None
                }
            }
            
            # Execute the graph
            thread_id = str(uuid.uuid4())
            config = config or {"configurable": {"thread_id": thread_id}}
            
            logger.info(f"Invoking LangGraph with thread_id: {thread_id}")
            final_state = await app.ainvoke(initial_state, config)
            
            # Add completion metadata
            final_state["metadata"]["completed_at"] = datetime.utcnow().isoformat()
            final_state["metadata"]["success"] = len(final_state["failed_steps"]) == 0
            
            # Calculate duration
            started_at = datetime.fromisoformat(final_state["metadata"]["started_at"])
            completed_at = datetime.fromisoformat(final_state["metadata"]["completed_at"])
            duration_ms = int((completed_at - started_at).total_seconds() * 1000)
            
            logger.info(f"LangGraph execution completed in {duration_ms}ms")
            logger.info(f"Completed steps: {final_state['completed_steps']}")
            logger.info(f"Failed steps: {final_state['failed_steps']}")
            
            # Langfuse trace is automatically tracked and flushed
            logger.info(f"Langfuse trace ID: {trace.id if trace and hasattr(trace, 'id') else 'N/A'}")
            
            return final_state
            
        except Exception as e:
            logger.error(f"LangGraph execution error: {str(e)}", exc_info=True)
            raise
