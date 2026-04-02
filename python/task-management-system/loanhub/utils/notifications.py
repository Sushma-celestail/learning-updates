import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime

# Setup notification logging
notif_logger = logging.getLogger("notifications")
notif_logger.setLevel(logging.INFO)
hdlr = logging.FileHandler("logs/notifications.log")
hdlr.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
notif_logger.addHandler(hdlr)

class NotificationStrategy(ABC):
    """
    OCP-compliant strategy for notifications.
    """
    @abstractmethod
    async def send(self, message: str):
        pass

class LogFileNotification(NotificationStrategy):
    async def send(self, message: str):
        # Simulate async delay
        await asyncio.sleep(0.1)
        notif_logger.info(message)

class ConsoleNotification(NotificationStrategy):
    async def send(self, message: str):
        await asyncio.sleep(0.1)
        print(f"NOTIFICATION: {message}")

class NotificationService:
    def __init__(self, strategies: list[NotificationStrategy]):
        self.strategies = strategies

    async def notify_all(self, message: str):
        """
        Runs multiple notification channels concurrently using asyncio.gather.
        (Day 2 Requirement)
        """
        tasks = [s.send(message) for s in self.strategies]
        await asyncio.gather(*tasks)

# Pre-configured instance
notification_service = NotificationService([LogFileNotification(), ConsoleNotification()])
