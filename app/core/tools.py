from datetime import datetime, timedelta
from typing import Optional
from langchain_core.tools import tool

from app.hotel.services import HotelService
from app.hotel.vector_db import HotelVectorDatabase
from app.hotel.guardrails import HotelGuardrails
from app.hotel.models import (
    RoomNotAvailableException,
    PaymentPendingException,
    BlacklistedGuestException
)

@tool
def get_hotel_status() -> str:
    """Returns real-time hotel operational statistics: total rooms (60), available count, occupied count, cleaning count, occupancy rate %, and active stays."""
    try:
        service = HotelService()
        stats = service.get_hotel_stats()
        return (
            f"Hotel Apex Residency Operational Status:\n"
            f"- Total Inventory: {stats['total_rooms']} Rooms (Floors 1-3)\n"
            f"- Vacant / Available: {stats['available_count']}\n"
            f"- Occupied Stays: {stats['occupied_count']}\n"
            f"- Housekeeping Queue: {stats['cleaning_count']}\n"
            f"- Live Occupancy Rate: {stats['occupancy_rate']}%\n"
            f"- Active Guest Folios: {stats['active_stays']}\n"
            f"- Total Realized Revenue: ₹{stats['total_revenue']:,.2f}"
        )
    except Exception as e:
        return f"Error retrieving hotel status: {str(e)}"

@tool
def check_room_availability(category: str = "All", nights: int = 1) -> str:
    """Checks room availability for a specified category ('Standard', 'Deluxe', 'Suite', or 'All') and quotes calculated tariffs including taxes and surcharges."""
    try:
        service = HotelService()
        check_in_date = datetime.now().strftime("%Y-%m-%d")
        res = service.check_availability(category=category, nights=nights, check_in_date=check_in_date)
        
        quote_info = ""
        if res.get("quotation"):
            q = res["quotation"]
            quote_info = (
                f"\nTariff Quotation for {nights} night(s):\n"
                f"- Base Tariff/Night: ₹{q['base_tariff_per_night']:,.2f}\n"
                f"- Weekend Surcharge: {'Yes (+15%)' if q['has_weekend_surcharge'] else 'No'}\n"
                f"- Long Stay Discount: {'Yes (-10%)' if q['has_long_stay_discount'] else 'No'}\n"
                f"- Room Charges: ₹{q['room_charges']:,.2f}\n"
                f"- Luxury Tax (12%): ₹{q['estimated_taxes']:,.2f}\n"
                f"- Estimated Total: ₹{q['estimated_total']:,.2f}"
            )
        
        rooms_sample = res['available_rooms'][:10]
        return (
            f"Category: {res['category']}\n"
            f"- Available Units Count: {res['available_count']}\n"
            f"- Sample Available Room Numbers: {rooms_sample}\n"
            f"{quote_info}"
        )
    except Exception as e:
        return f"Error checking room availability: {str(e)}"

@tool
def book_hotel_room(
    guest_name: str,
    phone: str,
    id_proof: str,
    category: str = "Standard",
    nights: int = 1,
    room_number: Optional[int] = None
) -> str:
    """Allots and books a room atomically for a guest. Enforces security guardrails and blacklist checking.
    Use this tool IMMEDIATELY when a customer provides their name and wants to book or reserve a room.
    Parameters:
    - guest_name: Full name of the guest (e.g. 'Rama Raju')
    - phone: Contact phone number (e.g. '8978239929')
    - id_proof: Government ID, Aadhaar or Passport number (e.g. '939530780031')
    - category: Room category ('Standard', 'Deluxe', 'Suite'). If room number is provided, infer category automatically.
    - nights: Duration of stay in nights (e.g. 4)
    - room_number: Optional specific room number requested by the guest (e.g. 310)
    """
    try:
        service = HotelService()
        is_valid, reason = HotelGuardrails.validate_guest_credentials(
            guest_name, phone, id_proof, service.collections["blacklisted_ids"]
        )
        if not is_valid:
            return f"GUARDRAIL REJECTION: {reason}"

        # If a specific room is requested, infer category if needed
        if room_number:
            for r in service.collections["all_rooms"]:
                if r.room_number == room_number:
                    category = r.__class__.__name__.replace("Room", "")
                    break

        check_in = datetime.now().strftime("%Y-%m-%d")
        check_out = (datetime.now() + timedelta(days=max(1, nights))).strftime("%Y-%m-%d")
        
        res = service.book_and_checkin(
            guest_name=guest_name,
            phone=phone,
            id_proof=id_proof,
            category=category,
            check_in=check_in,
            check_out=check_out,
            preferred_room=room_number
        )
        return (
            f"Reservation & Check-In Confirmed!\n"
            f"- Booking ID: {res['booking_id']}\n"
            f"- Guest: {res['guest_name']} ({res['guest_id']})\n"
            f"- Room Allotted: #{res['room_number']} ({res['category']}, Floor {res['floor']})\n"
            f"- Duration: {res['nights']} Night(s) ({res['check_in']} to {res['check_out']})\n"
            f"- Total Estimated: ₹{res['total_estimated']:,.2f} (incl. 12% Luxury Tax)\n"
            f"- Keycard: Issued & Active\n"
            f"- Status: Active In-House Guest"
        )
    except BlacklistedGuestException as bge:
        return f"SECURITY ALERT: Guest check-in blocked by security guardrail: {str(bge)}"
    except RoomNotAvailableException:
        return f"UNAVAILABLE: Room #{room_number or category} is not currently available for check-in."
    except Exception as e:
        return f"Booking error: {str(e)}"

