import ast
from typing import Any, Dict, Tuple


def validate_telemetry_schema(attributes: Dict[str, Dict[str, Any]], data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate `data` against `attributes` schema.

    Expected attributes shape:
      { name: { type: 'integer'|'string', required: bool } }

    Rules:
    - Reject unknown fields
    - Reject missing required fields
    - Enforce the declared type
    """
    # Reject unknown fields
    for key in data.keys():
        if key not in attributes:
            return False, f"unknown field: {key}"

    # Check required
    for name, meta in attributes.items():
        if meta.get("required") and name not in data:
            return False, f"missing required field: {name}"

    # Type check (supporting 'integer' and 'string')
    for name, value in data.items():
        expected = attributes[name].get("type")
        if expected in ("integer", "int"):
            if not isinstance(value, int):
                return False, f"{name} expected integer"
        elif expected in ("string", "str"):
            if not isinstance(value, str):
                return False, f"{name} expected string"
        else:
            return False, f"unsupported attribute type: {expected}"

    return True, ""


ALLOWED_AST_NODES = {
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Num,
    ast.Name,
    ast.Load,
    ast.Compare,
    ast.Call,
    ast.BoolOp,
    ast.And,
    ast.Or,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Mod,
    ast.Pow,
    ast.USub,
}


def safe_eval_condition(condition: str, variables: Dict[str, Any]) -> bool:
    """Safely evaluate condition like 'temperature > 80' using telemetry variables."""
    try:
        node = ast.parse(condition, mode="eval")
    except Exception:
        raise ValueError("invalid condition expression")

    for n in ast.walk(node):
        if not isinstance(n, tuple(ALLOWED_AST_NODES)):
            raise ValueError(f"unsafe expression: {type(n).__name__}")

    compiled = compile(node, "<condition>", mode="eval")
    # Only allow the provided variables
    safe_locals = {k: v for k, v in variables.items()}
    return bool(eval(compiled, {"__builtins__": {}}, safe_locals))


from bson import ObjectId

def serialize_mongo(doc):
    if not doc:
        return doc
    if isinstance(doc, list):
        return [serialize_mongo(d) for d in doc]
    doc = dict(doc)
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            doc[k] = str(v)
    return doc