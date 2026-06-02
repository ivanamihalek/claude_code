# On ToolUseBlock

This is a question about using Claude API. Please explain `ToolUseBlock` class and 
how its contents change based on whether I am providing the tool nad its schema, or using a built-in tool.

The docs pages are JavaScript-rendered so I can't scrape the full content, but the search results plus my SDK knowledge give me enough to answer accurately.

---

## `ToolUseBlock` — the class itself

`ToolUseBlock` always has the same four fields, regardless of tool type:

| Field | Type | Description |
|-------|------|-------------|
| `type` | `Literal["tool_use"]` | Always `"tool_use"` |
| `id` | `str` | Unique call ID (used to match `tool_result` responses) |
| `name` | `str` | The tool name Claude chose |
| `input` | `dict` | Arguments Claude is passing, shaped by the tool's schema |

The **class doesn't change**. What changes is the surrounding workflow and what you're expected to do with it.

---

## The two cases

### Custom / Anthropic-schema client tools (`bash`, `text_editor`, `computer`, etc.)

The response contains a `tool_use` block, your code runs the operation, and you send back a `tool_result`. The `stop_reason` is `"tool_use"`, signaling that you must handle execution.

```python
# response.stop_reason == "tool_use"
for block in response.content:
    if block.type == "tool_use":
        result = my_dispatch(block.name, block.input)  # you execute this
        # then POST back a tool_result with block.id
```

The `input` dict mirrors your JSON schema exactly — if you defined `location: str` and `unit: str`, that's what shows up.

### Server tools (`web_search`, `web_fetch`, `code_execution`)

Server tools run on Anthropic's infrastructure: you see the results directly without handling execution. Anthropic executes the tool and returns the completed response in one shot — `stop_reason` is typically `"end_turn"`.

You may still see a `ToolUseBlock` in the content (for observability/logging), but you do **not** send back a `tool_result`. The results are already embedded in the response alongside it.

```python
# response.stop_reason == "end_turn"
for block in response.content:
    if block.type == "tool_use":
        pass  # informational only — Anthropic already ran it
    elif block.type == "text":
        print(block.text)  # the answer, incorporating the tool's output
```

---

## Summary

| | Custom tool | Server tool |
|---|---|---|
| `ToolUseBlock` structure | identical | identical |
| `input` content | matches your schema | matches Anthropic's built-in schema |
| `stop_reason` | `"tool_use"` | `"end_turn"` |
| You execute? | Yes | No |
| Send `tool_result`? | Yes | No |

So `ToolUseBlock` is just a uniform envelope — the behavioral difference lives in `stop_reason` and whether Anthropic's servers have already handled execution.


--------------------------------
This does not seem to be a complete answer. I notice that the ToolUseBlock looks like this, for example, when I use my own tool:


```
ToolUseBlock(id='toolu_01S8H1zhvwTaa2yrRBJAS74Z', caller=DirectCaller(type='direct'), 
             input={'date_format': '%H:%M:%S'}, 
             name='get_current_datetime', type='tool_use')
```

However, when I call the built-in text editor, it looks like this:

```
ToolUseBlock(id='toolu_015Emiv136S3BXXjPBJMtzu5', caller=DirectCaller(type='direct'), 
             input={'command': 'view', 'path': '/home/ivana/exercises/claude_code/sandbox'},
             name='str_replace_based_edit_tool', type='tool_use')
```

How do I know which response format to expect when using built-in tools?


Good catch — you noticed two things I omitted: the `caller` field, and the fact that `input` shape is tool-specific. Let me address both.

## The `caller` field

Every tool use block includes a `caller` field indicating how it was invoked. It has two shapes:

```python
# Claude called the tool directly (normal case):
caller=DirectCaller(type='direct')

# Claude wrote code that called the tool from within a code_execution sandbox:
caller=CodeExecutionCaller(type='code_execution_20260120', tool_id='srvtoolu_abc123')
```

The `tool_id` in the second form references the code execution tool instance that made the call. This matters for programmatic tool calling — you might need to route the `tool_result` differently based on which caller invoked it.

Both of your examples show `DirectCaller`, meaning Claude chose the tool directly, not via generated code.

## Knowing the expected `input` shape for built-in tools

Each built-in tool has its own fixed schema. Anthropic provides two kinds of tools: **server tools** that execute on Anthropic's infrastructure, and **client tools** where Anthropic defines the schema but your application handles execution.

The canonical source is the tool reference table:

| Tool | Type string | Execution | Your `input` keys |
|------|-------------|-----------|-------------------|
| Web search | `web_search_20260209` | Server | `query` |
| Web fetch | `web_fetch_20260209` | Server | `url` |
| Code execution | `code_execution_20260120` | Server | `code`, `language` |
| Text editor | `text_editor_20250728` | **Client** | `command`, `path`, `old_str`, `new_str`, `new_file` |
| Bash | `bash_20250124` | **Client** | `command`, `restart` |
| Computer use | `computer_20251124` | **Client** | `action`, `coordinate`, `text`, etc. |
| Memory | `memory_20250818` | **Client** | `action`, `content` |

For **client tools** (the ones you must handle), you can look up the exact schema on each tool's individual docs page — e.g. the text editor page lists every valid `command` value (`view`, `str_replace_based_edit`, `create`, `find`). The `input` dict in `ToolUseBlock` will always conform to that schema exactly.

For **server tools**, you'll still see a `ToolUseBlock` in the response content for observability, but `stop_reason`
will be `"end_turn"` and you don't need to dispatch anything.

------------------------------------
Is there anything in the response message that would enable me to infer the type string?

No — the type string (e.g. `text_editor_20250728`) does not appear in the response. The `type` field identifies the tool and its parameters for validation purposes; the `name` field is what's exposed to the model. The response only echoes back `name`.

The `name` is your only in-response signal, and it maps deterministically to the type string for Anthropic-provided tools:

| `type` (request) | `name` (in `ToolUseBlock`) |
|---|---|
| `text_editor_20250728` / `text_editor_20250124` | `str_replace_based_edit_tool` |
| `bash_20250124` | `bash` |
| `computer_20251124` | `computer` |
| `memory_20250818` | `memory` |

So if you need to infer the type from a response, you'd maintain a mapping from name → type yourself,
keyed on what you passed in the request. The practical implication: since you construct the request with the type strings, 
you already know which tools are active — you don't need to infer from the response.
-------------------------------

Can I count on   `text_editor_20250728` / `text_editor_20250124`  for example to have the same `input` keys?


No, you cannot always count on it. The docs explicitly call out a difference: the `text_editor_20250728` tool for Claude 4 models does not include the `undo_edit` command. So the set of valid `command` values in `input` differs between the two versions.

More broadly, older tool versions are not guaranteed to be backwards-compatible with newer models. You should always use the tool version that corresponds to your model version.

The safe assumption is: **a new version date = potentially a different schema**. Treat each version as its own contract and check the per-tool docs page when upgrading. For the text editor specifically, the known difference is:

| Command | `text_editor_20250124` | `text_editor_20250728` |
|---|---|---|
| `view` | ✅ | ✅ |
| `str_replace` | ✅ | ✅ |
| `create` | ✅ | ✅ |
| `insert` | ✅ | ✅ |
| `undo_edit` | ✅ | ❌ |

So if your handler dispatches on `command`, a `case "undo_edit"` branch would be dead code with the newer version —
and you'd want a guard against it appearing unexpectedly if you ever mix versions.

