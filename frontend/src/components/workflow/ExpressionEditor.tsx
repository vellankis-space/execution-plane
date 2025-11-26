import { useState, useEffect } from "react";
import { safeEvaluator } from "./SafeExpressionEvaluator";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Code2, Plus, X, Info } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface ExpressionEditorProps {
  value: string;
  onChange: (value: string) => void;
  availableData?: Record<string, any>;
  placeholder?: string;
}

export function ExpressionEditor({
  value,
  onChange,
  availableData = {},
  placeholder = "Enter expression...",
}: ExpressionEditorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [testInput, setTestInput] = useState("{}");
  const [testOutput, setTestOutput] = useState<any>(null);
  const [testError, setTestError] = useState<string>("");

  const EXPRESSION_EXAMPLES = [
    {
      category: "Data Access",
      examples: [
        { label: "Previous node output", code: "{{ $node.NodeName.json }}" },
        { label: "Specific field", code: "{{ $node.NodeName.json.fieldName }}" },
        { label: "Array item", code: "{{ $node.NodeName.json[0] }}" },
        { label: "Current item", code: "{{ $json.fieldName }}" },
      ],
    },
    {
      category: "Functions",
      examples: [
        { label: "String uppercase", code: "{{ $json.text.toUpperCase() }}" },
        { label: "String lowercase", code: "{{ $json.text.toLowerCase() }}" },
        { label: "Array length", code: "{{ $json.items.length }}" },
        { label: "Join array", code: "{{ $json.items.join(',') }}" },
      ],
    },
    {
      category: "Conditionals",
      examples: [
        { label: "If-else", code: "{{ $json.value > 10 ? 'high' : 'low' }}" },
        { label: "Null check", code: "{{ $json.field || 'default' }}" },
        { label: "Type check", code: "{{ typeof $json.value === 'string' }}" },
      ],
    },
    {
      category: "Math",
      examples: [
        { label: "Add", code: "{{ $json.price + 10 }}" },
        { label: "Multiply", code: "{{ $json.quantity * $json.price }}" },
        { label: "Round", code: "{{ Math.round($json.value) }}" },
        { label: "Random", code: "{{ Math.random() }}" },
      ],
    },
    {
      category: "Date/Time",
      examples: [
        { label: "Current timestamp", code: "{{ new Date().toISOString() }}" },
        { label: "Format date", code: "{{ new Date($json.date).toLocaleDateString() }}" },
        { label: "Unix timestamp", code: "{{ Date.now() }}" },
      ],
    },
  ];

  const VARIABLES = [
    { name: "$json", description: "Current item data" },
    { name: "$node.NodeName.json", description: "Output from specific node" },
    { name: "$input.all()", description: "All input items" },
    { name: "$input.first()", description: "First input item" },
    { name: "$input.last()", description: "Last input item" },
    { name: "$now", description: "Current timestamp" },
    { name: "$today", description: "Today's date" },
    { name: "$workflow.id", description: "Workflow ID" },
    { name: "$execution.id", description: "Execution ID" },
  ];

  const testExpression = () => {
    setTestError("");
    setTestOutput(null);
    try {
      const input = JSON.parse(testInput);
      // Safe expression evaluation
      const context = {
        $json: input,
        $node: availableData,
        $now: new Date().toISOString(),
        $today: new Date().toISOString().split("T")[0],
        $workflow: { id: "test-workflow" },
        $execution: { id: "test-execution" },
      };

      // Use safe evaluator instead of eval()
      const result = safeEvaluator.evaluateTemplate(value, context);
      setTestOutput(result);
    } catch (error: any) {
      setTestError(error.message);
    }
  };

  const insertExample = (code: string) => {
    onChange(value + (value ? " " : "") + code);
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <div className="relative">
          <Textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            className="font-mono text-sm pr-10"
            rows={3}
          />
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="absolute right-2 top-2"
            onClick={() => setIsOpen(true)}
          >
            <Code2 className="w-4 h-4" />
          </Button>
        </div>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[900px] max-h-[90vh]">
        <DialogHeader>
          <DialogTitle>Expression Editor</DialogTitle>
          <DialogDescription>
            Build expressions using data from previous nodes and built-in functions
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="editor" className="mt-4">
          <TabsList className="grid w-full grid-cols-3 bg-muted/60 rounded-full p-1">
            <TabsTrigger
              value="editor"
              className="rounded-full text-xs py-1.5 data-[state=active]:bg-background data-[state=active]:shadow-sm"
            >
              Editor
            </TabsTrigger>
            <TabsTrigger
              value="examples"
              className="rounded-full text-xs py-1.5 data-[state=active]:bg-background data-[state=active]:shadow-sm"
            >
              Examples
            </TabsTrigger>
            <TabsTrigger
              value="variables"
              className="rounded-full text-xs py-1.5 data-[state=active]:bg-background data-[state=active]:shadow-sm"
            >
              Variables
            </TabsTrigger>
          </TabsList>

          <TabsContent value="editor" className="space-y-4">
            <div>
              <Label>Expression</Label>
              <Textarea
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder="{{ $json.fieldName }}"
                className="font-mono text-sm mt-1"
                rows={6}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Use to write expressions. Reference data from previous nodes or use
                JavaScript.
              </p>
            </div>

            <div className="border-t pt-4">
              <Label>Test Expression</Label>
              <div className="grid grid-cols-2 gap-4 mt-2">
                <div>
                  <Label className="text-xs">Input Data (JSON)</Label>
                  <Textarea
                    value={testInput}
                    onChange={(e) => setTestInput(e.target.value)}
                    placeholder='{"key": "value"}'
                    className="font-mono text-xs mt-1"
                    rows={4}
                  />
                </div>
                <div>
                  <Label className="text-xs">Output</Label>
                  <div className="bg-muted rounded-md p-3 mt-1 h-[100px] overflow-auto">
                    {testError ? (
                      <div className="text-red-600 text-xs">Error: {testError}</div>
                    ) : (
                      <pre className="text-xs">
                        {testOutput !== null
                          ? JSON.stringify(testOutput, null, 2)
                          : "Click 'Test' to see output"}
                      </pre>
                    )}
                  </div>
                </div>
              </div>
              <Button onClick={testExpression} className="mt-2" size="sm">
                Test Expression
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="examples" className="space-y-4 max-h-[500px] overflow-y-auto">
            {EXPRESSION_EXAMPLES.map((category) => (
              <Card key={category.category} className="p-4">
                <h4 className="font-semibold mb-3">{category.category}</h4>
                <div className="space-y-2">
                  {category.examples.map((example, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-2 hover:bg-muted rounded-md group"
                    >
                      <div className="flex-1">
                        <p className="text-sm font-medium">{example.label}</p>
                        <code className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded mt-1 inline-block">
                          {example.code}
                        </code>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => insertExample(example.code)}
                        className="opacity-0 group-hover:opacity-100"
                      >
                        <Plus className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </Card>
            ))}
          </TabsContent>

          <TabsContent value="variables" className="space-y-2 max-h-[500px] overflow-y-auto">
            {VARIABLES.map((variable) => (
              <Card
                key={variable.name}
                className="p-3 hover:bg-muted cursor-pointer group"
                onClick={() => insertExample(variable.name)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <Badge variant="secondary" className="font-mono">
                      {variable.name}
                    </Badge>
                    <p className="text-sm text-muted-foreground mt-1">
                      {variable.description}
                    </p>
                  </div>
                  <Plus className="w-4 h-4 opacity-0 group-hover:opacity-100" />
                </div>
              </Card>
            ))}

            <Card className="p-4 bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
              <div className="flex gap-2">
                <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-sm text-blue-900 dark:text-blue-100">
                    Pro Tip
                  </h4>
                  <p className="text-xs text-blue-800 dark:text-blue-200 mt-1">
                    You can chain multiple operations:
                    <code className="bg-blue-100 dark:bg-blue-900 px-1 py-0.5 rounded mx-1">
                      {"{{ $json.name.toUpperCase().substring(0, 3) }}"}
                    </code>
                  </p>
                </div>
              </div>
            </Card>
          </TabsContent>
        </Tabs>

        <div className="flex justify-end gap-2 pt-4 border-t">
          <Button variant="outline" onClick={() => setIsOpen(false)}>
            Cancel
          </Button>
          <Button onClick={() => setIsOpen(false)}>Done</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

// Simple key-value parameter mapping
export function ParameterMapper({
  parameters,
  onChange,
}: {
  parameters: Record<string, string>;
  onChange: (params: Record<string, string>) => void;
}) {
  const [params, setParams] = useState<Array<{ key: string; value: string }>>(
    Object.entries(parameters || {}).map(([key, value]) => ({ key, value }))
  );

  // Sync with prop changes
  useEffect(() => {
    setParams(Object.entries(parameters || {}).map(([key, value]) => ({ key, value })));
  }, [parameters]);

  const addParameter = () => {
    setParams([...params, { key: "", value: "" }]);
  };

  const removeParameter = (index: number) => {
    const newParams = params.filter((_, i) => i !== index);
    setParams(newParams);
    updateParameters(newParams);
  };

  const updateParameter = (index: number, field: "key" | "value", value: string) => {
    const newParams = [...params];
    newParams[index][field] = value;
    setParams(newParams);
    updateParameters(newParams);
  };

  const updateParameters = (paramList: Array<{ key: string; value: string }>) => {
    const paramObj: Record<string, string> = {};
    paramList.forEach((p) => {
      if (p.key) paramObj[p.key] = p.value;
    });
    onChange(paramObj);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <Label>Parameters</Label>
          <p className="text-xs text-muted-foreground mt-0.5">
            Define key-value pairs to pass to this node
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={addParameter}>
          <Plus className="w-4 h-4 mr-1" />
          Add
        </Button>
      </div>

      {params.length === 0 ? (
        <div className="text-center py-8 border border-dashed rounded-lg">
          <p className="text-sm text-muted-foreground">No parameters defined</p>
          <p className="text-xs text-muted-foreground mt-1">Click "Add" to create a parameter</p>
        </div>
      ) : (
        <div className="space-y-2">
          {params.map((param, index) => (
            <div key={index} className="flex gap-2">
              <Input
                placeholder="Key (e.g., user_id)"
                value={param.key}
                onChange={(e) => updateParameter(index, "key", e.target.value)}
                className="flex-1 font-mono text-sm"
              />
              <Input
                placeholder="Value or {{ expression }}"
                value={param.value}
                onChange={(e) => updateParameter(index, "value", e.target.value)}
                className="flex-1 font-mono text-sm"
              />
              <Button
                variant="ghost"
                size="icon"
                onClick={() => removeParameter(index)}
                className="shrink-0"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
