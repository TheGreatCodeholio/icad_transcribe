### GPU passthrough with Docker (CUDA)

If you have an NVIDIA GPU, you can let the container use it for major speedups. The quick path:

1) Install the **NVIDIA driver** on the host (your normal OS packages).
2) Install the **NVIDIA Container Toolkit** (so Docker can see the GPU).
3) Start the container with GPU access (Compose or docker run).
4) In iCAD Transcribe, set the runtime **Device = `cuda`** (or `auto`).

Official docs (reference):
- NVIDIA Container Toolkit install guide: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
- Docker CLI `--gpus` flag: https://docs.docker.com/reference/cli/docker/container/run/#gpus
- Compose Spec (services): https://compose-spec.io

#### 1) Install the NVIDIA Container Toolkit
Follow NVIDIA’s guide for your distro, then configure Docker’s runtime and restart Docker:

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

*(On older setups you may see guidance about `default-runtime` = `nvidia` in `/etc/docker/daemon.json`; the `nvidia-ctk` command above writes the needed config.)*

#### 2) Verify Docker can see your GPU
You should be able to run `nvidia-smi` inside a CUDA base image:

```bash
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

You should see your GPU(s) listed. If you don’t, recheck the toolkit installation and Docker config.

#### 3A) Start with Docker Compose (recommended)
Add `gpus` to your service:

```yaml
services:
  transcription:
    image: thegreatcodeholio/icad_transcribe:1.0
    # ... your existing config (ports, volumes, env_file, user, etc.)
    gpus: all           # expose all GPUs to this service
    # Or target a specific GPU:
    # gpus:
    #   - "device=0"
```

> If your Compose version complains about `gpus`, upgrade Docker Engine + Compose. As a fallback, use 3B with `docker run --gpus all`.

#### 3B) Start with plain `docker run`
Equivalent one-liner:

```bash
docker run -d --name icad_transcribe \
  --gpus all \
  -p 9912:9912 \
  -v "$(pwd)"/log:/srv/app/log \
  -v "$(pwd)"/var:/srv/app/var \
  --env-file .env \
  thegreatcodeholio/icad_transcribe:1.0
```

#### 4) Select CUDA inside iCAD Transcribe
In the web UI when you **create** or **edit** a runtime:
- Set **Device** to **`cuda`** (or **`auto`**).
- Save, then **Load** the runtime.

That’s it—new transcriptions will run on the GPU.

---

### Troubleshooting

- **`nvidia-smi` works on the host but not in the container**
  - Ensure the NVIDIA Container Toolkit is installed *and* Docker was configured/restarted:
    `sudo nvidia-ctk runtime configure --runtime=docker` → `sudo systemctl restart docker`
  - Docs: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

- **Compose doesn’t recognize the `gpus` field**
  - Upgrade Docker Engine/Compose to a recent release that supports `gpus` in `docker compose`.
  - Fallback: start the container with `docker run --gpus all` (CLI docs: https://docs.docker.com/reference/cli/docker/container/run/#gpus)

- **Multiple GPUs; pick one**
  - Compose: set `gpus:` to `- "device=0"` (or 1, 2, …).
  - CLI: `--gpus "device=0"`

- **Runtime still shows CPU**
  - Edit the runtime and confirm **Device = `cuda`** (or `auto`), then **Load** again.
  - Check container logs for CUDA/driver errors: `docker logs -f icad_transcribe`
