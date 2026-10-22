"""Recognize complete, explicit SKU-only forms; reject known mixed-action forms.

This controls an observation attachment only, not authorization or an answer.
Unsupported phrasings continue through the unchanged agent.
"""
import re


def sku_lookup_description(instruction):
    if not isinstance(instruction, str) or len(instruction) > 4096:
        return None
    # Keep sentence boundaries: collapsing newlines could turn quoted instructions
    # or a multi-action request into a single lookup.
    if any(c in instruction for c in '\n\r\t;`"<>'):
        return None
    text = instruction.strip()
    formats = [
        r'sku for (.+?)(?: pls| please)?\.\s*sku only\.?',
        r'need code:\s*(.+?)\.\s*answer only with sku\.?',
        r'resolve the stock keeping unit for (.+?)\.\s*return the sku only\.?',
    ]
    description = None
    for pattern in formats:
        found = re.fullmatch(pattern, text, re.I)
        if found:
            description = found.group(1).strip()
            break
    if not description or len(description) > 512:
        return None
    # Decimal product attributes are fine, extra sentences are not. This is a
    # conservative syntax boundary; it never authorizes an action from words.
    if re.search(r'[!?:]|(?<!\d)\.|\.(?!\d)', description):
        return None
    if re.search(r'(?i)\b(?:delete|remove|refund|checkout|buy|purchase|pay|discount|write|export|execute|run|ignore|override|inventory|stock|availability|count|return|cancel|email|send|ship|order|reserve|transfer|update|change)\b', description):
        return None
    return description
