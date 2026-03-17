# PDF to PNG GUI (Tkinter)

A simple standalone Python GUI app to convert PDF pages into PNG images with selectable page ranges.

## Features

- Pick a PDF file
- Pick an output folder
- Choose page ranges:
  - `all` (default)
  - Single page: `3`
  - Range: `1-5`
  - Combination: `1-3,5,8-10`
- Set output DPI (default `200`)
- Live status/progress log
- Output naming format:
  - `<pdfname>_page_0001.png`

## Requirements (for source/developer use)

- Python 3.9+
- Tkinter (usually included with standard Python installs; on some Linux distros install `python3-tk`)
- [PyMuPDF](https://pymupdf.readthedocs.io/) (no Poppler dependency)

## End-user usage (Windows EXE)

If Jacob shares the built EXE with you:

1. Download `pdf-to-png-gui.exe`.
2. Double-click it to run.
3. Pick your PDF, output folder, page range, and click **Convert**.

No Python installation is required for end users.

## Build the Windows EXE (Jacob workflow)

On Windows, from this project folder, run:

```bat
build-windows.bat
```

This script will:

1. Create `.venv` if missing
2. Install Python dependencies
3. Install `pyinstaller`
4. Build a single-file, windowed EXE from `app.py`

## Run from source on Windows

For local source execution on Windows:

```bat
run-windows.bat
```

This sets up `.venv` (if needed), installs dependencies, and launches `app.py`.

## Output location

After a successful build, the EXE is located at:

- `dist\pdf-to-png-gui.exe`

## SmartScreen and first-run notes

Windows may show a **Microsoft Defender SmartScreen** warning for newly built unsigned EXEs.

- Click **More info**
- Click **Run anyway**

The first launch can also be slightly slower while Windows performs initial checks.

## Create a release

To build and publish a new Windows EXE via GitHub Actions:

```bash
git tag vX.Y.Z && git push origin vX.Y.Z
```

After the workflow completes, download `pdf-to-png-gui.exe` from the repo’s **Releases** page.

## Notes

- If page range is invalid or out of bounds, the app shows a clear error.
- Page numbers are 1-based in the UI (e.g., first page is `1`).
