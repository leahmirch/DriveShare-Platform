class RealPaymentProcessor:
    def process_payment(self, payer_id, receiver_id, amount):
        # Logic to update balances in the database
        import sqlite3
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()

            # Deduct from renter
            cursor.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, payer_id))

            # Add to owner
            cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, receiver_id))

            # Simulate notification
            print(f"NotifyObserver: ${amount} transferred from User {payer_id} to User {receiver_id}.")


class PaymentProxy:
    def __init__(self):
        self.processor = RealPaymentProcessor()

    def pay(self, payer_id, receiver_id, amount):
        print(f"Proxy: Initiating payment of ${amount} from {payer_id} to {receiver_id}")
        self.processor.process_payment(payer_id, receiver_id, amount)
