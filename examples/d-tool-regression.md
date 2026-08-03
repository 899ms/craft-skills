# Regression example — D tool

> **Regression example, not a hero identity.** It exists to test reduction and iteration behavior. It is not evidence that the concept is distinctive, publishable, or trademark-clear.

## Inspected revised fixture

<img src="../assets/examples/d-tool/d-tool-mark-mono.svg" width="220" alt="D tool mark combining a D, download arrow, and play counter">

![D tool semantic-fusion QA board](../assets/examples/d-tool/d-tool-qa-board.png)

These artifacts show the revised fixture after the failed first reduction. The QA board is an overview; the native-size PNG files below are the authoritative pixel checks.

<img src="../assets/examples/d-tool/icons/d-tool-16.png" width="16" height="16" alt="D tool at 16 px">
<img src="../assets/examples/d-tool/icons/d-tool-24.png" width="24" height="24" alt="D tool at 24 px">
<img src="../assets/examples/d-tool/icons/d-tool-32.png" width="32" height="32" alt="D tool at 32 px">
<img src="../assets/examples/d-tool/icons/d-tool-64.png" width="64" height="64" alt="D tool at 64 px">
<img src="../assets/examples/d-tool/icons/d-tool-128.png" width="128" height="128" alt="D tool at 128 px">

Editable sources: [d-tool-mark.svg](../assets/examples/d-tool/d-tool-mark.svg), [d-tool-mark-mono.svg](../assets/examples/d-tool/d-tool-mark-mono.svg), and [d-tool-qa-board.svg](../assets/examples/d-tool/d-tool-qa-board.svg).

## Regression prompt

“Recheck the D tool mark. Its `D` bowl and download arrow are intended to share one negative-space construction, but the arrow disappeared at 16 px in the previous render. Preserve the accepted direction and fix only the small-size failure.”

## Expected behavior

Lock these accepted invariants before editing:

- the outer `D` silhouette;
- one shared negative-space relationship, not a separate arrow;
- the dominant downward direction;
- the existing fill and corner system.

Then:

1. Inspect the actual 16, 24, and 32 px renders, not only the SVG source or prompt.
2. Mark the first result `revise`; do not average a failed 16 px test into a passing score.
3. Increase the arrow void’s minimum width or clearance and simplify its terminal while preserving the locked invariants.
4. Re-render all required sizes and re-run one-color, reverse, grayscale, and silhouette checks.
5. If the shared reading still fails, create a responsive micro-mark or reject the concept; do not paste in a second arrow.
6. Record similarity risk independently. A successful reduction test does not make a common `D + download` construction distinctive.

Pass condition: the core direction remains visibly intentional at 16 px, the `D` still reads at larger sizes, and both readings depend on the same void. If no revised artifact was inspected, report `QA not run` rather than `pass`.
