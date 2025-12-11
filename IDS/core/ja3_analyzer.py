import hashlib
from scapy.all import *
from scapy.layers.tls.all import *

class JA3Analyzer:
    def __init__(self):
        pass

    def process_packet(self, packet):
        """
        Extracts JA3 fingerprint from a TLS Client Hello packet.
        Returns: (ja3_hash, ja3_string) or None
        """
        if not packet.haslayer(TLSClientHello):
            return None

        try:
            client_hello = packet[TLSClientHello]
            
            # 1. SSL Version
            # Scapy stores version as int (e.g., 0x0303 for TLS 1.2)
            ssl_version = client_hello.version

            # 2. Cipher Suites
            # Scapy stores ciphers as a list of ints
            ciphers = client_hello.ciphers
            # JA3 requires removing GREASE values (0x?a?a)
            ciphers = [c for c in ciphers if not self._is_grease(c)]
            
            # 3. Extensions
            extensions = []
            curves = []
            point_formats = []
            
            if client_hello.ext:
                for ext in client_hello.ext:
                    extensions.append(ext.type)
                    
                    # Elliptic Curves (Supported Groups) - Type 10
                    if ext.type == 10:
                        curves = [g for g in ext.groups if not self._is_grease(g)]
                        
                    # Elliptic Curve Point Formats - Type 11
                    if ext.type == 11:
                        point_formats = ext.ecpl
            
            extensions = [e for e in extensions if not self._is_grease(e)]

            # Construct JA3 String
            # SSLVersion,Ciphers,Extensions,EllipticCurves,EllipticCurvePointFormats
            ja3_string = f"{ssl_version},"
            ja3_string += "-".join(map(str, ciphers)) + ","
            ja3_string += "-".join(map(str, extensions)) + ","
            ja3_string += "-".join(map(str, curves)) + ","
            ja3_string += "-".join(map(str, point_formats))

            # Calculate MD5
            ja3_hash = hashlib.md5(ja3_string.encode()).hexdigest()
            
            return ja3_hash, ja3_string

        except Exception as e:
            # print(f"JA3 Error: {e}")
            return None

    def _is_grease(self, val):
        """Checks if a value is a GREASE value (Reserved for testing)."""
        # GREASE values are of the form 0x?a?a
        if isinstance(val, int):
            return (val & 0x0f0f) == 0x0a0a
        return False
