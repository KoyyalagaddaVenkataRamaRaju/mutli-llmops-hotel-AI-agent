# StayEase: The Smart Hotel Booking, Billing and Housekeeping Coordinator
## Hotel Apex Residency — Enterprise Management System & AI Agent
### Project Architecture, Technical Specifications & Syllabus Mapping Report

---

## 1. Executive Summary
**StayEase** is an enterprise-grade Hotel Management, Billing, Housekeeping Coordinator, and AI Concierge system developed for **Hotel Apex Residency** (a 60-room property across 3 floors). 

The system automates front desk operations, eliminates double-booking race conditions through synchronized atomic allocations, manages real-time housekeeping queues, enforces business rules (weekend surcharges, peak occupancy tariffs, long-stay discounts, luxury taxes), executes daily night audits, provides pure binary byte stream backup/restoration (`invoices.dat`), and features an in-code **Vector Knowledge Database** with cosine similarity paired with a Groq-powered AI Concierge.

---

## 2. Comprehensive Concept Mapping Table

| Syllabus Topic / Requirement | StayEase Python Implementation | Class & File Location | Method / Construct | Real Logic Description |
| :--- | :--- | :--- | :--- | :--- |
| **Abstract Class** | `Room` (ABC) | `app/hotel/models.py` | `calculate_tariff(nights)`, `describe()` | Base class defining room state (`room_number`, `floor`, `status`, `base_tariff`) with abstract tariff calculation. |
| **Interface / Protocol** | `Serviceable` | `app/hotel/models.py` | `add_service()`, `get_service_total()`, `clear_services()` | Implemented by `DeluxeRoom` and `Suite` to support on-demand billing of dining, laundry, and spa amenities. |
| **Multilevel Hierarchy** | `Room` $\rightarrow$ `DeluxeRoom` $\rightarrow$ `Suite` | `app/hotel/models.py` | `super().__init__()`, `super().calculate_tariff()` | `DeluxeRoom` adds balcony & minibar; `Suite` adds living area & 24/7 butler service. Calls `super()` constructors. |
| **Final Semantics** | `Suite` declared final; `LUXURY_TAX_RATE`, `format_invoice_number()` | `app/hotel/models.py` | `Invoice.format_invoice_number()` | Fixed invoice prefix format (`INV-2026-XXXX`) and luxury tax rate (12%). |
| **Array Data Structures** | `char[][] floorPlan`, `double[7] weekdayMultipliers` | `app/hotel/models.py`, `app/hotel/services.py` | `get_floor_plan()`, `WEEKDAY_MULTIPLIERS` | Matrix of status codes (`A`, `O`, `C`) across 3 floors, and 7-day rate multiplier array. |
| **Method Overloading** | Overloaded Bookings & Constructors | `app/hotel/models.py`, `app/hotel/services.py` | `Guest.from_name()`, `Guest.from_contact()`, `Guest.from_full_details()` | Factory constructors allowing guest creation with variable argument sets. |
| **Method Overriding & Polymorphism** | Runtime Dynamic Method Dispatch | `app/hotel/models.py` | `StandardRoom.calculate_tariff()`, `DeluxeRoom.calculate_tariff()`, `Suite.calculate_tariff()` | A base `Room` reference dynamically invokes the overridden tariff logic during checkout invoice generation. |
| **Object Class Hierarchy** | Object overrides | `app/hotel/models.py` | `__str__()`, `__repr__()`, `__eq__()`, `__hash__()` | Overridden to ensure rooms and guests can be hashed and compared cleanly in collections. |
| **User-Defined Exceptions** | Custom Exception Hierarchy | `app/hotel/models.py` | `StayEaseException`, `RoomNotAvailableException`, `InvalidStayPeriodException`, `PaymentPendingException`, `BlacklistedGuestException` | Thrown when rooms are unavailable, dates invalid, checkout attempted with balance, or ID is blacklisted. |
| **Built-in Exceptions** | Exception Handling | `app/backend/api.py`, `app/hotel/services.py` | `try / except / finally` | Handles `ValueError`, `KeyError`, `IndexError`, `sqlite3.Error`, and `IOError` cleanly with logged tracebacks. |
| **Multithreading** | Worker Threads | `app/hotel/tasks.py` | `HousekeepingThread(threading.Thread)`, `NightAuditTask` | Background worker threads simulating room cleaning and daily night audit ledger reconciliation. |
| **Thread Lifecycle & State** | Thread Monitoring | `app/hotel/tasks.py` | `getState()` / activity logger | Tracks states (`RUNNABLE`, `WAITING`, `TERMINATED`) matching PDF Sample Output 3. |
| **Thread Synchronization** | Concurrency Control | `app/hotel/services.py` | `threading.Lock()`, `threading.Condition()` | Atomic lock prevents two front desk terminals from allocating the last room simultaneously. |
| **Inter-Thread Communication** | Wait & Notify Pattern | `app/hotel/services.py`, `app/hotel/tasks.py` | `condition.wait()`, `condition.notify()` | Housekeeper waits when queue is empty; check-out adds released room and signals `notify()`. |
| **Byte Stream I/O** | Binary Backup & Restore | `app/hotel/binary_backup.py` | `ByteStreamBackupManager.backup_to_binary()`, `restore_from_binary()` | Pure byte-level serialization (`open('invoices.dat', 'wb')` and `'rb'`) using `struct.pack`/`unpack`. |
| **Database Module** | SQLite DAO with Prepared Statements | `app/hotel/database.py` | `HotelDatabase._init_db()`, `get_connection()` | Creates `hotel.db` on first run with parameterized SQL statements across 8 tables; seeds 60 rooms and 20+ records. |
| **Smart Collections** | Java Collections Analogs | `app/hotel/database.py` | `load_smart_collections()` | Maps `ArrayList` (list), `LinkedList` (deque), `Vector` (list), `HashSet` (set), `TreeSet` (sorted list), `HashMap` (dict), `Hashtable` (dict). |
| **Hierarchical Chunking** | Semantic Windowing with Overlap | `app/hotel/chunker.py` | `HierarchicalSemanticChunker.chunk_document()` | 110-word sliding windows with 20-word overlaps enriched with role and section metadata. |
| **Pinecone & Vector Database** | Hybrid Cloud & Cosine Vector Space | `app/hotel/vector_db.py` | `HotelVectorDatabase.search()` | Serverless Pinecone Cloud index (`stayease-hotel-apex`) paired with normalized Cosine Similarity fallback. |
| **AI Guardrails Engine** | Dual Input/Output Safety | `app/hotel/guardrails.py` | `HotelGuardrails.check_input_safety()`, `filter_response()` | Enforces prompt injection filtering, security blacklist verification, and minimum rate floors (no $0 promises). |
| **AI Multi-Role Agent** | ReAct Agent with 12 Operational Tools | `app/core/ai_agent.py`, `app/core/tools.py` | `get_response_from_ai_agents()` | 5 leadership roles (Receptionist, Manager, Owner, Staff, Concierge) with 3-layer resilience & offline fallback. |
| **Modular Enterprise UI** | Light Luxury Modular Architecture | `app/frontend/ui.py`, `app/frontend/panels/` | Streamlit + Custom Light Luxury CSS | 9 isolated functional panels, executive top navbar, live KPI cards, and interactive floor plan. |

