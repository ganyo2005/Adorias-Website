# Adorias Enterprise Website V6
Built by restoring the V4.1 design base and replacing its catalogue layer with the verified master catalogue.

Changes:
- V4.1 homepage/color/design restored.
- No customer-facing database/catalogue record counts.
- Public navigation simplified into nine beginner-friendly departments.
- Exact models are published only when verified; unresolved exact models remain withheld.
- Family/variable-stock items remain searchable without pretending to be exact SKUs.
- Detailed specifications, batteries, power and compatibility are shown when present in the master.
- Product-image slots are prepared, but exact photographs are intentionally not fabricated or mismatched. A separate verified-image pass is still required for models without approved imagery.

V6.1 corrections:
- Removed the old “72 verified catalogue records” statistic.
- Removed the “9+ leading brands” numerical claim.
- Hero now emphasizes creator gear, special orders, and Ghana-wide fulfilment.
- Fulfilment copy now states nationwide delivery and Accra store pickup.
- Expanded the brand strip using confirmed catalogue brands.
- IMPORTANT: exact product photography is not yet complete. Existing icon/fallback visuals are not being represented as product photos.

V6.2 image pass started: exact manufacturer images wired for EOS R6 Mark II, EOS R5 Mark II, and Nikon Z6 III. Other products deliberately retain fallbacks until an exact image is verified.

V6.3 image batch 2: added exact camera images for Canon EOS R, Canon EOS RP, Canon EOS R6, Canon 7D Mark II, Canon EOS 5D Mark IV. EOS R50 was researched but deliberately not wired because the available official result did not expose a stable direct image asset URL.

V6.4 Nikon image batch: direct Nikon USA assets added for Nikon D7500, Nikon D850, Nikon Z50 II.

V6.5 Nikon image batch 2: added exact-model imagery for Nikon D3500, Nikon D5600, Nikon D750. Product identity was checked against Nikon USA model pages before assignment.

V6.6 Nikon image batch 3: exact-model photos added for Nikon D3100, Nikon D3200. Nikon D90 and D3300 identities were also verified during this batch, but no stable direct image asset was embedded yet.

V6.7: added five more exact Nikon DSLR photographs: Nikon D90, Nikon D3400, Nikon D5200, Nikon D5300, Nikon D7000.

Lens image batch (2026-10-04): wired exact-model photos for 25 of the 26 remaining Lenses catalogue items (LEN-0002–0008, 0013–0026, 0028–0031). Sources were, per item: official manufacturer/distributor product pages (asia.canon, th.hkyongnuo.com) where available; otherwise an authorized retailer's product listing (thecamerastore.com, lookingglassphoto.com) showing the manufacturer-supplied studio photo; and for four older/discontinued Nikon DSLR kit lenses and two Sigma Art primes with no live retailer listing, a freely-licensed photograph from Wikimedia Commons. Every image was downloaded and visually checked against the markings on the lens barrel before being wired in — not just assumed from the search result. Each item's `imageQaStatus` in catalogue.js records which of the three source tiers was used (OFFICIAL_PRODUCT_GALLERY_LOCAL_FILES / RETAILER_PRODUCT_PHOTO_LOCAL_FILE / COMMUNITY_PHOTO_LOCAL_FILE), and `imageSource` holds the exact page the photo came from. LEN-0027 (Tamron 70–300mm) was deliberately left unresolved: the source data itself flags its exact variant/mount as ambiguous, and Tamron sells several different 70–300mm lenses, so no photo was guessed for it. REMAINING_PRODUCT_IMAGES_V6_75.csv was updated to drop the 25 resolved SKUs; LEN-0027 remains listed.

Lens-adapter follow-up (2026-10-04): the Lenses category also included four generic lens-mount-adapter items (ADP-0002–0005) that were still unwired. Since these are explicitly "Various Models" family items rather than one exact SKU, a representative official photo was sourced for each: Canon Mount Adapter EF-EOS R and EF-EOS M from asia.canon, a Sony LA-EA (A-mount to E-mount) adapter from thecamerastore.com, and a Viltrox EF-L adapter from viltrox.com. All four were visually confirmed before wiring. The Lenses category is now fully covered except LEN-0027. (ADP-0001, Camera AC Adapters / Dummy Batteries, is a power accessory, not a lens adapter, and is out of scope for this pass.)

Cross-category image sweep (2026-10-04): a brand-based review turned up 295 items across the whole catalogue still missing images, not just within Lenses. Of these, 6 were genuinely specific named products and were resolved immediately: Yongnuo YN216, YN300-series, YN600-series, YN60RGB (on-camera light), and YN900 LED video lights (all sourced from th.hkyongnuo.com), plus the Canon SELPHY CP1000 photo printer (sourced from asia.canon). All six were visually confirmed before wiring. The remaining 289 items fall into two buckets intentionally deferred for a separate pass: ~99 generic "Various"-brand category types (softboxes, tripods, cables, backdrops, printer paper, etc.) that each need one representative photo per type rather than per SKU, and ~190 "Battery for <camera model>" / "Charger for <camera model>" rows that map down to roughly 15–20 actual distinct battery/charger products shared across many camera bodies.
