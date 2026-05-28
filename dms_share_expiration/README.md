# DMS Share Expiration

This module extends the OCA Document Management System (DMS) to allow creating multiple share links per file, each with its own individual expiration date and recipient tracking.

## Features

- **Multiple Share Links**: Generate as many unique share links as needed for a single file.
- **Individual Expiration**: Set specific expiration dates for each link independently.
- **Recipient Tracking**: Optionally record the recipient's email for each generated link.
- **Automatic Invalidation**: Links automatically become inaccessible once the expiration date has passed.
- **Token Management**: Unique, secure access tokens for every share link.

## Dependencies

### Odoo Modules
- **dms**: The base Document Management System module from OCA.

## Installation

1. Ensure the `dms` module from OCA is installed.
2. Install the `dms_share_expiration` module.

## Usage

### To Create a Share Link:
1. Navigate to a file within the DMS.
2. Click the **Create Share Link** button in the form view.
3. In the wizard:
    - (Optional) Set an **Expiration Date**.
    - (Optional) Provide a **Recipient Email**.
4. Click **Create Link**. The generated **Share URL** will be displayed and can be copied.

### To Manage Existing Links:
1. On the DMS file form view, click the **Share Links** stat button at the top.
2. Here you can view all active and expired links, see recipient details, or manually revoke access by deleting the link or changing its expiration date.

---
**Author**: Top-Tech
**License**: LGPL-3
**Version**: 18.0.2.0.0
