# V6.60 — Efia Guided Diagnosis Engine

## Implemented

Efia now supports progressive beginner/expert diagnosis. It extracts intended use, experience level, budget,
brand/category, hard requirements, preferences, exclusions, existing equipment, environment and workflow.
It asks one high-value follow-up question at a time, then filters the live Adorias catalogue and explains up
to three matching products. Hard requirements are enforced rather than silently ignored. If no product satisfies
all hard requirements, Efia says so instead of inventing a match.

The diagnosis layer sits above the existing catalogue search and uses `window.ADORIAS_CATALOGUE`, so suggestions
come from Adorias inventory records rather than an invented product list.

## Static checks
- diagnosis_engine: PASS
- generic_intent_router: PASS
- requirement_extraction: PASS
- hard_constraints: PASS
- soft_constraints: PASS
- owned_equipment: PASS
- progressive_questions: PASS
- catalogue_filtering: PASS
- candidate_explanations: PASS
- cross_category_offer: PASS
- no_match_guard: PASS

## Example conversations
**Beginner:** “I need a camera for church livestreaming.”  
Efia begins a guided intake instead of assuming the user understands camera terminology.

**Specific:** “I need a Sony APS-C E-mount camera for YouTube and I already own batteries.”  
Efia extracts the supplied constraints and avoids re-asking information it already has.

**Hard requirement:** “I need a camcorder with XLR and SDI.”  
Products lacking the stated hard requirements are filtered out; if none match, Efia reports that rather than substituting a near match.

## Safety/quality boundary
Budget is captured as a diagnostic constraint, but catalogue records currently do not contain reliable public selling prices,
so V6.60 does not pretend to price-filter products. Compatibility explanations are limited to information present in the catalogue.
