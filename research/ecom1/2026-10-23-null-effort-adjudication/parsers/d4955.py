import json

FIELDS = {
  "tree": ["root", "level"], "find": ["root", "name", "kind", "limit"],
  "search": ["root", "pattern", "limit"], "list": ["path"],
  "read": ["path", "number", "start_line", "end_line"],
  "write": ["path", "content"], "delete": ["path"], "stat": ["path"],
  "exec": ["path", "args", "stdin"],
  "report_completion": ["completed_steps_laconic", "message", "grounding_refs", "outcome"],
  "catalog": ["query", "limit"], "stores": ["query", "limit"], "stock": ["store", "skus"],
}

OUTCOMES = ["OUTCOME_OK", "OUTCOME_DENIED_SECURITY", "OUTCOME_NONE_CLARIFICATION",
      "OUTCOME_NONE_UNSUPPORTED", "OUTCOME_ERR_INTERNAL"]

REQUIRED_ARGUMENTS = {
  "tree": [], "find": ["name"], "search": ["pattern"], "list": ["path"],
  "read": ["path"], "write": ["path", "content"], "delete": ["path"],
  "stat": ["path"], "exec": ["path"],
  "report_completion": ["message", "outcome"],
  "catalog": ["query"], "stores": ["query"], "stock": ["store", "skus"],
}

def normalize_action(function):
  if not isinstance(function, dict):
    raise ValueError("Return one JSON action object")
  tool = function.get("tool")
  if not isinstance(tool, str) or tool not in FIELDS:
    raise ValueError('Return a documented tool, for example {"tool":"read","path":"/AGENTS.MD"}')
  function = dict(function)
  if tool == "search" and "path" in function:
    if "root" in function and function["root"] != function["path"]:
      raise ValueError("search path and root conflict; supply one root")
    if "root" not in function:
      function["root"] = function["path"]
    function.pop("path")
  for key in function:
    if key != "tool" and key not in FIELDS[tool]:
      raise ValueError("Unknown argument for " + tool + ": " + key)
  for key in REQUIRED_ARGUMENTS[tool]:
    if key not in function:
      raise ValueError(tool + " requires " + key)
  for key, value in function.items():
    if key in ["root", "path", "name", "pattern", "content", "stdin", "message", "outcome", "kind",
         "query", "store"]:
      if not isinstance(value, str):
        raise ValueError(tool + "." + key + " must be a string")
    elif key in ["level", "limit", "start_line", "end_line"]:
      if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(tool + "." + key + " must be an integer")
    elif key == "number":
      if not isinstance(value, bool):
        raise ValueError("read.number must be a boolean")
    elif key in ["args", "grounding_refs", "completed_steps_laconic", "skus"]:
      if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(tool + "." + key + " must be a list of strings")
  if tool == "find" and "kind" in function:
    kind = function["kind"]
    if kind == "file":
      kind = "files"
    elif kind == "dir":
      kind = "dirs"
    if kind not in ["all", "files", "dirs"]:
      raise ValueError("find.kind must be all, files or dirs")
    function["kind"] = kind
  if tool == "report_completion":
    if not function["message"].strip() or function["outcome"] not in OUTCOMES:
      raise ValueError("Completion requires a nonempty message and a documented outcome")
  return function

def first_action_object(content):
  text = content.strip()
  if text.startswith("```"):
    if "\n" not in text or not text.endswith("```"):
      raise ValueError("Incomplete JSON fence")
    text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
  if not text.startswith("{"):
    raise ValueError("Return one JSON action object")
  depth = 0
  in_string = False
  escaped = False
  for i, char in enumerate(text):
    if in_string:
      if escaped:
        escaped = False
      elif char == "\\":
        escaped = True
      elif char == '"':
        in_string = False
    elif char == '"':
      in_string = True
    elif char == "{":
      depth += 1
    elif char == "}":
      depth -= 1
      if depth == 0:
        return json.loads(text[:i + 1])
  raise ValueError("Incomplete JSON action object")

def parse_step(content):
  step = first_action_object(content)
  function = step.get("function", step) if isinstance(step, dict) else None
  return normalize_action(function)
