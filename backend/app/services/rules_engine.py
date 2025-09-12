import yaml, os, ast
from typing import Dict, Any, List, Tuple
from ..logging_utils import log_event

_RULES_PATH = os.path.join(os.path.dirname(__file__), "..", "fraud_rules.yaml")
_cached: Dict[str, List[Dict[str, Any]]] | None = None

ALLOWED_NODES = (
    ast.Expression, ast.BoolOp, ast.BinOp, ast.UnaryOp,
    ast.Compare, ast.Load, ast.Name, ast.Attribute,
    ast.And, ast.Or, ast.Not, ast.Eq, ast.NotEq, ast.Gt,
    ast.GtE, ast.Lt, ast.LtE, ast.Add, ast.Sub, ast.Mult,
    ast.Div, ast.Mod, ast.Num, ast.Constant
)

def _safe_eval(expr: str, ctx: Dict[str, Any]) -> bool:
    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED_NODES):
            raise ValueError(f"Nodo no permitido: {type(node).__name__}")
    return bool(eval(compile(tree, "<rule>", "eval"), {"__builtins__": {}}, ctx))

def load_rules() -> Dict[str, List[Dict[str, Any]]]:
    global _cached
    if _cached is not None:
        return _cached
    if not os.path.exists(_RULES_PATH):
        _cached = {"fraud": [], "review": []}
        return _cached
    with open(_RULES_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    _cached = {
        "fraud": data.get("fraud", []),
        "review": data.get("review", [])
    }
    log_event("rules_loaded", fraud=len(_cached["fraud"]), review=len(_cached["review"]))
    return _cached

def evaluate_rules(context: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    rules = load_rules()
    fraud_flags: List[str] = []
    review_flags: List[str] = []
    flat_ctx = _flatten_context(context)
    for r in rules["fraud"]:
        try:
            if _safe_eval(r["when"], flat_ctx):
                fraud_flags.append(r["id"])
        except Exception as e:
            log_event("rule_eval_error", rule=r.get("id"), error=str(e))
    for r in rules["review"]:
        try:
            if _safe_eval(r["when"], flat_ctx):
                review_flags.append(r["id"])
        except Exception as e:
            log_event("rule_eval_error", rule=r.get("id"), error=str(e))
    return fraud_flags, review_flags

def _flatten_context(ctx: Dict[str, Any], prefix: str = "", out=None):
    if out is None:
        out = {}
    for k, v in ctx.items():
        key = f"{prefix}{k}" if prefix else k
        if isinstance(v, dict):
            _flatten_context(v, key + ".", out)
        else:
            out[key] = v
    return out

def reload_rules():
    global _cached
    _cached = None
    load_rules()
    log_event("rules_reloaded")