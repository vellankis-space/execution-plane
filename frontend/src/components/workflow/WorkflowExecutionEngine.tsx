import { Node, Edge } from "reactflow";
import { toast } from "@/hooks/use-toast";
import { safeEvaluator } from "./SafeExpressionEvaluator";

export interface ExecutionContext {
  workflowId: string;
  executionId: string;
  variables: Record<string, any>;
  credentials: Record<string, any>;
}

export interface NodeExecutionResult {
  nodeId: string;
  status: "success" | "error" | "running" | "skipped";
  output: any;
  error?: string;
  executionTime: number;
  timestamp: string;
}

export interface WorkflowExecutionResult {
  executionId: string;
  status: "completed" | "failed" | "running" | "paused";
  nodeResults: NodeExecutionResult[];
  startTime: string;
  endTime?: string;
  totalExecutionTime?: number;
}

export class WorkflowExecutionEngine {
  private context: ExecutionContext;
  private nodes: Node[];
  private edges: Edge[];
  private executionResults: Map<string, NodeExecutionResult>;
  private isPaused: boolean = false;
  private isStopped: boolean = false;
  private onNodeUpdate?: (nodeId: string, status: string, output?: any) => void;
  private onExecutionUpdate?: (result: WorkflowExecutionResult) => void;
  private onUserInputRequired?: (node: Node, welcomeMessage: string) => Promise<string>;

  constructor(
    nodes: Node[],
    edges: Edge[],
    context: ExecutionContext,
    onNodeUpdate?: (nodeId: string, status: string, output?: any) => void,
    onExecutionUpdate?: (result: WorkflowExecutionResult) => void,
    onUserInputRequired?: (node: Node, welcomeMessage: string) => Promise<string>
  ) {
    this.nodes = nodes;
    this.edges = edges;
    this.context = context;
    this.executionResults = new Map();
    this.onNodeUpdate = onNodeUpdate;
    this.onExecutionUpdate = onExecutionUpdate;
    this.onUserInputRequired = onUserInputRequired;
  }

  async execute(): Promise<WorkflowExecutionResult> {
    const startTime = new Date().toISOString();
    const startTimestamp = Date.now();

    try {
      // Find start node
      const startNode = this.nodes.find((n) => n.type === "startNode");
      if (!startNode) {
        throw new Error("No start node found");
      }

      // Execute workflow from start node
      await this.executeNode(startNode, {});

      const endTime = new Date().toISOString();
      const totalExecutionTime = Date.now() - startTimestamp;

      const result: WorkflowExecutionResult = {
        executionId: this.context.executionId,
        status: this.isStopped ? "failed" : "completed",
        nodeResults: Array.from(this.executionResults.values()),
        startTime,
        endTime,
        totalExecutionTime,
      };

      this.onExecutionUpdate?.(result);
      return result;
    } catch (error: any) {
      const endTime = new Date().toISOString();
      const totalExecutionTime = Date.now() - startTimestamp;

      const result: WorkflowExecutionResult = {
        executionId: this.context.executionId,
        status: "failed",
        nodeResults: Array.from(this.executionResults.values()),
        startTime,
        endTime,
        totalExecutionTime,
      };

      this.onExecutionUpdate?.(result);
      throw error;
    }
  }

  private async executeNode(
    node: Node,
    inputData: any
  ): Promise<NodeExecutionResult> {
    // Check if paused
    while (this.isPaused && !this.isStopped) {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }

    // Check if stopped
    if (this.isStopped) {
      throw new Error("Execution stopped by user");
    }

    const startTime = Date.now();
    this.onNodeUpdate?.(node.id, "running");

    try {
      let output: any;

      // Execute based on node type
      switch (node.type) {
        case "startNode":
          output = { data: inputData, timestamp: new Date().toISOString() };
          break;

        case "agentNode":
          output = await this.executeAgentNode(node, inputData);
          break;

        case "conditionNode":
          output = await this.executeConditionNode(node, inputData);
          break;

        case "loopNode":
          output = await this.executeLoopNode(node, inputData);
          break;

        case "actionNode":
          output = await this.executeActionNode(node, inputData);
          break;

        case "errorHandlerNode":
          output = await this.executeErrorHandlerNode(node, inputData);
          break;

        case "chatNode":
          output = await this.executeChatNode(node, inputData);
          break;

        case "displayNode":
          output = await this.executeDisplayNode(node, inputData);
          break;

        case "endNode":
          output = { finalResult: inputData, timestamp: new Date().toISOString() };
          break;

        default:
          output = inputData;
      }

      const executionTime = Date.now() - startTime;
      const result: NodeExecutionResult = {
        nodeId: node.id,
        status: "success",
        output,
        executionTime,
        timestamp: new Date().toISOString(),
      };

      this.executionResults.set(node.id, result);
      this.onNodeUpdate?.(node.id, "completed", output);

      // Execute next nodes
      await this.executeNextNodes(node, output);

      return result;
    } catch (error: any) {
      const executionTime = Date.now() - startTime;
      const result: NodeExecutionResult = {
        nodeId: node.id,
        status: "error",
        output: null,
        error: error.message,
        executionTime,
        timestamp: new Date().toISOString(),
      };

      this.executionResults.set(node.id, result);
      this.onNodeUpdate?.(node.id, "failed");

      // Try error handler nodes
      const errorHandlers = this.getErrorHandlerNodes(node);
      if (errorHandlers.length > 0) {
        for (const handler of errorHandlers) {
          await this.executeNode(handler, { error: error.message, originalInput: inputData });
        }
      } else {
        throw error;
      }

      return result;
    }
  }

