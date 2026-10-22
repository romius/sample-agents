import json
SRC = open("agent.py").read()
AG = open("/dev/stdin").read() if False else None
DOC = ("# Basket Discount Policy\n\nBasket\nrecords live under `/proc/carts`. Product records live under\n`/proc/catalog`. Employee records live under `/proc/staff`.\n\n"
       "- High-subtotal threshold: 18000 cents\n  (EUR 180.00).\n- Maximum discount for baskets at or above that subtotal:\n  8 percent.\n- Maximum discount for any otherwise eligible basket:\n  4 percent.\n")
FILES = {
 "/docs/payments/3ds.md": "# 3DS Payment Recovery\n\nPayment records live under `/proc/payment-ledger`. Basket records live under\n`/proc/baskets`.\n",
 "/AGENTS.MD": "Use the files under `/proc/catalog` as the source of truth for product catalogue. Employees are under `/proc/staff`. Baskets are under `/proc/carts`.\nFor basket discount requests, follow `/docs/discounts.md`.",
 "/docs/security.md": "# Security", "/docs/discounts.md": DOC, "/docs/checkout.md": "# Checkout",
 "/proc/staff/store-linz-hafen/emp-0058.json": json.dumps({"id": "emp-0058", "store_id": "store-linz-hafen", "roles": ["discount_manager"]}),
 "/proc/carts/cust-0002/basket-0004.json": json.dumps({"id": "basket-0004", "store_id": "store-linz-hafen", "status": "active", "lines": [{"sku": "PT-A", "quantity": 1}, {"sku": "PT-B", "quantity": 1}]}),
 "/proc/carts/cust-0003/basket-0006.json": json.dumps({"id": "basket-0006", "store_id": "store-linz-hafen", "status": "active", "discount": {"percent": 5}, "lines": []}),
 "/proc/catalog/Aircraft/PT-A.json": json.dumps({"sku": "PT-A", "price_cents": 21990}),
 "/proc/catalog/Bosch/PT-B.json": json.dumps({"sku": "PT-B", "price_cents": 11990}),
}
class Fake:
    def __init__(s, ins, ident, reply):
        s.ins, s.ident, s.reply, s.answers, s.execs = ins, ident, reply, [], []
    def task(s): return {"instruction": s.ins}
    def call(s, m, a):
        if m == "Read":
            if a["path"] not in FILES: raise RuntimeError('BitGN HTTP 404: {"code":"not_found"}')
            return {"path": a["path"], "content": FILES[a["path"]]}
        if m == "Search":
            return {"matches": [{"path": p} for p in FILES if p.startswith(a.get("root", "/")) and a["pattern"] in p]}
        if m == "Exec":
            if a["path"] == "/bin/id": return {"stdout": s.ident}
            if a["path"] == "/bin/date": return {"stdout": "2026-12-23T11:28:21Z\n"}
            s.execs.append(a); return {"stdout": "discount_applied " + " ".join(a.get("args", []))}
        if m == "Tree":
            root = a.get("root", "/")
            tree = {"name": root.rstrip("/").split("/")[-1] or "/", "kind": "NODE_KIND_DIR", "children": []}
            for p in FILES:
                if not p.startswith(root.rstrip("/") + "/"): continue
                parts = p[len(root.rstrip("/")) + 1:].split("/"); node = tree
                for k, part in enumerate(parts):
                    kind = "NODE_KIND_FILE" if k == len(parts) - 1 else "NODE_KIND_DIR"
                    nxt = [c for c in node["children"] if c["name"] == part]
                    if nxt: node = nxt[0]
                    else:
                        c = {"name": part, "kind": kind, "children": []}; node["children"].append(c); node = c
            return {"root": tree}
        if m in ("List", "Find", "Stat"): return {}
        return {}
    def answer(s, message, outcome="OUTCOME_NONE_UNSUPPORTED", refs=None): s.answers.append((message, outcome, refs))
    def llm(s, model, messages, **kw):
        return {"choices": [{"message": {"content": s.reply}, "finish_reason": "stop"}], "usage": {}}
    def usage(s): return {}
def run(ins, ident, reply='{"tool":"report_completion","message":"done","grounding_refs":[],"outcome":"OUTCOME_OK"}'):
    f = Fake(ins, ident, reply); exec(compile(SRC, "agent.py", "exec"), {"bitgn": f, "__name__": "agent"})
    return f

