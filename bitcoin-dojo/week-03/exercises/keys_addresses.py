"""
Bitcoin Dojo - Week 3 Exercises: Keys, Addresses & Encoding
Code Orange Dev School | codeorange.dev

Based on Programming Bitcoin, Chapter 4
https://github.com/jimmysong/programmingbitcoin

Fill in the functions, then grade yourself (from the bitcoin-dojo folder):

    python3 week-03/check.py

The checks use real, public test vectors: BIP173's example key and the
answers to the book's exercises. Unfinished functions show up as
"not implemented yet", so you can go one at a time.

Provided (from lib/dojo.py - you built the curve math in Weeks 1-2):
    G                    the secp256k1 generator; secret * G is a public key Point
    point.x, point.y     coordinates (ints)
    sha256(b), hash256(b), hash160(b)
    bech32_segwit(hrp, version, program)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from dojo import G, Point, sha256, hash256, hash160, bech32_segwit  # noqa: E402,F401

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


# ---------------------------------------------------------------------------
# Exercise 1 - SEC format (serializing a public key)
#
#   uncompressed:  04 || x (32 bytes) || y (32 bytes)             65 bytes
#   compressed:    02 if y is even, 03 if odd || x (32 bytes)     33 bytes
#
# Numbers are big-endian: n.to_bytes(32, "big")
# ---------------------------------------------------------------------------
def sec(point: Point, compressed: bool = True) -> bytes:
    # YOUR CODE HERE
    if compressed:
        prefix = b"\x02" if point.y % 2 == 0 else b"\x03"
        return prefix + point.x.to_bytes(32, "big")
    return b"\x04" + point.x.to_bytes(32, "big") + point.y.to_bytes(32, "big")


# ---------------------------------------------------------------------------
# Exercise 2 - Base58
#
# Treat the bytes as one big number (int.from_bytes(b, "big")), repeatedly
# divmod by 58, and map each remainder to BASE58_ALPHABET (building the string
# from the right). Every leading 0x00 byte becomes a leading "1".
#
# Why not base64? No 0/O/I/l to confuse, and no +/ characters.
# ---------------------------------------------------------------------------
def encode_base58(b: bytes) -> str:
    # YOUR CODE HERE
    num = int.from_bytes(b, "big")
    result = ""
    alphabet = BASE58_ALPHABET
    while num > 0:
        num, remainder = divmod(num, 58)
        result = alphabet[remainder] + result
    return result


# ---------------------------------------------------------------------------
# Exercise 3 - Base58Check: append a 4-byte checksum, hash256(payload)[:4]
# ---------------------------------------------------------------------------
def encode_base58_check(payload: bytes) -> str:
    # YOUR CODE HERE
    hash = hash256(payload)[:4]
    return encode_base58(payload + hash)


# ---------------------------------------------------------------------------
# Exercise 4 - Decode Base58Check and verify the checksum
#
# Reverse Exercise 2: num = num * 58 + ALPHABET.index(c), convert back to bytes,
# restore one 0x00 per leading "1". Split off the last 4 bytes and raise
# ValueError if they don't equal hash256(payload)[:4]. Return the payload.
# ---------------------------------------------------------------------------
def decode_base58_check(s: str) -> bytes:
    # YOUR CODE HERE
    num = 0
    for c in s:
        if c not in BASE58_ALPHABET:
            raise ValueError(f"Invalid character {c} in Base58 string")
        num = num * 58 + BASE58_ALPHABET.index(c)
    
    # Convert the number back to bytes
    byte_length = (num.bit_length() + 7) // 8
    payload = num.to_bytes(byte_length, "big")
    
    # Verify the checksum
    if hash256(payload[:-4])[:4] != payload[-4:]:
        raise ValueError("Invalid checksum")
    
    return payload[:-4]


# ---------------------------------------------------------------------------
# Exercise 5 - P2PKH address:  base58check(version || hash160(sec))
#   version byte: 0x00 mainnet, 0x6f testnet
# ---------------------------------------------------------------------------
def p2pkh_address(sec_bytes: bytes, testnet: bool = False) -> str:
    # YOUR CODE HERE
    version_byte = b"\x6f" if testnet else b"\x00"
    sha_256_hash = sha256(sec_bytes)
    hash160_value = hash160(sha_256_hash)
    return encode_base58_check(version_byte + hash160_value)


# ---------------------------------------------------------------------------
# Exercise 6 - Native segwit (P2WPKH) address
#   bech32_segwit("bc" or "tb", 0, hash160(sec))
# Compare with Exercise 5: same hash160, different wrapper.
# ---------------------------------------------------------------------------
def p2wpkh_address(sec_bytes: bytes, testnet: bool = False) -> str:
    # YOUR CODE HERE
    hrp = "tb" if testnet else "bc"
    sha_256_hash = sha256(sec_bytes)
    hash160_value = hash160(sha_256_hash)
    return bech32_segwit(hrp, 0, hash160_value)


# ---------------------------------------------------------------------------
# Exercise 7 - WIF (Wallet Import Format) for a private key
#   base58check( 0x80 mainnet / 0xef testnet
#                || secret as 32 bytes big-endian
#                || 0x01 if the matching public key is compressed )
# ---------------------------------------------------------------------------
def wif(secret: int, compressed: bool = True, testnet: bool = False) -> str:
    # YOUR CODE HERE
    version_byte = b"\xef" if testnet else b"\x80"
    secret_bytes = secret.to_bytes(32, "big")
    if compressed:
        secret_bytes += b"\x01"
    return encode_base58_check(version_byte + secret_bytes)


# ---------------------------------------------------------------------------
# Discussion (bring to the call):
#  1. Walk the full path from a 256-bit secret to a bc1q... address. Why does
#     each step exist?
#  2. The same secret gives two different P2PKH addresses (compressed and
#     uncompressed). Why can that lose people money when they restore a wallet?
#  3. Why hash160 and not just sha256? What do we gain and give up with 20 bytes?
# ---------------------------------------------------------------------------
