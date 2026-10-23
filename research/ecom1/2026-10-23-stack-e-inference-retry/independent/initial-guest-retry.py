# Inserted as ordinary guest source. Inference only; never wraps world actions.
def inference_retryable(exc):
 if inference_cancelled(exc):
  return False
 text = str(exc)
 prefix = "Inference outcome/cost unconfirmed: "
 if text.startswith(prefix):
  text = text[len(prefix):]
 if inference_cancelled(RuntimeError(text)):
  return False
 status = re.match(r"^(?:OpenRouter )?HTTP ([0-9]{3})(?::| |$)", text)
 if status:
  if status.group(1) not in ("502", "503", "504"):
   return False
  body = text[status.end():].strip()
  if body.startswith("{"):
   try:
    body = json.loads(body)
   except (ValueError, TypeError):
    return False
   if not isinstance(body, dict) or any(k in body for k in ("id", "choices", "usage")):
    return False
  return True
 return text.startswith(("TimeoutError:", "ConnectionError:", "ConnectionResetError:",
                         "ConnectionAbortedError:", "ConnectionRefusedError:", "RemoteDisconnected:"))

def inference_call(*args, **kwargs):
 for attempt in range(3):
  try:
   return bitgn.llm(*args, **kwargs)
  except Exception as exc:
   if attempt == 2 or not inference_retryable(exc):
    raise
