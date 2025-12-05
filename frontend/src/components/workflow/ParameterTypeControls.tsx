// Type-specific parameter input controls

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Plus, X, Code2, Info } from "lucide-react";
import { ParameterSchema } from "./nodeParameterSchemas";
import { isExpression, extractExpressionContent, wrapInExpression } from "./parameterSchemaUtils";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface BaseParameterInputProps {
    schema: ParameterSchema;
    value: any;
    onChange: (value: any) => void;
    error?: string;
}

// String Parameter Input
export function StringParameterInput({ schema, value, onChange, error }: BaseParameterInputProps) {
    const [isExpressionMode, setIsExpressionMode] = useState(isExpression(value));

    const handleToggleExpression = () => {
        if (isExpressionMode) {
            // Convert from expression to plain text
            onChange(extractExpressionContent(value || ""));
        } else {
            // Convert to expression
            onChange(wrapInExpression(value || ""));
        }
        setIsExpressionMode(!isExpressionMode);
    };

    return (
        <div className="space-y-2">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Label>
                        {schema.label}
                        {schema.required && <span className="text-destructive ml-1">*</span>}
                    </Label>
                    {schema.description && (
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Info className="w-3 h-3 text-muted-foreground cursor-help" />
                                </TooltipTrigger>
                                <TooltipContent>
                                    <p className="text-xs max-w-xs">{schema.description}</p>
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                    )}
                </div>
                <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={handleToggleExpression}
                    className="h-7 text-xs"
                >
                    <Code2 className="w-3 h-3 mr-1" />
                    {isExpressionMode ? "Plain Text" : "Expression"}
                </Button>
            </div>
            <div className="relative">
                <Input
                    value={value || ""}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder={schema.placeholder}
                    className={`font-mono text-sm ${error ? "border-destructive" : ""} ${isExpressionMode ? "bg-blue-500/5 border-blue-500/30" : ""
                        }`}
                />
                {isExpressionMode && (
                    <Badge
                        variant="secondary"
                        className="absolute right-2 top-1/2 -translate-y-1/2 text-xs bg-blue-500/20 text-blue-400 border-blue-500/30"
                    >
                        Expression
                    </Badge>
                )}
            </div>
            {error && <p className="text-xs text-destructive">{error}</p>}
        </div>
    );
}

// Multiline Text Parameter Input
export function MultilineParameterInput({ schema, value, onChange, error }: BaseParameterInputProps) {
    const [isExpressionMode, setIsExpressionMode] = useState(isExpression(value));

    const handleToggleExpression = () => {
        if (isExpressionMode) {
            onChange(extractExpressionContent(value || ""));
        } else {
            onChange(wrapInExpression(value || ""));
        }
        setIsExpressionMode(!isExpressionMode);
    };

    return (
        <div className="space-y-2">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Label>
                        {schema.label}
                        {schema.required && <span className="text-destructive ml-1">*</span>}
                    </Label>
                    {schema.description && (
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Info className="w-3 h-3 text-muted-foreground cursor-help" />
                                </TooltipTrigger>
                                <TooltipContent>
                                    <p className="text-xs max-w-xs">{schema.description}</p>
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                    )}
                </div>
                <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={handleToggleExpression}
                    className="h-7 text-xs"
                >
                    <Code2 className="w-3 h-3 mr-1" />
                    {isExpressionMode ? "Plain Text" : "Expression"}
                </Button>
            </div>
            <div className="relative">
                <Textarea
                    value={value || ""}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder={schema.placeholder}
                    className={`font-mono text-sm ${error ? "border-destructive" : ""} ${isExpressionMode ? "bg-blue-500/5 border-blue-500/30" : ""
                        }`}
                    rows={4}
                />
                {isExpressionMode && (
                    <Badge
                        variant="secondary"
                        className="absolute right-2 top-2 text-xs bg-blue-500/20 text-blue-400 border-blue-500/30"
                    >
                        Expression
                    </Badge>
                )}
            </div>
            {error && <p className="text-xs text-destructive">{error}</p>}
        </div>
    );
}

