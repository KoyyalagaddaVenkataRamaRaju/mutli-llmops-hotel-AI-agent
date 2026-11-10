from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from app.core.ai_agent import get_response_from_ai_agents, execute_local_operational_fallback, DEFAULT_STAYEASE_SYSTEM_PROMPT
from app.hotel.services import HotelService
from app.hotel.models import (
    StayEaseException, RoomNotAvailableException,
    InvalidStayPeriodException, PaymentPendingException,
    BlacklistedGuestException
)
from app.config.settings import settings
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

app = FastAPI(
    title="StayEase Hotel Apex Residency AI Operations API",
    description="Smart Hotel Booking, Billing, Housekeeping Coordinator & AI Concierge",
    version="2.0.0"
)

hotel_service = HotelService()

# ----------------- Request Models -----------------
class RequestState(BaseModel):
    model_name: str
    system_prompt: Optional[str] = DEFAULT_STAYEASE_SYSTEM_PROMPT
    messages: List[Any]
    allow_search: bool = False
    active_role: Optional[str] = "General"

class BookingRequest(BaseModel):
    guest_name: str
    phone: str
    id_proof: str
    category: str
    check_in: str
    check_out: str
    address: Optional[str] = "Unspecified"
    room_number: Optional[int] = None

class CheckoutRequest(BaseModel):
    room_number: int
    payment_settled: bool = True

class ServiceOrderRequest(BaseModel):
    room_number: int
    service_name: str
    cost: Optional[float] = None

class HousekeepingCleanRequest(BaseModel):
    room_number: int

class StaffAssignmentRequest(BaseModel):
    room_number: int
    staff_name: str
    staff_role: Optional[str] = "Housekeeper"

class MaintenanceReportRequest(BaseModel):
    room_number: int
    category: str
    description: str
    reported_by: Optional[str] = "Staff"

class MaintenanceResolveRequest(BaseModel):
    ticket_id: str

# ----------------- AI Chat Endpoint -----------------
@app.post("/chat")
def chat_endpoint(request: RequestState):
    logger.info("Received AI agent request for model: %s (role: %s)", request.model_name, request.active_role)

    if request.model_name not in settings.ALLOWED_MODEL_NAMES:
        logger.warning("Invalid model name provided: %s", request.model_name)
        raise HTTPException(status_code=400, detail=f"Invalid model name. Allowed: {settings.ALLOWED_MODEL_NAMES}")

    try:
        response = get_response_from_ai_agents(
            request.model_name,
            request.messages,
            request.allow_search,
            request.system_prompt,
            active_role=request.active_role or "General"
        )
        return {"response": response}
    except Exception as e:
        logger.error("Error occurred during AI agent response generation: %s. Engaging operational fallback engine.", e)
        last_msg = request.messages[-1] if request.messages else "What is the hotel status?"
        fallback_res = execute_local_operational_fallback(last_msg, active_role=request.active_role or "General")
        return {"response": fallback_res}


# ----------------- Hotel Management Endpoints -----------------
@app.get("/stats")
def get_hotel_stats():
    """Returns overview statistics: room counts, occupancy rate, total revenue."""
    return hotel_service.get_hotel_stats()

@app.get("/floor-plan")
def get_floor_plan():
    """Returns the 3-floor plan matrix with 60 rooms and status codes (A, O, C)."""
    return {"floors": hotel_service.get_floor_plan()}

