from flask import Flask, render_template, request
from sympy import symbols, simplify
from sympy.parsing.sympy_parser import parse_expr
import re

app = Flask(__name__)
n = symbols('n')

def build_expression(expr):
    try:
        u0_match = re.search(r'U\(0\)\s*=\s*([\-0-9.]+)', expr)
        u1_match = re.search(r'U\(1\)\s*=\s*([\-0-9.]+)', expr)
        r_match = re.search(r'r\s*=\s*([\-0-9.]+)', expr)
        q_match = re.search(r'q\s*=\s*([\-0-9.]+)', expr)

        u0 = float(u0_match.group(1)) if u0_match else None
        u1 = float(u1_match.group(1)) if u1_match else None
        r = float(r_match.group(1)) if r_match else None
        q = float(q_match.group(1)) if q_match else None

        if u0 is not None and r is not None:
            return f"{u0} + {r}*n"
        elif u1 is not None and r is not None:
            return f"{u1 - r} + {r}*n"
        elif u0 is not None and q is not None:
            return f"{u0} * {q}**n"
        elif u1 is not None and q is not None:
            return f"{u1 / q} * {q}**n"
        else:
            return None
    except:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    result = {"delta": "", "ratio": "", "type": "", "expr": ""}
    if request.method == "POST":
        expr = request.form.get("expression", "").strip()
        built_expr = build_expression(expr)
        if built_expr:
            expr = built_expr

        result["expr"] = expr

        try:
            u = parse_expr(expr)
            delta = simplify(u.subs(n, n + 1) - u)
            ratio = simplify(u.subs(n, n + 1) / u)
            type1 = "✅ الدالة حسابية" if not delta.free_symbols else "❌ ليست حسابية"
            type2 = "✅ الدالة هندسية" if not ratio.free_symbols else "❌ ليست هندسية"
            result["delta"] = f"U(n+1) - U(n) = {delta}"
            result["ratio"] = f"U(n+1) / U(n) = {ratio}"
            result["type"] = f"{type1}<br>{type2}"
        except:
            result["delta"] = "⚠️ تحقق من الصيغة"
            result["type"] = ""
    return render_template("index.html", result=result)
