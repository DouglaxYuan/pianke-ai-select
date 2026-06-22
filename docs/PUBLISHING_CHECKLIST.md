# Publishing Checklist

Use this checklist before publishing the public `pianke-ai-select` repository.

## Attribution

- Keep original upstream link: `https://github.com/zhaoyue4810/pianke`
- Keep original author attribution.
- Keep the full `LICENSE` file unchanged.
- Keep the Pianke brand attribution visible.
- Include `FORK_NOTICE.md` in the repository root.

## License

- Use the upstream Pianke Software License Agreement v2.
- Do not replace it with MIT or another permissive license.
- Do not describe the project as unrestricted open source.
- Describe it as source-available under the Pianke license if needed.

## Repository Hygiene

- Remove `.venv/`.
- Remove `models/`.
- Remove `workspace/`.
- Remove logs and pid files.
- Remove private photos and generated sessions.
- Remove local-only absolute path notes unless intentionally documented.

## Suggested Commit Before Public Push

```bash
git status --short
git add FORK_NOTICE.md docs/LOCAL_MODIFICATIONS.md docs/PUBLISHING_CHECKLIST.md SECURITY.md CHANGELOG.md
git commit -m "docs: document fork attribution and publishing checklist"
```

## Suggested Public Description

```text
Local fork of zhaoyue4810/pianke with large-project resume and UI workflow improvements. Licensed under the original Pianke Software License Agreement v2.
```
