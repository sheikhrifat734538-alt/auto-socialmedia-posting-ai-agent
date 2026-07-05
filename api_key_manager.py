"""
API Key Rotation Manager
=========================
Manages multiple Gemini API keys with:
- Sequential key selection (NOT round-robin)
- 24-hour cooldown for rate-limited (429) keys
- Persistent cooldown state via JSON file
- Smart skip of cooled-down keys to save time
"""

import os
import json
import time
from pathlib import Path

# --- Configuration ---
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_key_state.json")

# All available Gemini API keys (loaded from .env)
def _load_keys() -> list:
    """Load all GEMINI_API_KEY entries from .env or environment."""
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    keys = []
    # Primary key
    primary = os.getenv("GEMINI_API_KEY", "")
    if primary:
        keys.append(primary)
    
    # Additional keys from GEMINI_API_KEY_2, GEMINI_API_KEY_3, etc.
    i = 2
    while True:
        key = os.getenv(f"GEMINI_API_KEY_{i}", "")
        if not key:
            break
        keys.append(key)
        i += 1
    
    return keys


def _load_state() -> dict:
    """Load the cooldown state from disk."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"cooldowns": {}}


def _save_state(state: dict):
    """Persist the cooldown state to disk."""
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except IOError as e:
        print(f"[!] Could not save API key state: {e}")


def mark_key_exhausted(api_key: str):
    """
    Mark an API key as exhausted (rate-limited).
    It will be put on a 24-hour cooldown and will not be used until the cooldown expires.
    """
    state = _load_state()
    cooldown_until = time.time() + (24 * 60 * 60)  # 24 hours from now
    
    # Store only last 8 chars for readability in logs
    key_id = api_key[-8:]
    state["cooldowns"][api_key] = {
        "cooldown_until": cooldown_until,
        "key_id": f"...{key_id}",
        "reason": "429 rate limit exceeded"
    }
    _save_state(state)
    print(f"[⏸] API Key ...{key_id} put on 24-hour cooldown.")


def _is_key_on_cooldown(api_key: str, state: dict) -> bool:
    """Check if a key is currently on cooldown."""
    if api_key in state.get("cooldowns", {}):
        cooldown_info = state["cooldowns"][api_key]
        cooldown_until = cooldown_info.get("cooldown_until", 0)
        
        if time.time() < cooldown_until:
            # Still on cooldown
            remaining_hours = (cooldown_until - time.time()) / 3600
            return True
        else:
            # Cooldown expired — remove it
            del state["cooldowns"][api_key]
            _save_state(state)
            key_id = api_key[-8:]
            print(f"[✓] API Key ...{key_id} cooldown expired. Back in rotation.")
            return False
    return False


def get_active_key() -> str | None:
    """
    Get the next available API key that is NOT on cooldown.
    
    Strategy:
    - Go through keys sequentially (key 1, key 2, key 3, ...)
    - Skip any key that is on 24-hour cooldown
    - Return the first active key found
    - Return None if ALL keys are exhausted
    """
    keys = _load_keys()
    state = _load_state()
    
    if not keys:
        print("[-] No API keys configured in .env!")
        return None
    
    active_keys = []
    cooldown_keys = []
    
    for key in keys:
        if _is_key_on_cooldown(key, state):
            cooldown_info = state["cooldowns"].get(key, {})
            remaining = (cooldown_info.get("cooldown_until", 0) - time.time()) / 3600
            cooldown_keys.append((key[-8:], f"{remaining:.1f}h remaining"))
        else:
            active_keys.append(key)
    
    # Log status
    total = len(keys)
    active_count = len(active_keys)
    cooldown_count = len(cooldown_keys)
    
    print(f"[🔑] API Keys: {active_count}/{total} active, {cooldown_count}/{total} on cooldown")
    
    if cooldown_keys:
        for key_id, remaining in cooldown_keys:
            print(f"    ⏸ ...{key_id} — {remaining}")
    
    if active_keys:
        selected = active_keys[0]  # Always pick the first available
        print(f"    ✓ Using: ...{selected[-8:]}")
        return selected
    else:
        print("[✗] ALL API keys are on cooldown! No keys available.")
        
        # Find the soonest key to come back
        soonest_time = float('inf')
        soonest_key = None
        for key in keys:
            if key in state.get("cooldowns", {}):
                until = state["cooldowns"][key].get("cooldown_until", float('inf'))
                if until < soonest_time:
                    soonest_time = until
                    soonest_key = key
        
        if soonest_key:
            wait_hours = (soonest_time - time.time()) / 3600
            print(f"    ⏰ Next key available in {wait_hours:.1f} hours (...{soonest_key[-8:]})")
        
        return None


def get_all_status() -> dict:
    """Get a full status report of all keys for diagnostics."""
    keys = _load_keys()
    state = _load_state()
    
    report = {
        "total_keys": len(keys),
        "active": [],
        "on_cooldown": []
    }
    
    for i, key in enumerate(keys):
        key_info = {
            "index": i + 1,
            "key_id": f"...{key[-8:]}",
        }
        
        if _is_key_on_cooldown(key, state):
            cooldown_info = state["cooldowns"].get(key, {})
            remaining = (cooldown_info.get("cooldown_until", 0) - time.time()) / 3600
            key_info["status"] = "cooldown"
            key_info["remaining_hours"] = round(remaining, 1)
            report["on_cooldown"].append(key_info)
        else:
            key_info["status"] = "active"
            report["active"].append(key_info)
    
    return report


# --- Direct test ---
if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    
    print("=" * 50)
    print("  API Key Manager — Status Report")
    print("=" * 50)
    
    report = get_all_status()
    print(f"\nTotal Keys: {report['total_keys']}")
    print(f"Active:     {len(report['active'])}")
    print(f"Cooldown:   {len(report['on_cooldown'])}")
    
    print("\n--- Active Keys ---")
    for k in report['active']:
        print(f"  #{k['index']}: {k['key_id']} ✓")
    
    print("\n--- Cooldown Keys ---")
    for k in report['on_cooldown']:
        print(f"  #{k['index']}: {k['key_id']} ⏸ ({k['remaining_hours']}h left)")
    
    print("\n--- Attempting to get a key ---")
    key = get_active_key()
    if key:
        print(f"Got key: ...{key[-8:]}")
    else:
        print("No keys available!")
