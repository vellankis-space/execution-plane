import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
    Sheet,
    SheetContent,
    SheetDescription,
    SheetHeader,
    SheetTitle,
    SheetFooter,
} from "@/components/ui/sheet";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Trash2, MessageSquare, Play, Save, Plus, History } from "lucide-react";
import { Node } from "reactflow";
import { ActionNodeConfig } from "./ActionNodeConfig";
import { ParameterMapper } from "./ExpressionEditor";
import { VisualExpressionBuilder } from "./VisualExpressionBuilder";
import { ScrollArea } from "@/components/ui/scroll-area";

interface NodeConfigPanelProps {
    isOpen: boolean;
    onOpenChange: (open: boolean) => void;
    selectedNode: Node | null;
    updateNode: (nodeId: string, updates: Partial<Node["data"]>) => void;
    handleSaveNode: () => void;
    handleDeleteNode: () => void;
    agents: Array<{ agent_id: string; name: string }>;
    credentials: Array<{ id: string; name: string; type: string }>;
}

export function NodeConfigPanel({
    isOpen,
    onOpenChange,
    selectedNode,
    updateNode,
    handleSaveNode,
    handleDeleteNode,
    agents,
    credentials,
}: NodeConfigPanelProps) {
    if (!selectedNode) return null;

    return (
        <Sheet open={isOpen} onOpenChange={onOpenChange}>
            <SheetContent className="w-[400px] sm:w-[540px] flex flex-col p-0 gap-0 border-l border-border bg-card">
                <SheetHeader className="px-6 py-4 border-b border-border bg-muted/10">
                    <div className="flex items-center justify-between">
                        <SheetTitle className="text-lg font-semibold flex items-center gap-2">
                            {selectedNode.data.label || selectedNode.type}
                            <span className="text-xs font-normal text-muted-foreground font-mono px-2 py-0.5 rounded bg-muted">
                                {selectedNode.id}
                            </span>
                        </SheetTitle>
                        <Button variant="ghost" size="icon" className="text-destructive hover:text-destructive hover:bg-destructive/10" onClick={handleDeleteNode}>
                            <Trash2 className="w-4 h-4" />
                        </Button>
                    </div>
                    <SheetDescription>
                        Configure properties and parameters for this task.
                    </SheetDescription>
                </SheetHeader>

                <Tabs defaultValue="general" className="flex-1 flex flex-col min-h-0">
                    <div className="px-6 py-2 border-b border-border bg-muted/5">
                        <TabsList className="grid w-full grid-cols-5 bg-muted/50 h-8">
                            <TabsTrigger value="general" className="text-xs">General</TabsTrigger>
                            <TabsTrigger value="parameters" className="text-xs">Params</TabsTrigger>
                            <TabsTrigger value="advanced" className="text-xs">Advanced</TabsTrigger>
                            <TabsTrigger value="output" className="text-xs">Output</TabsTrigger>
                            <TabsTrigger value="history" className="text-xs">History</TabsTrigger>
                        </TabsList>
                    </div>

                    <ScrollArea className="flex-1">
                        <div className="p-6 space-y-6">
                            <TabsContent value="general" className="space-y-4 mt-0">
                                <div className="space-y-2">
                                    <Label>Node Name</Label>
                                    <Input
                                        value={selectedNode.data.label || ""}
                                        onChange={(e) => updateNode(selectedNode.id, { label: e.target.value })}
                                        placeholder="e.g., Process Order"
                                    />
                                </div>

                                {selectedNode.type === "agentNode" && (
                                    <div className="space-y-2">
                                        <Label>Agent</Label>
                                        <Select
                                            value={selectedNode.data.agent_id || ""}
                                            onValueChange={(value) => {
                                                const selectedAgent = agents.find(a => a.agent_id === value);
                                                updateNode(selectedNode.id, {
                                                    agent_id: value,
                                                    label: selectedAgent ? selectedAgent.name : selectedNode.data.label
                                                });
                                            }}
                                        >
                                            <SelectTrigger>
                                                <SelectValue placeholder="Select an agent worker" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {agents.map((agent) => (
                                                    <SelectItem key={agent.agent_id} value={agent.agent_id}>
                                                        {agent.name}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                        <p className="text-[10px] text-muted-foreground">
                                            The AI agent that will execute this task.
                                        </p>
                                    </div>
                                )}

                                {selectedNode.type === "groupNode" && (
                                    <div className="space-y-4">
                                        <div className="space-y-2">
                                            <Label>Group Label</Label>
                                            <Input
                                                value={selectedNode.data.label || "Group"}
                                                onChange={(e) => updateNode(selectedNode.id, { label: e.target.value })}
                                                placeholder="e.g. Authentication Flow"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>Background Color</Label>
                                            <div className="flex flex-wrap gap-2">
                                                {["#f1f5f9", "#fee2e2", "#fef3c7", "#dcfce7", "#dbeafe", "#e0e7ff", "#f3e8ff", "#fae8ff"].map((color) => (
                                                    <button
                                                        key={color}
                                                        className={`w-6 h-6 rounded-full border ${selectedNode.data.color === color ? "ring-2 ring-offset-2 ring-black dark:ring-white" : ""}`}
                                                        style={{ backgroundColor: color }}
                                                        onClick={() => updateNode(selectedNode.id, { color })}
                                                    />
                                                ))}
                                                <button
                                                    className={`w-6 h-6 rounded-full border flex items-center justify-center ${!selectedNode.data.color ? "ring-2 ring-offset-2 ring-black dark:ring-white" : ""}`}
                                                    onClick={() => updateNode(selectedNode.id, { color: undefined })}
                                                >
                                                    <span className="w-full h-px bg-red-500 rotate-45" />
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {selectedNode.type === "conditionNode" && (
                                    <div className="space-y-2">
                                        <Label>Condition Expression</Label>
                                        <VisualExpressionBuilder
                                            value={selectedNode.data.condition || ""}
                                            onChange={(value) => updateNode(selectedNode.id, { condition: value })}
                                        />
                                        <p className="text-[10px] text-muted-foreground">
                                            Build conditions visually or write custom expressions
                                        </p>
                                    </div>
                                )}

                                {selectedNode.type === "loopNode" && (
                                    <>
                                        <div className="space-y-2">
                                            <Label>Collection Path</Label>
                                            <Input
                                                placeholder="{{ $json.items }}"
                                                value={selectedNode.data.collection_path || ""}
                                                onChange={(e) => updateNode(selectedNode.id, { collection_path: e.target.value })}
                                                className="font-mono text-sm"
                                            />
                                        </div>

                                        <div className="space-y-2">
                                            <Label>Max Iterations</Label>
                                            <Input
                                                type="number"
                                                value={selectedNode.data.iterations || 10}
                                                onChange={(e) => updateNode(selectedNode.id, { iterations: parseInt(e.target.value) || 10 })}
                                                min="1"
                                                max="1000"
                                            />
                                        </div>
                                    </>
                                )}

                                {selectedNode.type === "actionNode" && (
                                    <>
                                        <div className="space-y-2">
                                            <Label>Action Type</Label>
                                            <Select
                                                value={selectedNode.data.action_type || ""}
                                                onValueChange={(value) => updateNode(selectedNode.id, { action_type: value })}
                                            >
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Select action type" />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="api_call">API Call</SelectItem>
                                                    <SelectItem value="http_request">HTTP Request</SelectItem>
                                                    <SelectItem value="data_transform">Data Transform</SelectItem>
                                                    <SelectItem value="webhook">Webhook</SelectItem>
                                                    <SelectItem value="wait">Wait/Delay</SelectItem>
                                                    <SelectItem value="custom">Custom Script</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </div>

                                        {selectedNode.data.action_type && (
                                            <ActionNodeConfig
                                                actionType={selectedNode.data.action_type}
                                                config={selectedNode.data.action_config || {}}
                                                onChange={(config) => updateNode(selectedNode.id, { action_config: config })}
                                            />
                                        )}
                                    </>
                                )}

                                {selectedNode.type === "chatNode" && (
                                    <div className="space-y-2">
                                        <Label>Welcome Message</Label>
                                        <Textarea
                                            placeholder="Enter the message to display..."
                                            value={selectedNode.data.welcomeMessage || ""}
                                            onChange={(e) => updateNode(selectedNode.id, { welcomeMessage: e.target.value })}
                                            rows={4}
                                        />
                                    </div>
                                )}

                                {/* HTTP Request Node Configuration */}
                                {selectedNode.type === "httpRequestNode" && (
                                    <>
                                        <div className="space-y-2">
                                            <Label>HTTP Method</Label>
                                            <Select
                                                value={selectedNode.data.method || "GET"}
                                                onValueChange={(value) => updateNode(selectedNode.id, { method: value })}
                                            >
                                                <SelectTrigger>
                                                    <SelectValue />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="GET">GET</SelectItem>
                                                    <SelectItem value="POST">POST</SelectItem>
                                                    <SelectItem value="PUT">PUT</SelectItem>
                                                    <SelectItem value="PATCH">PATCH</SelectItem>
                                                    <SelectItem value="DELETE">DELETE</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </div>

                                        <div className="space-y-2">
                                            <Label>URL</Label>
                                            <Input
                                                placeholder="https://api.example.com/endpoint"
                                                value={selectedNode.data.url || ""}
                                                onChange={(e) => updateNode(selectedNode.id, { url: e.target.value })}
                                                className="font-mono text-sm"
                                            />
                                        </div>

                                        <div className="space-y-2">
                                            <Label>Authentication</Label>
                                            <Select
                                                value={selectedNode.data.auth || "none"}
                                                onValueChange={(value) => updateNode(selectedNode.id, { auth: value })}
                                            >
                                                <SelectTrigger>
                                                    <SelectValue />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="none">None</SelectItem>
                                                    <SelectItem value="bearer">Bearer Token</SelectItem>
                                                    <SelectItem value="basic">Basic Auth</SelectItem>
                                                    <SelectItem value="api_key">API Key</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </div>
                                    </>
                                )}

                                {/* Database Node Configuration */}
                                {selectedNode.type === "databaseNode" && (
                                    <>
                                        <div className="space-y-2">
                                            <Label>Database Operation</Label>
                                            <Select
                                                value={selectedNode.data.operation || "select"}
                                                onValueChange={(value) => updateNode(selectedNode.id, { operation: value })}
                                            >
                                                <SelectTrigger>
                                                    <SelectValue />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="select">SELECT</SelectItem>
                                                    <SelectItem value="insert">INSERT</SelectItem>
                                                    <SelectItem value="update">UPDATE</SelectItem>
                                                    <SelectItem value="delete">DELETE</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </div>

                                        <div className="space-y-2">
                                            <Label>Table Name</Label>
                                            <Input
                                                placeholder="users"
                                                value={selectedNode.data.table || ""}
                                                onChange={(e) => updateNode(selectedNode.id, { table: e.target.value })}
                                                className="font-mono text-sm"
                                            />
                                        </div>

                                        <div className="space-y-2">
                                            <Label>SQL Query</Label>
                                            <Textarea
                                                placeholder="SELECT * FROM users WHERE id = {{ $json.user_id }}"
                                                value={selectedNode.data.query || ""}
                                                onChange={(e) => updateNode(selectedNode.id, { query: e.target.value })}
                                                rows={4}
                                                className="font-mono text-sm"
                                            />
                                        </div>

                                        <div className="space-y-2">
                                            <Label>Connection</Label>
                                            <Input
                                                placeholder="postgresql://localhost:5432/mydb"
                                                value={selectedNode.data.connection || ""}
                                                onChange={(e) => updateNode(selectedNode.id, { connection: e.target.value })}
                                                className="font-mono text-xs"
                                            />
                                        </div>
                                    </>
                                )}

                                {/* Transform Node Configuration */}
                                {selectedNode.type === "transformNode" && (
                                    <>
                                        <div className="space-y-2">
                                            <Label>Transform Type</Label>
                                            <Select
                                                value={selectedNode.data.transformType || "map"}
                                                onValueChange={(value) => updateNode(selectedNode.id, { transformType: value })}
                                            >
                                                <SelectTrigger>
                                                    <SelectValue />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="map">Map Fields</SelectItem>
                                                    <SelectItem value="filter">Filter</SelectItem>
                                                    <SelectItem value="reduce">Reduce</SelectItem>
                                                    <SelectItem value="expression">Expression</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </div>

                                        <div className="space-y-2">
                                            <Label>Transform Expression</Label>
                                            <Textarea
                                                placeholder="{{ $json.firstName + ' ' + $json.lastName }}"
                                                value={selectedNode.data.expression || ""}
                                                onChange={(e) => updateNode(selectedNode.id, { expression: e.target.value })}
                                                rows={3}
                                                className="font-mono text-sm"
                                            />
                                            <p className="text-xs text-muted-foreground">
                                                Use expressions to transform data
                                            </p>
                                        </div>
                                    </>
                                )}

                                {/* Filter Node Configuration */}
                                {selectedNode.type === "filterNode" && (
                                    <>
                                        <div className="space-y-2">
                                            <Label>Filter Mode</Label>
                                            <Select
                                                value={selectedNode.data.filterMode || "keep"}
                                                onValueChange={(value) => updateNode(selectedNode.id, { filterMode: value })}
                                            >
                                                <SelectTrigger>
                                                    <SelectValue />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="keep">Keep Matching Items</SelectItem>
                                                    <SelectItem value="remove">Remove Matching Items</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </div>

                                        <div className="space-y-2">
                                            <Label>Filter Expression</Label>
                                            <Textarea
                                                placeholder="{{ $json.age >= 18 && $json.active === true }}"
                                                value={selectedNode.data.filterExpression || ""}
                                                onChange={(e) => updateNode(selectedNode.id, { filterExpression: e.target.value })}
                                                rows={3}
                                                className="font-mono text-sm"
                                            />
                                        </div>
                                    </>
                                )}

                                {/* Merge Node Configuration */}
                                {selectedNode.type === "mergeNode" && (
                                    <>
                                        <div className="space-y-2">
                                            <Label>Merge Strategy</Label>
                                            <Select
                                                value={selectedNode.data.mergeMode || "concatenate"}
                                                onValueChange={(value) => updateNode(selectedNode.id, { mergeMode: value })}
                                            >
                                                <SelectTrigger>
                                                    <SelectValue />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="concatenate">Concatenate Arrays</SelectItem>
                                                    <SelectItem value="merge">Merge Objects</SelectItem>
                                                    <SelectItem value="zip">Zip Arrays</SelectItem>
                                                    <SelectItem value="join">Join by Key</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </div>

                                        {selectedNode.data.mergeMode === "join" && (
                                            <div className="space-y-2">
                                                <Label>Merge Key</Label>
                                                <Input
                                                    placeholder="id"
                                                    value={selectedNode.data.mergeKey || ""}
                                                    onChange={(e) => updateNode(selectedNode.id, { mergeKey: e.target.value })}
                                                    className="font-mono text-sm"
                                                />
                                                <p className="text-xs text-muted-foreground">
                                                    Field name to join on
                                                </p>
                                            </div>
                                        )}

                                        <div className="space-y-2">
                                            <Label>Number of Inputs</Label>
                                            <Input
                                                type="number"
                                                value={selectedNode.data.inputCount || 2}
                                                onChange={(e) => updateNode(selectedNode.id, { inputCount: parseInt(e.target.value) || 2 })}
                                                min="2"
                                                max="10"
                                            />
                                        </div>
                                    </>
                                )}

                                {/* Delay Node Configuration */}
                                {selectedNode.type === "delayNode" && (
                                    <>
                                        <div className="space-y-2">
                                            <Label>Delay Type</Label>
                                            <Select
                                                value={selectedNode.data.delayType || "fixed"}
                                                onValueChange={(value) => updateNode(selectedNode.id, { delayType: value })}
                                            >
                                                <SelectTrigger>
                                                    <SelectValue />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="fixed">Fixed Delay</SelectItem>
                                                    <SelectItem value="until">Wait Until Time</SelectItem>
                                                    <SelectItem value="condition">Wait for Condition</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </div>

                                        {selectedNode.data.delayType === "fixed" && (
                                            <div className="space-y-2">
                                                <Label>Duration (milliseconds)</Label>
                                                <Input
                                                    type="number"
                                                    value={selectedNode.data.duration || 1000}
                                                    onChange={(e) => updateNode(selectedNode.id, { duration: parseInt(e.target.value) || 1000 })}
                                                    min="0"
                                                />
                                                <p className="text-xs text-muted-foreground">
                                                    {selectedNode.data.duration < 1000
                                                        ? `${selectedNode.data.duration}ms`
                                                        : `${(selectedNode.data.duration / 1000).toFixed(1)}s`}
                                                </p>
                                            </div>
                                        )}

                                        {selectedNode.data.delayType === "until" && (
                                            <div className="space-y-2">
                                                <Label>Wait Until</Label>
                                                <Input
                                                    type="datetime-local"
                                                    value={selectedNode.data.waitUntil || ""}
                                                    onChange={(e) => updateNode(selectedNode.id, { waitUntil: e.target.value })}
                                                />
                                            </div>
                                        )}

                                        {selectedNode.data.delayType === "condition" && (
                                            <div className="space-y-2">
                                                <Label>Condition Expression</Label>
                                                <Textarea
                                                    placeholder="{{ $json.status === 'completed' }}"
                                                    value={selectedNode.data.condition || ""}
                                                    onChange={(e) => updateNode(selectedNode.id, { condition: e.target.value })}
                                                    rows={2}
                                                    className="font-mono text-sm"
                                                />
                                            </div>
                                        )}
                                    </>
                                )}


                                <div className="space-y-2">
                                    <Label>Description</Label>
                                    <Textarea
                                        value={selectedNode.data.description || ""}
                                        onChange={(e) => updateNode(selectedNode.id, { description: e.target.value })}
                                        placeholder="Describe what this node does..."
                                        rows={3}
                                        className="resize-none"
                                    />
                                </div>
                            </TabsContent>

                            <TabsContent value="parameters" className="mt-0">
                                <ParameterMapper
                                    nodeType={selectedNode.type}
                                    parameters={selectedNode.data.parameters || {}}
                                    onChange={(params) => updateNode(selectedNode.id, { parameters: params })}
                                    credentials={credentials}
                                />
                            </TabsContent>

                            <TabsContent value="advanced" className="space-y-6 mt-0">
                                {/* Credentials Section - for Agent and Action nodes */}
                                {(selectedNode.type === "agentNode" || selectedNode.type === "actionNode") && (
                                    <div className="space-y-2">
                                        <Label>Credentials</Label>
                                        <Select
                                            value={selectedNode.data.credential_id || "none"}
                                            onValueChange={(value) => updateNode(selectedNode.id, { credential_id: value === "none" ? undefined : value })}
                                        >
                                            <SelectTrigger>
                                                <SelectValue placeholder="Select credential" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="none">None</SelectItem>
                                                {credentials.map((cred) => (
                                                    <SelectItem key={cred.id} value={cred.id}>
                                                        {cred.name} ({cred.type})
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                        <p className="text-xs text-muted-foreground">
                                            Authentication credentials for external services
                                        </p>
                                    </div>
                                )}

                                {/* Retry Policy - for Agent, Action, and Loop nodes */}
                                {(selectedNode.type === "agentNode" || selectedNode.type === "actionNode" || selectedNode.type === "loopNode") && (
                                    <div className="space-y-4 border rounded-lg p-4 bg-muted/10">
                                        <div>
                                            <Label className="text-base font-semibold">Retry Policy</Label>
                                            <p className="text-xs text-muted-foreground mt-1">
                                                Configure automatic retry behavior on failure
                                            </p>
                                        </div>
                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="space-y-2">
                                                <Label className="text-xs">Max Retries</Label>
                                                <Input
                                                    type="number"
                                                    value={selectedNode.data.retry_policy?.max_retries ?? 3}
                                                    onChange={(e) => updateNode(selectedNode.id, {
                                                        retry_policy: { ...selectedNode.data.retry_policy, max_retries: parseInt(e.target.value) || 0 }
                                                    })}
                                                    className="h-8"
                                                    min="0"
                                                    max="10"
                                                />
                                            </div>
                                            <div className="space-y-2">
                                                <Label className="text-xs">Initial Delay (s)</Label>
                                                <Input
                                                    type="number"
                                                    value={selectedNode.data.retry_policy?.initial_delay ?? 1}
                                                    onChange={(e) => updateNode(selectedNode.id, {
                                                        retry_policy: { ...selectedNode.data.retry_policy, initial_delay: parseFloat(e.target.value) || 1 }
                                                    })}
                                                    className="h-8"
                                                    min="0"
                                                    step="0.5"
                                                />
                                            </div>
                                        </div>
                                        <div className="space-y-2">
                                            <Label className="text-xs">Retry Strategy</Label>
                                            <Select
                                                value={selectedNode.data.retry_policy?.strategy || "exponential"}
                                                onValueChange={(value) => updateNode(selectedNode.id, {
                                                    retry_policy: { ...selectedNode.data.retry_policy, strategy: value }
                                                })}
                                            >
                                                <SelectTrigger className="h-8">
                                                    <SelectValue />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="exponential">Exponential Backoff</SelectItem>
                                                    <SelectItem value="fixed">Fixed Delay</SelectItem>
                                                    <SelectItem value="linear">Linear Backoff</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </div>
                                    </div>
                                )}

                                {/* Timeout Settings - for all executable nodes */}
                                {(selectedNode.type === "agentNode" || selectedNode.type === "actionNode" || selectedNode.type === "chatNode" || selectedNode.type === "loopNode") && (
                                    <div className="space-y-2">
                                        <Label>Timeout</Label>
                                        <div className="flex gap-2">
                                            <Input
                                                type="number"
                                                value={selectedNode.data.timeout || 30}
                                                onChange={(e) => updateNode(selectedNode.id, { timeout: parseInt(e.target.value) || 30 })}
                                                className="flex-1"
                                                min="1"
                                                max="3600"
                                            />
                                            <span className="flex items-center text-sm text-muted-foreground">seconds</span>
                                        </div>
                                        <p className="text-xs text-muted-foreground">
                                            Maximum execution time before timing out
                                        </p>
                                    </div>
                                )}

                                {/* Condition Node Advanced Settings */}
                                {selectedNode.type === "conditionNode" && (
                                    <>
                                        <div className="space-y-2">
                                            <Label>Condition Mode</Label>
                                            <Select
                                                value={selectedNode.data.mode || "binary"}
                                                onValueChange={(value) => {
                                                    if (value === "multi" && (!selectedNode.data.branches || selectedNode.data.branches.length === 0)) {
                                                        // Initialize with default branches
                                                        updateNode(selectedNode.id, {
                                                            mode: value,
                                                            branches: [
                                                                { id: "case-0", label: "Case 1", value: "value1" },
                                                                { id: "case-1", label: "Case 2", value: "value2" },
                                                            ]
                                                        });
                                                    } else {
                                                        updateNode(selectedNode.id, { mode: value });
                                                    }
                                                }}
                                            >
                                                <SelectTrigger>
                                                    <SelectValue />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="binary">Binary (True/False)</SelectItem>
                                                    <SelectItem value="multi">Multi-branch (Switch)</SelectItem>
                                                </SelectContent>
                                            </Select>
                                            <p className="text-xs text-muted-foreground">
                                                Binary for simple conditions, Multi-branch for switch-case logic
                                            </p>
                                        </div>

                                        {selectedNode.data.mode === "multi" && (
                                            <div className="space-y-3 border rounded-lg p-4 bg-muted/10">
                                                <div className="flex items-center justify-between">
                                                    <Label className="text-base font-semibold">Branches</Label>
                                                    <Button
                                                        variant="outline"
                                                        size="sm"
                                                        onClick={() => {
                                                            const branches = selectedNode.data.branches || [];
                                                            const newBranch = {
                                                                id: `case-${branches.length}`,
                                                                label: `Case ${branches.length + 1}`,
                                                                value: ""
                                                            };
                                                            updateNode(selectedNode.id, {
                                                                branches: [...branches, newBranch]
                                                            });
                                                        }}
                                                    >
                                                        <Plus className="w-3 h-3 mr-1" />
                                                        Add Branch
                                                    </Button>
                                                </div>

                                                <div className="space-y-2 max-h-[300px] overflow-y-auto">
                                                    {(selectedNode.data.branches || []).map((branch: any, index: number) => (
                                                        <Card key={branch.id || index} className="p-3 bg-background">
                                                            <div className="space-y-2">
                                                                <div className="flex items-center justify-between">
                                                                    <Badge variant="outline" className="text-[10px]">
                                                                        Branch {index + 1}
                                                                    </Badge>
                                                                    <Button
                                                                        variant="ghost"
                                                                        size="icon"
                                                                        className="h-6 w-6"
                                                                        onClick={() => {
                                                                            const branches = selectedNode.data.branches || [];
                                                                            updateNode(selectedNode.id, {
                                                                                branches: branches.filter((_: any, i: number) => i !== index)
                                                                            });
                                                                        }}
                                                                    >
                                                                        <Trash2 className="w-3 h-3" />
                                                                    </Button>
                                                                </div>

                                                                <div className="grid grid-cols-2 gap-2">
                                                                    <div className="space-y-1">
                                                                        <Label className="text-[10px]">Label</Label>
                                                                        <Input
                                                                            value={branch.label || ""}
                                                                            onChange={(e) => {
                                                                                const branches = [...(selectedNode.data.branches || [])];
                                                                                branches[index] = { ...branches[index], label: e.target.value };
                                                                                updateNode(selectedNode.id, { branches });
                                                                            }}
                                                                            placeholder="High Priority"
                                                                            className="h-7 text-xs"
                                                                        />
                                                                    </div>
                                                                    <div className="space-y-1">
                                                                        <Label className="text-[10px]">Match Value</Label>
                                                                        <Input
                                                                            value={branch.value || ""}
                                                                            onChange={(e) => {
                                                                                const branches = [...(selectedNode.data.branches || [])];
                                                                                branches[index] = { ...branches[index], value: e.target.value };
                                                                                updateNode(selectedNode.id, { branches });
                                                                            }}
                                                                            placeholder="high"
                                                                            className="h-7 text-xs font-mono"
                                                                        />
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </Card>
                                                    ))}
                                                </div>
                                                <p className="text-xs text-muted-foreground">
                                                    Each branch will create a separate output handle
                                                </p>
                                            </div>
                                        )}

                                        <div className="space-y-2">
                                            <Label>Error Handling</Label>
                                            <Select
                                                value={selectedNode.data.onError || "continue"}
                                                onValueChange={(value) => updateNode(selectedNode.id, { onError: value })}
                                            >
                                                <SelectTrigger>
                                                    <SelectValue />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="continue">Continue Workflow</SelectItem>
                                                    <SelectItem value="fail">Fail Workflow</SelectItem>
                                                    <SelectItem value="fallback">Use Fallback Value</SelectItem>
                                                </SelectContent>
                                            </Select>
                                            <p className="text-xs text-muted-foreground">
                                                What to do if expression evaluation fails
                                            </p>
                                        </div>
                                    </>
                                )}

                                {/* Loop-specific advanced settings */}
                                {selectedNode.type === "loopNode" && (
                                    <>
                                        <div className="space-y-2">
                                            <Label>Execution Mode</Label>
                                            <Select
                                                value={selectedNode.data.parallelMode ? "parallel" : "sequential"}
                                                onValueChange={(value) => updateNode(selectedNode.id, { parallelMode: value === "parallel" })}
                                            >
                                                <SelectTrigger>
                                                    <SelectValue />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="sequential">Sequential</SelectItem>
                                                    <SelectItem value="parallel">Parallel</SelectItem>
                                                </SelectContent>
                                            </Select>
                                            <p className="text-xs text-muted-foreground">
                                                Process items one-by-one or in parallel
                                            </p>
                                        </div>
                                        {selectedNode.data.parallelMode && (
                                            <div className="space-y-2">
                                                <Label>Max Concurrent</Label>
                                                <Input
                                                    type="number"
                                                    value={selectedNode.data.maxConcurrent || 5}
                                                    onChange={(e) => updateNode(selectedNode.id, { maxConcurrent: parseInt(e.target.value) || 5 })}
                                                    min="1"
                                                    max="20"
                                                />
                                                <p className="text-xs text-muted-foreground">
                                                    Maximum number of parallel executions
                                                </p>
                                            </div>
                                        )}
                                    </>
                                )}

                                {/* Display mode - for display nodes */}
                                {selectedNode.type === "displayNode" && (
                                    <div className="space-y-2">
                                        <Label>Default View Mode</Label>
                                        <Select
                                            value={selectedNode.data.viewMode || "json"}
                                            onValueChange={(value) => updateNode(selectedNode.id, { viewMode: value })}
                                        >
                                            <SelectTrigger>
                                                <SelectValue />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="json">JSON</SelectItem>
                                                <SelectItem value="table">Table</SelectItem>
                                                <SelectItem value="raw">Raw</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </div>
                                )}

                                {/* Notes Section - for all nodes */}
                                <div className="space-y-2 pt-4 border-t">
                                    <Label>Internal Notes</Label>
                                    <Textarea
                                        value={selectedNode.data.notes || ""}
                                        onChange={(e) => updateNode(selectedNode.id, { notes: e.target.value })}
                                        placeholder="Add internal notes about this node..."
                                        rows={3}
                                        className="resize-none text-sm"
                                    />
                                    <p className="text-xs text-muted-foreground">
                                        Private notes for documentation (not visible in execution)
                                    </p>
                                </div>
                            </TabsContent>

                            <TabsContent value="output" className="mt-0">
                                {selectedNode.data.lastOutput ? (
                                    <div className="space-y-2">
                                        <div className="flex items-center justify-between">
                                            <Label>Last Execution Output</Label>
                                            <span className="text-xs text-muted-foreground">{selectedNode.data.executionTime}ms</span>
                                        </div>
                                        <div className="rounded-lg border bg-slate-950 p-4 overflow-auto max-h-[400px]">
                                            <pre className="text-xs font-mono text-slate-50">
                                                {JSON.stringify(selectedNode.data.lastOutput, null, 2)}
                                            </pre>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="flex flex-col items-center justify-center py-12 text-muted-foreground border border-dashed rounded-lg">
                                        <Play className="w-8 h-8 mb-2 opacity-50" />
                                        <p className="text-sm">No output data available</p>
                                        <p className="text-xs">Run the workflow to see results</p>
                                    </div>
                                )}
                            </TabsContent>

                            <TabsContent value="history" className="mt-0">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="space-y-1">
                                        <Label className="text-base font-semibold">Version History</Label>
                                        <p className="text-xs text-muted-foreground">
                                            Save and restore configuration snapshots
                                        </p>
                                    </div>
                                    <Button
                                        size="sm"
                                        onClick={() => {
                                            const history = selectedNode.data.versionHistory || [];
                                            const newVersion = {
                                                id: Date.now().toString(),
                                                timestamp: new Date().toISOString(),
                                                data: JSON.parse(JSON.stringify(selectedNode.data)),
                                                description: `Version ${history.length + 1}`
                                            };
                                            updateNode(selectedNode.id, {
                                                versionHistory: [newVersion, ...history]
                                            });
                                        }}
                                    >
                                        <Save className="w-3 h-3 mr-2" />
                                        Save Version
                                    </Button>
                                </div>

                                <div className="space-y-3">
                                    {(!selectedNode.data.versionHistory || selectedNode.data.versionHistory.length === 0) ? (
                                        <div className="flex flex-col items-center justify-center py-8 text-muted-foreground border rounded-lg border-dashed">
                                            <History className="w-8 h-8 mb-2 opacity-20" />
                                            <p className="text-xs">No saved versions</p>
                                        </div>
                                    ) : (
                                        selectedNode.data.versionHistory.map((version: any) => (
                                            <Card key={version.id} className="p-3 bg-muted/10">
                                                <div className="flex items-center justify-between mb-2">
                                                    <div className="flex items-center gap-2 min-w-0 flex-1">
                                                        <Badge variant="outline" className="text-[10px] font-mono shrink-0">
                                                            {new Date(version.timestamp).toLocaleTimeString()}
                                                        </Badge>
                                                        <span className="text-xs font-medium truncate">{version.description}</span>
                                                    </div>
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        className="h-6 text-xs shrink-0 ml-2"
                                                        onClick={() => {
                                                            // Restore version but keep the history
                                                            const { versionHistory, ...restData } = version.data;
                                                            updateNode(selectedNode.id, {
                                                                ...restData,
                                                                versionHistory: selectedNode.data.versionHistory // Keep existing history
                                                            });
                                                        }}
                                                    >
                                                        Restore
                                                    </Button>
                                                </div>
                                                <div className="text-[10px] text-muted-foreground font-mono bg-background p-2 rounded border">
                                                    <div className="line-clamp-2">
                                                        {JSON.stringify(version.data, null, 2)}
                                                    </div>
                                                </div>
                                            </Card>
                                        ))
                                    )}
                                </div>
                            </TabsContent>
                        </div>
                    </ScrollArea>

                    <SheetFooter className="px-6 py-4 border-t border-border bg-muted/10 sm:justify-between">
                        <Button variant="outline" onClick={() => onOpenChange(false)}>Close</Button>
                        <Button onClick={handleSaveNode} className="gap-2">
                            <Save className="w-4 h-4" />
                            Save Changes
                        </Button>
                    </SheetFooter>
                </Tabs>
            </SheetContent>
        </Sheet >
    );
}
