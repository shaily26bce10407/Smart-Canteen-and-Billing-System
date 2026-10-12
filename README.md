# Smart Canteen Billing System

A lightweight, beginner-friendly Point of Sale (POS) and inventory management CLI tool built using Python's standard library. It handles interactive ordering, inventory tracking, multi-channel payment processing (including a simulated prepaid smart card), automated receipts, and administrative analytics.

---

## Features

- **Live Inventory & Menu Management**:
  - Displays menu items, live prices, and available units.
  - Automatic low-stock warnings (`(low!)` indicator) and sold-out flags.
- **Cart & Order Processing**:
  - Add or remove items dynamically.
  - Automatic quantity validation against real-time stock limits.
  - Bulk discount engine (10% off for orders over Rs. 300).
  - GST computation (5% tax added to net post-discount amount).
- **Flexible Payment Methods**:
  - **Cash**: Calculates change due based on the amount received.
  - **UPI (Simulated)**: Validates standard handle format and confirms simulated payments.
  - **Prepaid Smart Card (Wallet)**: Account balances stored by Card ID (e.g., student roll number) with balance deductions.
- **Receipt Generation & Storage**:
  - Formatted monospaced receipts printed to the console.
  - Invoices automatically saved as text files (`bill_XXXX.txt`) under `canteen_data/receipts/`.
- **PIN-Protected Admin Console**:
  - Add, reprice, restock, or remove catalog items.
  - Instant low-stock review list.
  - Detailed sales analytics: all-time totals, today's sales, top 5 bestsellers, and revenue broken down by payment mode.
- **Data Persistence**: Uses plain JSON files inside a local data folder—no database setup required.

---

## Directory Structure

```text
.
├── smart_canteen.py       # Main application script
├── README.md              # Project documentation
└── canteen_data/          # Auto-created on first run
    ├── menu.json          # Menu catalog & live stock counts
    ├── wallets.json       # Registered card IDs, names & balances
    ├── sales.json         # Historical transaction log
    └── receipts/          # Archived receipt text files
        ├── bill_0001.txt
        └── ...
```

---

## Requirements

- **Python 3.7+**
- No external dependencies required (`json`, `os`, `datetime` are all built into Python).

---

## Getting Started

1. Save the canteen code as `smart_canteen.py`.
2. Open your terminal or command prompt in that directory.
3. Run:
   ```bash
   python smart_canteen.py
   ```

*(On the first launch, the `canteen_data/` folder and default menu items are created automatically.)*

---

## System Walkthrough

### 1. Main Navigation
```text
--- MAIN MENU ---
1. New order / billing
2. View menu
3. Smart card (wallet)
5. Exit
```
*(Note: Option `4` accesses the **Admin Menu**, protected by default PIN `1234`)*

### 2. Placing an Order
1. Select **1** from the main menu.
2. View the menu, add items by ID, and specify quantities (bounded by live stock).
3. Select **Checkout** to review the itemized breakdown, discounts, and GST.
4. Pick a payment method (Cash, UPI, or Smart Card).
5. Once payment completes, stock updates automatically, sales logs append the transaction, and a receipt is saved to `canteen_data/receipts/`.

### 3. Smart Card Wallet
Manage cardholder balances from **Option 3**:
- **Register card**: Associate a cardholder's name with an ID (e.g., Student Roll Number).
- **Top up**: Add money directly to a card's balance.
- **Check balance**: View the current balance on file.

### 4. Admin Tools & Reports
Enter `4` at the main menu and input the PIN (`1234` by default) to unlock:
- Catalog editing (Add, Reprice, Restock, Remove).
- Low-stock alerts (`<= 5` units remaining by default).
- Comprehensive sales reporting.

---

## Sample Receipt (`bill_0001.txt`)

```text
============================================
        SMART CANTEEN - RECEIPT
============================================
Bill No : 1
Date    : 2026-10-11 21:55:00
Payment : Cash
--------------------------------------------
ITEM                 QTY    PRICE     TOTAL
--------------------------------------------
Veg Thali              3    90.00    270.00
Masala Dosa            2    60.00    120.00
--------------------------------------------
Subtotal                             390.00
Discount (10%)                       -39.00
GST (5%)                              17.55
--------------------------------------------
GRAND TOTAL                          368.55
============================================
      Thank you! Visit again :)
============================================
```

---

## Configuration

You can customize operational settings directly at the top of `smart_canteen.py`:

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `DATA_FOLDER` | `"canteen_data"` | Root folder where data files and receipts reside |
| `CURRENCY` | `"Rs."` | Currency prefix symbol for prices and receipts |
| `GST_PERCENT` | `5` | Percentage tax applied post-discount |
| `DISCOUNT_LIMIT` | `300` | Subtotal threshold required to unlock bulk discount |
| `DISCOUNT_PERCENT` | `10` | Percentage discount applied on qualifying orders |
| `LOW_STOCK_LEVEL` | `5` | Threshold triggering low-stock indicators and alerts |
| `ADMIN_PIN` | `"1234"` | Security PIN required to enter the Admin menu |

---

## License

This project is open-source and free to adapt for personal, educational, or commercial use.

