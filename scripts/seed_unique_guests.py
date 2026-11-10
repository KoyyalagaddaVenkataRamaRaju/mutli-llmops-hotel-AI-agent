import sqlite3

conn = sqlite3.connect('hotel.db')
cursor = conn.cursor()

# Get all currently occupied rooms
cursor.execute("SELECT room_number FROM rooms WHERE status = 'Occupied' ORDER BY room_number")
occ_rooms = [r[0] for r in cursor.fetchall()]
print(f"Occupied rooms count: {len(occ_rooms)}: {occ_rooms}")

sample_guests = [
    ('G101', 'Ananya Roy', '9834567891', 'AADHAAR-8901-2345', 'Kolkata, WB'),
    ('G102', 'Vikram Malhotra', '9945123476', 'DL-KA01-2018-87', 'Bengaluru, KA'),
    ('G103', 'Sophie Laurent', '9765432109', 'PASSPORT-FR78901', 'Paris, France'),
    ('G104', 'Farhan Ahmed', '9876543210', 'PASSPORT-A12903', 'Bangalore, KA'),
    ('G105', 'Priya Sharma', '9823412345', 'AADHAAR-2341-5678', 'Mumbai, MH'),
    ('G106', 'Rama Raju', '8978239929', 'AADHAAR-9395-3078', 'Hyderabad, TS'),
    ('G107', 'Rahul Verma', '9123456780', 'VOTER-DL-9876', 'New Delhi, DL'),
    ('G108', 'Sneha Patel', '9898123456', 'AADHAAR-4567-8901', 'Ahmedabad, GJ'),
    ('G109', 'Arjun Mehta', '9811223344', 'PASSPORT-IN8821', 'Pune, MH'),
    ('G110', 'Kavita Nair', '9845012345', 'AADHAAR-5678-1234', 'Kochi, KL'),
    ('G111', 'David Miller', '9712398450', 'PASSPORT-US89211', 'New York, USA'),
    ('G112', 'Michael Chang', '9756123987', 'PASSPORT-SG9012', 'Singapore'),
    ('G113', 'Aditi Rao', '9812345670', 'AADHAAR-1234-9876', 'Chennai, TN'),
    ('G114', 'Carlos Silva', '9723456781', 'PASSPORT-BR4401', 'Sao Paulo, Brazil'),
    ('G115', 'Rohan Deshmukh', '9832109874', 'DL-MH12-2021-09', 'Nagpur, MH'),
]

for i, rm in enumerate(occ_rooms):
    g_info = sample_guests[i % len(sample_guests)]
    gid, gname, gphone, gidproof, gaddr = g_info
    
    cursor.execute("INSERT OR REPLACE INTO guests VALUES (?, ?, ?, ?, ?)", (gid, gname, gphone, gidproof, gaddr))
    
    bid = f"BK-2026-OCC-{rm}"
    nights = 2 + (rm % 4)
    cursor.execute("SELECT tariff FROM rooms WHERE room_number = ?", (rm,))
    tariff = cursor.fetchone()[0]
    total_rent = tariff * nights
    
    cursor.execute("DELETE FROM bookings WHERE room_number = ? AND status = 'Active'", (rm,))
    cursor.execute(
        "INSERT INTO bookings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (bid, gid, rm, "2026-11-08", "2026-11-12", nights, "Active", total_rent, 0.0)
    )
    
    cursor.execute("DELETE FROM services WHERE booking_id = ?", (bid,))
    if i % 3 == 0:
        cursor.execute("INSERT INTO services VALUES (?, ?, ?, ?, ?)",
                       (f"SRV-{rm}-1", bid, "Hyderabadi Dum Biryani Feast", 650.0, "2026-11-09 13:30:00"))
    elif i % 3 == 1:
        cursor.execute("INSERT INTO services VALUES (?, ?, ?, ?, ?)",
                       (f"SRV-{rm}-1", bid, "Royal Breakfast Buffet Platter", 450.0, "2026-11-09 08:45:00"))
    else:
        cursor.execute("INSERT INTO services VALUES (?, ?, ?, ?, ?)",
                       (f"SRV-{rm}-1", bid, "Gourmet Cappuccino & Pastry", 300.0, "2026-11-09 16:15:00"))

conn.commit()
conn.close()
print("Successfully assigned distinct unique customers to all occupied rooms!")

