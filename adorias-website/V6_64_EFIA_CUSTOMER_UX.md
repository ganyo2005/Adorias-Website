# V6.64 — Efia Customer-Facing Answers + Chat Launcher Fix

- launcher hides while chat open: PASS
- sports customer route: PASS
- pros included: PASS
- consider/con included: PASS
- essentials included: PASS
- optional included: PASS
- camera-only sports pool: PASS
- internal filtered phrase removed: PASS
- internal evidence phrase removed: PASS

## Customer experience change
For use-case questions such as “I need a camera for sport,” Efia now answers in the format customers actually need:
a short list of camera options, concise Pros, a practical Consider/limitation, then Essentials and Optional accessories.

Internal implementation language such as “I filtered the catalogue” and “closest evidence-backed catalogue match”
has been removed from customer-facing paths.

## Sports logic
Sports intent is locked to actual Camera / Video Camera records. Efia scores only characteristics present in catalogue
knowledge and does not invent frame rates, autofocus performance, prices or lens compatibility when those facts are absent.

## Floating Efia
The persistent Ask Efia launcher and its hint now hide while the Efia conversation is open, preventing the launcher
from covering long messages or the typing area. It returns when the chat is closed.