@tool
def allot_housekeeping_staff(room_number: int, staff_name: str, staff_role: str = "Housekeeper") -> str:
    """Allots a specific housekeeping team member (e.g. 'Ramesh', 'Sunita', 'Supervisor Anita') to clean or inspect a room."""
    try:
        service = HotelService()
        res = service.assign_housekeeping_staff(room_number, staff_name, staff_role)
        return (
            f"Housekeeping Staff Allotted:\n"
            f"- Assignment ID: {res['assignment_id']}\n"
            f"- Target Room: #{res['room_number']}\n"
            f"- Staff Member: {res['staff_name']} ({res['staff_role']})\n"
            f"- Time Assigned: {res['assigned_at']}\n"
            f"- Room Status: Transitioned to 'Cleaning' Queue"
        )
    except Exception as e:
        return f"Error allotting housekeeping staff: {str(e)}"

@tool
def clean_room_housekeeping(room_number: int) -> str:
    """Marks a room currently in 'Cleaning' status as clean and restores it to 'Available' inventory."""
    try:
        service = HotelService()
        service.mark_room_cleaned(room_number)
        return f"Room #{room_number} has been sanitized by housekeeping staff, inspected, and restored to AVAILABLE inventory."
    except Exception as e:
        return f"Error updating room status: {str(e)}"

@tool
def report_maintenance_issue(room_number: int, category: str, description: str, reported_by: str = "Staff") -> str:
    """Logs an engineering maintenance ticket (e.g. category 'AC', 'Plumbing', 'Electrical') for room repairs."""
    try:
        service = HotelService()
        res = service.report_maintenance_ticket(room_number, category, description, reported_by)
        return (
            f"Maintenance Ticket Logged:\n"
            f"- Ticket ID: {res['ticket_id']}\n"
            f"- Room: #{res['room_number']}\n"
            f"- Category: {res['category']}\n"
            f"- Description: {res['description']}\n"
            f"- Reported By: {res['reported_by']}\n"
            f"- Status: Open (Engineering SLA: 15-45 mins)"
        )
    except Exception as e:
        return f"Error logging maintenance issue: {str(e)}"

@tool
def get_maintenance_status(status: str = "All") -> str:
    """Retrieves active engineering and maintenance tickets across the hotel."""
    try:
        service = HotelService()
        tickets = service.get_maintenance_tickets(status)
        if not tickets:
            return "No maintenance tickets reported. All facilities operating normally."
        lines = [f"- [{t['ticket_id']}] Room #{t['room_number']} | {t['category']}: {t['description']} | Status: {t['status']}" for t in tickets[:5]]
        return f"Active Maintenance Tickets ({len(tickets)} total):\n" + "\n".join(lines)
    except Exception as e:
        return f"Error retrieving maintenance status: {str(e)}"

