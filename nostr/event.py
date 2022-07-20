import time
import json
from enum import IntEnum
from secp256k1 import PrivateKey, PublicKey
from hashlib import sha256

class EventKind(IntEnum):
    SET_METADATA = 0
    TEXT_NOTE = 1
    RECOMMEND_RELAY = 2

class Event():
    def __init__(
            self, 
            public_key: str, 
            content: str, 
            created_at: int=int(time.time()), 
            kind: int=EventKind.TEXT_NOTE, 
            tags: "list[list[str]]"=[], 
            id: int=None, 
            signature: str=None) -> None:
        self.id = id if id != None else sha256(Event.serialize(public_key, created_at, kind, tags, content)).hexdigest()
        self.public_key = public_key
        self.content = content
        self.created_at = created_at
        self.kind = kind
        self.tags = tags
        self.signature = signature

    @staticmethod
    def serialize(public_key: str, created_at: int, kind: int, tags: "list[list[str]]", content: str) -> bytes:
        data = [0, public_key, created_at, kind, tags, content]
        data_str = json.dumps(data, separators=(',', ':'))
        return data_str.encode()

    def sign(self, sk: str) -> None:
        private_key = PrivateKey(bytes.fromhex(sk))
        sig = private_key.schnorr_sign(bytes.fromhex(self.id), None, raw=True)
        self.signature = sig.hex()

    def verify(self) -> bool:
        pub_key = PublicKey(bytes.fromhex("02" + self.public_key), True) # add 02 for schnorr (bip340)
        return pub_key.schnorr_verify(bytes.fromhex(self.id), bytes.fromhex(self.signature), None, raw=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "pubkey": self.public_key,
            "created_at": self.created_at,
            "kind": self.kind,
            "tags": self.tags,
            "content": self.content,
            "sig": self.signature
        }