@app.get("/active-stays")
def get_active_stays():
    """Returns list of occupied rooms with active guest details."""
    conn = hotel_service.db.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.booking_id, b.room_number, r.category, r.floor, r.tariff,
                   g.guest_id, g.name AS guest_name, g.phone, b.check_in, b.check_out, b.nights
            FROM bookings b
            JOIN guests g ON b.guest_id = g.guest_id
            JOIN rooms r ON b.room_number = r.room_number
            WHERE b.status = 'Active'
            ORDER BY b.room_number ASC
        """)
        rows = [dict(r) for r in cursor.fetchall()]
        return {"active_stays": rows}
    finally:
        conn.close()

@app.get("/availability")
def check_availability(category: str = "All", nights: int = 1, check_in: Optional[str] = None):
    """Checks available rooms and estimated tariffs."""
    return hotel_service.check_availability(category=category, nights=nights, check_in_date=check_in)

@app.post("/book")
def book_room(request: BookingRequest):
    """Processes guest check-in / reservation atomically."""
    try:
        res = hotel_service.book_and_checkin(
            guest_name=request.guest_name,
            phone=request.phone,
            id_proof=request.id_proof,
            category=request.category,
            check_in=request.check_in,
            check_out=request.check_out,
            address=request.address,
            preferred_room=request.room_number
        )
        return res
    except BlacklistedGuestException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except (InvalidStayPeriodException, RoomNotAvailableException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/checkout")
def checkout_room(request: CheckoutRequest):
    """Checks out a room, produces itemized invoice, and moves room to cleaning queue."""
    try:
        res = hotel_service.checkout_guest(
            room_number=request.room_number,
            payment_settled=request.payment_settled
        )
        return res
    except PaymentPendingException as e:
        raise HTTPException(status_code=402, detail=str(e))
    except StayEaseException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/services/catalog")
def get_service_catalog():
    """Returns available hotel services and pricing."""
    hotel_service.reload_collections()
    return {"catalog": hotel_service.collections["service_prices"]}

@app.post("/services/order")
def order_room_service(request: ServiceOrderRequest):
    """Adds a room service order to an active guest stay."""
    try:
        return hotel_service.add_room_service(
            room_number=request.room_number,
            service_name=request.service_name,
            custom_cost=request.cost
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/housekeeping/queue")
def get_housekeeping_queue():
    """Returns rooms currently awaiting cleaning."""
    hotel_service.reload_collections()
    queue = [r.to_dict() for r in hotel_service.collections["housekeeping_queue"]]
    return {"queue": queue, "count": len(queue)}

@app.post("/housekeeping/assign-staff")
def assign_housekeeping_staff_endpoint(request: StaffAssignmentRequest):
    """Allots cleaning personnel to a specific room."""
    try:
        return hotel_service.assign_housekeeping_staff(request.room_number, request.staff_name, request.staff_role or "Housekeeper")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/housekeeping/assignments")
def get_housekeeping_assignments_endpoint():
    """Returns active housekeeping staff allotments."""
    return {"assignments": hotel_service.get_housekeeping_assignments()}

@app.post("/maintenance/report")
def report_maintenance_endpoint(request: MaintenanceReportRequest):
    """Logs an engineering maintenance ticket."""
    try:
        return hotel_service.report_maintenance_ticket(request.room_number, request.category, request.description, request.reported_by or "Staff")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/maintenance/tickets")
def get_maintenance_tickets_endpoint(status: str = "All"):
    """Returns active hotel maintenance tickets."""
    return {"tickets": hotel_service.get_maintenance_tickets(status)}

@app.post("/maintenance/resolve")
def resolve_maintenance_endpoint(request: MaintenanceResolveRequest):
    """Resolves an engineering maintenance ticket."""
    return hotel_service.resolve_maintenance_ticket(request.ticket_id)

@app.get("/owner/financial-summary")
def get_owner_financial_summary_endpoint():
    """Returns executive analytics (ADR, RevPAR, gross revenue, taxes) for Owner and GM."""
    return hotel_service.get_financial_executive_summary()

@app.get("/guardrails/status")
def get_guardrails_status():
    """Returns active AI Guardrails configuration status."""
    return {
        "status": "Active & Enforced",
        "input_guardrails": [
            "Prompt Injection & Jailbreak Filter",
            "PII & Guest Credential Validator",
            "Security Blacklist Interceptor"
        ],
        "output_guardrails": [
            "Tariff Integrity & Rate Floor Protector (No unauthorized zero rates)",
            "Unpaid Folio Checkout Gatekeeper",
            "Professional Hospitality Persona Filter"
        ]
    }

@app.post("/housekeeping/clean")
def clean_room(request: HousekeepingCleanRequest):
    """Marks a room in cleaning as clean and available."""
    try:
        hotel_service.mark_room_cleaned(request.room_number)
        return {"status": "success", "room_number": request.room_number, "new_status": "Available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/housekeeping/start-worker")
def start_housekeeper_worker():
    """Starts the background Housekeeping worker thread."""
    msg = hotel_service.start_housekeeping_thread_worker()
    return {"message": msg}

@app.post("/night-audit")
def run_night_audit():
    """Triggers night audit posting and reconciliation."""
    return hotel_service.run_night_audit()

@app.post("/backup")
def binary_backup():
    """Exports all invoices to binary invoices.dat using byte streams."""
    try:
        return hotel_service.export_invoices_binary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/restore")
def binary_restore():
    """Reloads invoices from binary invoices.dat and verifies record integrity."""
    try:
        return hotel_service.restore_invoices_binary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from app.hotel.vector_db import HotelVectorDatabase

hotel_vdb = HotelVectorDatabase()

class VectorSearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3

@app.post("/vector-db/search")
def search_vector_db(request: VectorSearchRequest):
    """Searches the in-code vector database using cosine similarity."""
    return {"results": hotel_vdb.search(request.query, top_k=request.top_k)}

class PineconeConfigRequest(BaseModel):
    api_key: str
    index_name: Optional[str] = "stayease-hotel-apex"

@app.post("/pinecone/connect")
def connect_pinecone_endpoint(request: PineconeConfigRequest):
    """Connects to Pinecone vector database and persists API key to .env."""
    success, message = hotel_vdb.connect_pinecone(request.api_key, request.index_name)
    if success:
        hotel_vdb.save_pinecone_api_key_to_env(request.api_key, request.index_name)
        return {"status": "success", "message": message, "connected": True}
    else:
        # Still save to .env if requested so the user doesn't have to re-enter
        hotel_vdb.save_pinecone_api_key_to_env(request.api_key, request.index_name)
        raise HTTPException(status_code=400, detail=message)

@app.get("/pinecone/status")
def get_pinecone_status():
    """Returns Pinecone connection status and settings."""
    return {
        "is_connected": hotel_vdb.is_pinecone_connected,
        "index_name": hotel_vdb.pinecone_index_name,
        "error": hotel_vdb.pinecone_error,
        "api_key_configured": bool(settings.PINECONE_API_KEY and settings.PINECONE_API_KEY.strip()),
        "total_vectors": len(hotel_vdb.documents)
    }

@app.get("/vector-db/status")
def get_vector_db_status():
    """Returns vector database status and index statistics."""
    return {
        "status": "Operational",
        "pinecone_connected": hotel_vdb.is_pinecone_connected,
        "active_engine": "Pinecone Cloud" if hotel_vdb.is_pinecone_connected else "In-Code Vector Engine (TF-IDF Cosine)",
        "index_name": hotel_vdb.pinecone_index_name,
        "total_vectors": len(hotel_vdb.documents),
        "vocabulary_size": len(hotel_vdb.vocabulary),
        "documents": hotel_vdb.documents
    }