// Number Parameter Input
export function NumberParameterInput({ schema, value, onChange, error }: BaseParameterInputProps) {
    return (
        <div className="space-y-2">
            <div className="flex items-center gap-2">
                <Label>
                    {schema.label}
                    {schema.required && <span className="text-destructive ml-1">*</span>}
                </Label>
                {schema.description && (
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Info className="w-3 h-3 text-muted-foreground cursor-help" />
                            </TooltipTrigger>
                            <TooltipContent>
                                <p className="text-xs max-w-xs">{schema.description}</p>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>
                )}
            </div>
            <Input
                type="number"
                value={value ?? ""}
                onChange={(e) => onChange(e.target.value ? Number(e.target.value) : undefined)}
                placeholder={schema.placeholder}
                min={schema.min}
                max={schema.max}
                className={error ? "border-destructive" : ""}
            />
            {error && <p className="text-xs text-destructive">{error}</p>}
        </div>
    );
}

// Boolean Parameter Toggle
export function BooleanParameterToggle({ schema, value, onChange, error }: BaseParameterInputProps) {
    return (
        <div className="space-y-2">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Label>
                        {schema.label}
                        {schema.required && <span className="text-destructive ml-1">*</span>}
                    </Label>
                    {schema.description && (
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Info className="w-3 h-3 text-muted-foreground cursor-help" />
                                </TooltipTrigger>
                                <TooltipContent>
                                    <p className="text-xs max-w-xs">{schema.description}</p>
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                    )}
                </div>
                <Switch checked={value || false} onCheckedChange={onChange} />
            </div>
            {error && <p className="text-xs text-destructive">{error}</p>}
        </div>
    );
}

// Select Parameter Dropdown
export function SelectParameterDropdown({ schema, value, onChange, error }: BaseParameterInputProps) {
    return (
        <div className="space-y-2">
            <div className="flex items-center gap-2">
                <Label>
                    {schema.label}
                    {schema.required && <span className="text-destructive ml-1">*</span>}
                </Label>
                {schema.description && (
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Info className="w-3 h-3 text-muted-foreground cursor-help" />
                            </TooltipTrigger>
                            <TooltipContent>
                                <p className="text-xs max-w-xs">{schema.description}</p>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>
                )}
            </div>
            <Select value={value || schema.default || ""} onValueChange={onChange}>
                <SelectTrigger className={error ? "border-destructive" : ""}>
                    <SelectValue placeholder={`Select ${schema.label.toLowerCase()}...`} />
                </SelectTrigger>
                <SelectContent>
                    {schema.options?.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                            {option.label}
                        </SelectItem>
                    ))}
                </SelectContent>
            </Select>
            {error && <p className="text-xs text-destructive">{error}</p>}
        </div>
    );
}

