import Ajv2020 from "ajv/dist/2020";
import addFormats from "ajv-formats";
import schema from "./user-response.schema.json";
import type { ApiResponse, User } from "./types";

const ajv = new Ajv2020({ allErrors: true, strict: false });
addFormats(ajv);

const validateFn = ajv.compile(schema);

export interface ValidateResult {
  ok: boolean;
  user?: User;
  errors: string[];
}

// Validates an unknown value against the user-response schema. On success,
// returns the unwrapped User (response.data).
export function validateUserResponse(json: unknown): ValidateResult {
  const valid = validateFn(json);
  if (!valid) {
    const errors = (validateFn.errors ?? []).map((e) => {
      const where = e.instancePath || "(root)";
      return `${where} ${e.message ?? "is invalid"}`.trim();
    });
    return {
      ok: false,
      errors: errors.length ? errors.slice(0, 8) : ["Unknown validation error"],
    };
  }
  return {
    ok: true,
    user: (json as unknown as ApiResponse<User>).data,
    errors: [],
  };
}
