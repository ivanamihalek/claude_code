# Structured output rules

The key rules for Anthropic's structured output schema:

1. **Every `"type": "object"` node** — including nested ones inside array `items` — must have `"additionalProperties": False`.
2. **Wrap the list in an envelope object** — the top-level schema must be an object; you can't use `"type": "array"` at the root.
3. **`required` keys must exactly match `properties` keys** .