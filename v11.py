import struct
import hashlib

class NexusV11_UDPFrame:
    """V11 PRO - Raw Binary UDP Frame - 100% Real"""
    MAGIC = 0xFA
    HEADER_FMT = "!B I H"  # ! = Network Byte Order (Big Endian) - Bug Fix
    HEADER_SIZE = struct.calcsize(HEADER_FMT)  # 7 bytes fixed

    def build_frame(self, msg_id: int, payload: str) -> bytes:
        payload_bytes = payload.encode('utf-8')
        if len(payload_bytes) > 65535:
            raise ValueError("Payload too big for UDP (max 65KB)")
        
        # ! = Network order, B=1, I=4, H=2 => 7 bytes
        header = struct.pack(self.HEADER_FMT, self.MAGIC, msg_id, len(payload_bytes))
        
        # Checksum for corruption check
        checksum = hashlib.md5(payload_bytes).digest()[:2]  # 2 bytes
        
        frame = header + checksum + payload_bytes
        print(f"[v11] Built: MAGIC=0x{self.MAGIC:02X} ID={msg_id} Len={len(payload_bytes)} Total={len(frame)}B | HTTP hota to 200B+")
        return frame

    def parse_frame(self, frame: bytes) -> dict:
        if len(frame) < self.HEADER_SIZE + 2:
            raise ValueError("Frame too short")
        
        magic, msg_id, length = struct.unpack(self.HEADER_FMT, frame[:self.HEADER_SIZE])
        
        if magic != self.MAGIC:
            raise ValueError(f"Bad Magic: 0x{magic:02X}")
        
        checksum = frame[self.HEADER_SIZE:self.HEADER_SIZE+2]
        payload_bytes = frame[self.HEADER_SIZE+2:]
        
        if len(payload_bytes) != length:
            raise ValueError(f"Length mismatch: {len(payload_bytes)} vs {length}")
        
        # Verify checksum
        real_checksum = hashlib.md5(payload_bytes).digest()[:2]
        if checksum != real_checksum:
            raise ValueError("Checksum FAIL - Corrupted packet")
        
        payload = payload_bytes.decode('utf-8')
        print(f"[v11] Parsed: ID={msg_id} Payload='{payload}' Checksum OK")
        return {"msg_id": msg_id, "payload": payload}

# ========== REAL TEST ==========
v11 = NexusV11_UDPFrame()
print("--- TERA V11 vs MERA V11.1 ---")

# Tera wala
print(f"Tera header size: {struct.calcsize('B I H')} bytes (system dependent - BUG)")

# Mera wala
print(f"Mera header size: {v11.HEADER_SIZE} bytes (fixed - Network order)")

print("\n--- BUILD + PARSE VERIFY ---")
frame = v11.build_frame(777, "Order Placed")
print(f"Raw bytes: {frame[:20]}...")
print(f"HTTP hota to: ~250 bytes | Mera frame: {len(frame)} bytes | Saved: {250 - len(frame)} bytes ({(1-len(frame)/250)*100:.0f}%)")
parsed = v11.parse_frame(frame)

# Corruption test
print("\n--- Corruption Test ---")
corrupted = frame[:-1] + b'X'
try:
    v11.parse_frame(corrupted)
except Exception as e:
    print(f"Corruption detected correctly: {e}")
