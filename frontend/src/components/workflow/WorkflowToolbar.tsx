import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
    Play,
    Pause,
    Square,
    Save,
    Download,
    Upload,
    Trash2,
    Home,
    CheckCircle2,
    AlertCircle,
    Settings,
    ChevronLeft,
    Activity
} from "lucide-react";
import { useNavigate } from "react-router-dom";

interface WorkflowToolbarProps {
    workflowName: string;
    setWorkflowName: (name: string) => void;
    workflowId: string;
    isExecuting: boolean;
    isPaused: boolean;
    testMode: boolean;
    setTestMode: (mode: boolean) => void;
    executionStatus?: "completed" | "failed" | "running" | "pending" | "paused";
    onExecute: () => void;
    onPause: () => void;
    onStop: () => void;
    onSave: () => void;
    onExport: () => void;
    onImport: () => void;
    onClear: () => void;
    showPerformance: boolean;
    onTogglePerformance: () => void;
}

export function WorkflowToolbar({
    workflowName,
    setWorkflowName,
    workflowId,
    isExecuting,
    isPaused,
    testMode,
    setTestMode,
    executionStatus,
    onExecute,
    onPause,
    onStop,
    onSave,
    onExport,
    onImport,
    onClear,
    showPerformance,
    onTogglePerformance,
}: WorkflowToolbarProps) {
    const navigate = useNavigate();

    return (
        <div className="h-16 border-b bg-background/80 backdrop-blur-md flex items-center justify-between px-6 sticky top-0 z-10">
            <div className="flex items-center gap-4 flex-1">
                <Button variant="ghost" size="icon" onClick={() => navigate("/")} className="hover:bg-muted/50">
                    <ChevronLeft className="w-5 h-5" />
                </Button>

                <div className="flex flex-col">
                    <Input
                        value={workflowName}
                        onChange={(e) => setWorkflowName(e.target.value)}
                        className="h-8 text-lg font-semibold border-none shadow-none focus-visible:ring-0 px-0 bg-transparent w-[300px]"
                        placeholder="Untitled Workflow"
                    />
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span className="font-mono opacity-50">{workflowId}</span>
                        {executionStatus && (
                            <Badge
                                variant={executionStatus === "completed" ? "default" : executionStatus === "failed" ? "destructive" : "secondary"}
                                className="h-4 px-1.5 text-[10px] uppercase tracking-wider"
                            >
                                {executionStatus}
                            </Badge>
                        )}
                    </div>
                </div>
            </div>

            <div className="flex items-center gap-2">
                <div className="flex items-center bg-gradient-to-r from-slate-900/80 to-slate-800/80 border border-slate-700/50 rounded-xl p-1 mr-2 shadow-lg backdrop-blur-sm">
                    <Button
                        variant={testMode ? "default" : "ghost"}
                        size="sm"
                        onClick={() => setTestMode(true)}
                        className={`h-8 px-4 text-xs font-medium transition-all duration-200 ${testMode
                            ? "bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white shadow-md shadow-blue-500/30"
                            : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                            }`}
                    >
                        <CheckCircle2 className={`w-3.5 h-3.5 mr-1.5 ${testMode ? "animate-pulse" : ""}`} />
                        Test Mode
                    </Button>
                    <Button
                        variant={!testMode ? "default" : "ghost"}
                        size="sm"
                        onClick={() => setTestMode(false)}
                        className={`h-8 px-4 text-xs font-medium transition-all duration-200 ${!testMode
                            ? "bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-700 hover:to-emerald-600 text-white shadow-md shadow-emerald-500/30"
                            : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                            }`}
                    >
                        <AlertCircle className={`w-3.5 h-3.5 mr-1.5 ${!testMode ? "animate-pulse" : ""}`} />
                        Production
                    </Button>
                </div>

                <div className="h-6 w-px bg-border/50 mx-2" />

                <Button
                    onClick={onExecute}
                    disabled={isExecuting}
                    size="sm"
                    className="bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg shadow-emerald-500/20"
                >
                    <Play className="w-4 h-4 mr-2" />
                    {testMode ? "Test Run" : "Run"}
                </Button>

                {isExecuting && (
                    <>
                        <Button onClick={onPause} variant="outline" size="sm">
                            <Pause className="w-4 h-4" />
                        </Button>
                        <Button onClick={onStop} variant="destructive" size="sm">
                            <Square className="w-4 h-4" />
                        </Button>
                    </>
                )}

                <Button
                    variant={showPerformance ? "secondary" : "ghost"}
                    size="icon"
                    onClick={onTogglePerformance}
                    title="Performance Profile"
                    className={showPerformance ? "bg-blue-500/10 text-blue-600 hover:bg-blue-500/20" : ""}
                >
                    <Activity className="w-4 h-4" />
                </Button>

                <div className="h-6 w-px bg-border/50 mx-2" />

                <Button onClick={onSave} variant="outline" size="sm">
                    <Save className="w-4 h-4 mr-2" />
                    Save
                </Button>

                <Button onClick={onExport} variant="ghost" size="icon" title="Export">
                    <Download className="w-4 h-4" />
                </Button>

                <Button onClick={onImport} variant="ghost" size="icon" title="Import">
                    <Upload className="w-4 h-4" />
                </Button>

                <Button onClick={onClear} variant="ghost" size="icon" className="text-muted-foreground hover:text-destructive" title="Clear Canvas">
                    <Trash2 className="w-4 h-4" />
                </Button>
            </div>
        </div>
    );
}
