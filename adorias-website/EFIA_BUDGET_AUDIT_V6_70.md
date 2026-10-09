# V6.70 — Efia Budget Intelligence Audit

## Pricing basis
- Budget currency: Ghana cedi (GHS).
- FX reference used in code: **USD 1 = GHS 11.55**, Bank of Ghana daily interbank mid-rate for 18 Sep 2026.
- Manufacturer reference prices are external benchmarks, **not Adorias selling prices**.
- Planning estimates apply a **10–30% allowance above direct USD→GHS conversion** to account for landed/local-market variation.
- The allowance is deliberately a planning heuristic, not a claim about Ghana retail price, tax, duty, freight, margin or Adorias price.

## Current benchmark anchors
- Canon EOS R50 — USD 679.99 Canon US reference.
- Canon EOS R6 Mark II — USD 1,999 Canon US current sale reference.
- Nikon Z50 II — USD 1,009.95 current Nikon US starting price.
- Nikon Z5 II — USD 1,599.95 current Nikon US starting price.
- Nikon Z6 II — USD 1,399.95 current Nikon US starting price.
- Nikon Z6 III — USD 1,999.95 current Nikon US starting price.
- Panasonic Lumix GH7 — USD 1,899.99 current Panasonic US sale price.

## Runtime budget testing
- **100 budget questions**: 10 use cases × 10 GHS budget levels.
- Budget levels: GHS 2,500; 5,000; 7,500; 10,000; 15,000; 20,000; 25,000; 30,000; 40,000; 60,000.
- Use cases include weddings, sports, wildlife, portraits, YouTube, events, church photography, graduations, family and action.
- Result: **100/100 PASS**.
- `node --check app.js`: **PASS**.

## Guardrails
Efia must say these are external-market planning estimates. It must not present them as Adorias prices. Products without a reliable benchmark remain price-unknown rather than receiving an invented price.
