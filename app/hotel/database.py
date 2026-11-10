import os
import sqlite3
import random
from collections import deque
from typing import List, Dict, Set, Optional, Tuple, Any
from datetime import datetime, timedelta

from app.hotel.models import (
    Room, StandardRoom, DeluxeRoom, Suite,
    Guest, Booking, ServiceOrder, Invoice
)
from app.common.logger import get_logger

logger = get_logger(__name__)

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "hotel.db"))

class HotelDatabase:
    """
    DAO / Database Manager for StayEase Hotel Apex Residency.
    Handles SQLite schema creation, CRUD operations, test-data seeding, and collection caches.
    """
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()
        self._seed_sample_data_if_empty()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Creates tables: rooms, guests, bookings, services, invoices, blacklisted_ids."""
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS rooms (
                        room_number INTEGER PRIMARY KEY,
                        category TEXT NOT NULL,
                        floor INTEGER NOT NULL,
                        tariff REAL NOT NULL,
                        status TEXT NOT NULL
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS guests (
                        guest_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        id_proof TEXT NOT NULL,
                        address TEXT NOT NULL
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS bookings (
                        booking_id TEXT PRIMARY KEY,
                        guest_id TEXT NOT NULL,
                        room_number INTEGER NOT NULL,
                        check_in TEXT NOT NULL,
                        check_out TEXT NOT NULL,
                        nights INTEGER NOT NULL,
                        status TEXT NOT NULL,
                        total_amount REAL NOT NULL,
                        paid REAL NOT NULL,
                        FOREIGN KEY (guest_id) REFERENCES guests(guest_id),
                        FOREIGN KEY (room_number) REFERENCES rooms(room_number)
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS services (
                        service_id TEXT PRIMARY KEY,
                        booking_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        cost REAL NOT NULL,
                        timestamp TEXT NOT NULL,
                        FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS invoices (
                        invoice_id TEXT PRIMARY KEY,
                        booking_id TEXT NOT NULL,
                        guest_name TEXT NOT NULL,
                        room_number INTEGER NOT NULL,
                        room_category TEXT NOT NULL,
                        nights INTEGER NOT NULL,
                        room_charges REAL NOT NULL,
                        service_charges REAL NOT NULL,
                        taxes REAL NOT NULL,
                        total_amount REAL NOT NULL,
                        created_at TEXT NOT NULL
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS blacklisted_ids (
                        id_proof TEXT PRIMARY KEY,
                        reason TEXT NOT NULL
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS staff_assignments (
                        assignment_id TEXT PRIMARY KEY,
                        room_number INTEGER NOT NULL,
                        staff_name TEXT NOT NULL,
                        staff_role TEXT NOT NULL,
                        assigned_at TEXT NOT NULL,
                        status TEXT NOT NULL
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS maintenance_records (
                        ticket_id TEXT PRIMARY KEY,
                        room_number INTEGER NOT NULL,
                        category TEXT NOT NULL,
                        description TEXT NOT NULL,
                        reported_by TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                """)

            logger.info("StayEase Database tables initialized successfully at %s", self.db_path)
        finally:
            conn.close()

    def _seed_sample_data_if_empty(self):
        """Seeds 60 rooms across 3 floors and at least 20 records across all tables."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM rooms")
            room_count = cursor.fetchone()[0]

            if room_count >= 60:
                return  # already seeded

            logger.info("Seeding StayEase database with 60 rooms and sample records...")
            with conn:
                # 1. Seed 60 Rooms:
                # Standard: Floor 1 (101-115) + Floor 2 (201-215) = 30 rooms
                # Deluxe: Floor 2 (216-220) + Floor 3 (301-315) = 20 rooms
                # Suite: Floor 3 (316-325) = 10 rooms
                rooms_data = []
                for num in range(101, 116):
                    rooms_data.append((num, "Standard", 1, 2500.0, "Available"))
                for num in range(201, 216):
                    rooms_data.append((num, "Standard", 2, 2500.0, "Available"))
                for num in range(216, 221):
                    rooms_data.append((num, "Deluxe", 2, 4200.0, "Available"))
                for num in range(301, 316):
                    rooms_data.append((num, "Deluxe", 3, 4200.0, "Available"))
                for num in range(316, 326):
                    rooms_data.append((num, "Suite", 3, 7800.0, "Available"))

                cursor.executemany(
                    "INSERT OR REPLACE INTO rooms (room_number, category, floor, tariff, status) VALUES (?, ?, ?, ?, ?)",
                    rooms_data
                )

                # 2. Blacklisted IDs
                blacklisted = [
                    ("PASSPORT-BL-9912", "Fraudulent card attempts"),
                    ("AADHAAR-9999-0000", "Banned guest policy violation"),
                    ("DL-DL04-2019-902", "Previous non-payment incident")
                ]
                cursor.executemany(
                    "INSERT OR IGNORE INTO blacklisted_ids (id_proof, reason) VALUES (?, ?)",
                    blacklisted
                )

                # 3. Seed 25 Guests
                names = [
                    ("Farhan", "9876543210", "PASSPORT-A12903", "Bangalore, India"),
                    ("Priya Sharma", "9823412345", "AADHAAR-2341-5678", "Mumbai, India"),
                    ("David Miller", "9712398450", "PASSPORT-US89211", "New York, USA"),
                    ("Ananya Roy", "9834567891", "AADHAAR-8901-2345", "Kolkata, India"),
                    ("Vikram Malhotra", "9945123476", "DL-KA01-2018-87", "Bengaluru, India"),
                    ("Sophie Laurent", "9765432109", "PASSPORT-FR3490", "Paris, France"),
                    ("Rahul Verma", "9845012378", "AADHAAR-4567-8901", "Delhi, India"),
                    ("Sneha Patel", "9898123456", "DL-GJ01-2020-43", "Ahmedabad, India"),
                    ("Michael Chang", "9756123987", "PASSPORT-SG7712", "Singapore"),
                    ("Aditi Rao", "9812345670", "AADHAAR-6789-0123", "Hyderabad, India"),
                    ("Carlos Silva", "9723456781", "PASSPORT-BR4432", "Sao Paulo, Brazil"),
                    ("Rohan Deshmukh", "9832109874", "DL-MH12-2017-91", "Pune, India"),
                    ("Fatima Sheikh", "9871234098", "PASSPORT-AE6601", "Dubai, UAE"),
                    ("Kavita Nair", "9845678123", "AADHAAR-1234-5678", "Kochi, India"),
                    ("John Peterson", "9789012345", "PASSPORT-UK1123", "London, UK"),
                    ("Arjun Kapoor", "9823145698", "DL-DL03-2021-12", "Chandigarh, India"),
                    ("Elena Rostova", "9734567890", "PASSPORT-RU8823", "Moscow, Russia"),
                    ("Manish Gupta", "9819012345", "AADHAAR-7890-1234", "Jaipur, India"),
                    ("Tanya Sen", "9834129876", "DL-WB02-2019-34", "Kolkata, India"),
                    ("Siddharth Jain", "9845198765", "AADHAAR-3456-7890", "Indore, India"),
                    ("Meera Nambiar", "9823456712", "PASSPORT-IN9941", "Chennai, India"),
                    ("Lucas Becker", "9745612309", "PASSPORT-DE5519", "Berlin, Germany"),
                    ("Deepa Menon", "9812903456", "AADHAAR-5678-9012", "Trivandrum, India"),
                    ("Gaurav Mehta", "9834567129", "DL-MH01-2022-77", "Mumbai, India"),
                    ("Aisha Al-Mansoor", "9790123456", "PASSPORT-QA4402", "Doha, Qatar"),
                ]
                guests_data = []
                for idx, (name, phone, id_proof, addr) in enumerate(names, start=101):
                    gid = f"G{idx}"
                    guests_data.append((gid, name, phone, id_proof, addr))

                cursor.executemany(
                    "INSERT OR REPLACE INTO guests (guest_id, name, phone, id_proof, address) VALUES (?, ?, ?, ?, ?)",
                    guests_data
                )

                # 4. Seed Active & Past Bookings (at least 20)
                # Let's assign 12 currently occupied rooms, 4 cleaning rooms, and past completed bookings
                occupied_rooms = [102, 105, 108, 112, 203, 207, 218, 220, 305, 308, 316, 320]
                cleaning_rooms = [103, 212, 301, 312]

                for rm in occupied_rooms:
                    cursor.execute("UPDATE rooms SET status = 'Occupied' WHERE room_number = ?", (rm,))
                for rm in cleaning_rooms:
                    cursor.execute("UPDATE rooms SET status = 'Cleaning' WHERE room_number = ?", (rm,))

                bookings_data = []
                services_data = []
                invoices_data = []

                today = datetime.now()

                # Seed 12 Active bookings for occupied rooms
                for idx, rm in enumerate(occupied_rooms, start=1):
                    bid = f"BK-2026-{100 + idx}"
                    gid = f"G{100 + idx}"
                    check_in = (today - timedelta(days=idx % 3 + 1)).strftime("%Y-%m-%d")
                    check_out = (today + timedelta(days=idx % 2 + 1)).strftime("%Y-%m-%d")
                    nights = (idx % 3 + 2)
                    cat_tariff = 7800.0 if rm >= 316 else (4200.0 if rm >= 216 else 2500.0)
                    total = cat_tariff * nights
                    bookings_data.append((bid, gid, rm, check_in, check_out, nights, "Active", total, 0.0))

                    # Add room services to some active bookings
                    sid1 = f"SRV-2026-{200 + idx}"
                    services_data.append((sid1, bid, "Gourmet Dinner Buffet", 950.0, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    if idx % 2 == 0:
                        sid2 = f"SRV-2026-{300 + idx}"
                        services_data.append((sid2, bid, "Express Laundry Service", 450.0, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

                # Seed 15 Past Completed bookings and Invoices
                past_room_list = [101, 104, 106, 109, 110, 114, 202, 204, 206, 209, 211, 215, 217, 302, 304, 307, 310, 317, 318, 319, 322]
                for idx, rm in enumerate(past_room_list, start=13):
                    bid = f"BK-2026-{100 + idx}"
                    gid = f"G{100 + (idx % 25) + 1}"
                    check_in = (today - timedelta(days=idx + 5)).strftime("%Y-%m-%d")
                    check_out = (today - timedelta(days=idx)).strftime("%Y-%m-%d")
                    nights = 3 if idx % 2 == 0 else 4
                    cat_str = "Suite" if rm >= 316 else ("Deluxe" if rm >= 216 else "Standard")
                    cat_tariff = 7800.0 if rm >= 316 else (4200.0 if rm >= 216 else 2500.0)
                    room_charges = cat_tariff * nights
                    srv_cost = 650.0 if idx % 3 == 0 else 1200.0
                    taxes = round((room_charges + srv_cost) * 0.12, 2)
                    total_amount = room_charges + srv_cost + taxes

                    bookings_data.append((bid, gid, rm, check_in, check_out, nights, "Completed", total_amount, total_amount))

                    # Service record
                    sid = f"SRV-2026-{400 + idx}"
                    services_data.append((sid, bid, "Chef Specials & Refreshments", srv_cost, check_in + " 20:00:00"))

                    # Invoice record
                    inv_id = Invoice.format_invoice_number(380 + idx)
                    cursor.execute("SELECT name FROM guests WHERE guest_id = ?", (gid,))
                    gname = cursor.fetchone()[0]
                    invoices_data.append((
                        inv_id, bid, f"{gid} - {gname}", rm, cat_str, nights,
                        room_charges, srv_cost, taxes, total_amount, check_out + " 11:30:00"
                    ))

                cursor.executemany(
                    "INSERT OR REPLACE INTO bookings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    bookings_data
                )
                cursor.executemany(
                    "INSERT OR REPLACE INTO services VALUES (?, ?, ?, ?, ?)",
                    services_data
                )
                cursor.executemany(
                    "INSERT OR REPLACE INTO invoices VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    invoices_data
                )

            logger.info("Database seeding finished. 60 rooms, %d bookings, %d services, %d invoices.",
                        len(bookings_data), len(services_data), len(invoices_data))
        finally:
            conn.close()

    # ----------------- Smart Collections Loader -----------------
    def load_smart_collections(self) -> Dict[str, Any]:
        """
        Loads database records into the specific collection structures required:
        - ArrayList: all_rooms (list[Room])
        - LinkedList: housekeeping_queue (deque[Room])
        - Vector: night_audit_messages (list[str])
        - HashSet: blacklisted_ids (set[str])
        - TreeSet: available_rooms (sorted list/set[int])
        - HashMap: room_to_guest (dict[int, Guest])
        - Hashtable: service_prices (dict[str, float])
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            # 1. Rooms List (ArrayList analog)
            cursor.execute("SELECT room_number, category, floor, tariff, status FROM rooms ORDER BY room_number ASC")
            all_rooms: List[Room] = []
            housekeeping_queue: deque = deque()
            available_rooms: Set[int] = set()

            for row in cursor.fetchall():
                r_num, cat, fl, tariff, status = row
                if cat == "Standard":
                    room_obj = StandardRoom(r_num, fl, status, tariff)
                elif cat == "Deluxe":
                    room_obj = DeluxeRoom(r_num, fl, status, tariff)
                else:
                    room_obj = Suite(r_num, fl, status, tariff)

                all_rooms.append(room_obj)
                if status == "Cleaning":
                    housekeeping_queue.append(room_obj)
                elif status == "Available":
                    available_rooms.add(r_num)

            # 2. Blacklisted ID Set (HashSet analog)
            cursor.execute("SELECT id_proof FROM blacklisted_ids")
            blacklisted_set = {r[0] for r in cursor.fetchall()}

            # 3. Room to Current Guest Map (HashMap analog)
            cursor.execute("""
                SELECT b.room_number, g.guest_id, g.name, g.phone, g.id_proof, g.address
                FROM bookings b
                JOIN guests g ON b.guest_id = g.guest_id
                WHERE b.status = 'Active'
            """)
            room_to_guest: Dict[int, Guest] = {}
            for r in cursor.fetchall():
                rm_no, gid, name, ph, idp, addr = r
                room_to_guest[rm_no] = Guest.from_full_details(gid, name, ph, idp, addr)

            # 4. Service Catalog Prices (Hashtable analog)
            service_prices = {
                "Continental Breakfast": 450.0,
                "Royal Buffet Dinner": 950.0,
                "Express Laundry & Press": 350.0,
                "Luxury Ayurvedic Spa (60 min)": 2200.0,
                "Airport Luxury Chauffeur": 1500.0,
                "Premium Minibar Restock": 800.0,
                "High Tea & Snacks": 300.0
            }

            # 5. Night Audit Messages (Vector analog)
            night_audit_messages: List[str] = [
                f"[SYSTEM AUDIT] Initialized at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"[SYSTEM AUDIT] Total rooms managed: {len(all_rooms)} (Floors 1-3)"
            ]

            return {
                "all_rooms": all_rooms,
                "housekeeping_queue": housekeeping_queue,
                "night_audit_messages": night_audit_messages,
                "blacklisted_ids": blacklisted_set,
                "available_rooms": sorted(list(available_rooms)),
                "room_to_guest": room_to_guest,
                "service_prices": service_prices
            }
        finally:
            conn.close()
