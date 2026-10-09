# V6.59 — Camera/Video Provenance + Gallery File QA

## Manufacturer provenance
Direct manufacturer sources attached for the newly added/corrected records:
Sony ZV-E10, Sony ZV-E10 II (ZV-E10M2), Nikon D800, Panasonic LUMIX GH7 (DC-GH7), Canon XA70, Canon XA75, Sony HDR-XR550 and Sony HDR-XR520V.

## Catalogue naming correction
The corrected XR550 record is standardized to Sony's official full model designation **HDR-XR550**.

## Local card/gallery asset QA
- Camera/video products: **97**
- Products with no image reference: **0**
- Broken local image references: **0**
- Invalid/corrupt image files: **0**
- Remote image references in camera/video galleries: **0**
- Identical image hashes reused across different SKUs: **6**

## Gallery code checks
- uses_images_array: PASS
- thumbnail_support: PASS
- detail_open_handler: PASS
- image_error_fallback: PASS

## Important QA boundary
This pass verifies local file existence, decodability, duplicate-file reuse and static gallery wiring. It does **not** relabel the images `LOCAL_RENDER_VERIFIED`: actual browser rendering and a semantic visual check that every photograph depicts the exact intended model still require a rendered-browser inspection. This report intentionally does not fake that step.
