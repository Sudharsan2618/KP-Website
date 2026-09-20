# Legacy content freeze

Frozen on 2026-09-19 from the checked-in `site/` source only. The inventory generator performs no network requests.

## Verification

- Source baseline commit: `5938e76da55ba9acc06d4fd0b1908b76e664c46d`
- Language: German (`de`)
- Pages: 13 mapped pages, 0 unmapped
- Jobs: exactly 17
- Assets: 172 hashed assets
- Unique local media references: 28
- Links: 190 total, 31 external
- Unicode replacement characters: none
- Canonical route set: verified against the migration plan

## Deterministic hashes

Running `python migration-data/build_inventory.py` twice produced identical SHA-256 hashes:

- `migration-data/content.json`: `BDE5387D7507EBC11EBEC587C9C90BE4453C79F76D17CB02F69D2A5A08A44D51`
- `migration-data/manifest.json`: `0DAAD020B5ABA12075269E686D27A4A609305AB08DC988035C7487F1DA8BC4B3`

These files are frozen migration inputs. Do not edit them manually; update the generator and repeat the verification if the approved source changes.
