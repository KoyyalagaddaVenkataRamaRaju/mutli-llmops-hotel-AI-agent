import time
import threading
from datetime import datetime
from typing import List, Dict, Any

from app.common.logger import get_logger

logger = get_logger(__name__)

class HousekeepingThread(threading.Thread):
    """
    Background Housekeeping Worker Thread.
    Processes rooms released after check-out and marks them available.
    Demonstrates thread lifecycle (RUNNABLE, WAITING, TERMINATED) & inter-thread signaling.
    """
    def __init__(self, service_ref: Any, condition: threading.Condition):
        super().__init__(name="HousekeepingThread", daemon=True)
        self.service = service_ref
        self.condition = condition
        self.running = True
        self.activity_log: List[str] = []

    def log(self, message: str, state: str = "RUNNABLE"):
        entry = f"HousekeepingThread | {message} | state: {state}"
        self.activity_log.append(entry)
        logger.info(entry)

    def run(self):
        self.log("Thread started with priority NORM_PRIORITY", "RUNNABLE")
        while self.running:
            room_to_clean = None
            with self.condition:
                while self.running and len(self.service.collections["housekeeping_queue"]) == 0:
                    self.log("waiting for cleaning tasks", "WAITING")
                    self.condition.wait(timeout=5)
                    if not self.running:
                        break

                if not self.running:
                    break

                if len(self.service.collections["housekeeping_queue"]) > 0:
                    room_to_clean = self.service.collections["housekeeping_queue"].popleft()

            if room_to_clean:
                self.log(f"Cleaning Room {room_to_clean.room_number}", "RUNNABLE")
                time.sleep(1.0)
                self.service.mark_room_cleaned(room_to_clean.room_number)
                self.log(f"Room {room_to_clean.room_number} clean, notify() dispatched", "RUNNABLE")

        self.log("Housekeeping worker stopped", "TERMINATED")


class NightAuditTask:
    """
    Night Audit Worker Task (Runnable pattern).
    Posts nightly room charges, audits occupied inventory, and records messages.
    """
    def __init__(self, service_ref: Any):
        self.service = service_ref
        self.activity_log: List[str] = []

    def log(self, message: str, state: str = "RUNNABLE"):
        entry = f"NightAuditTask | {message} | state: {state}"
        self.activity_log.append(entry)
        logger.info(entry)

    def run(self) -> Dict[str, Any]:
        self.log("priority MAX_PRIORITY initiated", "RUNNABLE")
        time.sleep(0.3)
        self.log("scanning occupied rooms for daily ledger posting", "RUNNABLE")

        conn = self.service.db.get_connection()
        total_posted = 0.0
        audited_count = 0
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.booking_id, b.room_number, r.category, r.tariff 
                FROM bookings b
                JOIN rooms r ON b.room_number = r.room_number
                WHERE b.status = 'Active'
            """)
            occupied = cursor.fetchall()
            audited_count = len(occupied)

            for row in occupied:
                bid, r_num, cat, tariff = row
                total_posted += tariff

            self.log(f"posted room charges for {audited_count} occupied rooms (₹{total_posted:,.2f})", "RUNNABLE")
            self.log("night audit ledger reconciliation finished", "TERMINATED")

            return {
                "total_rooms": 60,
                "total_revenue": total_posted,
                "occupied_count": audited_count,
                "cleaning_count": len(self.service.collections.get("housekeeping_queue", [])),
                "occupancy_rate": round((audited_count / 60.0) * 100.0, 1),
                "audit_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "rate_multiplier_status": "20% Peak Surcharge Active" if (audited_count / 60.0) > 0.9 else "Standard Rate Multiplier (1.0x)",
                "total_charges_posted": total_posted,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "log": list(self.activity_log)
            }
        finally:
            conn.close()

