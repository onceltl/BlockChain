import pickle
import crypto

def get_hash(data):
    if type(data) == bytes:
        return crypto.get_hash(data)
    else:
        return crypto.get_hash(pickle.dumps(data))

if __name__ == "__main__":
    pass