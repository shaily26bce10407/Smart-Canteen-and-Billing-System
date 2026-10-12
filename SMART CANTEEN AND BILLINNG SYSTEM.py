"""
SMART CANTEEN BILLING SYSTEM  (beginner friendly, standard library only)

Features
  1. Menu with prices and live stock
  2. Billing with a cart, GST and a bulk-order discount
  3. Payment by Cash, UPI (simulated) or a prepaid Smart Card wallet
  4. Receipts printed on screen and saved as text files
  5. Admin tools: add / edit / remove items, restock, low-stock alerts
  6. Sales report: totals, top-selling items, payment-mode split

Run it with:   python smart_canteen.py      (Python 3.7+, no packages needed)
Data is saved in the "canteen_data" folder, so it survives restarts.
"""

import json
import os
from datetime import datetime

# ----- SETTINGS (change these to suit your canteen) -----
DATA_FOLDER = "canteen_data"
RECEIPT_FOLDER = os.path.join(DATA_FOLDER, "receipts")
MENU_FILE = os.path.join(DATA_FOLDER, "menu.json")
WALLET_FILE = os.path.join(DATA_FOLDER, "wallets.json")
SALES_FILE = os.path.join(DATA_FOLDER, "sales.json")

CURRENCY = "Rs."
GST_PERCENT = 5           # tax added to every bill
DISCOUNT_LIMIT = 300      # bills above this amount get a discount
DISCOUNT_PERCENT = 10
LOW_STOCK_LEVEL = 5       # warn when stock is this low or lower
ADMIN_PIN = "1234"

# Starter menu, used only the first time the program runs.
DEFAULT_MENU = {
    "1": {"name": "Samosa",       "price": 15, "stock": 50},
    "2": {"name": "Veg Sandwich", "price": 40, "stock": 30},
    "3": {"name": "Masala Dosa",  "price": 60, "stock": 25},
    "4": {"name": "Veg Thali",    "price": 90, "stock": 20},
    "5": {"name": "Tea",          "price": 10, "stock": 100},
    "6": {"name": "Coffee",       "price": 20, "stock": 80},
    "7": {"name": "Cold Drink",   "price": 25, "stock": 60},
}


# ----- FILE HELPERS -----
def load_json(path, default):
    """Read a JSON file. If it is missing or broken, return the default."""
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print("Warning: could not read", path, "- using empty data.")
        return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ----- INPUT / DISPLAY HELPERS -----
def ask(prompt):
    """Ask for text and remove extra spaces."""
    return input(prompt).strip()


def ask_number(prompt, minimum=0, maximum=None, whole=False):
    """Keep asking until the user types a valid number in range."""
    while True:
        text = ask(prompt)
        try:
            number = int(text) if whole else float(text)
        except ValueError:
            print("  Please enter a valid number.")
            continue
        if number < minimum:
            print("  Must be at least", minimum)
        elif maximum is not None and number > maximum:
            print("  Must be at most", maximum)
        else:
            return number


def money(amount):
    return f"{CURRENCY} {amount:.2f}"

def line(char="-"):
    print(char * 44)

def show_menu(menu):
    """Print the menu as a neat table."""
    print()
    line("=")
    print(f"{'ID':<4}{'ITEM':<18}{'PRICE':>8}{'STOCK':>8}")
    line("=")
    for item_id in sorted(menu, key=int):
        item = menu[item_id]
        note = ""
        if item["stock"] == 0:
            note = "  (sold out)"
        elif item["stock"] <= LOW_STOCK_LEVEL:
            note = "  (low!)"
        print(f"{item_id:<4}{item['name']:<18}{item['price']:>8}"
              f"{item['stock']:>8}{note}")
    line("=")


def pick_item(menu, action):
    """Show the menu, ask for an ID, return it (or None if invalid)."""
    show_menu(menu)
    item_id = ask(f"Item ID to {action}: ")
    if item_id not in menu:
        print("No such item.")
        return None
    return item_id


