def inference_cancelled(exc):
 text = str(exc)
 for prefix in ("Inference outcome/cost unconfirmed: ", "TimeoutError: ", "ConnectionError: ", "ConnectionResetError: ", "ConnectionAbortedError: ", "ConnectionRefusedError: ", "RemoteDisconnected: "):
  if text.startswith(prefix):
   text = text[len(prefix):]
 http = re.match(r"^(?:OpenRouter )?HTTP [0-9]{3}(?::| |$)", text)
 if http:
  text = text[http.end():].strip()
  if text.startswith("{"):
   try:
    body = json.loads(text)
   except (ValueError, TypeError):
    return False
   error = body.get("error") if isinstance(body, dict) else None
   text = error.get("message", "") if isinstance(error, dict) else ""
   if not isinstance(text, str):
    return False
 return re.match(r"(?i)^(?:(?:cancelled|canceled)(?:$|[: ])|(?:sandbox )?(?:job|request) (?:was )?(?:cancelled|canceled)\b|cancellation requested(?:$|[: ]))", text) is not None
