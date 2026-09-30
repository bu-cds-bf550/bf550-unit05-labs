"""Self-checks for the lab notebooks.

Every check reports; nothing here ever raises, and nothing here grades.
Three states:

  #   not attempted yet — the name the task asks for does not exist
  X   not passing yet — what came back, what was expected, and a hint
  OK  passing

Run a check cell as often as you like. It only reads your work.
"""
import inspect


def _report(mark, text):
    print(f"{mark} {text}")


def check(name, expect, args=None, hint=""):
    """Report whether `name` — a variable, or a function called with `args` —
    equals `expect`. Looks the name up in the notebook the check runs in."""
    namespace = inspect.currentframe().f_back.f_globals
    if name not in namespace:
        _report("⬜", f"{name} — not defined yet. Write it in the cell above, "
                      "run that cell, then re-run this one.")
        return
    value = namespace[name]
    label = name
    if args is None and callable(value):
        _report("❌", f"{name} is a function, but this task asks for a variable named {name} "
                      "that stores a value.")
        print(f"   Compute the value in the cell above and store it as {name} = ... ; "
              "the check reads the variable and does not call it.")
        return
    if args is not None and not callable(value):
        _report("❌", f"{name} holds the value {value!r}, but this task asks for a function "
                      f"named {name} that the check can call.")
        print(f"   Write it in the cell above with def {name}(...): and a return line.")
        return
    if args is not None:
        # a repr carrying a memory address (e.g. a generator) reads as noise —
        # show the type's name instead
        shown = ", ".join(type(a).__name__ if " at 0x" in repr(a) else repr(a)
                          for a in args)
        label = f"{name}({shown})"
        try:
            value = value(*args)
        except Exception as error:  # a check never raises — it reports
            _report("⚠️", f"{label} raised {type(error).__name__}: {error}")
            print("   Read the error top to bottom, fix the cell above, and re-run.")
            return
    try:
        comparison = (value == expect)
        if hasattr(comparison, "__len__"):   # arrays compare element by element
            passed = bool(comparison.all()) and len(value) == len(expect)
        else:
            passed = bool(comparison)
    except Exception:               # shapes that cannot even be compared
        passed = False
    if passed:
        _report("✅", f"{label} — passing")
    else:
        _report("❌", f"{label} came back with {value!r}; expected {expect!r}.")
        if hint:
            print(f"   Hint: {hint}")


# ---------------------------------------------------------------------------
# Added for the problem sets (Sep 2026). Same contract: report, never raise.

_results = []      # every check's (label, passed), in order — what a grader reads
_since_summary = 0


def ready(*names):
    """Report which of `names` are not yet defined in the notebook. True when all are."""
    global _since_summary
    namespace = inspect.currentframe().f_back.f_globals
    missing = [n for n in names if n not in namespace]
    for n in missing:
        _report("⬜", f"{n} — not defined yet. Write it in the cell above, run that cell, "
                      "then re-run this one.")
        _results.append((f"{n} defined", False))
        _since_summary += 1       # so a checks block's closing count includes it
    return not missing


def check_that(label, condition, detail=""):
    """Report whether `condition` holds. `label` is the claim in words; `detail` is what
    came back, shown only on failure."""
    global _since_summary
    passed = bool(condition)
    _results.append((label, passed))
    _since_summary += 1
    if passed:
        _report("✅", label)
    else:
        _report("❌", label)
        if detail:
            print(f"   {detail}")


def summary(label):
    """One line closing a check cell: how many of its checks passed."""
    global _since_summary
    recent = _results[-_since_summary:] if _since_summary else []
    passed = sum(1 for _, ok in recent if ok)
    mark = "✅" if passed == len(recent) and recent else "❌"
    _report(mark, f"{label}: {passed} of {len(recent)} checks passed")
    _since_summary = 0


def results():
    """Every check so far, as (label, passed) pairs."""
    return list(_results)


class checks:
    """A check cell:  with checks("Question 3"):  ...check_that(...)...

    Nothing inside raises to the notebook. A function that does not exist yet, or one whose
    body is still the stub, reports ⬜; any other exception reports ⚠️ with its message; and
    the block closes with a one-line count.
    """

    def __init__(self, label):
        self.label = label

    def __enter__(self):
        global _since_summary
        _since_summary = 0
        return self

    def __exit__(self, exc_type, exc, tb):
        global _since_summary
        if exc_type is NameError:
            name = str(exc).split("'")[1] if "'" in str(exc) else str(exc)
            _report("⬜", f"{name} — not defined yet. Write it in the cell above, run that cell, "
                          "then re-run this one.")
            _results.append((f"{self.label}: {name} defined", False)); _since_summary += 1
        elif exc_type is NotImplementedError:
            _report("⬜", f"{self.label} — not written yet: a function above still has its "
                          "`raise NotImplementedError` line. Replace it with your code.")
            _results.append((f"{self.label}: written", False)); _since_summary += 1
        elif exc_type is not None:
            _report("⚠️", f"{self.label} — your code raised {exc_type.__name__}: {exc}")
            print("   Read the message, fix the cell above, and re-run this one.")
            _results.append((f"{self.label}: ran without error", False)); _since_summary += 1
        if exc_type is None:
            summary(self.label)     # the count only means something when the checks ran
        return True   # a check cell never shows a traceback