---

## 3. Verified Sample Outputs (Matching PDF Specifications)

### Sample Output 1: Check-out Invoice
```text
----- CHECK-OUT INVOICE -----
Invoice: INV-2026-0388
Guest: G118 - Farhan
Room: 305 (Deluxe)
Nights: 3
Room Charges: Rs. 10,500.00
Services: Rs. 1,240.00
Taxes: Rs. 1,409.00
Total: Rs. 13,149.00
-----------------------------
```

### Sample Output 2: Room Status
```text
----- ROOM STATUS -----
Available: 44
Occupied: 11
Cleaning: 5
Housekeeping Queue: 103, 212, 301, 312, 102
Occupancy: 18.3%
```

### Sample Output 3: Thread Activity Log
```text
----- THREAD ACTIVITY LOG -----
HousekeepingThread | priority NORM_PRIORITY | state: RUNNABLE
NightAuditTask | priority MAX_PRIORITY | state: RUNNABLE
NightAuditTask | scanning occupied rooms | state: WAITING
HousekeepingThread | room clean, notify() dispatched | state: RUNNABLE
NightAuditTask | resumed, charges posted | state: RUNNABLE
HousekeepingThread | finished | state: TERMINATED
```

### Sample Output 4: Error Handling
```text
----- ERROR MESSAGES -----
RoomNotAvailableException: No available rooms in category 'Deluxe' at this time.
InvalidStayPeriodException: Check-out date (2026-11-10) must be after check-in date (2026-11-10).
PaymentPendingException: Check-out attempted with unpaid balance of Rs. 10,724.00 for booking BK-2026-101.
BlacklistedGuestException: ID proof 'PASSPORT-BL-9912' is blacklisted by hotel security.
```

