# Whisper Runtimes — User Guide (for users)

This guide explains how to **use** Whisper runtimes in the app: viewing, creating, editing, deleting, and how they behave during transcription (defaults, lazy loading, batching). It is **not** about internal database tables or code.

---

## What’s a runtime?
A **Whisper runtime** is a saved preset that tells the system:
- which model to use (e.g., large-v3, large-v3-turbo, small.en, or a local/HF path)
- where to run it (CPU or GPU)
- precision/compute type
- optional batching settings

You pick a runtime when you transcribe, or let the app pick the default.

---

## Where to manage them
**Admin → Whisper Runtimes** shows a list. Each row has:
- **Status**: unloaded, downloading, loading, loaded, failed, or cancelled
- **Loaded** badge when the model is in memory
- Quick actions (Prepare, Load, Cancel, Unload, Set Default, Edit, Delete)

Click a row to view full details.

---

## Creating a runtime (step-by-step)
1) **New Runtime**
2) Fill in:
    - **Name**: unique friendly label (e.g., v3-turbo-gpu)
    - **Model**: Select a model from the dropdown
    - **Device**: `auto` (recommended), `cuda` (GPU), or `cpu`
    - **Device Index** If device is set to GPU select the GPU you would like to use, can select more than one for sharding.
    - **Compute Type**: `auto` (recommended). Typically float16 on GPU, int8 on CPU
    - **CPU Threads / Workers**: leave defaults unless you know you need to tune
    - **Batched**: enable only if you plan to process many files concurrently; set a **Batch Size** (>0)
    - **Enabled**: leave on unless you’re just drafting
    - **Default**: check if this should become the app’s default runtime
3) **Save**
    - If **Enabled**, the app will prepare files when needed and load the runtime on first use (lazy load). Progress shows as **downloading → loading → loaded**.

**Good defaults**: `Device = auto`, `Compute = auto`, leave Device Index empty. Choose a model that fits your GPU memory.

---

## The default runtime (how it works)
- There is **exactly one** default at any time.
- The default is used whenever a transcription doesn’t explicitly name a runtime and no profile runtime is set.
- The default is usually kept ready and loaded at startup.
- You **cannot unload or delete** the current default. To replace it, set another runtime as default first.

**Set as default**: open a runtime → **Set Default** (or toggle in Edit). The app marks it as default and starts loading it in the background.

---

## Lazy loading & auto-unload
- **Lazy loading**: enabled non-default runtimes are loaded only when first used.
- **Auto-unload**: non-default runtimes automatically unload after being idle for a while (e.g., ~15 minutes), freeing memory.
- Running transcriptions hold a **lease**, so the runtime won’t unload mid-job.

You generally don’t need to micromanage this.

---

## Common actions on a runtime
- **Prepare (download)**: pre-fetch model weights so first use is fast.
- **Load**: force loading now (useful before a big batch).
- **Cancel Load**: stop an in-progress load.
- **Unload**: free memory (not allowed for the current default unless you switch defaults).
- **Set Default**: make this the fallback runtime.
- **Enable / Disable**: disabled runtimes won’t be used; if loaded, they’ll be unloaded.

If something fails, the row shows a human-friendly error and a suggested fix (e.g., GPU out of memory, CUDA not available, disk full).

---

## Editing a runtime
Open a runtime → **Edit**:
- Changing **model, device, compute type, batching, enabled** will trigger a reload the next time it’s used (or immediately if it’s already loaded).
- Renaming only changes the label.
- Toggling **Enabled → off** unloads it if it’s loaded.

---

## Deleting a runtime
- You can delete any **non-default, non-protected** runtime.
- If it’s loaded, the app unloads it first, then deletes.
- You **cannot** delete the current default — pick a new default first.

---

## Using runtimes in transcription

### How the app chooses a runtime for a request
Order of precedence:
1) **Explicit runtime** you selected by **name** (or id) in the request/job
2) **Profile runtime** (if your user/profile specifies one)
3) **Default runtime**

If the chosen runtime isn’t prepared yet, you’ll see **downloading** progress, then **loading**, then the job runs.

### Options you can choose per job
- **Task**: `transcribe` (same language) or `translate` (to English)
- **Timestamps**: `segment` (default) or `word` (more detailed)
- **Response format**: simple text/JSON or verbose JSON (includes segments and optional words)
- **Clip ranges**: transcribe parts of the audio only (e.g., `0:30-1:45; 2:00-2:15`)

### Streaming
If you choose streaming output, you’ll receive **per-segment** (or **per-word**) events and a final `transcription.completed` summary.

While a job is running, the runtime is leased and won’t be auto-unloaded.

---

## Status badges you’ll see
- **unloaded**: preset exists but not in memory
- **downloading**: fetching/verifying model files (shows a %)
- **loading**: initializing on CPU/GPU
- **loaded**: ready to use
- **failed**: something went wrong (open for details)
- **cancelled**: a download/load was cancelled

---

## Tips & recommendations
- **Model choice**:
    - `large-v3-turbo` or `large-v3` for highest quality (needs a capable GPU)
    - `small.en` or `base.en` for CPU-friendly/lightweight usage
- **GPU**: keep `Device = auto`; it will prefer CUDA if available.
- **Precision**: `Compute = auto` → float16 on GPU, int8 on CPU.
- **Batching**: enable only if you’re submitting many files concurrently and you want higher throughput.
- **Multiple GPUs**: set Device Index to `[0,1]` (for example) to use both.

---

## Troubleshooting (quick fixes)

**Got an HTML page saying Redirecting… when calling an API URL?**  
You’re not authenticated. Use the UI, or add your auth to API requests.

**GPU out of memory**  
Use a smaller model, free GPU memory, or switch to CPU with int8 (`Device=cpu, Compute=int8`).

**CUDA not available**  
Update/install NVIDIA driver/CUDA, or switch Device to CPU.

**Disk full or permission denied**  
Free space and ensure the model/cache directories are writable.

**Stuck downloading**  
Click **Cancel**, then **Prepare** again; or try a different model.

---

## Quick start checklist
1) Create a runtime with `Device=auto` and `Compute=auto` using a sensible model for your hardware.
2) Mark it **Default** if you want it loaded all the time, and for it to be used when a request specifies no model.
3) (Optional) Click **Prepare** to pre-download weights, this should be automatic when creating a new runtime.
4) Start a transcription — the runtime will load on demand.
5) Add additional runtimes for special cases (CPU-only, batched pipeline, alternative models).

---
