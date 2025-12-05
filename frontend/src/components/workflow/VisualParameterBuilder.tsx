import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { ScrollArea } from "@/components/ui/scroll-area";
import { AlertCircle, Code2, Eye } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
    getNodeParameterSchema,
    validateParameter,
    isFieldVisible,
    mergeWithDefaults,
} from "./parameterSchemaUtils";
import {
    StringParameterInput,
    MultilineParameterInput,
    NumberParameterInput,
    BooleanParameterToggle,
    SelectParameterDropdown,
    ObjectParameterBuilder,
    ExpressionParameterInput,
    CredentialParameterSelector,
} from "./ParameterTypeControls";

interface VisualParameterBuilderProps {
    nodeType: string;
    parameters: Record<string, any>;
    onChange: (params: Record<string, any>) => void;
    credentials?: Array<{ id: string; name: string; type: string }>;
    onModeChange?: (mode: "visual" | "advanced") => void;
}

export function VisualParameterBuilder({
    nodeType,
    parameters,
    onChange,
    credentials = [],
    onModeChange,
}: VisualParameterBuilderProps) {
    const [errors, setErrors] = useState<Record<string, string>>({});
    const schema = getNodeParameterSchema(nodeType);

    // If no schema exists for this node type, show a message
    if (!schema || schema.length === 0) {
        return (
            <div className="p-4 border border-dashed rounded-lg text-center">
                <p className="text-sm text-muted-foreground">
                    No visual configuration available for this node type.
                </p>
                <Button
                    variant="link"
                    size="sm"
                    onClick={() => onModeChange?.("advanced")}
                    className="mt-2"
                >
                    Switch to Advanced Mode
                </Button>
            </div>
        );
    }

    // Validate parameters when they change
    useEffect(() => {
        const newErrors: Record<string, string> = {};
        schema.forEach((field) => {
            if (isFieldVisible(field, parameters)) {
                const result = validateParameter(field, parameters[field.key]);
                if (!result.valid && result.error) {
                    newErrors[field.key] = result.error;
                }
            }
        });
        setErrors(newErrors);
    }, [parameters, schema]);

    const handleParamChange = (key: string, value: any) => {
        const newParams = { ...parameters, [key]: value };
        onChange(newParams);
    };

    const renderControl = (field: any) => {
        const commonProps = {
            schema: field,
            value: parameters[field.key],
            onChange: (val: any) => handleParamChange(field.key, val),
            error: errors[field.key],
        };

        switch (field.type) {
            case "string":
                return <StringParameterInput {...commonProps} />;
            case "multiline":
                return <MultilineParameterInput {...commonProps} />;
            case "number":
                return <NumberParameterInput {...commonProps} />;
            case "boolean":
                return <BooleanParameterToggle {...commonProps} />;
            case "select":
                return <SelectParameterDropdown {...commonProps} />;
            case "object":
                return <ObjectParameterBuilder {...commonProps} />;
            case "expression":
                return <ExpressionParameterInput {...commonProps} />;
            case "credential":
                return (
                    <CredentialParameterSelector
                        {...commonProps}
                        credentials={credentials}
                    />
                );
            default:
                return <StringParameterInput {...commonProps} />;
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between mb-4">
                <div className="space-y-1">
                    <h4 className="text-sm font-medium">Configuration</h4>
                    <p className="text-xs text-muted-foreground">
                        Configure parameters using the visual builder
                    </p>
                </div>
                <div className="flex items-center space-x-2">
                    <Label htmlFor="mode-toggle" className="text-xs">
                        Visual Mode
                    </Label>
                    <Switch
                        id="mode-toggle"
                        checked={true}
                        onCheckedChange={(checked) => {
                            if (!checked) onModeChange?.("advanced");
                        }}
                    />
                </div>
            </div>

            <div className="space-y-4">
                {schema.map((field) => {
                    if (!isFieldVisible(field, parameters)) return null;

                    return (
                        <div
                            key={field.key}
                            className="p-4 rounded-lg border bg-card/50 hover:bg-card/80 transition-colors"
                        >
                            {renderControl(field)}
                        </div>
                    );
                })}
            </div>

            {Object.keys(errors).length > 0 && (
                <Alert variant="destructive" className="mt-4">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                        Please fix the validation errors above before saving.
                    </AlertDescription>
                </Alert>
            )}
        </div>
    );
}
