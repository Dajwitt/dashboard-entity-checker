# Documentation maintenance

The documentation is bilingual and keeps Markdown as the single source of truth.

## Structure

- `en/` — English source pages
- `de/` — German source pages
- `build_html.py` — deterministic standard-library generator
- `validate_docs.py` — bilingual structure, link, example, version, and route validation
- `site/index.html` — generated self-contained GitHub Pages site
- `site/.nojekyll` — disables Jekyll processing

The separate community-post draft is kept outside the public documentation tree under `arbeitsstand/forumsbeitrag-entwurf.md`.

## Update workflow

1. Update the matching page in both `en/` and `de/`.
2. Keep the public version markers aligned with `custom_components/dashboard_entity_checker/manifest.json`.
3. Run:

   ```bash
   python3 docs/build_html.py
   python3 docs/validate_docs.py
   ```

4. Review `docs/site/index.html` locally.
5. Commit the Markdown changes, generator, validator, and generated site together.

The Documentation workflow regenerates and validates the site. It fails when the committed HTML is stale or a generated file is untracked. Pushes to `main` deploy `docs/site/` through GitHub Pages; pull requests receive read-only permissions and never deploy.

## GitHub Pages configuration

This repository is prepared to publish through **GitHub Actions**. Before the first deployment, a repository administrator must open **Settings → Pages → Build and deployment** and set **Source** to **GitHub Actions**. The normal workflow token does not perform this one-time enablement automatically.

Public project URL after the first successful `main` deployment:

```text
https://dajwitt.github.io/dashboard-entity-checker/
```

## Release-version rule

Home Assistant and HACS already render the release name or tag as the update-dialog heading. A GitHub release body must therefore **not** start with another version heading such as `# 0.3.6`. Start directly with the user-facing introduction or a descriptive heading such as `## What's new`, then verify the real Home Assistant update dialog after publication.