// Object Parameter Builder (key-value pairs)
export function ObjectParameterBuilder({ schema, value, onChange, error }: BaseParameterInputProps) {
    const [pairs, setPairs] = useState<Array<{ key: string; value: string }>>(
        Object.entries(value || {}).map(([k, v]) => ({ key: k, value: String(v) }))
    );

    const addPair = () => {
        const newPairs = [...pairs, { key: "", value: "" }];
        setPairs(newPairs);
    };

    const removePair = (index: number) => {
        const newPairs = pairs.filter((_, i) => i !== index);
        setPairs(newPairs);
        updateValue(newPairs);
    };

    const updatePair = (index: number, field: "key" | "value", val: string) => {
        const newPairs = [...pairs];
        newPairs[index][field] = val;
        setPairs(newPairs);
        updateValue(newPairs);
    };

    const updateValue = (pairList: Array<{ key: string; value: string }>) => {
        const obj: Record<string, string> = {};
        pairList.forEach((p) => {
            if (p.key) obj[p.key] = p.value;
        });
        onChange(obj);
    };

    return (
        <div className="space-y-2">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Label>
                        {schema.label}
                        {schema.required && <span className="text-destructive ml-1">*</span>}
                    </Label>
                    {schema.description && (
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Info className="w-3 h-3 text-muted-foreground cursor-help" />
                                </TooltipTrigger>
                                <TooltipContent>
                                    <p className="text-xs max-w-xs">{schema.description}</p>
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                    )}
                </div>
                <Button type="button" variant="outline" size="sm" onClick={addPair} className="h-7">
                    <Plus className="w-3 h-3 mr-1" />
                    Add
                </Button>
            </div>

            {pairs.length === 0 ? (
                <div className="text-center py-4 border border-dashed rounded-md bg-muted/20">
                    <p className="text-xs text-muted-foreground">No properties defined</p>
                </div>
            ) : (
                <div className="space-y-2 border rounded-md p-3 bg-muted/10">
                    {pairs.map((pair, index) => (
                        <div key={index} className="flex gap-2">
                            <Input
                                placeholder="Key"
                                value={pair.key}
                                onChange={(e) => updatePair(index, "key", e.target.value)}
                                className="flex-1 font-mono text-xs h-8"
                            />
                            <Input
                                placeholder="Value or {{ expression }}"
                                value={pair.value}
                                onChange={(e) => updatePair(index, "value", e.target.value)}
                                className="flex-1 font-mono text-xs h-8"
                            />
                            <Button
                                type="button"
                                variant="ghost"
                                size="icon"
                                onClick={() => removePair(index)}
                                className="h-8 w-8 shrink-0"
                            >
                                <X className="w-3 h-3" />
                            </Button>
                        </div>
                    ))}
                </div>
            )}
            {error && <p className="text-xs text-destructive">{error}</p>}
        </div>
    );
}

// Expression Parameter Input (always in expression mode)
export function ExpressionParameterInput({ schema, value, onChange, error }: BaseParameterInputProps) {
    return (
        <div className="space-y-2">
            <div className="flex items-center gap-2">
                <Label>
                    {schema.label}
                    {schema.required && <span className="text-destructive ml-1">*</span>}
                </Label>
                {schema.description && (
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Info className="w-3 h-3 text-muted-foreground cursor-help" />
                            </TooltipTrigger>
                            <TooltipContent>
                                <p className="text-xs max-w-xs">{schema.description}</p>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>
                )}
                <Badge variant="secondary" className="text-xs bg-blue-500/20 text-blue-400 border-blue-500/30">
                    Expression
                </Badge>
            </div>
            <Textarea
                value={value || ""}
                onChange={(e) => onChange(e.target.value)}
                placeholder={schema.placeholder || "{{ $json.fieldName }}"}
                className={`font-mono text-sm bg-blue-500/5 border-blue-500/30 ${error ? "border-destructive" : ""}`}
                rows={3}
            />
            <p className="text-xs text-muted-foreground">
                Use expressions to reference data from previous nodes
            </p>
            {error && <p className="text-xs text-destructive">{error}</p>}
        </div>
    );
}

// Credential Parameter Selector
export function CredentialParameterSelector({
    schema,
    value,
    onChange,
    error,
    credentials = [],
}: BaseParameterInputProps & { credentials?: Array<{ id: string; name: string; type: string }> }) {
    return (
        <div className="space-y-2">
            <div className="flex items-center gap-2">
                <Label>
                    {schema.label}
                    {schema.required && <span className="text-destructive ml-1">*</span>}
                </Label>
                {schema.description && (
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Info className="w-3 h-3 text-muted-foreground cursor-help" />
                            </TooltipTrigger>
                            <TooltipContent>
                                <p className="text-xs max-w-xs">{schema.description}</p>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>
                )}
            </div>
            <Select value={value || ""} onValueChange={onChange}>
                <SelectTrigger className={error ? "border-destructive" : ""}>
                    <SelectValue placeholder="Select credential..." />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value="">None</SelectItem>
                    {credentials.map((cred) => (
                        <SelectItem key={cred.id} value={cred.id}>
                            {cred.name} ({cred.type})
                        </SelectItem>
                    ))}
                </SelectContent>
            </Select>
            {error && <p className="text-xs text-destructive">{error}</p>}
        </div>
    );
}
