
import struct

def _rotr(x, n):
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF

def _ch(x, y, z):
    return (x & y) ^ (~x & z)

def _maj(x, y, z):
    return (x & y) ^ (x & z) ^ (y & z)

def _big_sigma0(x):
    return _rotr(x, 2) ^ _rotr(x, 13) ^ _rotr(x, 22)

def _big_sigma1(x):
    return _rotr(x, 6) ^ _rotr(x, 11) ^ _rotr(x, 25)

def _small_sigma0(x):
    return _rotr(x, 7) ^ _rotr(x, 18) ^ (x >> 3)

def _small_sigma1(x):
    return _rotr(x, 17) ^ _rotr(x, 19) ^ (x >> 10)

K = [
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
]

def sha256_bytes(message_bytes: bytes) -> bytes:
    # Initial hash values (first 32 bits of fractional parts of the square roots of the first 8 primes)
    H = [
        0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
        0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19
    ]

    ml = len(message_bytes) * 8  # message length in bits

    # Padding
    padded = message_bytes + b'\x80'
    while (len(padded) + 8) % 64 != 0:
        padded += b'\x00'
    padded += struct.pack('>Q', ml)

    # Process each 512-bit chunk
    for chunk_start in range(0, len(padded), 64):
        chunk = padded[chunk_start:chunk_start+64]
        w = list(struct.unpack('>16I', chunk)) + [0]*48
        for t in range(16, 64):
            s0 = _small_sigma0(w[t-15]) & 0xFFFFFFFF
            s1 = _small_sigma1(w[t-2]) & 0xFFFFFFFF
            w[t] = (w[t-16] + s0 + w[t-7] + s1) & 0xFFFFFFFF

        a,b,c,d,e,f,g,h = H

        for t in range(64):
            T1 = (h + _big_sigma1(e) + _ch(e,f,g) + K[t] + w[t]) & 0xFFFFFFFF
            T2 = (_big_sigma0(a) + _maj(a,b,c)) & 0xFFFFFFFF
            h = g
            g = f
            f = e
            e = (d + T1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (T1 + T2) & 0xFFFFFFFF

        H = [
            (H[0]+a) & 0xFFFFFFFF,
            (H[1]+b) & 0xFFFFFFFF,
            (H[2]+c) & 0xFFFFFFFF,
            (H[3]+d) & 0xFFFFFFFF,
            (H[4]+e) & 0xFFFFFFFF,
            (H[5]+f) & 0xFFFFFFFF,
            (H[6]+g) & 0xFFFFFFFF,
            (H[7]+h) & 0xFFFFFFFF
        ]

    return b''.join(struct.pack('>I', part) for part in H)

def sha256_hex(message_bytes: bytes) -> str:
    return sha256_bytes(message_bytes).hex()

# Optional self-test if run directly
if __name__ == "__main__":
    tests = [
        (b"", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        (b"abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
    ]
    for inp, expect in tests:
        out = sha256_hex(inp)
        print(f"input={inp!r} out={out} ok={out==expect}")
