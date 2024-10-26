
# KiLib Bookstore 📚

**KiLib Bookstore** is an e-commerce Django project designed to simplify the buying and leasing of books. This platform allows sellers to list their books for different buyers to purchase or lease. Buyers can use their wallet balance or make payments directly through Mpesa, with built-in safeguards for book returns in leasing agreements.

## Features

### 1. User and Seller Accounts
   - **Seller Accounts**: Sellers can create profiles, list books for sale or lease, and manage their book listings.
   - **Buyer Accounts**: Buyers can register to browse, purchase, or lease books. Additionally, they have access to their purchase and lease history.

### 2. Book Listings and Management
   - **Add, Edit, Delete**: Sellers can add new books, update their book listings, or remove them.
   - **Search Functionality**: Both buyers and sellers can search for specific books to easily find desired items.

### 3. Leasing Conditions
   - Buyers must have a balance in their account equal to or greater than the book's price to qualify for a lease. If the book is not returned, it is considered a purchase, and the price is deducted from the buyer’s wallet.
   - This approach provides security for sellers while allowing buyers flexibility in their reading options.

### 4. Payment Options
   - **Wallet Payments**: Users can make purchases using their wallet balance, which they can top up via Mpesa.
   - **Mpesa Integration**: Buyers have the option to pay directly through Mpesa. After making a payment, they can confirm by entering the Mpesa receipt number, completing the transaction.

### 5. History and Tracking
   - **Buyer History**: Buyers can view a complete record of their purchases and leases, making it easy to keep track of all transactions.
   - **Seller History**: Sellers have access to a history of their sales and leases, allowing them to monitor their book transactions.

## Technologies Used

- **Django**: Web framework for building the application.
- **Mpesa Integration**: Provides secure and convenient payment options.
- **Django Models and Views**: For managing user accounts, book listings, payments, and transaction history.
- **HTML/CSS & JavaScript**: Used for the frontend design and interactive elements.

## How It Works

1. **Register and Log In**: Users and sellers create accounts to access full platform features.
2. **Manage Books** (Sellers): Sellers can add, edit, or remove book listings, choosing to offer books for purchase or lease.
3. **Search and Select Books** (Buyers): Buyers can browse and search listings, then select to buy or lease a book.
4. **Payment**: Buyers can pay via wallet balance or directly through Mpesa, confirming payments with a receipt number for transaction completion.
5. **History Access**: Both buyers and sellers can view a complete transaction history for purchases, leases, and sales.

## Getting Started

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/JamesMatata/KiLibBookStore.git
   cd KiLib-Bookstore
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Start the Server**:
   ```bash
   python manage.py runserver
   ```

5. **Access the Application**:
   - Open [http://localhost:8000](http://localhost:8000) in your browser.

## Future Improvements

- **Enhanced Search Filters**: Add advanced search and filter options for easier book discovery by genre, author, price range, etc.
- **Lease Reminders**: Notify users of upcoming lease deadlines to avoid accidental purchases.
- **Detailed Wallet Management**: Include a complete transaction history and automatic refunds on returned leases.

## Contributing

We welcome contributions! If you have ideas or improvements, please fork the repository, make your changes, and create a pull request.
