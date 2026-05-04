# Contributing

Thanks for contributing to Smart Holiday Agent.

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
pip install black isort
```

3. Run local checks before opening a PR:

```bash
make ci
```

## Before opening a PR

- [ ] `make lint` passes.
- [ ] `make test` passes.
- [ ] Changes are scoped and documented.
- [ ] UI copy changes are reflected in README/docs when relevant.

## Useful commands

- Format code: `make format`
- Lint/check style: `make lint`
- Run tests: `make test`
- Run full CI-equivalent checks: `make ci`
