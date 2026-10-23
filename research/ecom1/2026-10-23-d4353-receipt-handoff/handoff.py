# These records are scoped to this invocation of receipt_availability.
RECEIPT_PENDING = []


def receipt_capture(path, result):
  if (not isinstance(result, dict) or "lookup_error" in result
      or result.get("path", path) != path
      or not isinstance(result.get("content"), str) or not result["content"]):
    return False
  RECEIPT_PENDING.append(({"tool": "read", "path": path}, dict(result)))
  return True


def receipt_handoff(messages):
  if len(RECEIPT_PENDING) != 2:
    return messages
  additions = []
  provenance = []
  for function, result in RECEIPT_PENDING:
    # Metadata comes from this actual Read; no inferred hashes or cached files.
    metadata = {k: result[k] for k in ("path", "sha256", "contentType", "truncated") if k in result}
    body = result["content"]
    complete = not result.get("truncated") and len(body) <= 10000
    ordinary = observation(function, result)
    text = ordinary + "\n[Observed Read metadata: " + json.dumps(metadata) + "]"
    present = False
    conflict = False
    for message in messages:
      if message.get("role") != "user":
        continue
      content = message.get("content", "")
      if not isinstance(content, str) or "\n" not in content:
        continue
      first, rest = content.split("\n", 1)
      try:
        prior = json.loads(first)
      except ValueError:
        continue
      if not isinstance(prior, dict) or prior.get("tool") != "read" or prior.get("path") != function["path"]:
        continue
      if content in (ordinary, text) and complete:
        present = True
      elif not prior.get("start_line") and not prior.get("end_line") and not prior.get("number"):
        conflict = True
    if present and not conflict:
      continue
    item = {"role": "user", "content": text}
    if conflict or not complete or len(json.dumps(item).encode("utf-8")) > 12288:
      metadata["content_omitted"] = True
      metadata["reason"] = "conflicting prior observation" if conflict else "source incomplete or too large"
      item = {"role": "user", "content": json.dumps(function) + "\n"
              + "[Receipt fallback: content unavailable here; retrieve a narrower current Read before relying on it. "
              + json.dumps(metadata) + "]"}
    else:
      provenance.append((function, result))
    additions.append(item)
  # All-or-none transfer; measure the actual escaped UTF-8 JSON, not characters.
  if (not additions or len(json.dumps(additions).encode("utf-8")) > 16384
      or len(json.dumps(messages + additions).encode("utf-8")) > 54000):
    return messages
  for function, result in provenance:
    note_policy_read(function, result)
  return messages + additions


def receipt_pressure(messages, bootstrap_count, added):
  # Only discard our own initial additions. Preserve original history handling.
  if added and len(json.dumps(messages).encode("utf-8")) > 56000:
    messages = messages[:bootstrap_count - added] + messages[bootstrap_count:]
    bootstrap_count -= added
    added = 0
  return messages, bootstrap_count, added
