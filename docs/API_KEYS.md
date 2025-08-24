# API Keys — User Guide

This guide shows how to **view, create, update, rotate, revoke, and delete API keys** in the app, and how to **use** them with your requests.

---

## What an API key is (and how it’s checked)

An API key is a secret token you include in requests (OpenAI-style) via `Authorization: Bearer sk_...`. The server:

- Looks up your key by its **prefix**, then verifies the full secret using a secure HMAC.
- Enforces the key’s **lifecycle and policy**:
    - `enabled` / `revoked` / `expires_at`
    - **IP allowlist** (specific IPs or CIDR ranges)
    - **Scopes** (e.g., `transcribe:read`, `transcribe:write`, `realtime:connect`)
    - **Model/Runtime access** via allow/deny patterns (e.g., `default`, `cpu-*`, `large-*`, or numeric runtime ids)
    - Optional **per-minute rate limit**
- Attaches the key to the request context and logs usage.
- When your request specifies a **runtime** (by `runtime_id` or `runtime name`) or a **model** (OpenAI’s `model` field), access is checked against your allow/deny rules.

You will see only the **prefix** of each key in the UI; the **full secret is shown once** on creation or rotation.

---

## Where to manage API keys

**Dashboard → API Keys** shows your keys. You can:
- Search by label or prefix
- Toggle `Show archived`
- Create a new key
- Edit, enable/disable, archive/unarchive, **revoke**, **rotate**, or **delete permanently**

Each card shows:
- **Label** and **prefix**
- Status badge: Enabled / Disabled / Revoked / Archived
- Scopes as chips
- Created / Expires / Last used timestamps

---

## Creating a key (step-by-step)

1) Click **New Key**.
2) Fill in:
    - **Label**: friendly name (e.g., `CI server`, `Staging`, `Mobile app`)
    - **Scopes**: comma-separated (default is `transcribe:read, transcribe:write`)
    - **Model allowlist** (optional): comma-separated names/ids/globs (e.g., `default, cpu-*, 2,3`)
    - **Model denylist** (optional): comma-separated (e.g., `large-*, 5`). **Denylist wins** if both set.
    - **IP allowlist** (optional): comma-separated IPs or CIDR (e.g., `127.0.0.1, 10.0.0.0/8`)
    - **Rate limit / min** (optional): integer
    - **Daily hard limit** (optional): integer
    - **Expires at** (optional): date/time; leave empty for no expiry
3) Click **Create**.
4) The **full secret** is revealed **once**. **Copy it now**; after closing the modal you cannot view it again.

**Tip:** Keep allowlists/denylists simple at first. You can refine later.

---

## Using your key in requests

Include the header:

```http
Authorization: Bearer sk_live_your-secret-here
```

Typical OpenAI-style endpoints in this app accept `runtime_id`, `runtime` (name), or `model`. Access checks use your key’s allow/deny patterns:

- If you pass `runtime_id`, that named runtime is checked.
- If you pass `runtime` (by name), that runtime is checked.
- If you pass `model` only, the server tries to resolve it to a single enabled runtime; otherwise, it treats it as a model id/slug and checks patterns against that.

If a route requires a runtime but none resolves, the server returns `RUNTIME_NOT_FOUND`. If your key isn’t allowed to use the requested runtime/model, it returns `MODEL_FORBIDDEN`.

---

## Editing a key

Open a key → **Edit**. You can change:

- **Label**
- **Scopes** (comma-separated)
- **Model allowlist / denylist** (comma-separated names/ids/globs; e.g., `default, cpu-*`)
- **IP allowlist** (comma-separated IPs/CIDRs)
- **Rate limit / min**, **Daily hard limit**, **Expires at**
- **Enabled** (toggle)
- **Revoked** (toggle)

Click **Save** to apply.

**Behavior notes**
- **Enable/Disable**: disabled keys are rejected even if not revoked.
- **Revoked**: a revoked key is rejected. You can uncheck Revoked in Edit to restore, but best practice is to rotate instead of un-revoking if the secret leaked.
- **Expires at**: once past the timestamp, requests are rejected.

---

## Rotating a key (replace the secret)

Use **Rotate Secret** (inside **Edit**). Rotation:

- Generates a **new secret** for the same key record (new HMAC; **prefix may change**).
- **Immediately invalidates** the old secret.
- Shows the **new full secret once** — copy it right away.

Use rotation when a secret might be exposed, or as a periodic hygiene practice.

---

## Revoking a key (stop it now)

Use **Revoke…** from the card menu (or toggle `Revoked` in Edit). Revocation:

- Immediately blocks further use of the secret.
- Keeps the record for audit/history.
- You can create a new key or rotate another key for replacement.

---

## Archiving (hide from default views)

Use **Archive** / **Unarchive** from the card menu (or `Show archived` to display them). Archiving:

- Does **not** change enabled/revoked status.
- Simply hides keys from default lists to reduce clutter.

---

## Deleting a key permanently

Use **Delete permanently…**. Notes:

- You may be asked to **revoke/disable first** if it’s still active.
- If the key has usage records, deletion can require an extra confirmation (or `?force=1` via API).
- This action removes the key and may purge associated usage (subject to confirmation). **Cannot be undone.**

---

## Common errors and fixes

- `UNAUTHORIZED: Missing API key` → Add `Authorization: Bearer ...` header.
- `UNAUTHORIZED: Unknown/Bad API key` → Typo or wrong secret. Rotate and retry.
- `FORBIDDEN: Key disabled or revoked` → Re-enable or un-revoke (or create a new key).
- `FORBIDDEN: Key expired` → Extend `Expires at` or create a new key.
- `FORBIDDEN: IP not allowed` → Add your client IP/CIDR to the key’s IP allowlist.
- `INSUFFICIENT_SCOPE` → Add the required scope (e.g., `transcribe:write`) to the key.
- `MODEL_FORBIDDEN` → Adjust model/runtime allow/deny patterns or pick an allowed runtime.
- `RATE_LIMIT: Too many requests` → Reduce QPS, increase the key’s per-minute limit, or shard across keys.

---

## Best practices

- **Least privilege**: give keys only the scopes they need.
- **Segment**: separate keys per environment (CI, staging, production).
- **IP allowlist** when possible.
- **Rotate** regularly and on any incident.
- **Archive** old/rarely used keys; **delete** when truly done.

---

## Quick start checklist

1) Create a key with the scopes you need (`transcribe:read, transcribe:write`) and optional IP allowlist.
2) Copy the secret immediately.
3) Use it via `Authorization: Bearer ...`.
4) If you need to lock usage to certain models/runtimes, fill `model_allowlist` (and optionally `model_denylist`).
5) Rotate secrets periodically; revoke and replace on incidents.
6) Archive or delete keys you no longer need.

---