@tool
def add_room_service_order(room_number: int, service_name: str, cost: float = 0.0) -> str:
    """Adds a dining, laundry, or wellness service order to an active occupied room folio."""
    try:
        service = HotelService()
        custom_cost = cost if cost > 0 else None
        res = service.add_room_service(room_number=room_number, service_name=service_name, custom_cost=custom_cost)
        return (
            f"Room Service Added Successfully:\n"
            f"- Service ID: {res['service_id']}\n"
            f"- Booking ID: {res['booking_id']}\n"
            f"- Room: #{res['room_number']} ({res['guest_name']})\n"
            f"- Item: {res['service_name']}\n"
            f"- Charge: ₹{res['cost']:,.2f}\n"
            f"- Timestamp: {res['timestamp']}"
        )
    except Exception as e:
        return f"Error adding room service: {str(e)}"

@tool
def checkout_guest_room(room_number: int) -> str:
    """Checks out an occupied room, generates itemized invoice matching PDF standards, and moves room to housekeeping."""
    try:
        service = HotelService()
        res = service.checkout_guest(room_number=room_number, payment_settled=True)
        return (
            f"Check-Out Complete for Room #{room_number}!\n\n"
            f"{res['invoice_text']}\n\n"
            f"Note: Room #{room_number} has been queued for Housekeeping Sanitization."
        )
    except PaymentPendingException as ppe:
        return f"PAYMENT GUARDRAIL BLOCKED: {str(ppe)}"
    except Exception as e:
        return f"Checkout error: {str(e)}"

@tool
def execute_night_audit() -> str:
    """Executes the daily StayEase night audit task to post charges for occupied rooms and reconcile ledger records."""
    try:
        service = HotelService()
        res = service.run_night_audit()
        return (
            f"Night Audit Completed:\n"
            f"- Occupied Rooms Audited: {res['occupied_count']}\n"
            f"- Total Daily Charges Posted: ₹{res['total_charges_posted']:,.2f}\n"
            f"- Timestamp: {res['timestamp']}\n"
            f"- Audit Activity Logs:\n" + "\n".join(f"  * {entry}" for entry in res['log'])
        )
    except Exception as e:
        return f"Night audit error: {str(e)}"

@tool
def get_owner_financial_summary() -> str:
    """Calculates executive financial metrics for the Hotel Owner & General Manager: ADR, RevPAR, gross revenue, and tax remittances."""
    try:
        service = HotelService()
        summary = service.get_financial_executive_summary()
        return (
            f"Hotel Apex Residency — Executive Financial Summary:\n"
            f"- Total Inventory: {summary['total_inventory']} Rooms\n"
            f"- Occupancy Rate: {summary['occupancy_rate']}%\n"
            f"- Active Guest Stays: {summary['active_guest_stays']}\n"
            f"- Total Invoices Generated: {summary['total_invoices_generated']}\n"
            f"- Gross Realized Revenue: ₹{summary['gross_revenue']:,.2f}\n"
            f"- Room Revenue: ₹{summary['room_revenue']:,.2f}\n"
            f"- F&B and Services Revenue: ₹{summary['food_and_beverage_revenue']:,.2f}\n"
            f"- Luxury Taxes Remitted (12%): ₹{summary['luxury_taxes_remitted']:,.2f}\n"
            f"- Average Daily Rate (ADR): ₹{summary['adr_average_daily_rate']:,.2f}\n"
            f"- Revenue Per Available Room (RevPAR): ₹{summary['revpar']:,.2f}"
        )
    except Exception as e:
        return f"Error generating financial summary: {str(e)}"

@tool
def search_hotel_knowledge_base(query: str, role_filter: str = "") -> str:
    """Searches the StayEase Vector Database using semantic cosine similarity for hotel policies, room amenities, and staff SOPs."""
    try:
        vdb = HotelVectorDatabase()
        filter_val = role_filter.strip() if role_filter.strip() else None
        results = vdb.search(query, top_k=2, role_filter=filter_val)
        if not results:
            return "No matching policy or knowledge vector found."
        formatted = []
        for r in results:
            doc = r["document"]
            source = r.get("source", "Vector Store")
            formatted.append(f"[{doc['title']} | Role: {doc.get('role', 'All')} | Match: {r['score']*100:.1f}% | Source: {source}]\n{doc['content']}")
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Error searching vector database: {str(e)}"

HOTEL_OPERATIONAL_TOOLS = [
    get_hotel_status,
    check_room_availability,
    book_hotel_room,
    allot_housekeeping_staff,
    clean_room_housekeeping,
    report_maintenance_issue,
    get_maintenance_status,
    add_room_service_order,
    checkout_guest_room,
    execute_night_audit,
    get_owner_financial_summary,
    search_hotel_knowledge_base
]

