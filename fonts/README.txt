If you want to bundle the 'Inter' font for a more iOS-like look:

1) Download Inter from https://rsms.me/inter/ (Open Font License).
2) Place Inter-Regular.ttf (and any weights you want) inside this folder.
3) The application will auto-register 'fonts/Inter-Regular.ttf' at startup if present.

If you prefer the system font, Windows uses 'Segoe UI' by default and will be used automatically.

Automatic fetch helper:

1) A small helper script was added at `scripts/fetch_fonts.py` to download Inter-Regular and Inter-Bold into this folder.
2) Run it with:

	python scripts/fetch_fonts.py

It requires the `requests` package. If not installed run `pip install requests` first.
