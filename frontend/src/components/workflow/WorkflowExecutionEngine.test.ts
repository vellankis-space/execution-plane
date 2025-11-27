
import { describe, it, expect, mock } from "bun:test";
import { WorkflowExecutionEngine } from "./WorkflowExecutionEngine";
import { Node, Edge } from "reactflow";

describe("WorkflowExecutionEngine", () => {
    it("should pass executionTime to onNodeUpdate callback", async () => {
        // Mock nodes and edges
        const nodes: Node[] = [
            {
                id: "start",
                type: "startNode",
                position: { x: 0, y: 0 },
                data: { label: "Start" },
            },
            {
                id: "end",
                type: "endNode",
                position: { x: 100, y: 0 },
                data: { label: "End" },
            },
        ];

        const edges: Edge[] = [
            {
                id: "e1",
                source: "start",
                target: "end",
            },
        ];

        const context = {
            workflowId: "test-workflow",
            executionId: "test-exec",
            variables: {},
            credentials: {},
        };

        // Mock callback
        const onNodeUpdate = mock((nodeId: string, status: string, output?: any, executionTime?: number) => { });

        // Initialize engine
        const engine = new WorkflowExecutionEngine(
            nodes,
            edges,
            context,
            onNodeUpdate
        );

        // Execute
        await engine.execute();

        // Verify calls
        // Start node running
        expect(onNodeUpdate).toHaveBeenCalledWith("start", "running");

        // Start node completed - should have execution time
        // Note: Since we can't easily check the exact number, we check it's defined
        const startCompleteCall = onNodeUpdate.mock.calls.find(
            call => call[0] === "start" && call[1] === "completed"
        );
        expect(startCompleteCall).toBeDefined();
        expect(startCompleteCall?.[3]).toBeDefined();
        expect(typeof startCompleteCall?.[3]).toBe("number");

        // End node completed
        const endCompleteCall = onNodeUpdate.mock.calls.find(
            call => call[0] === "end" && call[1] === "completed"
        );
        expect(endCompleteCall).toBeDefined();
        expect(endCompleteCall?.[3]).toBeDefined();
        expect(typeof endCompleteCall?.[3]).toBe("number");
    });
});
