from app.services import code_analysis as ca
from tests.conftest import register_and_login


# --- Deterministic complexity heuristics ----------------------------------
def test_nested_loops_detected_as_quadratic():
    code = """
def solve(a):
    n = len(a)
    for i in range(n):
        for j in range(n):
            if a[i] + a[j] == 0:
                return True
    return False
"""
    assert ca.max_loop_nesting(code, "python") == 2
    est = ca.estimate_complexity(code, "python")
    assert est["time"] == "O(n^2)"
    assert est["estimate"] is True


def test_single_loop_is_linear_and_sort_is_nlogn():
    linear = "def f(a):\n    for x in a:\n        print(x)\n"
    assert ca.estimate_complexity(linear, "python")["time"] == "O(n)"

    with_sort = "def f(a):\n    a.sort()\n    return a[0]\n"
    assert ca.estimate_complexity(with_sort, "python")["time"] == "O(n log n)"


def test_recursion_detected():
    rec = "def fib(n):\n    if n < 2:\n        return n\n    return fib(n-1) + fib(n-2)\n"
    assert ca.has_recursion(rec, "python") is True
    est = ca.estimate_complexity(rec, "python")
    assert "recursive" in est["time"] or est["uses_recursion"] is True


def test_brace_language_nesting():
    cpp = """
int main(){
    for(int i=0;i<n;i++){
        for(int j=0;j<n;j++){
            sum += a[i]*a[j];
        }
    }
}
"""
    assert ca.max_loop_nesting(cpp, "cpp") == 2


def test_findings_flag_tle_on_big_constraints():
    code = "for i in range(n):\n    for j in range(n):\n        pass\n"
    findings = ca.static_findings(code, "python", constraints="1 <= n <= 10^5")
    kinds = {f["type"] for f in findings}
    assert "complexity" in kinds
    tle = next(f for f in findings if f["type"] == "complexity")
    assert tle["severity"] == "high"  # big constraints → likely TLE


def test_cpp_overflow_and_io_findings():
    cpp = "int main(){ int a=1000000; int b = a * a; cout << b << endl; }"
    findings = ca.static_findings(cpp, "cpp")
    kinds = {f["type"] for f in findings}
    assert "overflow" in kinds and "io_performance" in kinds


# --- API ------------------------------------------------------------------
def test_analyze_endpoint_returns_structured_result(client):
    h = register_and_login(client)
    code = "def f(a):\n    for i in a:\n        for j in a:\n            pass\n"
    r = client.post("/code/analyze", json={
        "language": "python", "code": code, "constraints": "n up to 10^5", "verdict": "TIME_LIMIT_EXCEEDED",
    }, headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["complexity"]["time"] == "O(n^2)"
    assert any(f["type"] == "complexity" for f in body["findings"])
    assert "review" in body and "summary" in body["review"]


def test_analyze_with_question_uses_rag(client):
    h = register_and_login(client)
    r = client.post("/code/analyze", json={
        "language": "python",
        "code": "for i in range(n):\n    for j in range(n):\n        pass\n",
        "question": "why is this timing out and how do I make it faster?",
        "constraints": "n up to 10^5",
    }, headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["answer"], "a question should produce a grounded answer"
    assert body["sources"], "the answer should cite retrieved docs"
