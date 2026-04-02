import asyncio
import logging
from datetime import datetime

# Setup notification logging
notif_logger = logging.getLogger("notifications_logger")
file_handler = logging.FileHandler("logs/notifications.log")
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
notif_logger.addHandler(file_handler)
notif_logger.setLevel(logging.INFO)

async def simulate_email(loan_id: int, status: str):
    await asyncio.sleep(0.1)
    return f"Email sent for Loan #{loan_id}: {status}"

async def simulate_sms(loan_id: int, status: str):
    await asyncio.sleep(0.1)
    return f"SMS sent for Loan #{loan_id}: {status}"

async def simulate_push(loan_id: int, status: str):
    await asyncio.sleep(0.1)
    return f"Push notification sent for Loan #{loan_id}: {status}"

async def send_notifications(loan_id: int, username: str, status: str):
    """Requirement 3 & 6: Async notification simulation using asyncio.gather."""
    results = await asyncio.gather(
        simulate_email(loan_id, status),
        simulate_sms(loan_id, status),
        simulate_push(loan_id, status)
    )
    
    log_msg = f"Loan #{loan_id} for user '{username}' has been {status} — notification sent"
    notif_logger.info(log_msg)
    return results

def log_new_application(loan_id: int, username: str, purpose: str, amount: int):
    log_msg = f"New loan application #{loan_id} by '{username}' for {purpose} — ₹{amount}"
    notif_logger.info(log_msg)