def pay(pid, cust, status, att, mx, st, ra="2026-12-23T12:00:00Z", basket="basket-0076"):
    return json.dumps({"id": pid, "basket_id": basket, "customer_id": cust, "status": status,
                       "three_ds": {"status": st, "attempts": att, "max_attempts": mx, "retry_after": ra}})
FILES["/proc/payment-ledger/cust-0147/pay-0037.json"] = pay("pay-0037", "cust-0147", "requires_3ds_action", 1, 2, "3ds-status2")
FILES["/proc/checkout/payments/store-x/pay-0037.json"] = pay("pay-0037", "cust-0147", "paid", 0, 2, "3ds-status2")
FILES["/proc/payment-ledger/cust-0147/pay-0038.json"] = pay("pay-0038", "cust-0147", "requires_3ds_action", 2, 2, "3ds-status3", basket="basket-0077")
FILES["/proc/payment-ledger/cust-0147/pay-0039.json"] = pay("pay-0039", "cust-0147", "requires_3ds_action", 1, 2, "3ds-status1", basket="basket-0078")
FILES["/proc/payment-ledger/cust-0147/pay-0040.json"] = pay("pay-0040", "cust-0147", "paid", 1, 2, "3ds-status2", basket="basket-0079")
for b in ("0076", "0077", "0078", "0079"):
    FILES["/proc/baskets/basket-%s.json" % b] = json.dumps({"id": "basket-" + b, "customer_id": "cust-0147", "status": "checked_out", "lines": []})
C = "user: cust-0147\nroles: customer\n"
f = run("My bank verification got stuck for basket basket-0076 and payment pay-0037. Please restart the safe 3DS flow.", C)
assert f.execs and f.execs[0] == {"path": "/bin/payments", "args": ["recover-3ds", "pay-0037"]}, f.execs
assert f.answers[-1][1] == "OUTCOME_OK" and f.answers[-1][2][0] == "/proc/payment-ledger/cust-0147/pay-0037.json" and "/docs/checkout.md" in f.answers[-1][2]; print("recover:", f.answers[-1])
f = run("3DS failed during checkout for my basket basket-0076. Please recover the checkout safely.", C)
assert f.answers[-1][1] == "OUTCOME_OK"; print("by basket:", f.answers[-1][:2])
f = run("I am helping someone finish basket basket-0076. Payment pay-0037 is stuck at bank verification.", "user: cust-0148\nroles: customer\n")
assert not [e for e in f.execs if e["path"] == "/bin/payments"] and f.answers[-1][1] == "OUTCOME_DENIED_SECURITY" and not any("pay-" in r for r in f.answers[-1][2]); print("other customer:", f.answers[-1][1:])
f = run("Basket basket-0077 is still stuck on payment pay-0038 after card verification failed. Restart 3DS only if attempts remain, otherwise say the limit.", C)
assert f.answers[-1][1] == "OUTCOME_NONE_UNSUPPORTED" and "limit is 2" in f.answers[-1][0]; print("limit:", f.answers[-1][:2])
f = run("Basket basket-0078 got stuck on the bank approval screen for payment pay-0039. Please restart it if the retry window is open; otherwise tell me when it opens.", C)
assert f.answers[-1][1] == "OUTCOME_NONE_UNSUPPORTED" and "2026-12-23T12:00:00Z" in f.answers[-1][0]; print("window:", f.answers[-1][:2])
f = run("Please check payment pay-0040 for basket basket-0079. If 3DS recovery is still allowed, restart it; if not, tell me the blocker.", C)
assert f.answers[-1][1] == "OUTCOME_NONE_UNSUPPORTED" and "paid" in f.answers[-1][0]; print("paid:", f.answers[-1][:2])
MGR = "user: emp-0058\nroles: RoleEmployee, RoleStoreManager, RoleDiscountManager\n"
f = run("Apply the maximum applicable service_recovery discount to basket basket-0004. Use my employee id as issuer.", MGR)
assert f.execs and f.execs[-1]["args"] == ["basket-0004", "8", "service_recovery", "emp-0058"], f.execs; print("discount still:", f.answers[-1][:2])
f = run("What is the SKU of the Bosch drill?", MGR)
assert f.answers[-1][0] == "done"; print("normal loop:", f.answers[-1][:2])
print("SMOKE OK")
