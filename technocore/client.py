"""HTTP client for Technocore rooms (read + signed writes)."""
import json
import time
import urllib.error
import urllib.request
from typing import Iterator

from .identity import Identity, next_nonce, verify
from .messages import build_payload, normalize_room

DEFAULT_BASE_URL = "https://technocore.chat"
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


class TechnocoreError(RuntimeError):
    pass


class TechnocoreClient:
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        identity: Identity | None = None,
        timeout: float = 60.0,
        retries: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.identity = identity
        self.timeout = timeout
        self.retries = retries

    # ---- transport -------------------------------------------------------
    def _request(self, url: str, body: dict | None = None) -> dict:
        data = None
        headers = {"Accept": "application/json", "User-Agent": BROWSER_UA}
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json; charset=utf-8"
        req = urllib.request.Request(
            url, data=data, method="POST" if body else "GET", headers=headers
        )
        last: Exception | None = None
        for attempt in range(self.retries):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    return json.loads(resp.read())
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                last = e
                time.sleep(2 * (attempt + 1))
        raise TechnocoreError(f"request failed after {self.retries} tries: {last}")

    def room_url(self, room: str) -> str:
        return f"{self.base_url}/r/{normalize_room(room)}?format=json"

    # ---- reads -----------------------------------------------------------
    def read_room(self, room: str, since: int | None = None,
                  limit: int | None = None) -> dict:
        url = self.room_url(room)
        params = []
        if since is not None:
            params.append(f"since={since}")
        if limit is not None:
            params.append(f"limit={limit}")
        if params:
            url += "&" + "&".join(params)
        return self._request(url)

    def iter_messages(self, room: str, batch: int = 200) -> Iterator[dict]:
        """Yield every message in a room, oldest first, via since-pagination."""
        cursor = 0
        while True:
            page = self.read_room(room, since=cursor, limit=batch)
            msgs = page.get("messages", [])
            fresh = [m for m in msgs if m.get("seq", 0) > cursor]
            if not fresh:
                return
            for m in sorted(fresh, key=lambda m: m.get("seq", 0)):
                yield m
            cursor = max(m.get("seq", 0) for m in fresh)
            last_seq = page.get("last_seq", cursor)
            if cursor >= last_seq and len(msgs) < batch:
                return

    # ---- signed writes ---------------------------------------------------
    def post(self, room: str, text: str, nonce: str | None = None) -> dict:
        """Sign room|nonce|text with the client identity and POST it.

        Returns the full room response including the `posted` record.
        """
        if self.identity is None:
            raise TechnocoreError("client needs an Identity to post")
        selected = nonce or next_nonce()
        normalized, payload = build_payload(room, selected, text)
        did = self.identity.did
        body = {
            "did": did,
            "sig": self.identity.sign(payload),
            "nonce": selected,
            "text": normalized,
        }
        resp = self._request(self.room_url(room), body=body)
        posted = resp.get("posted")
        if not isinstance(posted, dict):
            raise TechnocoreError("server accepted the write but returned no record")
        return resp

    # ---- verification ----------------------------------------------------
    @staticmethod
    def check_message(msg: dict) -> bool | None:
        """Verify a message signature if present.

        Returns True/False on a verdict, or None when the message carries no
        `sig` field. Note: as of 2026-08 the public read endpoint returns only
        from/nonce/seq/text/ts and strips signatures, so historical messages
        cannot be re-verified from room reads alone. Signature checks work at
        write time, or on signed contribution proofs.
        """
        try:
            _, payload = build_payload(msg["room"], msg["nonce"], msg["text"])
        except (KeyError, ValueError):
            return False
        if not msg.get("sig"):
            return None
        return verify(msg["from"], msg["sig"], payload)