# ----- ADMIN: MENU MANAGEMENT -----
def add_menu_item(menu):
    name = ask("New item name: ")
    if name == "":
        print("Name cannot be empty.")
        return
    price = ask_number("Price: ", minimum=1)
    stock = ask_number("Starting stock: ", minimum=0, whole=True)
    item_id = str(max([int(i) for i in menu] + [0]) + 1)   # next free ID
    menu[item_id] = {"name": name, "price": price, "stock": stock}
    save_json(MENU_FILE, menu)
    print(f"Added {name} with ID {item_id}.")


def update_price(menu):
    item_id = pick_item(menu, "change price of")
    if item_id:
        menu[item_id]["price"] = ask_number("New price: ", minimum=1)
        save_json(MENU_FILE, menu)
        print("Price updated.")


def restock_item(menu):
    item_id = pick_item(menu, "restock")
    if item_id:
        extra = ask_number("Units to add: ", minimum=1, whole=True)
        menu[item_id]["stock"] += extra
        save_json(MENU_FILE, menu)
        print(f"{menu[item_id]['name']} stock is now {menu[item_id]['stock']}.")


def remove_menu_item(menu):
    item_id = pick_item(menu, "remove")
    if item_id and ask(f"Really remove {menu[item_id]['name']}? (y/n): ").lower() == "y":
        del menu[item_id]
        save_json(MENU_FILE, menu)
        print("Item removed.")


def show_low_stock(menu):
    low = [m for m in menu.values() if m["stock"] <= LOW_STOCK_LEVEL]
    print("\nItems that need restocking:" if low else "\nEverything is well stocked.")
    for item in low:
        print(f"  {item['name']}: {item['stock']} left")


# ----- SMART CARD (WALLET) -----
def register_card(wallets):
    card_id = ask("Choose a card ID (e.g. roll number): ")
    if card_id == "":
        print("Card ID cannot be empty.")
    elif card_id in wallets:
        print("That card already exists.")
    else:
        wallets[card_id] = {"name": ask("Card holder name: "), "balance": 0.0}
        save_json(WALLET_FILE, wallets)
        print("Card created.")


def top_up_card(wallets):
    card_id = ask("Card ID: ")
    if card_id not in wallets:
        print("Card not found.")
        return
    wallets[card_id]["balance"] += ask_number("Amount to add: ", minimum=1)
    save_json(WALLET_FILE, wallets)
    print("New balance:", money(wallets[card_id]["balance"]))


def check_balance(wallets):
    card_id = ask("Card ID: ")
    if card_id not in wallets:
        print("Card not found.")
    else:
        card = wallets[card_id]
        print(f"{card['name']} has {money(card['balance'])}")


# ----- BILLING -----
def add_to_cart(menu, cart):
    item_id = pick_item(menu, "add")
    if item_id is None:
        return
    item = menu[item_id]
    available = item["stock"] - cart.get(item_id, 0)
    if available <= 0:
        print(f"  Sorry, {item['name']} is out of stock.")
        return
    qty = ask_number(f"Quantity (max {available}): ", minimum=1,
                     maximum=available, whole=True)
    cart[item_id] = cart.get(item_id, 0) + qty
    print(f"  Added {qty} x {item['name']}")


def remove_from_cart(menu, cart):
    item_id = ask("Item ID to remove from cart: ")
    if item_id in cart:
        print(f"  Removed {menu[item_id]['name']}.")
        del cart[item_id]
    else:
        print("  That item is not in the cart.")


def cart_lines(menu, cart):
    """Return the item rows of a bill as a list of text lines."""
    rows = [f"{'ITEM':<18}{'QTY':>5}{'PRICE':>9}{'TOTAL':>10}", "-" * 44]
    for item_id, qty in cart.items():
        item = menu[item_id]
        rows.append(f"{item['name']:<18}{qty:>5}{item['price']:>9}"
                    f"{item['price'] * qty:>10.2f}")
    rows.append("-" * 44)
    return rows


def calculate_bill(menu, cart):
    """Work out subtotal, discount, tax and grand total."""
    subtotal = sum(menu[i]["price"] * q for i, q in cart.items())
    discount = 0.0
    if subtotal > DISCOUNT_LIMIT:
        discount = subtotal * DISCOUNT_PERCENT / 100
    tax = (subtotal - discount) * GST_PERCENT / 100
    return {"subtotal": subtotal, "discount": discount, "tax": tax,
            "total": subtotal - discount + tax}


