import datetime
import logging
import os
from Crypto.PublicKey import RSA

MAX_DATA_SIZE = 64

n = 0xa337e14c4fa536382c3c290af8314a53d3be2025e1ad1343c2e017e9366f4e732007edc50eb280700ea877e2feace49a298c4f1734b93d4734bcb54b705848e458caaf24e6ce013d0db638a5c6c8c05675e452d868259c19710bbb7cdbe75f97ef4526e38a11a82ae4f33c2f1a37f672ed2ae6c12d8a06b722d3745abde383b1
e = 0x10001
pubkey = RSA.construct((n, e), )


class DB:
    def __init__(self, dir_name: str):
        os.makedirs(dir_name, exist_ok=True)
        self._dir_name = dir_name
        self._data = dict()
        self._load()

    def _load(self):
        try:
            for file_name in os.listdir(self._dir_name):
                full_name = os.path.join(self._dir_name, file_name)
                if os.path.isfile(full_name) and os.path.getsize(full_name) <= MAX_DATA_SIZE:
                    with open(full_name) as f:
                        data = f.read()
                    self._data[file_name] = data
            logging.info("Loaded %d items from %r", len(self._data), self._dir_name)
        except Exception:
            logging.exception("Error loading data from %r", self._dir_name)

    def put(self, key: str, value: str):
        with open(os.path.join(self._dir_name, key), "w") as f:
            f.write(value)
        self._data[key] = value

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()


def check_signature(flag_id: str, signature: str):
    try:
        time_str, signature = signature.split(":", maxsplit=1)
        time = datetime.datetime.strptime(time_str, "%Y%m%d%H%M%S")
        if (datetime.datetime.now() - time).total_seconds() > 10:
            logging.debug("Too old signature")
            return False
        signed_data = (flag_id + ":" + time_str).encode()
        return pubkey.verify(signed_data, (int(signature, 16),))
    except Exception as e:
        logging.debug("Bad signature: %s", e)
        return False
