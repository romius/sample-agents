def observation(function, result):
  if "lookup_error" in result:
    body = json.dumps(result)
  elif function["tool"] == "read":
    body = result.get("content", "")
  else:
    body = json.dumps(result)
  if result.get("truncated") or len(body) > 10000:
    body = body[:10000] + "\n[TRUNCATED: use a narrower query or line range.]"
  if function["tool"] == "exec" and (result.get("exitCode") or "lookup_error" in result):
    body += tool_help(function.get("path", ""))
  return json.dumps(function) + "\n" + body