def total_lines(bill):
    """Return the totals part of a bill as a list of text lines."""
    rows = [f"{'Subtotal':<30}{bill['subtotal']:>12.2f}"]
    if bill["discount"] > 0:
        label = f"Discount ({DISCOUNT_PERCENT}%)"
        rows.append(f"{label:<30}{-bill['discount']:>12.2f}")
    label = f"GST ({GST_PERCENT}%)"
    rows.append(f"{label:<30}{bill['tax']:>12.2f}")
    rows.append("-" * 44)
    rows.append(f"{'GRAND TOTAL':<30}{bill['total']:>12.2f}")
    return rows


def pay_cash(bill):
    while True:
        given = ask_number("Cash received: ")
        if given >= bill["total"]:
            print("Change to return:", money(given - bill["total"]))
            return "Cash"
        print("  Not enough cash. Try again.")


def pay_upi(bill):
    upi_id = ask("Customer UPI ID: ")
    if "@" not in upi_id:
        print("  That does not look like a UPI ID (needs an @).")
        return None
    print(f"  Payment request of {money(bill['total'])} sent to {upi_id}")
    if ask("  Payment received? (y/n): ").lower() == "y":
        return "UPI"
    print("  Payment not confirmed.")
    return None


def pay_card(bill, wallets):
    card_id = ask("Card ID: ")
    if card_id not in wallets:
        print("  Card not found.")
        return None
    card = wallets[card_id]
    if card["balance"] < bill["total"]:
        print(f"  Not enough balance ({money(card['balance'])}).")
        return None
    card["balance"] -= bill["total"]
    save_json(WALLET_FILE, wallets)
    print("  Paid from card. Remaining balance:", money(card["balance"]))
    return "Card"


def take_payment(bill, wallets):
    """Ask how to pay. Returns the payment mode, or None if it failed."""
    print("\nPayment method:  1. Cash   2. UPI   3. Smart Card   4. Cancel")
    choice = ask_number("Choose 1-4: ", minimum=1, maximum=4, whole=True)
    if choice == 1:
        return pay_cash(bill)
    if choice == 2:
        return pay_upi(bill)
    if choice == 3:
        return pay_card(bill, wallets)
    print("Payment cancelled.")
    return None


def finish_sale(menu, cart, bill, mode, sales):
    """Reduce stock, record the sale, then print and save the receipt."""
    for item_id, qty in cart.items():          # 1. reduce stock
        menu[item_id]["stock"] -= qty
    save_json(MENU_FILE, menu)

    bill_no = len(sales) + 1                   # 2. record the sale
    when = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sales.append({"bill_no": bill_no, "time": when, "mode": mode,
                  "total": round(bill["total"], 2),
                  "items": {menu[i]["name"]: q for i, q in cart.items()}})
    save_json(SALES_FILE, sales)

    receipt = ["=" * 44, "        SMART CANTEEN - RECEIPT", "=" * 44,
               f"Bill No : {bill_no}", f"Date    : {when}",
               f"Payment : {mode}", "-" * 44]
    receipt += cart_lines(menu, cart) + total_lines(bill)
    receipt += ["=" * 44, "      Thank you! Visit again :)", "=" * 44]

    print("\n" + "\n".join(receipt))            # 3. print + save receipt
    filename = os.path.join(RECEIPT_FOLDER, f"bill_{bill_no:04d}.txt")
    with open(filename, "w") as f:
        f.write("\n".join(receipt))
    print(f"(Receipt saved to {filename})")

    for item_id in cart:                       # 4. low-stock warning
        item = menu[item_id]
        if item["stock"] <= LOW_STOCK_LEVEL:
            print(f"** Alert: {item['name']} is running low "
                  f"({item['stock']} left) **")


