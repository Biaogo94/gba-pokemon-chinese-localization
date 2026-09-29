# Localization engine regression tests

The copied `tools/i18n` modules are the reference implementation used by the Heart & Soul source audit. Run from this repository root with:

```bash
python -m unittest discover -s scripts/tools/i18n -p 'test_*.py'
```

The standalone scripts under `scripts/` remain convenient entry points, while the packaged modules preserve the full corpus, conditional-branch, injector guard, and punctuation tests.
