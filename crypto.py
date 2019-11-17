import base64
from cryptography.hazmat import backends
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


# Generate 256-bit private key.
def gen_key_private():
    key = ec.generate_private_key(ec.SECP256K1(), backends.default_backend())
    key_private = '{:0>64x}'.format(key.private_numbers().private_value)
    return key_private


# Generate 512-bit public key.
def gen_key_public(key_private):
    key = ec.derive_private_key(int(key_private, base=16), ec.SECP256K1(), backends.default_backend())
    key = key.public_key()
    key_public = '{:0>64x}{:0>64x}'.format(key.public_numbers().x, key.public_numbers().y)
    return key_public


# Generate address.
def gen_addr(key_public):
    hash_engine = hashes.Hash(hashes.SHA512(), backends.default_backend())
    hash_engine.update(int(key_public, base=16).to_bytes(64, byteorder='big'))
    key_hash = hash_engine.finalize()
    addr = base64.b64encode(key_hash).decode('utf-8')
    return addr


# Verify address.
def verify_addr(addr, key_public):
    try:
        addr_key = gen_addr(key_public)
    except Exception:
        return False
    return addr == addr_key


# Sign data.
def sign(data, key_private):
    key = ec.derive_private_key(int(key_private, base=16), ec.SECP256K1(), backends.default_backend())
    sig = base64.b64encode(key.sign(data, ec.ECDSA(hashes.SHA512()))).decode('utf-8')
    return sig


# Verify signature.
def verify_sig(data, sig, key_public):
    try:
        x = int(key_public[:64], base=16)
        y = int(key_public[64:], base=16)
        sig = base64.b64decode(sig)
        key = ec.EllipticCurvePublicNumbers(x, y, ec.SECP256K1()).public_key(backends.default_backend())
        key.verify(sig, data, ec.ECDSA(hashes.SHA512()))
        return True
    except Exception:
        return False


# Generate hash of data.
def get_hash(data):
    hash_engine = hashes.Hash(hashes.SHA512(), backends.default_backend())
    hash_engine.update(data)
    data_hash = hash_engine.finalize()
    hashed = '{:0>128x}'.format(int.from_bytes(data_hash, byteorder='big'))
    return hashed


if __name__ == "__main__":
    pass
