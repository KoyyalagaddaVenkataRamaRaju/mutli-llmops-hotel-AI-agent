from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from app.common.custom_exception import CustomException

# Constants as defined in StayEase specifications
LUXURY_TAX_RATE = 0.12  # 12% Luxury Tax
WEEKEND_SURCHARGE_RATE = 0.15  # 15% Weekend Surcharge
LONG_STAY_DISCOUNT_RATE = 0.10  # 10% Discount for stays >= 7 nights
PEAK_OCCUPANCY_THRESHOLD = 0.90  # 90% Occupancy threshold
PEAK_SURCHARGE_RATE = 0.20  # 20% Peak Surcharge

# 7-element array of weekday multipliers (Mon=1.0, Tue=1.0, Wed=1.0, Thu=1.0, Fri=1.10, Sat=1.15, Sun=1.15)
WEEKDAY_MULTIPLIERS = [1.0, 1.0, 1.0, 1.0, 1.10, 1.15, 1.15]


# ----------------- User-Defined Exceptions -----------------
class StayEaseException(CustomException):
    """Common parent exception for StayEase Hotel Management System."""
    def __init__(self, message: str, error_detail: Optional[Exception] = None):
        super().__init__(message, error_detail=error_detail)

class RoomNotAvailableException(StayEaseException):
    """Thrown when the chosen category has no free room for the dates."""
    def __init__(self, category: str):
        super().__init__(f"RoomNotAvailableException: No available rooms in category '{category}' at this time.")

class InvalidStayPeriodException(StayEaseException):
    """Thrown when check-out date is on or before check-in date."""
    def __init__(self, check_in: str, check_out: str):
        super().__init__(f"InvalidStayPeriodException: Check-out date ({check_out}) must be after check-in date ({check_in}).")

class PaymentPendingException(StayEaseException):
    """Thrown when check-out is attempted with an unpaid balance."""
    def __init__(self, booking_id: str, balance: float):
        super().__init__(f"PaymentPendingException: Check-out attempted with unpaid balance of ₹{balance:.2f} for booking {booking_id}.")

class BlacklistedGuestException(StayEaseException):
    """Thrown when a guest ID proof is in the blacklisted ID registry."""
    def __init__(self, id_proof: str):
        super().__init__(f"BlacklistedGuestException: ID proof '{id_proof}' is blacklisted by hotel security.")


# ----------------- Serviceable Interface / Protocol -----------------
class Serviceable(ABC):
    """Interface declaring room service capabilities."""
    
    @abstractmethod
    def add_service(self, name: str, cost: float) -> None:
        pass

    @abstractmethod
    def get_service_total(self) -> float:
        pass

    @abstractmethod
    def clear_services(self) -> None:
        pass


