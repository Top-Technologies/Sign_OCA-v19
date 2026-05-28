# DMS PDF Tools

This module extends the OCA Document Management System (DMS) with PDF manipulation utilities.

## Features

### 1. Split PDF
- **Select Specific Pages**: Extract only the pages you need from a large PDF document.
- **Split into Multiple Files**: Create new DMS files from specified page ranges.
- **Automatic Naming**: New files are automatically named based on the original file and page ranges.

### 2. Merge PDFs
- **Combine Multiple Files**: Select two or more PDF files in the DMS and merge them into a single PDF.
- **Order Preservation**: Maintains the order of selected files in the final document.
- **Direct Integration**: Merged files are saved directly into the same DMS directory.

## Dependencies

### Odoo Modules
- **dms**: The base Document Management System module from OCA.

### Python Libraries
- **pypdf**: Used for all PDF processing logic.
  ```bash
  pip install pypdf
  ```

## Installation

1. Ensure the `pypdf` library and dms module from OCA are installed.
2. Install the `dms_pdf_tools` module.
3. The PDF tools will appear as actions in the DMS file views.

## Usage

### To Split a PDF:
1. Navigate to your DMS file and select it (Go into the form view).
2. Find and press the "Split PDF" button on the top left of the form view.
3. Specify specific page or page ranges (e.g., `1, 3-5, 10`).
4. Click **Split** to generate new documents.

### To Merge PDFs:
1. Select multiple PDF files from the DMS list view.
2. Select **Merge PDFs** from the **Actions** menu.
3. Provide a name for the new combined file and click **Merge**.

---
**Author**: Top-Tech
**License**: LGPL-3
**Version**: 18.0.1.0.0
