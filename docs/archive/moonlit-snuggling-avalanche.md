# Streamlit Linear Equation Solver -- Implementation Plan

## 1. Objective

Build a Streamlit-based educational tool that solves systems of linear equations via Gaussian elimination, displaying each row operation with exact fraction arithmetic and short explanatory text so students understand why each step is performed.

## 2. Scope

- Hand-written Gaussian elimination with `fractions.Fraction` (no numpy for core algorithm)
- User-selectable square system size (2-6 variables, always n equations in n unknowns)
- Inputs limited to rational numbers (integers, fractions, terminating decimals); irrational symbolic constants (sqrt, pi, e) are out of scope for the first pass
- Manual coefficient entry and randomized system generation
- Three system types: unique solution, inconsistent (no solution), dependent (infinite solutions)
- Three detail levels: final answer only, matrix steps only, steps with explanations
- Progressive reveal via "Next Step" button -- students advance through elimination one operation at a time rather than seeing all steps at once
- Custom mix of text and visual output: LaTeX-rendered matrices alongside short educational text
- Dynamic layout that scales with the number of variables (coefficient grid adapts columns/spacing)
- Both forward elimination and back-substitution steps are shown (when detail level includes steps)

## 3. Non-goals

- Other solution methods (Cramer's rule, matrix inverse, LU decomposition)
- Irrational or symbolic inputs (sqrt(2), pi); sympy-based symbolic engine
- Full parametric solution display for dependent systems (v1 identifies free variables but does not write the parametric form)
- File export, save/load, persistence
- Multi-page app or deployment configuration
- Fully verbose paragraph-level explanations per step
- Non-square systems (m equations in n unknowns where m != n)

## 4. Current State

Fresh starter-template repo. No application code exists. Contains only repo scaffolding: style guides, license files, test infrastructure, and `source_me.sh`.

## 5. Architecture Boundaries and Ownership

| Component | File | Responsibility | Owner |
|-----------|------|----------------|-------|
| solver module | `gauss_solver.py` | Gaussian elimination, step recording, LaTeX generation, random system creation | coder |
| app module | `linear_solver.py` | Streamlit UI, layout, user input, step display | coder |
| test suite | `tests/test_gauss_solver.py` | Unit tests for solver correctness | tester |
| documentation | `README.md`, `docs/CHANGELOG.md`, `pip_requirements.txt` | Docs and dependency manifest | planner |

**Boundary rule:** `gauss_solver.py` must not import Streamlit. `linear_solver.py` must not contain math logic beyond calling the solver.

## 6. Mapping: Milestones and Workstreams to Components and Patches

| Milestone | Workstream | Component | Patches |
|-----------|------------|-----------|---------|
| M1 | WS-A: Solver core | solver module | Patch 1, Patch 2 |
| M1 | WS-B: Random generation | solver module | Patch 3 |
| M2 | WS-C: Streamlit UI | app module | Patch 4, Patch 5 |
| M2 | WS-D: Tests | test suite | Patch 6 |
| M3 | WS-E: Docs and polish | documentation, app module | Patch 7 |

## 7. Milestone Plan

### Milestone M1: Solver Foundation

**Depends on:** none
**Entry criteria:** repo cloned, `source_me.sh` works, `streamlit` in pip_requirements.txt
**Deliverables:** Working `gauss_solver.py` with elimination, step capture, LaTeX output, and random generation
**Exit criteria:** All unit tests in `tests/test_gauss_solver.py` pass; solver handles unique, inconsistent, and dependent systems correctly; preserves exact rational arithmetic throughout all steps

### Milestone M2: Streamlit Application

**Depends on:** M1 (solver module must exist and pass tests)
**Entry criteria:** M1 exit criteria met
**Deliverables:** Working `linear_solver.py` that loads in browser, accepts input, calls solver, renders steps
**Exit criteria:** App launches with `streamlit run linear_solver.py`; manual walkthrough of all three system types succeeds; all three detail levels render correctly

### Milestone M3: Documentation and Polish

**Depends on:** M2 (app must be functional)
**Entry criteria:** M2 exit criteria met
**Deliverables:** Updated README, CHANGELOG, pip_requirements.txt; pyflakes passes
**Exit criteria:** `pytest tests/test_pyflakes_code_lint.py` passes; README documents how to run the app

## 8. Workstream Breakdown

### WS-A: Solver Core
- **Goal:** Implement Gaussian elimination with partial pivoting using `fractions.Fraction`, recording each step with operation string and educational explanation
- **Owner:** coder
- **Work packages:** WP-1, WP-2
- **Interfaces:** Provides `solve_system()` returning list of step dicts; provides `matrix_to_latex()`
- **Expected patches:** 2 (elimination engine, LaTeX renderer)

### WS-B: Random Generation
- **Goal:** Generate random augmented matrices for unique, inconsistent, and dependent systems
- **Owner:** coder
- **Work packages:** WP-3
- **Interfaces:** Provides `generate_random_system(n, system_type)`
- **Expected patches:** 1

### WS-C: Streamlit UI
- **Goal:** Build the app layout: sidebar controls, coefficient input grid, solve button, step display
- **Owner:** coder
- **Work packages:** WP-4, WP-5
- **Interfaces:** Needs solver module functions; provides runnable Streamlit app
- **Expected patches:** 2 (input/controls, step display)

### WS-D: Tests
- **Goal:** Unit tests for solver correctness across all system types
- **Owner:** tester
- **Work packages:** WP-6
- **Interfaces:** Needs solver module
- **Expected patches:** 1

### WS-E: Docs and Polish
- **Goal:** README, CHANGELOG, dependency manifest, pyflakes compliance
- **Owner:** planner
- **Work packages:** WP-7
- **Interfaces:** Needs final app code
- **Expected patches:** 1

## 9. Work Package Specs

### WP-1: Implement Gaussian elimination with step recording
- **Owner:** coder
- **Touch points:** `gauss_solver.py`
- **Acceptance criteria:**
  - Forward elimination with partial pivoting using `fractions.Fraction`
  - Back substitution with step recording
  - Returns a result dict:
    ```python
    {
      "outcome": str,          # "unique", "inconsistent", or "dependent"
      "steps": list[dict],     # each: {"operation": str, "explanation": str, "matrix": list[list[Fraction]]}
      "solution": dict | None, # {"x": Fraction(2,1), "y": Fraction(1,1)} or None
      "free_variables": list,  # e.g. ["z"] for dependent systems
      "message": str,          # human-readable outcome summary
    }
    ```
  - Steps include both forward elimination and back-substitution operations
  - Detects three outcomes: unique (full-rank), inconsistent (contradictory row like 0=5), dependent (zero row, identifies free variables)
  - For dependent systems, message names the free variable(s): "The system has infinitely many solutions. x3 is a free variable."
  - Explanation strings follow pattern: "[Action] to [purpose]" (e.g. "Eliminate x2 from row 3 using the pivot in row 2")
  - Preserves exact rational arithmetic throughout; no float conversion at any step
- **Verification commands:**
  ```
  source source_me.sh && python -c "import gauss_solver; print('import OK')"
  ```
- **Dependencies:** none

### WP-2: Implement LaTeX rendering functions
- **Owner:** coder
- **Touch points:** `gauss_solver.py`
- **Acceptance criteria:**
  - `matrix_to_latex(matrix, var_names)` renders augmented matrix with fraction display
  - `operation_to_latex(op_str)` renders row operation notation
  - Variable names: x, y, z for n<=3; x1..xN for n>3
- **Verification commands:**
  ```
  source source_me.sh && python -c "import gauss_solver; print(gauss_solver.matrix_to_latex([[1,2,3],[4,5,6]], ['x','y']))"
  ```
- **Dependencies:** WP-1

### WP-3: Implement random system generation
- **Owner:** coder
- **Touch points:** `gauss_solver.py`
- **Acceptance criteria:**
  - `generate_random_system(n, system_type)` with system_type in ("unique", "inconsistent", "dependent", "mixed")
  - Random rational coefficients with small denominators (e.g. Fraction(3,4), Fraction(-2,3)); denominators limited to 1-4 for readability
  - For square systems, unique systems are generated with full-rank coefficient matrices
  - Inconsistent systems contain a contradictory row
  - Dependent systems contain a linearly dependent row
  - "mixed" picks a random type
- **Verification commands:**
  ```
  source source_me.sh && python -c "import gauss_solver; m = gauss_solver.generate_random_system(3, 'unique'); print(m)"
  ```
- **Dependencies:** WP-1

### WP-4: Build Streamlit input and controls
- **Owner:** coder
- **Touch points:** `linear_solver.py`
- **Acceptance criteria:**
  - Sidebar: slider for variable count (2-6), detail level selector, system type selector, randomize button
  - Main area: dynamic coefficient input grid using `st.number_input` in columns; grid scales with variable count (columns adapt spacing for 2-6 variables)
  - Session state persists coefficient matrix across reruns
  - Randomize button populates inputs via session state
  - Input validation: rational numbers only; show clear message if irrational constants entered
  - Caption near inputs: "This version supports rational numbers: integers and decimals"
- **Verification commands:**
  ```
  source source_me.sh && python -m streamlit run linear_solver.py --server.headless true
  ```
- **Dependencies:** WP-1 (needs solver import for type definitions)

### WP-5: Build step-by-step display
- **Owner:** coder
- **Touch points:** `linear_solver.py`
- **Acceptance criteria:**
  - "Solve" button computes all steps and stores in session state
  - "Next Step" button reveals one step at a time (progressive reveal); "Show All" button reveals remaining steps
  - Step counter displayed: "Step 3 of 8"
  - Each step in a bordered container with LaTeX matrix and row operation
  - Detail level "final answer only" shows only solution (no Next Step button)
  - Detail level "matrix steps" shows operations and matrices via progressive reveal
  - Detail level "steps + explanations" adds educational text alongside each matrix
  - Unique solution: `st.success()` with variable values
  - Inconsistent: `st.error()` with explanation of why no solution exists
  - Dependent: `st.warning()` with explanation of infinite solutions
- **Verification commands:**
  ```
  source source_me.sh && python -m streamlit run linear_solver.py --server.headless true
  ```
- **Dependencies:** WP-2, WP-4

### WP-6: Write unit tests for solver
- **Owner:** tester
- **Touch points:** `tests/test_gauss_solver.py`
- **Acceptance criteria:**
  - Test unique 2x2 and 3x3 systems with known solutions
  - Test inconsistent system detection
  - Test dependent system detection
  - Test that step count > 0 for non-trivial systems
  - Test fraction output (no float artifacts)
  - Test random generation produces valid matrices for each type
- **Verification commands:**
  ```
  source source_me.sh && python -m pytest tests/test_gauss_solver.py -v
  ```
- **Dependencies:** WP-1, WP-2, WP-3

### WP-7: Update documentation and dependencies
- **Owner:** planner
- **Touch points:** `README.md`, `docs/CHANGELOG.md`, `pip_requirements.txt`
- **Acceptance criteria:**
  - `pip_requirements.txt` lists `streamlit`
  - `README.md` updated with project description and run command
  - `docs/CHANGELOG.md` updated with additions entry
  - `pytest tests/test_pyflakes_code_lint.py` passes for all new files
- **Verification commands:**
  ```
  source source_me.sh && python -m pytest tests/test_pyflakes_code_lint.py
  ```
- **Dependencies:** WP-5

## 10. Patch Plan and Reporting

- Patch 1: solver module -- Gaussian elimination engine with fraction arithmetic and step recording
- Patch 2: solver module -- LaTeX rendering functions for matrices and operations
- Patch 3: solver module -- random system generation for unique, inconsistent, and dependent types
- Patch 4: app module -- Streamlit input controls, sidebar, coefficient grid, session state
- Patch 5: app module -- step-by-step display with detail levels and outcome-specific messaging
- Patch 6: tests -- unit tests for solver correctness across all system types
- Patch 7: docs -- README, CHANGELOG, pip_requirements.txt updates

## 11. Acceptance Criteria and Gates

**Unit gate:** `pytest tests/test_gauss_solver.py` -- all tests pass
**Integration gate:** App launches, randomize + solve produces correct LaTeX output for all three system types
**Regression gate:** `pytest tests/test_pyflakes_code_lint.py` -- no lint errors in new files
**Release gate:** Manual walkthrough: select each system size (2, 3, 4), each system type, each detail level; verify output is educational and correct

## 12. Test Strategy

| Level | What | Command |
|-------|------|---------|
| Unit | Solver correctness, fraction arithmetic, system type detection | `pytest tests/test_gauss_solver.py -v` |
| Lint | Pyflakes on all new files | `pytest tests/test_pyflakes_code_lint.py` |
| Smoke | App loads without error | `streamlit run linear_solver.py --server.headless true` |
| Manual | Full walkthrough of all system types and detail levels | Browser test |

## 13. Migration and Compatibility

Not applicable. Greenfield project, no existing code to migrate. No backward compatibility concerns.

## 14. Risk Register

| Risk | Impact | Trigger | Owner | Mitigation |
|------|--------|---------|-------|------------|
| Fraction display ugly in LaTeX | Medium | Large denominators from pivoting | coder | Use partial pivoting to minimize fraction growth; simplify fractions at each step |
| Singular matrix not detected | High | Edge case in elimination | tester | Explicit tests for zero-pivot detection and row-of-zeros detection |
| Streamlit reruns reset input | Medium | Session state mismanagement | coder | Initialize all state with `setdefault` at top of app; test rerun behavior |
| Random inconsistent/dependent generation unreliable | Medium | Degenerate random coefficients | coder | Construct by design (linear combination of rows), not by random retry |

## 15. Rollout and Release Checklist

1. All unit tests pass
2. Pyflakes passes on all new files
3. App launches and manual walkthrough succeeds
4. README has run instructions
5. CHANGELOG updated
6. Commit with descriptive message

## 16. Documentation Close-out

- `README.md`: project description, quick start, link to docs/CHANGELOG.md
- `docs/CHANGELOG.md`: entry under current date with Additions section
- `pip_requirements.txt`: `streamlit` added

## 17. Open Questions

None. Requirements are clear from user discussion.
