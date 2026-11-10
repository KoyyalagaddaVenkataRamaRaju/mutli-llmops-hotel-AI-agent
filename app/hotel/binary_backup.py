import os
import struct
from typing import List, Dict, Any, Tuple

BACKUP_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "invoices.dat"))

class ByteStreamBackupManager:
    """
    Handles true byte-level binary serialization and deserialization for invoices.dat.
    Uses Python binary byte streams (wb / rb) and binary packing to guarantee byte integrity.
    """
    MAGIC_HEADER = b"STAYEASE_BIN_V1"

    @classmethod
    def backup_to_binary(cls, invoices: List[Dict[str, Any]], file_path: str = BACKUP_FILE_PATH) -> Tuple[int, int]:
        """
        Exports invoice records to a binary file using FileOutputStream equivalent (open(..., 'wb')).
        Returns (records_written, bytes_written).
        """
        raw_bytes = bytearray()
        raw_bytes.extend(cls.MAGIC_HEADER)
        raw_bytes.extend(struct.pack(">I", len(invoices)))

        for inv in invoices:
            inv_id_b = inv["invoice_id"].encode("utf-8")
            booking_id_b = inv["booking_id"].encode("utf-8")
            guest_b = inv["guest_name"].encode("utf-8")
            cat_b = inv["room_category"].encode("utf-8")
            date_b = inv.get("created_at", "").encode("utf-8")

            chunk = struct.pack(
                ">H", len(inv_id_b)
            ) + inv_id_b + struct.pack(
                ">H", len(booking_id_b)
            ) + booking_id_b + struct.pack(
                ">H", len(guest_b)
            ) + guest_b + struct.pack(
                ">III", inv["room_number"], inv["nights"], len(cat_b)
            ) + cat_b + struct.pack(
                ">ddddH",
                float(inv["room_charges"]),
                float(inv["service_charges"]),
                float(inv["taxes"]),
                float(inv["total_amount"]),
                len(date_b)
            ) + date_b

            raw_bytes.extend(chunk)

        with open(file_path, "wb") as f:
            f.write(raw_bytes)

        return len(invoices), len(raw_bytes)

    @classmethod
    def restore_from_binary(cls, file_path: str = BACKUP_FILE_PATH) -> Tuple[List[Dict[str, Any]], int]:
        """
        Reloads invoices from binary file using FileInputStream equivalent (open(..., 'rb')).
        Returns (restored_invoices, bytes_read).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Binary backup file not found at {file_path}")

        with open(file_path, "rb") as f:
            data = f.read()

        total_bytes = len(data)
        if not data.startswith(cls.MAGIC_HEADER):
            raise ValueError("Invalid binary format: missing StayEase magic header")

        offset = len(cls.MAGIC_HEADER)
        record_count, = struct.unpack_from(">I", data, offset)
        offset += 4

        restored: List[Dict[str, Any]] = []
        for _ in range(record_count):
            inv_id_len, = struct.unpack_from(">H", data, offset)
            offset += 2
            inv_id = data[offset:offset+inv_id_len].decode("utf-8")
            offset += inv_id_len

            bid_len, = struct.unpack_from(">H", data, offset)
            offset += 2
            bid = data[offset:offset+bid_len].decode("utf-8")
            offset += bid_len

            guest_len, = struct.unpack_from(">H", data, offset)
            offset += 2
            guest_name = data[offset:offset+guest_len].decode("utf-8")
            offset += guest_len

            room_no, nights, cat_len = struct.unpack_from(">III", data, offset)
            offset += 12
            category = data[offset:offset+cat_len].decode("utf-8")
            offset += cat_len

            charges, srv, tax, total, date_len = struct.unpack_from(">ddddH", data, offset)
            offset += 34
            created_at = data[offset:offset+date_len].decode("utf-8")
            offset += date_len

            restored.append({
                "invoice_id": inv_id,
                "booking_id": bid,
                "guest_name": guest_name,
                "room_number": room_no,
                "room_category": category,
                "nights": nights,
                "room_charges": charges,
                "service_charges": srv,
                "taxes": tax,
                "total_amount": total,
                "created_at": created_at
            })

        return restored, total_bytes

