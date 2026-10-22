def clarification_skus(message, outcome, refs):
  # Display the alternatives already cited by a clarification. Never choose a winner.
  if outcome != "OUTCOME_NONE_CLARIFICATION":
    return message
  paths = [ref.split("#", 1)[0] for ref in refs]
  skus = []
  for product in WORLD["products"]:
    sku = product.get("sku")
    if product.get("_path") in paths and isinstance(sku, str) and sku and sku not in skus:
      skus.append(sku)
  if len(skus) < 2:
    return message
  missing = [sku for sku in skus if not re.search("(?i)(?<![\\w-])" + re.escape(sku) + "(?![\\w-])", message)]
  return message + " Candidates: " + ", ".join(missing) if missing else message
