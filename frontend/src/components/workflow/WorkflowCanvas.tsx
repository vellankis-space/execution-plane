import { useRef } from "react";
import ReactFlow, {
    Node,
    Edge,
    Connection,
    Background,
    BackgroundVariant,
    ReactFlowInstance,
    Panel,
    NodeChange,
    EdgeChange,
    Controls,
    MiniMap,
} from "reactflow";
import "reactflow/dist/style.css";
import { nodeTypes } from "./CustomNodes";
import { Maximize, Minus, Plus } from "lucide-react";

interface WorkflowCanvasProps {
    nodes: Node[];
    edges: Edge[];
    onNodesChange: (changes: NodeChange[]) => void;
    onEdgesChange: (changes: EdgeChange[]) => void;
    onConnect: (params: Connection) => void;
    onNodeClick: (event: React.MouseEvent, node: Node) => void;
    onInit: (instance: ReactFlowInstance) => void;
    onDrop: (event: React.DragEvent) => void;
    onDragOver: (event: React.DragEvent) => void;
    showMinimap?: boolean;
}

export function WorkflowCanvas({
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    onNodeClick,
    onInit,
    onDrop,
    onDragOver,
    showMinimap = true,
}: WorkflowCanvasProps) {
    const reactFlowWrapper = useRef<HTMLDivElement>(null);

    return (
        <div className="flex-1 flex flex-col h-full bg-slate-950 relative">
            <div className="flex-1 h-full" ref={reactFlowWrapper}>
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    onNodeClick={onNodeClick}
                    onInit={onInit}
                    onDrop={onDrop}
                    onDragOver={onDragOver}
                    nodeTypes={nodeTypes}
                    fitView
                    minZoom={0.1}
                    maxZoom={2}
                    defaultEdgeOptions={{
                        type: 'smoothstep',
                        animated: true,
                        style: { stroke: '#64748b', strokeWidth: 2 },
                    }}
                    className="bg-slate-950"
                >
                    <Background
                        variant={BackgroundVariant.Cross}
                        gap={20}
                        size={1}
                        color="#1e293b"
                        className="bg-slate-950"
                    />

                    <Controls
                        className="bg-card border border-border shadow-sm rounded-md overflow-hidden !bottom-4 !left-4 !m-0"
                        showInteractive={false}
                    />

                    {showMinimap && (
                        <MiniMap
                            nodeStrokeWidth={3}
                            zoomable
                            pannable
                            className="!bg-card !border-border !bottom-4 !right-4 !m-0 rounded-md shadow-sm"
                            maskColor="rgba(0, 0, 0, 0.3)"
                            nodeColor={(node) => {
                                switch (node.type) {
                                    case 'startNode': return '#10b981';
                                    case 'endNode': return '#ef4444';
                                    case 'agentNode': return '#3b82f6';
                                    case 'conditionNode': return '#eab308';
                                    default: return '#64748b';
                                }
                            }}
                        />
                    )}

                    <Panel position="top-right" className="m-4">
                        <div className="flex items-center gap-4 px-3 py-1.5 bg-card/80 backdrop-blur border border-border rounded-full shadow-sm text-xs font-mono text-muted-foreground">
                            <div className="flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                <span>System Online</span>
                            </div>
                            <div className="w-px h-3 bg-border" />
                            <span>{nodes.length} Nodes</span>
                            <div className="w-px h-3 bg-border" />
                            <span>{edges.length} Edges</span>
                        </div>
                    </Panel>
                </ReactFlow>
            </div>
        </div>
    );
}
