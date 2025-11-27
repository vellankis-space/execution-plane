
import { describe, it, expect } from "bun:test";
import {
    validateParameter,
    isFieldVisible,
    getNodeParameterSchema,
    ParameterSchema
} from "./parameterSchemaUtils";

describe("Parameter Schema Utils", () => {
    describe("validateParameter", () => {
        it("should validate required fields", () => {
            const schema: ParameterSchema = {
                key: "test",
                label: "Test",
                type: "string",
                required: true
            };

            expect(validateParameter(schema, "value").valid).toBe(true);
            expect(validateParameter(schema, "").valid).toBe(false);
            expect(validateParameter(schema, null).valid).toBe(false);
            expect(validateParameter(schema, undefined).valid).toBe(false);
        });

        it("should validate number fields", () => {
            const schema: ParameterSchema = {
                key: "count",
                label: "Count",
                type: "number",
                min: 0,
                max: 10
            };

            expect(validateParameter(schema, 5).valid).toBe(true);
            expect(validateParameter(schema, "5").valid).toBe(true); // Should accept string numbers
            expect(validateParameter(schema, -1).valid).toBe(false);
            expect(validateParameter(schema, 11).valid).toBe(false);
            expect(validateParameter(schema, "abc").valid).toBe(false);
        });

        it("should validate select fields", () => {
            const schema: ParameterSchema = {
                key: "option",
                label: "Option",
                type: "select",
                options: [
                    { label: "A", value: "a" },
                    { label: "B", value: "b" }
                ]
            };

            expect(validateParameter(schema, "a").valid).toBe(true);
            expect(validateParameter(schema, "c").valid).toBe(false);
        });
    });

    describe("isFieldVisible", () => {
        it("should always be visible if no dependencies", () => {
            const schema: ParameterSchema = {
                key: "test",
                label: "Test",
                type: "string"
            };
            expect(isFieldVisible(schema, {})).toBe(true);
        });

        it("should respect dependencies", () => {
            const schema: ParameterSchema = {
                key: "child",
                label: "Child",
                type: "string",
                dependsOn: { field: "parent", value: "show" }
            };

            expect(isFieldVisible(schema, { parent: "show" })).toBe(true);
            expect(isFieldVisible(schema, { parent: "hide" })).toBe(false);
            expect(isFieldVisible(schema, {})).toBe(false);
        });

        it("should respect array dependencies", () => {
            const schema: ParameterSchema = {
                key: "child",
                label: "Child",
                type: "string",
                dependsOn: { field: "parent", value: ["a", "b"] }
            };

            expect(isFieldVisible(schema, { parent: "a" })).toBe(true);
            expect(isFieldVisible(schema, { parent: "b" })).toBe(true);
            expect(isFieldVisible(schema, { parent: "c" })).toBe(false);
        });
    });

    describe("getNodeParameterSchema", () => {
        it("should return schema for known node types", () => {
            const schema = getNodeParameterSchema("httpRequestNode");
            expect(schema).toBeDefined();
            expect(Array.isArray(schema)).toBe(true);
            expect(schema.length).toBeGreaterThan(0);
        });

        it("should return empty array for unknown node types", () => {
            const schema = getNodeParameterSchema("unknownNode");
            expect(schema).toEqual([]);
        });
    });
});
