# V6.49 — Efia 501/501 Knowledge Gap Fix

The V6.48 strict audit found 29 records missing one or more core Efia fields:
- 10 lenses
- 19 lighting products

This pass fills those structural knowledge gaps conservatively.

Rules preserved:
- Exact lens mount/edition is not invented where the catalogue name is ambiguous.
- Sony/Sigma/Yongnuo family records explicitly require exact variant confirmation.
- Lighting records with unresolved generation/identity retain explicit verification warnings.
- Official manufacturer sources are attached only where a defensible product/family identity was available.
- No image-completion claim is made.

Post-fix strict audit: 501/501 records contain description, specs/key specifications, compatibility, use cases and catalogueKnowledgeStatus.