  private async executeAgentNode(node: Node, inputData: any): Promise<any> {
    const { agent_id, description, parameters } = node.data;

    if (!agent_id) {
      throw new Error(`Agent not configured for node ${node.id}`);
    }

    // Prepare agent input by evaluating parameters with expressions
    let agentInput = inputData;
    
    if (parameters && Object.keys(parameters).length > 0) {
      // If node has parameters, map them from context
      agentInput = {};
      for (const [key, expression] of Object.entries(parameters)) {
        if (typeof expression === 'string') {
          agentInput[key] = this.evaluateExpression(expression as string, {
            ...this.context.variables,
            ...inputData
          });
        } else {
          agentInput[key] = expression;
        }
      }
    }

    // Convert input to string if it's an object
    let inputText = agentInput;
    if (typeof agentInput === 'object') {
      // Check for common input fields
      inputText = agentInput.query || agentInput.input || agentInput.text || JSON.stringify(agentInput);
    }

    // Call backend API to execute agent - FIXED: agent_id in URL path
    const response = await fetch(`http://localhost:8000/api/v1/agents/${agent_id}/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        input: inputText
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Agent execution failed: ${response.statusText} - ${errorText}`);
    }

    const result = await response.json();
    return result;
  }

  private async executeConditionNode(node: Node, inputData: any): Promise<any> {
    const { condition } = node.data;

    if (!condition) {
      throw new Error(`Condition not configured for node ${node.id}`);
    }

    // Evaluate condition
    const conditionResult = this.evaluateExpression(condition, inputData);

    // Get next nodes based on condition - DON'T execute here, return the result
    // executeNextNodes will handle the actual execution
    return { condition: conditionResult, data: inputData, branchTaken: conditionResult ? "true" : "false" };
  }

  private async executeLoopNode(node: Node, inputData: any): Promise<any> {
    const { iterations = 10 } = node.data;
    const results: any[] = [];

    // Get loop body nodes (those connected with "loop" handle)
    const loopEdges = this.edges.filter(
      (e) => e.source === node.id && e.sourceHandle === "loop"
    );

    for (let i = 0; i < iterations; i++) {
      if (this.isStopped) break;

      for (const edge of loopEdges) {
        const nextNode = this.nodes.find((n) => n.id === edge.target);
        if (nextNode) {
          const result = await this.executeNode(nextNode, {
            ...inputData,
            loopIndex: i,
            loopTotal: iterations,
          });
          results.push(result.output);
        }
      }
    }

    return { iterations, results, data: inputData };
  }

  private async executeActionNode(node: Node, inputData: any): Promise<any> {
    const { action_type, description } = node.data;

    switch (action_type) {
      case "api_call":
        return await this.executeApiCall(node, inputData);
      case "data_transform":
        return this.executeDataTransform(node, inputData);
      case "webhook":
        return await this.executeWebhook(node, inputData);
      case "custom":
        return this.executeCustomScript(node, inputData);
      default:
        return inputData;
    }
  }

  private async executeErrorHandlerNode(node: Node, inputData: any): Promise<any> {
    const { error_type, description } = node.data;
    console.error("Error handled:", inputData);
    return inputData;
  }

  private async executeChatNode(node: Node, inputData: any): Promise<any> {
    const welcomeMessage = node.data.welcomeMessage || "Please provide your input:";
    
    // Check if we have a callback for user input
    if (!this.onUserInputRequired) {
      throw new Error("Chat node requires user input callback to be configured");
    }

    // Request user input through the callback
    const userMessage = await this.onUserInputRequired(node, welcomeMessage);
    
    // Return the user's message in a format accessible to next nodes
    return {
      message: userMessage,
      userInput: userMessage,
      welcomeMessage: welcomeMessage,
      timestamp: new Date().toISOString(),
      nodeId: node.id
    };
  }

  private async executeDisplayNode(node: Node, inputData: any): Promise<any> {
    // Display node passes data through and marks it for visualization
    return {
      displayed: true,
      data: inputData,
      timestamp: new Date().toISOString()
    };
  }

  private async executeApiCall(node: Node, inputData: any): Promise<any> {
    return { apiCallResult: "success", data: inputData };
  }

  private executeDataTransform(node: Node, inputData: any): any {
    return { transformed: true, data: inputData };
  }

  private async executeWebhook(node: Node, inputData: any): Promise<any> {
    // Implement webhook call
    return { webhookSent: true, data: inputData };
  }

  private executeCustomScript(node: Node, inputData: any): any {
    // Implement custom script execution
    return { customExecuted: true, data: inputData };
  }

  private async executeNextNodes(node: Node, outputData: any): Promise<void> {
    // Special handling for condition nodes
    if (node.type === "conditionNode") {
      const branchTaken = outputData.branchTaken;
      const nextEdges = this.edges.filter(
        (e) => e.source === node.id && e.sourceHandle === branchTaken
      );

      for (const edge of nextEdges) {
        const nextNode = this.nodes.find((n) => n.id === edge.target);
        if (nextNode) {
          await this.executeNode(nextNode, outputData.data);
        }
      }
      return;
    }

    // Special handling for loop nodes
    if (node.type === "loopNode") {
      // After loop completes, execute next nodes
      const nextEdges = this.edges.filter(
        (e) => e.source === node.id && e.sourceHandle !== "loop"
      );

      for (const edge of nextEdges) {
        const nextNode = this.nodes.find((n) => n.id === edge.target);
        if (nextNode) {
          await this.executeNode(nextNode, outputData);
        }
      }
      return;
    }

    // Find all edges coming from this node
    const nextEdges = this.edges.filter((e) => e.source === node.id);

    // Execute all next nodes in parallel
    const executions = nextEdges.map(async (edge) => {
      const nextNode = this.nodes.find((n) => n.id === edge.target);
      if (nextNode && nextNode.type !== "endNode") {
        await this.executeNode(nextNode, outputData);
      } else if (nextNode && nextNode.type === "endNode") {
        // End node - just mark as completed
        const result: NodeExecutionResult = {
          nodeId: nextNode.id,
          status: "success",
          output: { finalResult: outputData },
          executionTime: 0,
          timestamp: new Date().toISOString(),
        };
        this.executionResults.set(nextNode.id, result);
        this.onNodeUpdate?.(nextNode.id, "completed", outputData);
      }
    });

    await Promise.all(executions);
  }

  private getErrorHandlerNodes(node: Node): Node[] {
    // Find error handler nodes connected to this node
    const errorEdges = this.edges.filter(
      (e) => e.source === node.id && e.type === "error"
    );
    return errorEdges
      .map((e) => this.nodes.find((n) => n.id === e.target))
      .filter((n): n is Node => n !== undefined && n.type === "errorHandlerNode");
  }

  private evaluateExpression(expression: string, data: any): any {
    try {
      // Safe expression evaluation
      const context = {
        $json: data,
        data,
        output: data,
        ...this.context.variables,
      };

      // Use safe evaluator to handle {{ }} template expressions
      // evaluateTemplate returns the actual value for {{ $json.field }}
      if (expression.includes('{{') && expression.includes('}}')) {
        return safeEvaluator.evaluateTemplate(expression, context);
      }
      
      // Otherwise evaluate as condition (for boolean expressions)
      return safeEvaluator.evaluateCondition(expression, context);
    } catch (error) {
      console.error("Expression evaluation error:", error);
      // Return the expression as-is if evaluation fails
      return expression;
    }
  }

  pause(): void {
    this.isPaused = true;
  }

  resume(): void {
    this.isPaused = false;
  }

  stop(): void {
    this.isStopped = true;
  }

  getExecutionResults(): NodeExecutionResult[] {
    return Array.from(this.executionResults.values());
  }
}
