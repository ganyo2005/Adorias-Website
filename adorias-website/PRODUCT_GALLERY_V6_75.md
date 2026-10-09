# V6.75 — Product gallery repair and first lens image batch

## Gallery repair
- Moved the detail handlers out of the category click handler and matched the rendered card selectors.
- Deferred scripts until the detail panel exists; removed the competing broken quick-view path.
- Product cards now open photos, available specifications, compatibility, battery/power details, enquiry and WhatsApp actions.
- Thumbnails switch the main photo and show the selected view. Single-image products explicitly say one photo is available.
- Added keyboard opening, Escape, focus handling and a visible close control; repaired narrow-screen overflow.
- Included seven recently added camera models in the camera category filter.

## First lens batch
13 local official Canon images across five entries:
- EF 50mm f/1.8 STM: 5 views
- RF 50mm f/1.8: 2 views
- RF 85mm f/2 Macro: 2 views
- RF 70–200mm f/2.8L: 1 view
- RF 70–200mm f/4L: 3 views

Source pages, URLs, dimensions and hashes are in LENS_IMAGE_SOURCES_V6_75.json.
Other categories are not complete. Remaining work is listed in REMAINING_PRODUCT_IMAGES_V6_75.csv. Generation- or mount-ambiguous entries require identification before choosing photos. Existing third-party lens links outside this batch have not yet been replaced.

## Verification
Headless Chromium: all 97 camera/video detail views, hero-image decoding, expected thumbnail counts and specifications passed. Actual card click, photo switching, enquiry action, Escape and mobile five-image lens gallery passed. Desktop/mobile screenshots visually reviewed. New lens image files decode successfully and exact-product Canon gallery source mappings recorded.
