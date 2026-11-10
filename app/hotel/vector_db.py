import os
import math
import re
from typing import List, Dict, Any, Tuple, Optional
from dotenv import load_dotenv, set_key

from app.config.settings import settings
from app.common.logger import get_logger

logger = get_logger(__name__)

ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

from app.hotel.chunker import HierarchicalSemanticChunker


# ----------------- Hybrid Vector Database -----------------
class HotelVectorDatabase:
    """
    Hybrid Vector Knowledge Database for StayEase Hotel Apex Residency.
    - Cloud Vector DB: Pinecone Integration (Serverless Vector Search)
    - In-Code Fallback: Normalized TF-IDF Vector Space with Cosine Similarity
    - Chunking: Hierarchical Semantic Windowing with Overlap
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(HotelVectorDatabase, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.documents: List[Dict[str, Any]] = []
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.doc_vectors: List[List[float]] = []

        # Pinecone Cloud properties
        self.pinecone_client = None
        self.pinecone_index = None
        self.is_pinecone_connected = False
        self.pinecone_error: Optional[str] = None
        self.pinecone_index_name = settings.PINECONE_INDEX_NAME or "stayease-hotel-apex"

        self._load_and_chunk_hotel_knowledge()
        self._build_index()

        # Connect to Pinecone if API key present
        if settings.PINECONE_API_KEY and settings.PINECONE_API_KEY.strip():
            self.connect_pinecone(settings.PINECONE_API_KEY, self.pinecone_index_name)

        self._initialized = True
        logger.info("HotelVectorDatabase initialized with %d semantic knowledge chunks.", len(self.documents))

    def _load_and_chunk_hotel_knowledge(self):
        """Loads and applies semantic hierarchical chunking across all 5 operational roles."""
        knowledge_corpus = [
            # 1. RECEPTIONIST ROLE
            {
                "id": "KB-REC-01",
                "role": "Receptionist",
                "category": "Front Desk Check-In",
                "title": "Guest Check-In & Room Allotment Protocol",
                "text": "Front Desk staff must greet guests with StayEase hospitality standard. Request official photo ID (Passport, Aadhaar, or Driving License). Validate against security blacklist database before room assignment. Allot room atomically through StayEase PMS to avoid double booking. Standard check-in begins at 14:00 (2:00 PM). Early check-in from 10:00 AM is complimentary for Suites and ₹1,000 for Standard/Deluxe if vacant. Explain keycard usage, Wi-Fi password, and breakfast timings."
            },
            {
                "id": "KB-REC-02",
                "role": "Receptionist",
                "category": "Front Desk Departure",
                "title": "Guest Departure & Folio Settlement",
                "text": "Standard check-out is strictly 11:00 AM. Inquire about minibar and recent room dining usage. Generate itemized check-out invoice including room tariff, weekend surcharge (+15% for Sat/Sun stays), 12% Luxury Tax, and all room service chits. Confirm full balance payment before marking folio closed. Upon checkout, room automatically transitions to 'Cleaning' status and is routed to the Housekeeping Queue."
            },

            # 2. GENERAL MANAGER ROLE
            {
                "id": "KB-MGR-01",
                "role": "General Manager",
                "category": "Operations & Yield Management",
                "title": "Peak Surcharge & Dynamic Yield Management",
                "text": "General Manager oversees all 60 room allocations across Floors 1 to 3. When occupancy exceeds 90% (more than 54 rooms occupied), PMS automatically activates the 20% Peak Surcharge to maximize revenue. Stays of 7 nights or longer qualify for a 10% Long Stay Discount on base tariff. General Manager conducts daily staff alignment at 08:30 and audits occupancy percentages twice per shift."
            },
            {
                "id": "KB-MGR-02",
                "role": "General Manager",
                "category": "Staff Supervision",
                "title": "Housekeeping Staff Allotment & Quality Inspection",
                "text": "Manager assigns dedicated staff (e.g., Housekeeper Ramesh, Sunita, or Supervisor Anita) to specific floors and cleaning queues. Rooms in Cleaning status cannot be allotted until marked inspected. If a VIP guest is arriving, Manager flags room for Executive Inspection with complementary fruit basket and welcoming card."
            },

            # 3. HOTEL OWNER & INVESTOR ROLE
            {
                "id": "KB-OWN-01",
                "role": "Hotel Owner",
                "category": "Financial Analytics",
                "title": "Executive Financial Metrics: ADR & RevPAR",
                "text": "Hotel Owner evaluates Average Daily Rate (ADR = Total Room Revenue / Rooms Sold) and Revenue Per Available Room (RevPAR = Total Room Revenue / 60 Total Inventory). Monthly revenue targets mandate maintaining RevPAR above ₹2,800. Owner reviews gross revenue, food & beverage sales, and luxury tax remittances through the Ledger Audit panel."
            },
            {
                "id": "KB-OWN-02",
                "role": "Hotel Owner",
                "category": "Data Governance",
                "title": "Binary Data Integrity & invoices.dat Compliance",
                "text": "Per hotel corporate audit standards, all guest folios and closed invoices must be backed up to the binary byte-stream file invoices.dat using FileOutputStream equivalent serialization. Restoration verification confirms 100% record count match against SQLite hotel.db database with zero byte discrepancy."
            },

            # 4. HOUSEKEEPING & MAINTENANCE STAFF ROLE
            {
                "id": "KB-HK-01",
                "role": "Housekeeping Staff",
                "category": "Housekeeping SOP",
                "title": "Room Sanitization & Turnaround Workflow",
                "text": "Housekeeping staff operates on a strict 20-30 minute turnaround per checkout room. Process: Strip all bed linens and towels; disinfect bathroom fixtures, door handles, remotes, and switches; replenish toiletries, tea kits, and minibar; vacuum carpets; and make bed with fresh hotel linen. Mark room 'Cleaned' in StayEase to release room back to Available status for the Front Desk."
            },
            {
                "id": "KB-MNT-01",
                "role": "Staff",
                "category": "Engineering Maintenance",
                "title": "Room Maintenance Ticketing & Repair Protocol",
                "text": "Engineering staff handles urgent room repairs: Air Conditioning (AC), Plumbing, Electrical, and Furniture. Housekeeping or Front Desk logs an electronic maintenance ticket (category, room number, description). Maintenance SLA is 15 minutes for occupied rooms and 45 minutes for vacant rooms. Upon resolution, technician marks ticket 'Resolved' in PMS."
            },

            # 5. GUEST SUPPORT & CONCIERGE ROLE
            {
                "id": "KB-CON-01",
                "role": "Support",
                "category": "Dining & Room Services",
                "title": "Dining Services & Amenity Pricing Catalog",
                "text": "Breakfast Buffet is served in The Grand Atrium from 07:00 to 10:30 (₹450). Royal Buffet Dinner is available from 19:30 to 23:00 (₹950). Express Laundry delivers pressed clothes in 4 hours (₹350). Luxury Ayurvedic Spa treatments (60 mins) operate from 08:00 to 21:00 (₹2,200). Premium Minibar Restock is ₹800. Room service orders are posted instantly to active booking folios."
            },
            {
                "id": "KB-CON-02",
                "role": "Support",
                "category": "Concierge & Policies",
                "title": "Airport Chauffeur, Pet Rules & Smoke-Free Policy",
                "text": "Hotel Apex Residency provides private luxury Mercedes chauffeur transfers to Kempegowda Airport (BLR) for ₹1,500 (approx 45-60 min travel). The property is 100% smoke-free indoors with designated garden cabanas. Pets under 15 kg are permitted in Ground Floor Garden Suites with advance booking notice."
            }
        ]

        # Apply Hierarchical Semantic Window Chunking with Overlap
        self.documents = []
        for item in knowledge_corpus:
            chunks = HierarchicalSemanticChunker.chunk_document(
                doc_id=item["id"],
                role=item["role"],
                category=item["category"],
                title=item["title"],
                raw_text=item["text"],
                window_size_words=110,
                overlap_words=20
            )
            self.documents.extend(chunks)

    # ----------------- Pinecone Connection & Sync -----------------
    def connect_pinecone(self, api_key: str, index_name: Optional[str] = None) -> Tuple[bool, str]:
        clean_key = api_key.strip() if api_key else ""
        if not clean_key:
            self.is_pinecone_connected = False
            self.pinecone_error = "Pinecone API key is empty."
            return False, self.pinecone_error

        chosen_index = (index_name or self.pinecone_index_name or "stayease-hotel-apex").strip().lower()

        try:
            from pinecone import Pinecone, ServerlessSpec
            logger.info("Connecting to Pinecone with index: %s", chosen_index)
            self.pinecone_client = Pinecone(api_key=clean_key)

            existing_indexes = [idx.name for idx in self.pinecone_client.list_indexes()]
            dim = len(self.vocabulary) if self.vocabulary else 128

            if chosen_index in existing_indexes:
                try:
                    desc = self.pinecone_client.describe_index(chosen_index)
                    if desc.dimension != dim:
                        logger.info("Recreating Pinecone index %s due to dimension change (%d -> %d)", chosen_index, desc.dimension, dim)
                        self.pinecone_client.delete_index(chosen_index)
                        existing_indexes.remove(chosen_index)
                except Exception as desc_err:
                    logger.warning("Could not check Pinecone index description: %s", desc_err)

            if chosen_index not in existing_indexes:
                logger.info("Creating serverless Pinecone index: %s (dim=%d)", chosen_index, dim)
                try:
                    self.pinecone_client.create_index(
                        name=chosen_index,
                        dimension=dim,
                        metric="cosine",
                        spec=ServerlessSpec(cloud="aws", region="us-east-1")
                    )
                except Exception as create_err:
                    logger.warning("Could not create Pinecone index: %s", create_err)

            self.pinecone_index = self.pinecone_client.Index(chosen_index)
            self.pinecone_index_name = chosen_index
            self.is_pinecone_connected = True
            self.pinecone_error = None
            logger.info("Successfully connected to Pinecone index: %s", chosen_index)

            self.sync_vectors_to_pinecone()
            return True, f"Successfully connected to Pinecone index '{chosen_index}'!"

        except Exception as e:
            self.is_pinecone_connected = False
            self.pinecone_error = str(e)
            logger.error("Pinecone connection error: %s", e)
            return False, f"Pinecone connection failed: {str(e)}"

    def sync_vectors_to_pinecone(self) -> int:
        if not self.is_pinecone_connected or not self.pinecone_index:
            return 0

        try:
            records = []
            for idx, doc in enumerate(self.documents):
                vec = self.doc_vectors[idx]
                records.append({
                    "id": doc["id"],
                    "values": vec,
                    "metadata": {
                        "title": doc["title"],
                        "role": doc.get("role", "General"),
                        "category": doc["category"],
                        "content": doc["content"]
                    }
                })

            self.pinecone_index.upsert(vectors=records)
            logger.info("Synced %d semantic chunks to Pinecone index %s", len(records), self.pinecone_index_name)
            return len(records)
        except Exception as e:
            logger.error("Error upserting vectors to Pinecone: %s", e)
            return 0

    def save_pinecone_api_key_to_env(self, api_key: str, index_name: str = "stayease-hotel-apex") -> bool:
        try:
            clean_key = api_key.strip()
            clean_index = index_name.strip()
            settings.PINECONE_API_KEY = clean_key
            settings.PINECONE_INDEX_NAME = clean_index
            set_key(ENV_FILE_PATH, "PINECONE_API_KEY", clean_key)
            set_key(ENV_FILE_PATH, "PINECONE_INDEX_NAME", clean_index)
            load_dotenv(ENV_FILE_PATH, override=True)
            logger.info("Stored Pinecone configuration to .env file at %s", ENV_FILE_PATH)
            return True
        except Exception as e:
            logger.error("Failed to update .env with Pinecone key: %s", e)
            return False

    # ----------------- In-Code TF-IDF Vector Space -----------------
    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\b[a-zA-Z0-9]{2,}\b", text.lower())

    def _build_index(self):
        doc_tokens = [self._tokenize(d["content"]) for d in self.documents]
        N = len(self.documents)

        df: Dict[str, int] = {}
        for tokens in doc_tokens:
            unique_terms = set(tokens)
            for t in unique_terms:
                df[t] = df.get(t, 0) + 1

        self.vocabulary = {term: idx for idx, term in enumerate(sorted(df.keys()))}
        self.idf = {term: math.log((N + 1) / (df[term] + 1)) + 1.0 for term in df}

        self.doc_vectors = []
        for tokens in doc_tokens:
            vec = [0.0] * len(self.vocabulary)
            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            for t, count in tf.items():
                if t in self.vocabulary:
                    vec[self.vocabulary[t]] = (count / len(tokens)) * self.idf[t]
            norm = math.sqrt(sum(v * v for v in vec))
            if norm > 0:
                vec = [v / norm for v in vec]
            self.doc_vectors.append(vec)

    def vectorize_query(self, query: str) -> List[float]:
        tokens = self._tokenize(query)
        vec = [0.0] * len(self.vocabulary)
        if not tokens:
            return vec
        tf: Dict[str, int] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        for t, count in tf.items():
            if t in self.vocabulary:
                vec[self.vocabulary[t]] = (count / len(tokens)) * self.idf.get(t, 1.0)
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    # ----------------- Semantic Search -----------------
    def search(self, query: str, top_k: int = 3, role_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Searches knowledge vectors using Cosine Similarity.
        Supports role filtering (e.g. 'Receptionist', 'Manager', 'Owner', 'Housekeeping', 'Support').
        """
        # Try Pinecone query if connected
        if self.is_pinecone_connected and self.pinecone_index:
            try:
                q_vec = self.vectorize_query(query)
                filter_dict = {"role": {"$eq": role_filter}} if role_filter else None
                res = self.pinecone_index.query(vector=q_vec, top_k=top_k, include_metadata=True, filter=filter_dict)
                results = []
                for match in res.get("matches", []):
                    meta = match.get("metadata", {})
                    results.append({
                        "document": {
                            "id": match["id"],
                            "title": meta.get("title", ""),
                            "role": meta.get("role", "General"),
                            "category": meta.get("category", ""),
                            "content": meta.get("content", "")
                        },
                        "score": round(match.get("score", 0.0), 4),
                        "source": "Pinecone Cloud Index"
                    })
                if results:
                    return results
            except Exception as e:
                logger.warning("Pinecone query fallback: %s", e)

        # In-code Cosine Similarity Search
        q_vec = self.vectorize_query(query)
        if not any(q_vec):
            return [{"document": d, "score": 0.1, "source": "In-Code Engine"} for d in self.documents[:top_k]]

        scores: List[Tuple[int, float]] = []
        for idx, d_vec in enumerate(self.doc_vectors):
            doc = self.documents[idx]
            if role_filter and doc.get("role", "").lower() != role_filter.lower():
                continue
            dot = sum(q * d for q, d in zip(q_vec, d_vec))
            scores.append((idx, dot))

        scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in scores[:top_k]:
            results.append({
                "document": self.documents[idx],
                "score": round(score, 4),
                "source": "In-Code TF-IDF Cosine Vector"
            })
        return results
