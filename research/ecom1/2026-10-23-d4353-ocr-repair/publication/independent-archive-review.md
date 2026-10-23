# Final archive verification

**PASS.** `complete.tar.gz` is1,187,491bytes with495 regular-file members, SHA256 `e19207c4e4373c516f5e470c7ad3b1a0dd159924e6abc66da3cafc4be8600ebd`.

I extracted it into a clean temporary directory, checked safe relative paths, unique deterministic path-component ordering, normalized metadata, all494 bundle-manifest entries, the440-entry record-audit seal, and every source/report pin from the prior independent build verification. Every archived file equals the corresponding reviewed working-tree file. Candidate SHA256 remains `420e904a4cb502221f8609f99bd0f62370deda775abb41b5be9880042f0b7bf8`; its exact parent equals the separately audited d4353 source SHA256 `588b654758ea1ee07935feeb65b430fb3b7a6ca40c4bd712b9de0517de6d3a2e`.

The included `package_bundle.py` recreates the identical archive bytes under Python3.12.7 and3.14.3. Its gzip OS-byte normalization is explicit; payload metadata and member bytes are unchanged. Repacking modified no sealed input. The source and fixtures exactly match the clean-directory reproduction of300 parser and112 whole-agent checks, so those tests were not repeated for packaging. Later additions are reviewed documentation, the complementary independent review, and packaging materials. The README now explicitly excludes the separate d4702 t016 case; this is a limitation statement, not new validated recovery coverage.

`verify_archive.py` reproduces these packaging checks without running agent tests or modifying sealed working-tree members. Its result is `independent-archive-verification.json`. These three final verification files are in excluded `publication/` and do not alter the archive pin. No paid call, submission, promotion or full100 improvement claim follows from archive integrity.