def new_order(menu, wallets, sales):
    """The billing screen: build a cart, then check out."""
    cart = {}
    while True:
        print("\n--- NEW ORDER ---")
        print("1. Show menu   2. Add item   3. Remove item")
        print("4. View cart   5. Checkout   6. Cancel order")
        choice = ask("Choose: ")

        if choice == "1":
            show_menu(menu)
        elif choice == "2":
            add_to_cart(menu, cart)
        elif choice == "3":
            remove_from_cart(menu, cart)
        elif choice == "4":
            print("\n" + ("\n".join(cart_lines(menu, cart)) if cart
                          else "Cart is empty."))
        elif choice == "5":
            if not cart:
                print("  Cart is empty - add something first.")
                continue
            bill = calculate_bill(menu, cart)
            print("\n" + "\n".join(cart_lines(menu, cart) + total_lines(bill)))
            mode = take_payment(bill, wallets)
            if mode is not None:
                finish_sale(menu, cart, bill, mode, sales)
                return
            print("Payment did not go through. Cart is kept.")
        elif choice == "6":
            print("Order cancelled.")
            return
        else:
            print("  Please choose 1-6.")


# ----- REPORTS -----
def sales_report(sales):
    print()
    line("=")
    print("SALES REPORT")
    line("=")
    if not sales:
        print("No sales yet.")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    todays = [s for s in sales if s["time"].startswith(today)]
    print("Bills (all time) :", len(sales))
    print("Sales (all time) :", money(sum(s["total"] for s in sales)))
    print("Bills today      :", len(todays))
    print("Sales today      :", money(sum(s["total"] for s in todays)))

    item_counts = {}       # item name -> number sold
    mode_totals = {}       # payment mode -> money collected
    for sale in sales:
        for name, qty in sale["items"].items():
            item_counts[name] = item_counts.get(name, 0) + qty
        mode_totals[sale["mode"]] = mode_totals.get(sale["mode"], 0) + sale["total"]

    print("\nTop selling items:")
    ranked = sorted(item_counts.items(), key=lambda pair: pair[1], reverse=True)
    for rank, (name, qty) in enumerate(ranked[:5], start=1):
        print(f"  {rank}. {name:<16} {qty} sold")

    print("\nSales by payment mode:")
    for mode, total in mode_totals.items():
        print(f"  {mode:<6} {money(total)}")


# ----- SUB-MENUS -----
def admin_menu(menu, sales):
    if ask("Enter admin PIN: ") != ADMIN_PIN:
        print("Wrong PIN.")
        return
    while True:
        print("\n--- ADMIN MENU ---")
        print("1. Add item      2. Change price   3. Restock")
        print("4. Remove item   5. Low stock      6. Sales report")
        print("7. Back")
        choice = ask("Choose: ")
        if choice == "1":
            add_menu_item(menu)
        elif choice == "2":
            update_price(menu)
        elif choice == "3":
            restock_item(menu)
        elif choice == "4":
            remove_menu_item(menu)
        elif choice == "5":
            show_low_stock(menu)
        elif choice == "6":
            sales_report(sales)
        elif choice == "7":
            return
        else:
            print("  Please choose 1-7.")


def wallet_menu(wallets):
    while True:
        print("\n--- SMART CARD MENU ---")
        print("1. Register card   2. Top up   3. Check balance   4. Back")
        choice = ask("Choose: ")
        if choice == "1":
            register_card(wallets)
        elif choice == "2":
            top_up_card(wallets)
        elif choice == "3":
            check_balance(wallets)
        elif choice == "4":
            return
        else:
            print("  Please choose 1-4.")


# ----- MAIN PROGRAM -----
def main():
    os.makedirs(RECEIPT_FOLDER, exist_ok=True)
    menu = load_json(MENU_FILE, None)
    if menu is None:                    # first run: use the starter menu
        menu = DEFAULT_MENU
        save_json(MENU_FILE, menu)
    wallets = load_json(WALLET_FILE, {})
    sales = load_json(SALES_FILE, [])

    print("\n" + "=" * 44)
    print("     WELCOME TO THE SMART CANTEEN SYSTEM")
    print("=" * 44)

   
    while True:
        print("\n--- MAIN MENU ---")
        print("1. New order / billing")
        print("2. View menu")
        print("3. Smart card (wallet)")
        print("5. Exit")
        choice = ask("Choose: ")

        if choice == "1":
            new_order(menu, wallets, sales)
        elif choice == "2":
            show_menu(menu)
        elif choice == "3":
            wallet_menu(wallets)
        elif choice == "4":
            admin_menu(menu, sales)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("  Please choose 1-5.")



if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram closed.")