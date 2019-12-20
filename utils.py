import pickle
import crypto

node_num = 5

def sign(data, key_private):
    if type(data) == bytes:
        return crypto.sign(data, key_private)
    else:
        return crypto.sign(pickle.dumps(data), key_private)


def verify_sig(data, sig, key_public):
    if type(data) == bytes:
        return crypto.verify_sig(data, sig, key_public)
    else:
        return crypto.verify_sig(pickle.dumps(data), sig, key_public)


def get_hash(data):
    if type(data) == bytes:
        return crypto.get_hash(data)
    else:
        return crypto.get_hash(pickle.dumps(data))


if __name__ == "__main__":
    pass
