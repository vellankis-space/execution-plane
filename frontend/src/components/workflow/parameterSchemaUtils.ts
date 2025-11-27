// Utility functions for working with parameter schemas

import { NODE_PARAMETER_SCHEMAS, ParameterSchema } from "./nodeParameterSchemas";

export interface ValidationResult {
    valid: boolean;
    error?: string;
}

/**
 * Get parameter schema for a specific node type
 */
export function getNodeParameterSchema(nodeType: string): ParameterSchema[] {
    return NODE_PARAMETER_SCHEMAS[nodeType] || [];
}

/**
 * Validate a parameter value against its schema
 */
export function validateParameter(
    schema: ParameterSchema,
    value: any
): ValidationResult {
    // Check required fields
    if (schema.required && (value === undefined || value === null || value === "")) {
        return { valid: false, error: `${schema.label} is required` };
    }

    // Skip validation if value is empty and not required
    if (!schema.required && (value === undefined || value === null || value === "")) {
        return { valid: true };
    }

    // Type-specific validation
    switch (schema.type) {
        case "number":
            if (typeof value !== "number" && isNaN(Number(value))) {
                return { valid: false, error: `${schema.label} must be a number` };
            }
            const numValue = Number(value);
            if (schema.min !== undefined && numValue < schema.min) {
                return { valid: false, error: `${schema.label} must be at least ${schema.min}` };
            }
            if (schema.max !== undefined && numValue > schema.max) {
                return { valid: false, error: `${schema.label} must be at most ${schema.max}` };
            }
            break;

        case "boolean":
            if (typeof value !== "boolean") {
                return { valid: false, error: `${schema.label} must be a boolean` };
            }
            break;

        case "select":
            if (schema.options && !schema.options.some((opt) => opt.value === value)) {
                return { valid: false, error: `${schema.label} has an invalid value` };
            }
            break;

        case "array":
            if (!Array.isArray(value)) {
                return { valid: false, error: `${schema.label} must be an array` };
            }
            break;

        case "object":
            if (typeof value !== "object" || Array.isArray(value)) {
                return { valid: false, error: `${schema.label} must be an object` };
            }
            break;
    }

    // Custom validation function
    if (schema.validation) {
        const result = schema.validation(value);
        if (result !== true) {
            return { valid: false, error: typeof result === "string" ? result : "Validation failed" };
        }
    }

    return { valid: true };
}

/**
 * Generate default parameters from schema
 */
export function getDefaultParameters(nodeType: string): Record<string, any> {
    const schema = getNodeParameterSchema(nodeType);
    const defaults: Record<string, any> = {};

    schema.forEach((field) => {
        if (field.default !== undefined) {
            defaults[field.key] = field.default;
        }
    });

    return defaults;
}

/**
 * Check if a field should be visible based on dependencies
 */
export function isFieldVisible(
    schema: ParameterSchema,
    allParams: Record<string, any>
): boolean {
    if (!schema.dependsOn) {
        return true;
    }

    const { field, value } = schema.dependsOn;
    const currentValue = allParams[field];

    // If dependsOn value is an array, check if current value is in the array
    if (Array.isArray(value)) {
        return value.includes(currentValue);
    }

    // Otherwise, check for exact match
    return currentValue === value;
}

/**
 * Validate all parameters for a node
 */
export function validateAllParameters(
    nodeType: string,
    parameters: Record<string, any>
): { valid: boolean; errors: Record<string, string> } {
    const schema = getNodeParameterSchema(nodeType);
    const errors: Record<string, string> = {};
    let valid = true;

    schema.forEach((field) => {
        // Skip validation if field is not visible
        if (!isFieldVisible(field, parameters)) {
            return;
        }

        const result = validateParameter(field, parameters[field.key]);
        if (!result.valid && result.error) {
            errors[field.key] = result.error;
            valid = false;
        }
    });

    return { valid, errors };
}

/**
 * Merge parameters with defaults
 */
export function mergeWithDefaults(
    nodeType: string,
    parameters: Record<string, any>
): Record<string, any> {
    const defaults = getDefaultParameters(nodeType);
    return { ...defaults, ...parameters };
}

/**
 * Check if a value is an expression (wrapped in {{ }})
 */
export function isExpression(value: any): boolean {
    if (typeof value !== "string") return false;
    const trimmed = value.trim();
    return trimmed.startsWith("{{") && trimmed.endsWith("}}");
}

/**
 * Extract expression content (without {{ }})
 */
export function extractExpressionContent(expression: string): string {
    const trimmed = expression.trim();
    if (trimmed.startsWith("{{") && trimmed.endsWith("}}")) {
        return trimmed.slice(2, -2).trim();
    }
    return expression;
}

/**
 * Wrap content in expression syntax
 */
export function wrapInExpression(content: string): string {
    return `{{ ${content.trim()} }}`;
}
