#!/usr/bin/env python3
"""Tkinter GUI: Convert PDF pages to PNG with page range support.

Requirements covered:
- PDF picker, output folder picker, page range input, DPI input, convert button
- Status/progress text area
- Page ranges: all, single pages, ranges, combinations
- Range validation against total page count
- Output naming: <pdfname>_page_0001.png
- Uses PyMuPDF (fitz), no Poppler required
"""

from __future__ import annotations

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from typing import List

import fitz  # PyMuPDF


class PDFToPNGApp:
    """Main GUI app for PDF to PNG conversion."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PDF to PNG Converter")
        self.root.geometry("760x460")

        self.pdf_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.page_range = tk.StringVar(value="all")
        self.dpi = tk.StringVar(value="200")

        self._build_ui()

    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 6}

        # PDF file picker
        ttk.Label(self.root, text="PDF file:").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(self.root, textvariable=self.pdf_path, width=70).grid(
            row=0, column=1, sticky="ew", **pad
        )
        ttk.Button(self.root, text="Browse...", command=self.pick_pdf).grid(
            row=0, column=2, sticky="ew", **pad
        )

        # Output folder picker
        ttk.Label(self.root, text="Output folder:").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(self.root, textvariable=self.output_dir, width=70).grid(
            row=1, column=1, sticky="ew", **pad
        )
        ttk.Button(self.root, text="Browse...", command=self.pick_output_dir).grid(
            row=1, column=2, sticky="ew", **pad
        )

        # Page range and DPI
        ttk.Label(self.root, text="Page range:").grid(row=2, column=0, sticky="w", **pad)
        ttk.Entry(self.root, textvariable=self.page_range).grid(
            row=2, column=1, sticky="ew", **pad
        )

        ttk.Label(self.root, text="DPI:").grid(row=3, column=0, sticky="w", **pad)
        ttk.Entry(self.root, textvariable=self.dpi).grid(row=3, column=1, sticky="w", **pad)

        # Convert button
        self.convert_btn = ttk.Button(self.root, text="Convert", command=self.start_convert)
        self.convert_btn.grid(row=4, column=1, sticky="w", **pad)

        # Status/progress text
        ttk.Label(self.root, text="Status / Progress:").grid(
            row=5, column=0, sticky="nw", padx=10, pady=(10, 4)
        )
        self.status = ScrolledText(self.root, height=14, wrap="word")
        self.status.grid(row=5, column=1, columnspan=2, sticky="nsew", padx=10, pady=(10, 10))
        self.status.configure(state="disabled")

        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(5, weight=1)

    def log(self, text: str) -> None:
        """Append a log line to the status text box."""
        self.status.configure(state="normal")
        self.status.insert("end", text + "\n")
        self.status.see("end")
        self.status.configure(state="disabled")

    def pick_pdf(self) -> None:
        """Select a PDF file and auto-fill output directory if empty."""
        path = filedialog.askopenfilename(
            title="Select PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if path:
            self.pdf_path.set(path)
            if not self.output_dir.get().strip():
                self.output_dir.set(os.path.dirname(path))

    def pick_output_dir(self) -> None:
        """Select an output directory."""
        path = filedialog.askdirectory(title="Select output folder")
        if path:
            self.output_dir.set(path)

    @staticmethod
    def parse_page_range(page_range: str, total_pages: int) -> List[int]:
        """Parse user-provided page range and return 1-based page numbers.

        Supports:
        - "all"
        - "3"
        - "1-5"
        - "1-3,5,8-10"
        """
        if total_pages < 1:
            raise ValueError("The selected PDF has no pages to convert.")

        raw = page_range.strip().lower()
        if raw in ("", "all"):
            return list(range(1, total_pages + 1))

        if ",," in raw or raw.startswith(",") or raw.endswith(","):
            raise ValueError(
                "Invalid page range: empty segment detected. Use values like '1-3,5'."
            )

        pages = set()
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        if not parts:
            raise ValueError("Page range is empty. Use 'all' or values like '1-3,5'.")

        for part in parts:
            if "-" in part:
                bounds = [x.strip() for x in part.split("-")]
                if len(bounds) != 2 or not bounds[0].isdigit() or not bounds[1].isdigit():
                    raise ValueError(f"Invalid range segment '{part}'. Use format like '2-5'.")

                start, end = int(bounds[0]), int(bounds[1])
                if start > end:
                    raise ValueError(f"Invalid range '{part}': start page is greater than end page.")

                if start < 1 or end > total_pages:
                    raise ValueError(
                        f"Range '{part}' is out of bounds. PDF has pages 1 to {total_pages}."
                    )
                for p in range(start, end + 1):
                    pages.add(p)
            else:
                if not part.isdigit():
                    raise ValueError(f"Invalid page '{part}'. Use a number like '3'.")

                page = int(part)
                if page < 1 or page > total_pages:
                    raise ValueError(
                        f"Page '{part}' is out of bounds. PDF has pages 1 to {total_pages}."
                    )
                pages.add(page)

        return sorted(pages)

    def start_convert(self) -> None:
        """Validate basic fields and start conversion in a background thread."""
        pdf_path = self.pdf_path.get().strip()
        output_dir = self.output_dir.get().strip()

        if not pdf_path:
            messagebox.showerror("Missing PDF", "Please select a PDF file.")
            return

        if not os.path.isfile(pdf_path):
            messagebox.showerror("Invalid PDF", "Selected PDF file does not exist.")
            return

        if not output_dir:
            messagebox.showerror("Missing Output Folder", "Please select an output folder.")
            return

        if not os.path.isdir(output_dir):
            messagebox.showerror("Invalid Output Folder", "Selected output folder does not exist.")
            return

        try:
            dpi = int(self.dpi.get().strip())
            if dpi <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid DPI", "DPI must be a positive integer (e.g., 200).")
            return

        self.convert_btn.config(state="disabled")
        self.log("Starting conversion...")

        worker = threading.Thread(
            target=self.convert_pdf,
            args=(pdf_path, output_dir, self.page_range.get(), dpi),
            daemon=True,
        )
        worker.start()

    def convert_pdf(self, pdf_path: str, output_dir: str, page_range: str, dpi: int) -> None:
        """Convert selected PDF pages to PNG files."""
        try:
            with fitz.open(pdf_path) as doc:
                total_pages = doc.page_count
                pages_to_convert = self.parse_page_range(page_range, total_pages)

                self.root.after(
                    0,
                    lambda: self.log(
                        f"Loaded PDF ({total_pages} pages). Converting {len(pages_to_convert)} page(s)..."
                    ),
                )

                zoom = dpi / 72.0
                matrix = fitz.Matrix(zoom, zoom)
                base_name = os.path.splitext(os.path.basename(pdf_path))[0]

                for idx, page_number in enumerate(pages_to_convert, start=1):
                    page = doc.load_page(page_number - 1)  # PyMuPDF uses 0-based indexing
                    pix = page.get_pixmap(matrix=matrix, alpha=False)

                    filename = f"{base_name}_page_{page_number:04d}.png"
                    output_path = os.path.join(output_dir, filename)
                    pix.save(output_path)

                    self.root.after(
                        0,
                        lambda i=idx, total=len(pages_to_convert), name=filename: self.log(
                            f"[{i}/{total}] Saved {name}"
                        ),
                    )

            self.root.after(0, lambda: self.log("Done. Conversion completed successfully."))
            self.root.after(
                0,
                lambda: messagebox.showinfo("Success", "PDF to PNG conversion completed successfully."),
            )

        except Exception as exc:  # Keep user-facing errors clear
            self.root.after(0, lambda: self.log(f"Error: {exc}"))
            self.root.after(0, lambda: messagebox.showerror("Conversion Failed", str(exc)))

        finally:
            self.root.after(0, lambda: self.convert_btn.config(state="normal"))


def main() -> None:
    root = tk.Tk()
    app = PDFToPNGApp(root)
    app.log("Ready. Select a PDF and output folder, then click Convert.")
    root.mainloop()


if __name__ == "__main__":
    main()
