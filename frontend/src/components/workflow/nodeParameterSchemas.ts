// Parameter schema definitions for each node type
// These schemas define the structure and validation for node parameters

export type ParameterFieldType =
    | "string"
    | "number"
    | "boolean"
    | "select"
    | "array"
    | "object"
    | "credential"
    | "expression"
    | "multiline";

export interface ParameterSchema {
    key: string;
    label: string;
    type: ParameterFieldType;
    required?: boolean;
    default?: any;
    description?: string;
    options?: Array<{ label: string; value: any }>; // For select type
    placeholder?: string;
    validation?: (value: any) => boolean | string;
    dependsOn?: { field: string; value: any }; // Show field only if another field has specific value
    children?: ParameterSchema[]; // For nested objects
    min?: number; // For number type
    max?: number; // For number type
}

export const NODE_PARAMETER_SCHEMAS: Record<string, ParameterSchema[]> = {
    httpRequestNode: [
        {
            key: "method",
            label: "HTTP Method",
            type: "select",
            required: true,
            default: "GET",
            description: "The HTTP method to use for this request",
            options: [
                { label: "GET", value: "GET" },
                { label: "POST", value: "POST" },
                { label: "PUT", value: "PUT" },
                { label: "PATCH", value: "PATCH" },
                { label: "DELETE", value: "DELETE" },
            ],
        },
        {
            key: "url",
            label: "URL",
            type: "expression",
            required: true,
            placeholder: "https://api.example.com/endpoint",
            description: "The endpoint URL to send the request to",
        },
        {
            key: "headers",
            label: "Headers",
            type: "object",
            description: "HTTP headers to include in the request",
        },
        {
            key: "body",
            label: "Request Body",
            type: "expression",
            description: "Request body data (for POST/PUT/PATCH)",
            dependsOn: { field: "method", value: ["POST", "PUT", "PATCH"] },
        },
        {
            key: "auth",
            label: "Authentication",
            type: "select",
            default: "none",
            description: "Authentication method",
            options: [
                { label: "None", value: "none" },
                { label: "Bearer Token", value: "bearer" },
                { label: "Basic Auth", value: "basic" },
                { label: "API Key", value: "api_key" },
            ],
        },
    ],

    databaseNode: [
        {
            key: "operation",
            label: "Operation",
            type: "select",
            required: true,
            default: "select",
            description: "Database operation to perform",
            options: [
                { label: "SELECT", value: "select" },
                { label: "INSERT", value: "insert" },
                { label: "UPDATE", value: "update" },
                { label: "DELETE", value: "delete" },
            ],
        },
        {
            key: "table",
            label: "Table Name",
            type: "string",
            required: true,
            placeholder: "users",
            description: "Name of the database table",
        },
        {
            key: "query",
            label: "SQL Query",
            type: "multiline",
            placeholder: "SELECT * FROM users WHERE id = {{ $json.user_id }}",
            description: "SQL query to execute",
        },
        {
            key: "connection",
            label: "Connection String",
            type: "credential",
            description: "Database connection credentials",
        },
    ],

    agentNode: [
        {
            key: "agent_id",
            label: "Agent",
            type: "select",
            required: true,
            description: "The AI agent to execute this task",
            options: [], // Will be populated dynamically
        },
        {
            key: "input",
            label: "Input Message",
            type: "expression",
            placeholder: "{{ $json.userMessage }}",
            description: "Input message or data to pass to the agent",
        },
        {
            key: "context",
            label: "Additional Context",
            type: "object",
            description: "Extra context data to pass to the agent",
        },
        {
            key: "description",
            label: "Task Description",
            type: "multiline",
            placeholder: "Describe what this agent should do...",
            description: "Human-readable description of the agent's task",
        },
    ],

    transformNode: [
        {
            key: "transformType",
            label: "Transform Type",
            type: "select",
            required: true,
            default: "map",
            description: "Type of data transformation to apply",
            options: [
                { label: "Map Fields", value: "map" },
                { label: "Filter", value: "filter" },
                { label: "Reduce", value: "reduce" },
                { label: "Expression", value: "expression" },
            ],
        },
        {
            key: "expression",
            label: "Transform Expression",
            type: "expression",
            placeholder: "{{ $json.firstName + ' ' + $json.lastName }}",
            description: "JavaScript expression to transform the data",
        },
    ],

    filterNode: [
        {
            key: "filterMode",
            label: "Filter Mode",
            type: "select",
            required: true,
            default: "keep",
            description: "Whether to keep or remove matching items",
            options: [
                { label: "Keep Matching Items", value: "keep" },
                { label: "Remove Matching Items", value: "remove" },
            ],
        },
        {
            key: "filterExpression",
            label: "Filter Expression",
            type: "expression",
            placeholder: "{{ $json.age >= 18 && $json.active === true }}",
            description: "Expression that evaluates to true/false",
        },
    ],

    mergeNode: [
        {
            key: "mergeMode",
            label: "Merge Strategy",
            type: "select",
            required: true,
            default: "concatenate",
            description: "How to combine multiple inputs",
            options: [
                { label: "Concatenate Arrays", value: "concatenate" },
                { label: "Merge Objects", value: "merge" },
                { label: "Zip Arrays", value: "zip" },
                { label: "Join by Key", value: "join" },
            ],
        },
        {
            key: "mergeKey",
            label: "Merge Key",
            type: "string",
            placeholder: "id",
            description: "Field name to join on (for join mode)",
            dependsOn: { field: "mergeMode", value: "join" },
        },
        {
            key: "inputCount",
            label: "Number of Inputs",
            type: "number",
            default: 2,
            min: 2,
            max: 10,
            description: "How many inputs to merge",
        },
    ],

    delayNode: [
        {
            key: "delayType",
            label: "Delay Type",
            type: "select",
            required: true,
            default: "fixed",
            description: "Type of delay to apply",
            options: [
                { label: "Fixed Delay", value: "fixed" },
                { label: "Wait Until Time", value: "until" },
                { label: "Wait for Condition", value: "condition" },
            ],
        },
        {
            key: "duration",
            label: "Duration (milliseconds)",
            type: "number",
            default: 1000,
            min: 0,
            description: "How long to wait",
            dependsOn: { field: "delayType", value: "fixed" },
        },
        {
            key: "waitUntil",
            label: "Wait Until",
            type: "string",
            placeholder: "2024-12-31T23:59:59",
            description: "Date/time to wait until",
            dependsOn: { field: "delayType", value: "until" },
        },
        {
            key: "condition",
            label: "Condition Expression",
            type: "expression",
            placeholder: "{{ $json.status === 'completed' }}",
            description: "Wait until this expression is true",
            dependsOn: { field: "delayType", value: "condition" },
        },
    ],

    loopNode: [
        {
            key: "collection_path",
            label: "Collection Path",
            type: "expression",
            placeholder: "{{ $json.items }}",
            description: "Path to the array to iterate over",
        },
        {
            key: "iterations",
            label: "Max Iterations",
            type: "number",
            default: 10,
            min: 1,
            max: 1000,
            description: "Maximum number of iterations",
        },
        {
            key: "parallelMode",
            label: "Parallel Execution",
            type: "boolean",
            default: false,
            description: "Execute iterations in parallel",
        },
    ],

    conditionNode: [
        {
            key: "condition",
            label: "Condition Expression",
            type: "expression",
            placeholder: "{{ $json.value > 100 }}",
            description: "Expression that evaluates to true/false",
        },
        {
            key: "mode",
            label: "Condition Mode",
            type: "select",
            default: "binary",
            description: "Binary for true/false, Multi-branch for switch-case",
            options: [
                { label: "Binary (True/False)", value: "binary" },
                { label: "Multi-branch (Switch)", value: "multi" },
            ],
        },
    ],

    actionNode: [
        {
            key: "action_type",
            label: "Action Type",
            type: "select",
            required: true,
            description: "Type of action to perform",
            options: [
                { label: "API Call", value: "api_call" },
                { label: "HTTP Request", value: "http_request" },
                { label: "Data Transform", value: "data_transform" },
                { label: "Webhook", value: "webhook" },
                { label: "Wait/Delay", value: "wait" },
                { label: "Custom Script", value: "custom" },
            ],
        },
        {
            key: "action_config",
            label: "Action Configuration",
            type: "object",
            description: "Configuration specific to the action type",
        },
    ],

    chatNode: [
        {
            key: "welcomeMessage",
            label: "Welcome Message",
            type: "multiline",
            placeholder: "Enter the message to display...",
            description: "Message shown to the user",
        },
    ],
};
