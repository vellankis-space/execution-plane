import uuid
import asyncio
import logging
import time
import psutil
import os
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from collections import defaultdict

from models.workflow import Workflow, WorkflowExecution, StepExecution
from schemas.workflow import WorkflowCreate, WorkflowUpdate, WorkflowExecutionCreate, StepExecutionCreate
from services.agent_service import AgentService
from services.error_handler import ErrorHandler, RetryPolicy, DEFAULT_RETRY_POLICY
from services.alerting_service import AlertingService
from services.cost_tracking_service import CostTrackingService
# Configure logging
logger = logging.getLogger(__name__)


class WorkflowService:
    def __init__(self, db: Session):
        self.db = db

    async def create_workflow(self, workflow_data: WorkflowCreate, user_id: Optional[str] = None, tenant_id: Optional[str] = None) -> Workflow:
        """Create a new workflow"""
        workflow_id = str(uuid.uuid4())
        
        # Convert definition to dict if it's a Pydantic model
        definition_dict = workflow_data.definition.dict() if hasattr(workflow_data.definition, 'dict') else workflow_data.definition
        
        db_workflow = Workflow(
            workflow_id=workflow_id,
            name=workflow_data.name,
            description=workflow_data.description,
            definition=definition_dict,
            created_by=user_id,
            version=1,  # Initial version
            tenant_id=tenant_id  # Set tenant_id for isolation
        )
        
        self.db.add(db_workflow)
        self.db.commit()
        self.db.refresh(db_workflow)
        
        return db_workflow

    async def get_workflow(self, workflow_id: str, tenant_id: Optional[str] = None) -> Optional[Workflow]:
        """Retrieve a workflow by ID, optionally filtered by tenant"""
        query = self.db.query(Workflow).filter(Workflow.workflow_id == workflow_id)
        
        # Apply tenant filter if provided
        if tenant_id:
            query = query.filter(Workflow.tenant_id == tenant_id)
        
        return query.first()

    async def get_workflows(self, skip: int = 0, limit: int = 100, tenant_id: Optional[str] = None) -> List[Workflow]:
        """Retrieve all workflows, optionally filtered by tenant"""
        query = self.db.query(Workflow)
        
        # Apply tenant filter if provided
        if tenant_id:
            query = query.filter(Workflow.tenant_id == tenant_id)
        
        return query.offset(skip).limit(limit).all()

    async def update_workflow(self, workflow_id: str, workflow_data: WorkflowUpdate, tenant_id: Optional[str] = None) -> Optional[Workflow]:
        """Update a workflow"""
        db_workflow = await self.get_workflow(workflow_id, tenant_id=tenant_id)
        if not db_workflow:
            return None
            
        update_data = workflow_data.dict(exclude_unset=True)
        
        # Handle definition conversion if it's a Pydantic model
        if 'definition' in update_data and update_data['definition'] is not None:
            if hasattr(update_data['definition'], 'dict'):
                update_data['definition'] = update_data['definition'].dict()
        
        for key, value in update_data.items():
            setattr(db_workflow, key, value)
            
        setattr(db_workflow, 'updated_at', datetime.utcnow())
        setattr(db_workflow, 'version', (db_workflow.version or 1) + 1)  # Increment version
        self.db.commit()
        self.db.refresh(db_workflow)
        
        return db_workflow

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        db_workflow = await self.get_workflow(workflow_id)
        if not db_workflow:
            return False
            
        self.db.delete(db_workflow)
        self.db.commit()
        return True

    async def create_workflow_execution(self, execution_data: WorkflowExecutionCreate, tenant_id: Optional[str] = None) -> WorkflowExecution:
        """Create a new workflow execution"""
        execution_id = str(uuid.uuid4())
        
        # Get workflow to inherit tenant_id
        workflow = await self.get_workflow(execution_data.workflow_id, tenant_id=tenant_id)
        if not workflow:
            raise ValueError("Workflow not found")
        
        # Use workflow's tenant_id or provided tenant_id
        execution_tenant_id = tenant_id or getattr(workflow, 'tenant_id', None)
        
        db_execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=execution_data.workflow_id,
            status="pending",
            input_data=execution_data.input_data,
            tenant_id=execution_tenant_id  # Set tenant_id for isolation
        )
        
        self.db.add(db_execution)
        self.db.commit()
        self.db.refresh(db_execution)
        
        return db_execution

    async def get_workflow_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Retrieve a workflow execution by ID"""
        return self.db.query(WorkflowExecution).filter(WorkflowExecution.execution_id == execution_id).first()

    async def update_workflow_execution_status(self, execution_id: str, status: str, 
                                             output_data: Optional[Dict[str, Any]] = None,
                                             error_message: Optional[str] = None) -> Optional[WorkflowExecution]:
        """Update workflow execution status"""
        db_execution = await self.get_workflow_execution(execution_id)
        if not db_execution:
            return None
            
        setattr(db_execution, 'status', status)
        if output_data is not None:
            setattr(db_execution, 'output_data', output_data)
        if error_message is not None:
            setattr(db_execution, 'error_message', error_message)
        if status == "running" and getattr(db_execution, 'started_at', None) is None:
            setattr(db_execution, 'started_at', datetime.utcnow())
        if status in ["completed", "failed", "cancelled"] and getattr(db_execution, 'completed_at', None) is None:
            setattr(db_execution, 'completed_at', datetime.utcnow())
            # Calculate execution time
            started_at = getattr(db_execution, 'started_at', None)
            if started_at is not None:
                execution_time = (datetime.utcnow() - started_at).total_seconds()
                setattr(db_execution, 'execution_time', execution_time)
            
        self.db.commit()
        self.db.refresh(db_execution)
        
        return db_execution

    async def create_step_execution(self, step_data: StepExecutionCreate) -> StepExecution:
        """Create a new step execution"""
        db_step = StepExecution(
            step_id=step_data.step_id,
            execution_id=step_data.execution_id,
            agent_id=step_data.agent_id,
            status="pending",
            input_data=step_data.input_data
        )
        
        self.db.add(db_step)
        self.db.commit()
        self.db.refresh(db_step)
        
        return db_step

    async def update_step_execution_status(self, step_id: str, execution_id: str, status: str,
                                         output_data: Optional[Dict[str, Any]] = None,
                                         error_message: Optional[str] = None) -> Optional[StepExecution]:
        """Update step execution status"""
        db_step = self.db.query(StepExecution).filter(
            StepExecution.step_id == step_id,
            StepExecution.execution_id == execution_id
        ).first()
        
        if not db_step:
            return None
            
        setattr(db_step, 'status', status)
        if output_data is not None:
            setattr(db_step, 'output_data', output_data)
        if error_message is not None:
            setattr(db_step, 'error_message', error_message)
        if status == "running" and getattr(db_step, 'started_at', None) is None:
            setattr(db_step, 'started_at', datetime.utcnow())
        if status in ["completed", "failed"] and getattr(db_step, 'completed_at', None) is None:
            setattr(db_step, 'completed_at', datetime.utcnow())
            # Calculate execution time
            started_at = getattr(db_step, 'started_at', None)
            if started_at is not None:
                execution_time = (datetime.utcnow() - started_at).total_seconds()
                setattr(db_step, 'execution_time', execution_time)
            
        self.db.commit()
        self.db.refresh(db_step)
        
        return db_step

    async def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any], tenant_id: Optional[str] = None) -> WorkflowExecution:
        """Execute a workflow with the given input"""
        # Get the workflow (with tenant filtering)
        workflow = await self.get_workflow(workflow_id, tenant_id=tenant_id)
        if not workflow:
            raise ValueError("Workflow not found")
        
        # Create workflow execution
        execution_data = WorkflowExecutionCreate(
            workflow_id=workflow_id,
            input_data=input_data
        )
        execution = await self.create_workflow_execution(execution_data, tenant_id=tenant_id)
        
        # Get the execution ID as a string
        execution_id = str(getattr(execution, 'execution_id'))
        
        
        # Capture initial resource usage
        try:
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            initial_cpu = process.cpu_percent()
        except Exception as e:
            logger.warning(f"Could not capture initial resource usage: {str(e)}")
            initial_memory = 0
            initial_cpu = 0
        
        # Update status to running
        await self.update_workflow_execution_status(execution_id, "running")
        
        try:
            # Parse workflow definition and execute steps
            workflow_definition = getattr(workflow, 'definition')
            start_time = time.time()
            output_data = await self._execute_workflow_graph(workflow_definition, input_data, execution_id)
            end_time = time.time()
            
            # Capture final resource usage
            try:
                process = psutil.Process(os.getpid())
                final_memory = process.memory_info().rss / 1024 / 1024  # MB
                final_cpu = process.cpu_percent()
            except Exception as e:
                logger.warning(f"Could not capture final resource usage: {str(e)}")
                final_memory = 0
                final_cpu = 0
            
            # Update workflow execution with enhanced metrics
            execution = await self.get_workflow_execution(execution_id)
            if execution:
                setattr(execution, 'step_count', len(workflow_definition.get("steps", [])))
                # Load step executions for counting
                step_executions = self.db.query(StepExecution).filter(
                    StepExecution.execution_id == execution_id
                ).all()
                success_count = len([s for s in step_executions if getattr(s, 'status') == "completed"])
                failure_count = len([s for s in step_executions if getattr(s, 'status') == "failed"])
                setattr(execution, 'success_count', success_count)
                setattr(execution, 'failure_count', failure_count)
                setattr(execution, 'resource_usage', {
                    "initial_memory_mb": initial_memory,
                    "final_memory_mb": final_memory,
                    "memory_change_mb": final_memory - initial_memory,
                    "initial_cpu_percent": initial_cpu,
                    "final_cpu_percent": final_cpu,
                    "cpu_change_percent": final_cpu - initial_cpu
                })
            
            # Update status to completed
            execution = await self.update_workflow_execution_status(execution_id, "completed", output_data)
            
            # Evaluate alert rules for completed execution
            if execution:
                try:
                    alerting_service = AlertingService(self.db)
                    await alerting_service.evaluate_alert_rules(execution)
                except Exception as alert_error:
                    logger.warning(f"Error evaluating alert rules: {str(alert_error)}")
            
        except Exception as e:
            # Update status to failed
            execution = await self.update_workflow_execution_status(execution_id, "failed", error_message=str(e))
            
            # Evaluate alert rules for failed execution
            if execution:
                try:
                    alerting_service = AlertingService(self.db)
                    await alerting_service.evaluate_alert_rules(execution)
                except Exception as alert_error:
                    logger.warning(f"Error evaluating alert rules: {str(alert_error)}")
            
            raise e
            
        return await self.get_workflow_execution(execution_id)

    async def _execute_workflow_graph(self, workflow_definition: Dict[str, Any], 
                                    input_data: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
        """Execute workflow as a graph with support for parallel execution, conditional branching, and monitoring"""
        steps = workflow_definition.get("steps", [])
        dependencies = workflow_definition.get("dependencies", {}) or {}
        conditions = workflow_definition.get("conditions", {}) or {}
        
        # Create a mapping of step IDs to step definitions
        step_map = {step["id"]: step for step in steps}
        
        # Track execution state
        context = input_data.copy()
        completed_steps = set()
        failed_steps = set()
        step_results = {}
        execution_order = []  # Track execution order for monitoring
        
        # Identify steps with no dependencies (starting points)
        starting_steps = [
            step_id for step_id in step_map.keys() 
            if step_id not in dependencies or not dependencies[step_id]
        ]
        
        # Execute workflow using a breadth-first approach with parallel execution
        while len(completed_steps) + len(failed_steps) < len(steps):
            # Find steps that can be executed now (all dependencies met)
            ready_steps = []
            for step_id, step_deps in dependencies.items():
                if step_id not in completed_steps and step_id not in failed_steps:
                    # Check if all dependencies are completed
                    deps_met = all(dep in completed_steps for dep in step_deps) if step_deps else True
                    
                    # Check conditional execution if defined
                    condition_met = True
                    if step_id in conditions:
                        condition_met = self._evaluate_condition(conditions[step_id], step_results, context)
                    
                    if deps_met and condition_met:
                        ready_steps.append(step_id)
            
            # Add starting steps if no other steps are ready
            if not ready_steps:
                for step_id in starting_steps:
                    if step_id not in completed_steps and step_id not in failed_steps:
                        # Check conditional execution for starting steps
                        condition_met = True
                        if step_id in conditions:
                            condition_met = self._evaluate_condition(conditions[step_id], step_results, context)
                        
                        if condition_met:
                            ready_steps.append(step_id)
            
            # If no steps are ready and we haven't completed all steps, there's a cycle or missing step
            if not ready_steps:
                remaining_steps = [
                    step_id for step_id in step_map.keys() 
                    if step_id not in completed_steps and step_id not in failed_steps
                ]
                if remaining_steps:
                    raise ValueError(f"Circular dependency or missing steps detected: {remaining_steps}")
                break
            
            # Log ready steps for monitoring
            logger.info(f"Ready to execute steps: {ready_steps}")
            execution_order.extend(ready_steps)
            
            # Execute ready steps in parallel
            step_tasks = [
                self._execute_single_step(
                    step_map[step_id], 
                    context, 
                    execution_id, 
                    step_results
                ) 
                for step_id in ready_steps
            ]
            
            # Wait for all ready steps to complete
            step_outputs = await asyncio.gather(*step_tasks, return_exceptions=True)
            
            # Process results
            for i, (step_id, result) in enumerate(zip(ready_steps, step_outputs)):
                if isinstance(result, Exception):
                    failed_steps.add(step_id)
                    step_results[step_id] = {"error": str(result)}
                    logger.error(f"Step {step_id} failed with error: {str(result)}")
                else:
                    completed_steps.add(step_id)
                    step_results[step_id] = result
                    # Update context with step results (only if result is a dict)
                    if isinstance(result, dict):
                        context.update(result)
                    logger.info(f"Step {step_id} completed successfully")
        
        # If any steps failed, raise an exception
        if failed_steps:
            raise ValueError(f"Workflow failed due to errors in steps: {list(failed_steps)}")
        
        # Add execution metadata to context for monitoring
        context["_workflow_execution_metadata"] = {
            "execution_order": execution_order,
            "completed_steps": list(completed_steps),
            "failed_steps": list(failed_steps),
            "step_results": step_results
        }
        
        return context

    async def _execute_single_step(self, step_definition: Dict[str, Any], 
                                 context: Dict[str, Any], execution_id: str,
                                 previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step in the workflow"""
        step_id = step_definition["id"]
        agent_id = step_definition["agent_id"]
        
        # Log step start
        logger.info(f"Starting execution of step {step_id} with agent {agent_id}")
        
        # Create step execution
        step_data = StepExecutionCreate(
            step_id=step_id,
            execution_id=execution_id,
            agent_id=agent_id,
            input_data=context
        )
        await self.create_step_execution(step_data)
        
        # Capture initial resource metrics
        try:
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            initial_cpu = process.cpu_percent()
            initial_io = process.io_counters() if hasattr(process, 'io_counters') else None
            io_operations_start = initial_io.read_count + initial_io.write_count if initial_io else 0
        except Exception as e:
            logger.warning(f"Could not capture initial resource metrics for step {step_id}: {str(e)}")
            initial_memory = 0
            initial_cpu = 0
            io_operations_start = 0
        
        # Update step status to running
        await self.update_step_execution_status(step_id, execution_id, "running")
        
        try:
            # Prepare input for the agent based on step configuration
            agent_input = self._prepare_agent_input(step_definition, context, previous_results)
            
            # Get retry policy from step definition or use default
            retry_config = step_definition.get("retry_policy") or {}
            retry_policy = RetryPolicy(
                max_retries=retry_config.get("max_retries", DEFAULT_RETRY_POLICY.max_retries),
                initial_delay=retry_config.get("initial_delay", DEFAULT_RETRY_POLICY.initial_delay),
                max_delay=retry_config.get("max_delay", DEFAULT_RETRY_POLICY.max_delay),
                exponential_base=retry_config.get("exponential_base", DEFAULT_RETRY_POLICY.exponential_base)
            )
            
            # Execute the agent with retry logic
            agent_service = AgentService(self.db)
            start_time = time.time()
            
            async def execute_agent_with_context():
                return await agent_service.execute_agent(agent_id, str(agent_input))
            
            agent_response = await ErrorHandler.retry_with_backoff(
                execute_agent_with_context,
                retry_policy
            )
            end_time = time.time()
            
            # Capture final resource metrics
            try:
                process = psutil.Process(os.getpid())
                final_memory = process.memory_info().rss / 1024 / 1024  # MB
                final_cpu = process.cpu_percent()
                final_io = process.io_counters() if hasattr(process, 'io_counters') else None
                io_operations_end = final_io.read_count + final_io.write_count if final_io else 0
            except Exception as e:
                logger.warning(f"Could not capture final resource metrics for step {step_id}: {str(e)}")
                final_memory = 0
                final_cpu = 0
                io_operations_end = 0
            
            # Update step execution with enhanced metrics
            db_step = self.db.query(StepExecution).filter(
                StepExecution.step_id == step_id,
                StepExecution.execution_id == execution_id
            ).first()
            
            if db_step:
                setattr(db_step, 'memory_usage', final_memory - initial_memory)
                setattr(db_step, 'cpu_usage', final_cpu - initial_cpu)
                setattr(db_step, 'io_operations', io_operations_end - io_operations_start)
                # For now, we'll set network requests to 0 as we don't have a way to measure them
                setattr(db_step, 'network_requests', 0)
                
                self.db.commit()
                self.db.refresh(db_step)
            
            # Update step status to completed
            await self.update_step_execution_status(
                step_id, execution_id, "completed", 
                output_data={"response": agent_response}
            )
            
            # Log successful completion
            logger.info(f"Step {step_id} completed successfully")
            
            # Return results for use by dependent steps
            return {step_id: agent_response}
            
        except Exception as e:
            # Get detailed error information
            error_details = ErrorHandler.get_error_details(e)
            category = error_details["category"]
            message = error_details["message"]
            
            # Log error with category
            logger.error(
                f"Step {step_id} failed with {category}: {message}. "
                f"Error type: {error_details['error_type']}"
            )
            
            # Update step status to failed with categorized error message
            await self.update_step_execution_status(
                step_id, execution_id, "failed", 
                error_message=f"[{category.upper()}] {message}"
            )
            
            # Re-raise with better error message
            raise Exception(f"Step {step_id} failed: {message}") from e

    def _prepare_agent_input(self, step_definition: Dict[str, Any], 
                           context: Dict[str, Any], 
                           previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input for an agent based on step configuration"""
        # Default to using the entire context
        agent_input = context.copy()
        
        # If step has specific input mapping, use that
        input_mapping = step_definition.get("input_mapping")
        if input_mapping:
            agent_input = {}
            for target_key, source_key in input_mapping.items():
                if source_key in context:
                    agent_input[target_key] = context[source_key]
                elif source_key in previous_results:
                    # Handle nested results
                    agent_input[target_key] = previous_results[source_key]
        
        return agent_input

    def _evaluate_condition(self, condition: Dict[str, Any], step_results: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a condition for conditional step execution"""
        try:
            # Get the condition type (simple or complex)
            condition_type = condition.get("type", "simple")
            
            if condition_type == "simple":
                return self._evaluate_simple_condition(condition, step_results, context)
            elif condition_type == "complex":
                return self._evaluate_complex_condition(condition, step_results, context)
            else:
                # Default to True if condition type is not recognized
                return True
        except Exception as e:
            logger.warning(f"Error evaluating condition: {str(e)}. Defaulting to True.")
            return True

    def _evaluate_simple_condition(self, condition: Dict[str, Any], step_results: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a simple condition (e.g., check if a step result equals a value)"""
        step_id = condition.get("step_id")
        field = condition.get("field")
        operator = condition.get("operator", "equals")
        value = condition.get("value")
        
        # Get the result to compare
        result_value = None
        if step_id and step_id in step_results:
            result = step_results[step_id]
            if isinstance(result, dict) and field in result:
                result_value = result[field]
            else:
                result_value = result
        elif field in context:
            result_value = context[field]
        else:
            # Field not found, condition cannot be evaluated
            return False
        
        # Perform comparison based on operator
        try:
            if operator in ["equals", "=="]:
                return result_value == value
            elif operator in ["not_equals", "!="]:
                return result_value != value
            elif operator in ["greater_than", ">"]:
                # Ensure both values are comparable
                if isinstance(result_value, (int, float)) and isinstance(value, (int, float)):
                    return result_value > value
                return False
            elif operator in ["less_than", "<"]:
                # Ensure both values are comparable
                if isinstance(result_value, (int, float)) and isinstance(value, (int, float)):
                    return result_value < value
                return False
            elif operator in ["greater_than_equal", ">="]:
                # Ensure both values are comparable
                if isinstance(result_value, (int, float)) and isinstance(value, (int, float)):
                    return result_value >= value
                return False
            elif operator in ["less_than_equal", "<="]:
                # Ensure both values are comparable
                if isinstance(result_value, (int, float)) and isinstance(value, (int, float)):
                    return result_value <= value
                return False
            elif operator == "contains":
                # Check if result_value is not None and is a valid container type
                if result_value is not None and isinstance(result_value, (str, list, dict)):
                    try:
                        if isinstance(result_value, dict):
                            # For dicts, check if value is in keys or values
                            contains_result = False
                            if result_value is not None:
                                # Check if value is in keys
                                try:
                                    contains_result = contains_result or self._safe_in_check(value, result_value.keys())
                                except (TypeError, AttributeError):
                                    pass
                                # Check if value is in values
                                try:
                                    dict_values = list(result_value.values())
                                    contains_result = contains_result or self._safe_in_check(value, dict_values)
                                except (TypeError, AttributeError):
                                    pass
                            return contains_result
                        else:
                            # For str/list, check if value is in the container
                            if result_value is not None:
                                try:
                                    return self._safe_in_check(value, result_value)
                                except (TypeError, AttributeError):
                                    return False
                            return False
                    except (TypeError, AttributeError):
                        return False
                return False
            elif operator == "not_contains":
                # Check if result_value is not None and is a valid container type
                if result_value is not None and isinstance(result_value, (str, list, dict)):
                    try:
                        if isinstance(result_value, dict):
                            # For dicts, check if value is not in keys and not in values
                            not_contains_result = True
                            if result_value is not None:
                                # Check if value is not in keys
                                try:
                                    not_contains_result = not_contains_result and not self._safe_in_check(value, result_value.keys())
                                except (TypeError, AttributeError):
                                    pass
                                # Check if value is not in values
                                try:
                                    dict_values = list(result_value.values())
                                    not_contains_result = not_contains_result and not self._safe_in_check(value, dict_values)
                                except (TypeError, AttributeError):
                                    pass
                            return not_contains_result
                        else:
                            # For str/list, check if value is not in the container
                            if result_value is not None:
                                try:
                                    return not self._safe_in_check(value, result_value)
                                except (TypeError, AttributeError):
                                    return True
                            return True
                    except (TypeError, AttributeError):
                        return True
                return True
            elif operator == "is_null":
                return result_value is None
            elif operator == "is_not_null":
                return result_value is not None
            elif operator == "is_empty":
                if isinstance(result_value, (str, list, dict)):
                    return len(result_value) == 0
                return result_value is None
            elif operator == "is_not_empty":
                if isinstance(result_value, (str, list, dict)):
                    return len(result_value) > 0
                return result_value is not None
            elif operator == "starts_with":
                if isinstance(result_value, str) and isinstance(value, str):
                    return result_value.startswith(value)
                return False
            elif operator == "ends_with":
                if isinstance(result_value, str) and isinstance(value, str):
                    return result_value.endswith(value)
                return False
            elif operator == "matches":
                # For regex matching
                import re
                if isinstance(result_value, str) and isinstance(value, str):
                    return bool(re.search(value, result_value))
                return False
            else:
                # Unknown operator, default to True
                logger.warning(f"Unknown operator: {operator}. Defaulting to True.")
                return True
        except Exception as e:
            logger.warning(f"Error evaluating condition with operator {operator}: {str(e)}. Defaulting to True.")
            return True

    def _safe_in_check(self, value: Any, container: Any) -> bool:
        """Safely check if a value is in a container, handling exceptions"""
        try:
            if container is not None:
                return value in container
            return False
        except (TypeError, AttributeError):
            return False

    def _evaluate_complex_condition(self, condition: Dict[str, Any], step_results: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a complex condition with logical operators (AND, OR, NOT)"""
        operator = condition.get("operator", "and").lower()
        conditions = condition.get("conditions", [])
        
        # Validate input
        if not conditions:
            logger.warning("Complex condition has no sub-conditions. Defaulting to True.")
            return True
        
        try:
            if operator == "and":
                for cond in conditions:
                    # Validate condition structure
                    if not isinstance(cond, dict):
                        logger.warning("Invalid condition structure in AND condition. Skipping.")
                        continue
                        
                    if not self._evaluate_condition(cond, step_results, context):
                        return False
                return True
            elif operator == "or":
                for cond in conditions:
                    # Validate condition structure
                    if not isinstance(cond, dict):
                        logger.warning("Invalid condition structure in OR condition. Skipping.")
                        continue
                        
                    if self._evaluate_condition(cond, step_results, context):
                        return True
                return False
            elif operator == "not":
                # For NOT, we expect only one condition
                if len(conditions) > 0:
                    cond = conditions[0]
                    # Validate condition structure
                    if not isinstance(cond, dict):
                        logger.warning("Invalid condition structure in NOT condition. Defaulting to True.")
                        return True
                        
                    return not self._evaluate_condition(cond, step_results, context)
                return True
            else:
                # Unknown operator, default to True
                logger.warning(f"Unknown complex condition operator: {operator}. Defaulting to True.")
                return True
        except Exception as e:
            logger.warning(f"Error evaluating complex condition with operator {operator}: {str(e)}. Defaulting to True.")
            return True

    async def get_workflow_executions(self, workflow_id: str, skip: int = 0, limit: int = 100) -> List[WorkflowExecution]:
        """Get all executions for a specific workflow"""
        executions = self.db.query(WorkflowExecution).filter(
            WorkflowExecution.workflow_id == workflow_id
        ).order_by(WorkflowExecution.created_at.desc()).offset(skip).limit(limit).all()
        
        # Load step executions for each
        for execution in executions:
            execution.step_executions = self.db.query(StepExecution).filter(
                StepExecution.execution_id == execution.execution_id
            ).all()
        
        return executions

    async def get_workflow_execution_with_steps(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Retrieve a workflow execution with its step executions"""
        execution = await self.get_workflow_execution(execution_id)
        if execution:
            # Load step executions
            execution.step_executions = self.db.query(StepExecution).filter(
                StepExecution.execution_id == execution_id
            ).all()
        return execution