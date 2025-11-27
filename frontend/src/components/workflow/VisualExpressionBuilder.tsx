import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Plus, X, Code2 } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";

interface Rule {
    id: string;
    field: string;
    operator: string;
    value: string;
}

interface ExpressionBuilderProps {
    value: string;
    onChange: (value: string) => void;
    mode?: "simple" | "advanced";
}

const OPERATORS = [
    { value: "==", label: "equals" },
    { value: "!=", label: "not equals" },
    { value: ">", label: "greater than" },
    { value: ">=", label: "greater or equal" },
    { value: "<", label: "less than" },
    { value: "<=", label: "less or equal" },
    { value: "contains", label: "contains" },
    { value: "startsWith", label: "starts with" },
    { value: "endsWith", label: "ends with" },
    { value: "isEmpty", label: "is empty" },
    { value: "isNotEmpty", label: "is not empty" },
];

export function VisualExpressionBuilder({
    value,
    onChange,
    mode = "simple",
}: ExpressionBuilderProps) {
    const [viewMode, setViewMode] = useState<"visual" | "code">(mode === "simple" ? "visual" : "code");
    const [rules, setRules] = useState<Rule[]>([
        { id: "1", field: "", operator: "==", value: "" },
    ]);
    const [logicOperator, setLogicOperator] = useState<"AND" | "OR">("AND");

    const addRule = () => {
        const newRule: Rule = {
            id: Date.now().toString(),
            field: "",
            operator: "==",
            value: "",
        };
        setRules([...rules, newRule]);
    };

    const removeRule = (id: string) => {
        if (rules.length > 1) {
            setRules(rules.filter((r) => r.id !== id));
        }
    };

    const updateRule = (id: string, updates: Partial<Rule>) => {
        setRules(rules.map((r) => (r.id === id ? { ...r, ...updates } : r)));
    };

    const generateExpression = () => {
        const expressions = rules
            .filter((r) => r.field && r.operator)
            .map((r) => {
                const field = `$json.${r.field}`;

                switch (r.operator) {
                    case "contains":
                        return `${field}.includes('${r.value}')`;
                    case "startsWith":
                        return `${field}.startsWith('${r.value}')`;
                    case "endsWith":
                        return `${field}.endsWith('${r.value}')`;
                    case "isEmpty":
                        return `!${field} || ${field}.length === 0`;
                    case "isNotEmpty":
                        return `${field} && ${field}.length > 0`;
                    default:
                        // For numeric values, don't add quotes
                        const isNumeric = !isNaN(Number(r.value));
                        const formattedValue = isNumeric ? r.value : `'${r.value}'`;
                        return `${field} ${r.operator} ${formattedValue}`;
                }
            });

        const expression =
            expressions.length > 1
                ? expressions.join(` ${logicOperator.toLowerCase()} `)
                : expressions[0] || "";

        return `{{ ${expression} }}`;
    };

    const applyExpression = () => {
        const expr = generateExpression();
        onChange(expr);
    };

    return (
        <div className="space-y-4">
            <Tabs value={viewMode} onValueChange={(v) => setViewMode(v as "visual" | "code")}>
                <TabsList className="grid w-full grid-cols-2 bg-muted/50">
                    <TabsTrigger value="visual" className="text-xs">
                        Visual Builder
                    </TabsTrigger>
                    <TabsTrigger value="code" className="text-xs">
                        Code Editor
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="visual" className="space-y-4 mt-4">
                    {/* Logic Operator Selector */}
                    {rules.length > 1 && (
                        <div className="flex items-center gap-2">
                            <Label className="text-xs">Match</Label>
                            <Select value={logicOperator} onValueChange={(v) => setLogicOperator(v as "AND" | "OR")}>
                                <SelectTrigger className="w-24 h-7 text-xs">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="AND">ALL</SelectItem>
                                    <SelectItem value="OR">ANY</SelectItem>
                                </SelectContent>
                            </Select>
                            <span className="text-xs text-muted-foreground">of the following rules</span>
                        </div>
                    )}

                    {/* Rules */}
                    <div className="space-y-2">
                        {rules.map((rule, index) => (
                            <Card key={rule.id} className="p-3 bg-muted/20">
                                <div className="space-y-2">
                                    <div className="flex items-center justify-between">
                                        <Badge variant="outline" className="text-[10px] h-5">
                                            Rule {index + 1}
                                        </Badge>
                                        {rules.length > 1 && (
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="h-6 w-6"
                                                onClick={() => removeRule(rule.id)}
                                            >
                                                <X className="w-3 h-3" />
                                            </Button>
                                        )}
                                    </div>

                                    <div className="grid grid-cols-[1fr_120px_1fr] gap-2">
                                        {/* Field */}
                                        <div className="space-y-1">
                                            <Label className="text-[10px] text-muted-foreground">Field</Label>
                                            <Input
                                                placeholder="age"
                                                value={rule.field}
                                                onChange={(e) => updateRule(rule.id, { field: e.target.value })}
                                                className="h-8 text-xs font-mono"
                                            />
                                        </div>

                                        {/* Operator */}
                                        <div className="space-y-1">
                                            <Label className="text-[10px] text-muted-foreground">Operator</Label>
                                            <Select
                                                value={rule.operator}
                                                onValueChange={(v) => updateRule(rule.id, { operator: v })}
                                            >
                                                <SelectTrigger className="h-8 text-xs">
                                                    <SelectValue />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    {OPERATORS.map((op) => (
                                                        <SelectItem key={op.value} value={op.value} className="text-xs">
                                                            {op.label}
                                                        </SelectItem>
                                                    ))}
                                                </SelectContent>
                                            </Select>
                                        </div>

                                        {/* Value */}
                                        {!["isEmpty", "isNotEmpty"].includes(rule.operator) && (
                                            <div className="space-y-1">
                                                <Label className="text-[10px] text-muted-foreground">Value</Label>
                                                <Input
                                                    placeholder="18"
                                                    value={rule.value}
                                                    onChange={(e) => updateRule(rule.id, { value: e.target.value })}
                                                    className="h-8 text-xs font-mono"
                                                />
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </Card>
                        ))}
                    </div>

                    {/* Add Rule Button */}
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={addRule}
                        className="w-full h-8 text-xs"
                    >
                        <Plus className="w-3 h-3 mr-1" />
                        Add Rule
                    </Button>

                    {/* Preview */}
                    <div className="space-y-1">
                        <Label className="text-xs">Generated Expression</Label>
                        <div className="p-2 bg-slate-950 rounded border border-slate-800">
                            <code className="text-xs font-mono text-slate-50">
                                {generateExpression() || "{{ }}"}
                            </code>
                        </div>
                    </div>

                    {/* Apply Button */}
                    <Button onClick={applyExpression} className="w-full" size="sm">
                        <Code2 className="w-3 h-3 mr-1" />
                        Apply Expression
                    </Button>
                </TabsContent>

                <TabsContent value="code" className="space-y-3 mt-4">
                    <div className="space-y-2">
                        <Label>Expression</Label>
                        <Textarea
                            value={value}
                            onChange={(e) => onChange(e.target.value)}
                            placeholder="{{ $json.age > 18 && $json.active === true }}"
                            className="font-mono text-sm min-h-[120px]"
                        />
                        <p className="text-xs text-muted-foreground">
                            Write custom expressions using JavaScript syntax and {'{{ }}'} template markers
                        </p>
                    </div>

                    {/* Quick Snippets */}
                    <div className="space-y-2">
                        <Label className="text-xs">Quick Snippets</Label>
                        <div className="grid grid-cols-2 gap-2">
                            <Button
                                variant="outline"
                                size="sm"
                                className="justify-start text-xs h-auto py-2"
                                onClick={() => onChange("{{ $json.field > 0 }}")}
                            >
                                <div className="text-left">
                                    <div className="font-medium">Numeric Check</div>
                                    <code className="text-[10px] text-muted-foreground">value &gt; 0</code>
                                </div>
                            </Button>
                            <Button
                                variant="outline"
                                size="sm"
                                className="justify-start text-xs h-auto py-2"
                                onClick={() => onChange("{{ $json.field.includes('text') }}")}
                            >
                                <div className="text-left">
                                    <div className="font-medium">Contains Text</div>
                                    <code className="text-[10px] text-muted-foreground">includes()</code>
                                </div>
                            </Button>
                            <Button
                                variant="outline"
                                size="sm"
                                className="justify-start text-xs h-auto py-2"
                                onClick={() => onChange("{{ $json.field && $json.field.length > 0 }}")}
                            >
                                <div className="text-left">
                                    <div className="font-medium">Not Empty</div>
                                    <code className="text-[10px] text-muted-foreground">length &gt; 0</code>
                                </div>
                            </Button>
                            <Button
                                variant="outline"
                                size="sm"
                                className="justify-start text-xs h-auto py-2"
                                onClick={() => onChange("{{ $json.field1 === $json.field2 }}")}
                            >
                                <div className="text-left">
                                    <div className="font-medium">Compare Fields</div>
                                    <code className="text-[10px] text-muted-foreground">field1 === field2</code>
                                </div>
                            </Button>
                        </div>
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
}