# ----------------- Room Class Hierarchy -----------------
class Room(ABC):
    """
    Abstract Room Class.
    Fields: room_number, floor, status ('Available', 'Occupied', 'Cleaning'), base_tariff.
    """
    def __init__(self, room_number: int, floor: int, status: str = "Available", base_tariff: float = 2500.0):
        self._room_number = room_number
        self._floor = floor
        self._status = status
        self._base_tariff = base_tariff

    @property
    def room_number(self) -> int:
        return self._room_number

    @property
    def floor(self) -> int:
        return self._floor

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, new_status: str):
        self._status = new_status

    @property
    def base_tariff(self) -> float:
        return self._base_tariff

    @abstractmethod
    def calculate_tariff(self, nights: int, has_weekend: bool = False, high_occupancy: bool = False) -> float:
        """Abstract method to calculate total tariff for the given nights with business rules."""
        pass

    @abstractmethod
    def describe(self) -> str:
        """Describe room features."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "room_number": self.room_number,
            "category": self.__class__.__name__.replace("Room", ""),
            "floor": self.floor,
            "tariff": self.base_tariff,
            "status": self.status,
            "description": self.describe()
        }

    def __str__(self) -> str:
        return f"Room {self.room_number} [{self.__class__.__name__}] Floor {self.floor} - {self.status}"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if isinstance(other, Room):
            return self.room_number == other.room_number
        return False

    def __hash__(self) -> int:
        return hash(self.room_number)


class StandardRoom(Room):
    """Standard Room with essential amenities."""
    def __init__(self, room_number: int, floor: int, status: str = "Available", base_tariff: float = 2500.0):
        super().__init__(room_number, floor, status, base_tariff)

    def calculate_tariff(self, nights: int, has_weekend: bool = False, high_occupancy: bool = False) -> float:
        rate = self.base_tariff
        if has_weekend:
            rate += self.base_tariff * WEEKEND_SURCHARGE_RATE
        if high_occupancy:
            rate += self.base_tariff * PEAK_SURCHARGE_RATE
        total = rate * nights
        if nights >= 7:
            total *= (1.0 - LONG_STAY_DISCOUNT_RATE)
        return round(total, 2)

    def describe(self) -> str:
        return "Cozy standard room with Queen bed, work desk, high-speed Wi-Fi, and en-suite bath."


class DeluxeRoom(Room, Serviceable):
    """
    Deluxe Room (extends Room and implements Serviceable).
    Adds private balcony and stocked minibar.
    """
    def __init__(
        self,
        room_number: int,
        floor: int,
        status: str = "Available",
        base_tariff: float = 4200.0,
        has_balcony: bool = True,
        has_minibar: bool = True
    ):
        super().__init__(room_number, floor, status, base_tariff)
        self.has_balcony = has_balcony
        self.has_minibar = has_minibar
        self._services: List[Dict[str, Any]] = []

    def calculate_tariff(self, nights: int, has_weekend: bool = False, high_occupancy: bool = False) -> float:
        rate = self.base_tariff
        if has_weekend:
            rate += self.base_tariff * WEEKEND_SURCHARGE_RATE
        if high_occupancy:
            rate += self.base_tariff * PEAK_SURCHARGE_RATE
        total = rate * nights
        if nights >= 7:
            total *= (1.0 - LONG_STAY_DISCOUNT_RATE)
        return round(total, 2)

    def describe(self) -> str:
        return "Deluxe room featuring king-size bedding, private scenic balcony, minibar & city view."

    # Serviceable implementation
    def add_service(self, name: str, cost: float) -> None:
        self._services.append({"name": name, "cost": cost})

    def get_service_total(self) -> float:
        return sum(s["cost"] for s in self._services)

    def clear_services(self) -> None:
        self._services.clear()


class Suite(DeluxeRoom):
    """
    Executive Luxury Suite (extends DeluxeRoom).
    Adds separate living area and 24/7 dedicated butler service.
    Declared final (should not be subclassed further).
    """
    def __init__(
        self,
        room_number: int,
        floor: int,
        status: str = "Available",
        base_tariff: float = 7800.0,
        has_living_area: bool = True,
        has_butler: bool = True
    ):
        super().__init__(room_number, floor, status, base_tariff, has_balcony=True, has_minibar=True)
        self.has_living_area = has_living_area
        self.has_butler = has_butler

    def calculate_tariff(self, nights: int, has_weekend: bool = False, high_occupancy: bool = False) -> float:
        # Calls parent tariff logic and adds luxury amenities premium
        base_calc = super().calculate_tariff(nights, has_weekend, high_occupancy)
        return round(base_calc, 2)

    def describe(self) -> str:
        return "Presidential Suite with expansive living area, private master bedroom, jacuzzi & 24/7 butler."


# ----------------- Guest Model -----------------
class Guest:
    """Guest model with overloaded constructor semantics."""
    def __init__(
        self,
        guest_id: str,
        name: str,
        phone: str = "",
        id_proof: str = "",
        address: str = ""
    ):
        self.guest_id = guest_id
        self.name = name
        self.phone = phone
        self.id_proof = id_proof
        self.address = address

    @classmethod
    def from_name(cls, guest_id: str, name: str) -> "Guest":
        return cls(guest_id=guest_id, name=name)

    @classmethod
    def from_contact(cls, guest_id: str, name: str, phone: str) -> "Guest":
        return cls(guest_id=guest_id, name=name, phone=phone)

    @classmethod
    def from_full_details(cls, guest_id: str, name: str, phone: str, id_proof: str, address: str) -> "Guest":
        return cls(guest_id=guest_id, name=name, phone=phone, id_proof=id_proof, address=address)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "guest_id": self.guest_id,
            "name": self.name,
            "phone": self.phone,
            "id_proof": self.id_proof,
            "address": self.address
        }

    def __str__(self) -> str:
        return f"Guest({self.guest_id}, {self.name}, {self.phone})"


# ----------------- Booking Model -----------------
class Booking:
    def __init__(
        self,
        booking_id: str,
        guest_id: str,
        room_number: int,
        check_in: str,
        check_out: str,
        nights: int,
        status: str = "Active",
        total_amount: float = 0.0,
        paid: float = 0.0
    ):
        self.booking_id = booking_id
        self.guest_id = guest_id
        self.room_number = room_number
        self.check_in = check_in
        self.check_out = check_out
        self.nights = nights
        self.status = status
        self.total_amount = total_amount
        self.paid = paid

    def to_dict(self) -> Dict[str, Any]:
        return {
            "booking_id": self.booking_id,
            "guest_id": self.guest_id,
            "room_number": self.room_number,
            "check_in": self.check_in,
            "check_out": self.check_out,
            "nights": self.nights,
            "status": self.status,
            "total_amount": self.total_amount,
            "paid": self.paid
        }


# ----------------- Service Order Model -----------------
class ServiceOrder:
    def __init__(
        self,
        service_id: str,
        booking_id: str,
        name: str,
        cost: float,
        timestamp: Optional[str] = None
    ):
        self.service_id = service_id
        self.booking_id = booking_id
        self.name = name
        self.cost = cost
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service_id": self.service_id,
            "booking_id": self.booking_id,
            "name": self.name,
            "cost": self.cost,
            "timestamp": self.timestamp
        }


# ----------------- Invoice Model -----------------
class Invoice:
    def __init__(
        self,
        invoice_id: str,
        booking_id: str,
        guest_name: str,
        room_number: int,
        room_category: str,
        nights: int,
        room_charges: float,
        service_charges: float,
        taxes: float,
        total_amount: float,
        created_at: Optional[str] = None
    ):
        self.invoice_id = invoice_id
        self.booking_id = booking_id
        self.guest_name = guest_name
        self.room_number = room_number
        self.room_category = room_category
        self.nights = nights
        self.room_charges = room_charges
        self.service_charges = service_charges
        self.taxes = taxes
        self.total_amount = total_amount
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def format_invoice_number(num: int) -> str:
        """Final method to format invoice code like INV-2026-0388."""
        return f"INV-2026-{num:04d}"

    def to_text_invoice(self) -> str:
        """Matches expected checkout invoice format from the PDF."""
        return (
            f"----- CHECK-OUT INVOICE -----\n"
            f"Invoice: {self.invoice_id}\n"
            f"Guest: {self.guest_name}\n"
            f"Room: {self.room_number} ({self.room_category})\n"
            f"Nights: {self.nights}\n"
            f"Room Charges: Rs. {self.room_charges:,.2f}\n"
            f"Services: Rs. {self.service_charges:,.2f}\n"
            f"Taxes: Rs. {self.taxes:,.2f}\n"
            f"Total: Rs. {self.total_amount:,.2f}\n"
            f"-----------------------------"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "invoice_id": self.invoice_id,
            "booking_id": self.booking_id,
            "guest_name": self.guest_name,
            "room_number": self.room_number,
            "room_category": self.room_category,
            "nights": self.nights,
            "room_charges": self.room_charges,
            "service_charges": self.service_charges,
            "taxes": self.taxes,
            "total_amount": self.total_amount,
            "created_at": self.created_at
        }