### Sample Output 5: Backup and Restore
```text
----- BACKUP AND RESTORE -----
File: invoices.dat
Records Written: 22
Bytes Written: 2,675
Records Restored: 22
Verification: All records match
```

---

## 4. Enhanced AI Agent & Interactive UI Capabilities

### 1. Clickable Room Keycards & Customer Folio Inspector
- Every room card in the 60-room matrix (`app/frontend/panels/floor_plan.py`) is an interactive button.
- Clicking any room opens an `@st.dialog` modal displaying:
  - **Occupied Rooms**: Registered guest name, contact phone, official ID / Aadhaar proof, check-in/out dates, nights stayed, room charges, in-room dining bill, 12% luxury tax, and grand realized revenue.
  - **Itemized Orders History**: Complete table of all culinary and amenity orders posted to this folio.
  - **Available Rooms**: Room specs, luxury amenities, and an instant Autonomous Check-In form.
  - **Cleaning Rooms**: Turnaround status and 1-click "Mark Room Cleaned & Ready".

### 2. Food AI Agent & In-Room Dining Concierge
- Integrated into both the Room Folio modal and the AI Terminal (`app/frontend/panels/agent_terminal.py`).
- Supports natural language culinary ordering (e.g., *"Order 2 Biryanis, Butter Chicken, and Mango Lassi to Room 112"*).
- Includes 1-click popular selections (Hyderabadi Dum Biryani ₹650, Breakfast Buffet ₹450, Gourmet Cappuccino ₹300, Woodfired Pizza ₹580, Belgian Truffle Cake ₹350).
- Automatically posts service orders to active bookings in `hotel.db`, computes taxes, and provides kitchen prep SLAs.

### 3. Persistent Floating Action Button (FAB)
- Fixed at the bottom-right of the viewport across all panels (`💬 Chat with StayEase AI`).
- Allows customers and staff to chat with the agent, book rooms, and request services without losing their current screen.

### 4. Authentic unDraw Vector Illustrations (`app/frontend/components/illustrations.py`)
- Sourced directly from the official unDraw collection (`https://undraw.co/illustrations` by Katerina Limpitsouni) and stored locally under `app/frontend/assets/illustrations/`.
- Includes official vectors: `chat-bot.svg`, `building.svg`, `booking.svg`, `order-confirmed.svg`, `clean-up.svg`, `maintenance.svg`, `eating-together.svg`, `business-analytics.svg`, `financial-data.svg`, and `cloud-hosting.svg`.
- Formatted with responsive viewBox preservation and unDraw signature colors (`#6C63FF`, `#2F2E41`, `#FFB8B8`, `#00F5D4`).

### 5. Official Icons8 Color Iconography & Offline Base64 Engine (`app/frontend/components/icons.py`)
- Official Icons8 color icon suite (`https://icons8.com/`) stored locally under `app/frontend/assets/icons/`.
- Renders via fast base64 data URIs (`data:image/png;base64,...`), guaranteeing 100% offline availability, zero cross-origin blocks, and instant sub-millisecond rendering across all browsers.
- Embedded across the sticky executive navbar, all 6 KPI cards, sidebar navigation, dialog modals, and chat message avatars.

### 6. Sticky Executive Navbar
- Uses pure CSS sticky positioning pinned to `top: 0px` with `z-index: 99999` and container overflow clipping overrides, ensuring the brand bar, live SQLite sync indicator, active AI persona, and live clock remain visible on all screen sizes during scrolling.

---

## 5. How to Execute
```powershell
# Run the complete application
.\venv\Scripts\python.exe app\main.py
```
Backend API will be live on `http://127.0.0.1:8000` and the Streamlit UI on `http://localhost:8501`.


