# C — Bakeable State: Why Pre-Baking Recovers ~13 s of a 1,124 s Cold Start

**Subject:** DeepSeek-V4-Flash appliance, 2× RTX PRO 6000 Blackwell Workstation (97,887 MiB each), TP2/DCP1, vLLM derivative `0.26.1rc0+infernal.invocation.cu133.r21.vllmd6cf36a.b12xf6dc512`
**Run analysed:** the single cold start captured in the Codex transcript `rollout-2026-08-26T11-08-50-01a03ed4-…jsonl`, container started `2026-08-29T04:15:13.87Z`, ready `04:20:14.34Z`, first inference completed `04:21:58.01Z`.
**Method:** de-wrapped and time-ordered every container log line in the transcript; reconciled against the owner's measured phase table to sub-second accuracy; cross-checked mechanism claims against vLLM docs, the OCI image spec, NVIDIA's CUDA checkpoint API, and two 2026 papers (Foundry, "Breaking the Ice"). Live host/guest inspection was strictly read-only (`free`, `nvidia-smi`, `lspci`, `docker info`, `docker system df`).

---

## 0. Executive summary

1. **The bake worked exactly as well as it could.** The 91,125,760-byte warm `/cache` layer maps onto precisely three cacheable artifacts — the `torch.compile`/Inductor cache, the AOT-compiled function, and the FlashInfer autotune configs, plus a couple of TileLang cubins. Those account for **13.01 s guaranteed, ~17–21 s optimistically**. Everything else in the 1,124.49 s is either bytes-on-the-wire, bytes-through-a-decompressor, live GPU device state, or dead time.

2. **The owner's hypothesis is half right and the implied remedy is wrong.** Yes, an OCI image is nothing but a stack of tar archives and therefore cannot contain a running process. But a VM image would not have saved this either: the state you want is in **GPU HBM and NVIDIA driver context**, which a VM snapshot does not capture — and these GPUs are raw VFIO PCIe passthrough (guest `lspci` shows two real `10de:2bb1` devices), which is exactly the configuration QEMU **cannot** snapshot or live-migrate at all.

3. **CUDA graphs are genuinely, structurally unserialisable** — not an OCI limitation, a CUDA limitation. There is no `cudaGraphSave`/`cudaGraphLoad`. A captured graph has real 64-bit device addresses baked into kernel argument buffers and points at cubins lazily loaded into *this* context.

4. **But graphs are not where the time goes here.** Graph capture is 17.82 s (1.6% of total). `torch.compile` is 13.01 s (1.2%). Together **2.8%**. The premise of the question — that unextracted graphs are hiding a big win — is false for this appliance, which has already set `--max-cudagraph-capture-size 48` and captures only 17 graphs.

5. **I found ~168 s that nobody has looked at**, and its two largest components are a **~61 s CUDA-graph *memory profiling* dry-run** (which vLLM's own log tells you how to turn off, and which the docs confirm `--kv-cache-memory` skips) and a **~85 s JIT-warmup / dummy-forward block**.

6. **I also found 101.74 s of previously unaccounted wall clock** — the residual between the phase table (1,022.75 s) and the reported total (1,124.49 s). It is dead time between "ready" at `04:20:14.34` and the first request at `04:21:56.01`. That single gap is **3.3× larger than graph capture and torch.compile combined**.

7. **The actual highest-leverage lever is image extraction: 577.02 s = 51.3% of the total**, and it is spent gzip-inflating ~155 GB of model weights that did not need to be inside the image at all.

---

## 1. Reconciling the 1,124.49 s — and the 101.74 s nobody counted

The owner's phase table sums to less than the reported total. This matters, so first, the arithmetic:

| phase | seconds | % of 1,124.49 |
|---|---:|---:|
| contract → manifest | 21.11 | 1.88% |
| blob transfer (156.3 GB) | 116.06 | 10.32% |
| **image extraction** | **577.02** | **51.31%** |
| container create → start | 6.08 | 0.54% |
| container start → ready | 300.47 | 26.72% |
| first inference | 2.01 | 0.18% |
| **subtotal** | **1,022.75** | **90.95%** |
| **residual (unlabelled)** | **101.74** | **9.05%** |
| **total** | **1,124.49** | 100% |

The three sub-phases (60.83 + 24.71 + 198.77 = 284.31) are *children* of the 300.47 s, not additional line items — they leave 16.16 s from graph-capture-done to ready.

**The residual is real and I can date it.** The log shows:

```
2026-08-29T04:20:14.338370303Z (APIServer pid=1) INFO:     Application startup complete.
2026-08-29T04:21:56.005888143Z (APIServer pid=1) INFO:     172.17.0.1:42720 - "GET /health HTTP/1.1" 200 OK
2026-08-29T04:21:58.014514431Z (APIServer pid=1) INFO:     172.17.0.1:42736 - "POST /v1/chat/completions HTTP/1.1" 200 OK
```

`04:21:56.006 − 04:20:14.338 = 101.67 s` — matching the 101.74 s residual to within 0.07 s. The 2.009 s from health-200 to completions-200 is the reported "first inference 2.01".

**So 101.74 s of a 1,124 s cold start is the harness not asking.** This is orchestration dead time — a health-poll interval, or the test sequence doing something else. It is free to fix and it is 7.8× the size of the entire bake win.

### Anchor verification (why I trust the rest of this report)

Every phase boundary lands on a log line to within 0.01 s:

| boundary | log evidence | timestamp | Δ vs. reported |
|---|---|---|---|
| model load begins | `[model_runner.py:491] Loading model from scratch...` | `04:16:14.700138` | t0 = `04:15:13.870` ⇒ 60.83 ✔ |
| model load ends | `[model_runner.py:513] Model loading took 80.99 GiB and 25.141342 seconds` | `04:16:39.406236` | 24.706 s ⇒ **24.71 ✔** |
| graph capture done | `[model_runner.py:1371] Graph capturing finished in 18 secs, took 0.19 GiB` | `04:19:58.174993` | 198.769 s ⇒ **198.77 ✔** |
| ready | `INFO: Application startup complete.` | `04:20:14.338370` | 300.468 s ⇒ **300.47 ✔** |

The inferred container-start instant `04:15:13.870Z` is 1.42 s before the first stdout line (`DS4 launch: mode=dspark …` at `04:15:15.292`), which is the entrypoint wrapper's first write. That is a plausible `docker start` → first-write latency.

---

## 2. Decomposing the 300.47 s — the logs the owner has never seen

This is the core of the report. Every line below is quoted verbatim from the transcript with its Docker-attached RFC3339 timestamp. Where the runtime emitted a tqdm progress bar (no timestamp prefix, written to stderr), I give the bar's own elapsed time and bound the window by the surrounding timestamped lines.

### Phase A — container start → model load begins: **60.83 s**

| Δ (s) | window | what happened |
|---:|---|---|
| 1.42 | `04:15:13.87` → `04:15:15.29` | `docker start` → entrypoint first write |
| 6.87 | `04:15:15.29` → `04:15:22.16` | Python interpreter + `import torch` (first `torch/utils/_pytree.py` warning, pid 1) |
| 5.37 | `04:15:22.16` → `04:15:27.53` | `import vllm` → CLI banner |
| 9.36 | `04:15:27.53` → `04:15:36.89` | config load, quantization detect, architecture resolve |
| 9.17 | `04:15:36.89` → `04:15:46.06` | **second** architecture resolve — the speculative draft model |
| 8.95 | `04:15:46.06` → `04:15:55.01` | scheduler / compilation config |
| 9.12 | `04:15:55.01` → `04:16:04.13` | **EngineCore process fork + full re-`import torch`** |
| 8.34 | `04:16:04.13` → `04:16:12.47` | **two worker processes fork + full re-`import torch`** |
| 1.32 | `04:16:12.47` → `04:16:13.79` | NCCL / PyNCCL communicator init, `world_size=2` |
| 0.91 | `04:16:13.79` → `04:16:14.70` | attention backend selection, rank assignment |

Key lines:

```
04:15:15.292350601Z DS4 launch: mode=dspark depth=fixed capacity_activation=disabled backend=b12x-a8-dglin
                    allreduce=b12x b12x_dma=0 indexer=b12x tp=2 dcp=1 max_seqs=8 graph=48
                    load_format=instanttensor instanttensor_backend=BUFFERED native_l2=0
                    allocator=expandable_segments:True model=/models/ds4
04:15:15.292412082Z Process-group interfaces: GLOO_SOCKET_IFNAME=lo NCCL_SOCKET_IFNAME=lo
04:15:22.159517573Z W0829 04:15:22.158000 1 torch/utils/_pytree.py:630] <enum 'KernelPreference'> …
04:15:27.533222541Z (APIServer pid=1) INFO … version 0.26.1rc0+infernal.invocation.cu133.r21.vllmd6cf36a.b12xf6dc512
04:15:36.892116761Z (APIServer pid=1) INFO … [model.py:680] Resolved architecture: DeepseekV4ForCausalLM
04:15:46.057594271Z (APIServer pid=1) INFO … [model.py:680] Resolved architecture: DeepSeekV4MTPModel
04:15:55.816470502Z (APIServer pid=1) INFO … [compilation.py:329] Enabled custom fusions: norm_quant, act_quant, allreduce_rms
04:16:00.324680440Z W0829 04:16:00.324000 374 torch/utils/_pytree.py:630] …          ← EngineCore re-imports torch
04:16:04.127689469Z (EngineCore pid=374) INFO … [core.py:121] Initializing a V1 LLM engine …
04:16:04.127888442Z (EngineCore pid=374) INFO … [multiproc_executor.py:165] DP group leader: node_rank=0 … world_size=2, local_world_size=2
04:16:08.442369377Z W0829 04:16:08.441000 400 torch/utils/_pytree.py:630] …          ← Worker 0 re-imports torch
04:16:08.463813167Z W0829 04:16:08.463000 401 torch/utils/_pytree.py:630] …          ← Worker 1 re-imports torch
04:16:12.465506009Z (Worker pid=400) INFO … [parallel_state.py:1938] world_size=2 rank=0 local_rank=0
                    distributed_init_method=file:///tmp/vllm_dist_3a73081ec90944d98b811264454a2df2 backend=nccl
04:16:13.735531734Z (Worker pid=400) INFO … [cuda_communicator.py:274] Using ['B12X_PCIE_ONESHOT_DMA', 'PYNCCL']
                    all-reduce backends (in dispatch order) for group 'tp:0' …
04:16:14.700138655Z (Worker_TP0 pid=400) INFO … [model_runner.py:491] Loading model from scratch...
```

**Finding A1:** ~26.4 s of this 60.83 s is **`import torch` executed three times** — once in the API server (pid 1), once in EngineCore (pid 374), once per worker (pids 400/401, concurrently). This is process-model overhead, not work.

**Finding A2:** ~27.4 s is **config and architecture resolution done twice** — once for `DeepseekV4ForCausalLM` and again for `DeepSeekV4MTPModel` (the DSpark draft head). With `--trust-remote-code`, this executes model Python from the checkpoint.

**Finding A3: NCCL initialisation is 1.32 s.** It is not a problem here. That matters for §4: the frequently cited "NCCL re-init cost" objection to GPU checkpointing is ~1.3 s on this box, not tens of seconds.

### Phase B — model load: **24.71 s**

```
04:16:15.066611653Z (Worker_TP0 pid=400) INFO … [attention.py:1174] Using FP8 indexer cache for Lightning Indexer.
     Loading safetensors using InstantTensor loader:   0% Completed | 0.00/155G [00:00<?, ?B/s]
     Loading safetensors using InstantTensor loader:   9% Completed | 13.3G/155G [00:01<00:10, 14.3GB/s]
04:16:25.978049034Z (Worker_TP0 pid=400) INFO … [default_loader.py:497] Loading weights took 10.39 seconds
04:16:27.168785844Z (Worker_TP0 pid=400) WARNING … [b12x_moe.py:842] B12X MoE force-A8 enabled:
                    using quant_mode=w4a8_mx for E8M0 FP4 weights.
04:16:29.030068650Z (Worker_TP0 pid=400) WARNING … [vllm.py:2625] `torch.compile` is turned on, but the model
                    /models/ds4 does not support it. …
04:16:38.053880198Z (Worker_TP0 pid=400) INFO … [dspark.py:576] DSpark draft model loaded: 97 params
04:16:38.054104971Z (Worker_TP0 pid=400) INFO … [default_loader.py:497] Loading weights took 8.92 seconds
04:16:39.387966520Z (Worker_TP1 pid=401) INFO … [model_runner.py:513] Model loading took 80.99 GiB and 25.139530 seconds
04:16:39.406235644Z (Worker_TP0 pid=400) INFO … [model_runner.py:513] Model loading took 80.99 GiB and 25.141342 seconds
```

Analysed in §6.

### Phase C — load done → graph capture done: **198.77 s**

This is the block the owner asked about. Reported inside it: `torch_compile_seconds_reported: 13.01`, `graph_capture_seconds_reported: 18`. **198.77 − 18 − 13.01 = 167.76 s unexplained.** Here it is:

| Δ (s) | window | sub-phase | cacheable? |
|---:|---|---|---|
| 2.80 | `04:16:39.41` → `04:16:42.21` | post-load handoff, OMP thread config | no |
| 10.95 | `04:16:42.21` → `04:16:53.16` | **`torch.compile` / TorchInductor** (13.01 s self-reported) | **YES** |
| ~84.87 | `04:16:53.16` → `04:18:18.03` | **JIT kernel warmup + dummy/profile forward** (TileLang, CuTeDSL, DeepGEMM, B12X) | partly |
| ~16 | `04:18:18.03` → `~04:18:34` | pre-profiling setup | no |
| **~61** | `~04:18:34` → `04:19:35.39` | **CUDA-graph MEMORY PROFILING (a dry rehearsal of capture)** | no — but **skippable by config** |
| 0.74 | `04:19:35.39` → `04:19:36.13` | KV cache sizing / allocation | no |
| 4.22 | `04:19:36.13` → `04:19:40.35` | **FlashInfer autotune** | **YES** |
| **17.82** | `04:19:40.35` → `04:19:58.17` | **real CUDA graph capture** | no |

The verbatim evidence:

```
04:16:42.213106066Z (Worker_TP0 pid=400) INFO … [backends.py:1094] Using cache directory:
   /cache/jit/cu133-torch213-vllmd6cf36ae0d-b12xf6dc512eb1-lmcachee045d729bc/vllm/torch_compile_cache/618cceda8d/rank_0_0/backbone
   for vLLM's torch.compile
04:16:51.919373857Z (Worker_TP0 pid=400) INFO … [backends.py:393] Compiling a graph for compile range (1, 4096) takes 8.53 s
04:16:53.162197275Z (Worker_TP0 pid=400) INFO … [decorators.py:708] saved AOT compiled function to
   /cache/jit/…/vllm/torch_compile_cache/torch_aot_compile/1f0359061970579fedb51aa5cfac428d1ace9cdb373e196bc15e2ff25d8f4a56/rank_0_0/model
04:16:53.162219765Z (Worker_TP0 pid=400) INFO … [monitor.py:53] torch.compile took 13.01 s in total

04:17:16.215234909Z (Worker_TP0 pid=400) [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129):
                    TileLang begins to compile kernel `hc_head_fuse_tilelang` with `out_idx=None`
04:17:16.215268409Z (Worker_TP0 pid=400) [TileLang…] (kernel.py:137): TileLang completes to compile kernel `hc_head_fuse_tilelang`
04:17:28.137499203Z (Worker_TP0 pid=400) [TileLang…] (kernel.py:129): TileLang begins to compile kernel `mhc_post_tilelang` …
04:17:28.137620964Z (Worker_TP0 pid=400) [TileLang…] (kernel.py:137): TileLang completes to compile kernel `mhc_post_tilelang`
04:17:29.652230330Z (Worker_TP1 pid=401) [TileLang…] (same two kernels, rank 1)

04:17:40.483161756Z (EngineCore pid=374) INFO … [shm_broadcast.py:801] No available shared memory broadcast block
                    found in 60 seconds. This typically happens when some processes are hanging or doing some
                    time-consuming work (e.g. compilation, weight/kv cache quantization).
04:18:15.998000435Z (Worker_TP0 pid=400) INFO … [kernel_warmup.py:484] Deferring runtime-dependent kernel warmup
                    until KV cache initialization.
04:18:18.025183987Z (Worker_TP0 pid=400) INFO … [indexer.py:687] DSA indexer decode path: use_flattening=False
                    use_varlen=False (next_n=6, use_fp4_indexer_cache=False)
04:18:40.544468046Z (EngineCore pid=374) INFO … [shm_broadcast.py:801] No available shared memory broadcast block
                    found in 60 seconds. …
```

Then the profiling dry-run (tqdm, no Docker timestamps — bounded by `04:18:40.54` and `04:19:35.39`):

```
Profiling CUDA graph memory (PIECEWISE): 100%|██████████| 9/9 [00:23<00:00,  2.62s/it]
Profiling CUDA graph memory (FULL):      100%|██████████| 8/8 [00:29<00:00,  3.66s/it]
Capturing dspark CUDA graphs (FULL):     100%|██████████| 8/8 [00:09<00:00,  1.20s/it]
Capturing DFlash context-KV CUDA graphs (FULL): 100%|██████████| 9/9 [00:00<00:00, 374.18it/s]
```

`23 + 29 + 9 + 0 = 61 s`. Then:

```
04:19:35.388812016Z (Worker_TP0 pid=400) INFO … [model_runner.py:1314] Estimated MRV2 CUDA graph memory:
                    0.64 GiB total (0.31 GiB retained in the reusable pool)
04:19:35.389038769Z (Worker_TP0 pid=400) INFO … [gpu_worker.py:675] Available KV cache memory: 8.28 GiB
04:19:35.389042299Z (Worker_TP0 pid=400) INFO … [gpu_worker.py:690] CUDA graph memory profiling is enabled
                    (default since v0.21.0). The current --gpu-memory-utilization=0.9750 is equivalent to
                    --gpu-memory-utilization=0.9683 without CUDA graph memory profiling. To maintain the same
                    effective KV cache size as before, increase --gpu-memory-utilization to 0.9817.
                    To disable, set VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=0.
04:19:35.398034132Z (EngineCore pid=374) INFO … [kv_cache_utils.py:2215] GPU KV cache size: 1,249,001 tokens,
                    Maximum concurrency for 1,048,576 tokens per request: 1.19x
04:19:36.127049096Z (Worker_TP0 pid=400) INFO … [kernel_warmup.py:621] Using FlashInfer autotune cache file:
                    /cache/jit/…/flashinfer-autotune/e3471a61401a968fc5793042397fd506145b172053545ff502ec674af32ec793/autotune_configs.json
04:19:40.346364828Z (Worker_TP0 pid=400) INFO - autotuner.py:2264 - flashinfer.jit: [Autotuner]: Saved 6 configs
                    to /cache/jit/…/autotune_configs.json (6 new, 0 from previous config)
```

Then the *real* capture:

```
Capturing CUDA graphs (PIECEWISE): 100%|██████████| 9/9 [00:04<00:00,  1.85it/s]
Capturing CUDA graphs (FULL):      100%|██████████| 8/8 [00:11<00:00,  1.48s/it]
Capturing dspark CUDA graphs (FULL): …
04:19:58.174993201Z (Worker_TP1 pid=401) INFO … [model_runner.py:1371] Graph capturing finished in 18 secs, took 0.19 GiB
04:19:58.175046411Z (Worker_TP1 pid=401) INFO … [gpu_worker.py:844] CUDA graph pool memory: 0.19 GiB (actual),
                    0.64 GiB (estimated), difference: 0.45 GiB (244.2%).
04:19:58.175052621Z (Worker_TP1 pid=401) INFO … [gpu_worker.py:907] Free memory on device (93.83/95.01 GiB) on startup.
                    Desired GPU memory utilization is (0.975, 92.63 GiB). Actual usage is 82.69 GiB for consumed memory
                    (weights + non-torch), 1.66 GiB for peak activation, and 0.19 GiB for CUDAGraph memory.
                    Replace gpu_memory_utilization config with `--kv-cache-memory-bytes=8538253005` (7.95 GiB) to fit
                    into requested memory, or `--kv-cache-memory-bytes=9820551680` (9.15 GiB) to fully utilize gpu
                    memory. Current kv cache memory in use is 8.28 GiB.
```

### Phase D — graph capture done → ready: **16.16 s**

```
04:20:12.109057101Z (EngineCore pid=374) INFO … [core.py:349] init engine (profile, create kv cache, warmup model)
                    took 212.68 s (compilation: 13.01 s)
04:20:13.844531670Z (APIServer pid=1) INFO … [api_server.py:689] Starting vLLM server on http://0.0.0.0:8000
04:20:13.860468335Z (APIServer pid=1) INFO:     Started server process [1]
04:20:14.338370303Z (APIServer pid=1) INFO:     Application startup complete.
```

13.94 s of deferred runtime-dependent kernel warmup + engine finalisation, then 2.23 s of route registration, tool/reasoning parser setup and uvicorn startup.

### The single most quotable number in the whole investigation

```
init engine (profile, create kv cache, warmup model) took 212.68 s (compilation: 13.01 s)
```

`212.68 s` is measured from the instant the weights finished landing in VRAM (`04:20:12.109 − 212.68 = 04:16:39.43`, which is the `OMP_NUM_THREADS` warning immediately after `Model loading took …`). **The runtime is telling you, in one line, that compilation is 6.1% of engine init.** Everything the OCI layer can hold is inside that 6.1%.

### Answer to Q1: what is the other ~168 s?

- **~85 s: JIT kernel compilation and warm-up forward passes** (TileLang `hc_head_fuse_tilelang` / `mhc_post_tilelang`, plus `enable_cutedsl_warmup`, `enable_jit_warmup`, DeepGEMM/B12X kernels), interleaved with the memory-profiling dummy run. Only ~4 s of it is *visibly* TileLang compilation on the two ranks; the rest is unlogged. EngineCore's two 60-second `shm_broadcast` timeouts at `04:17:40` and `04:18:40` are the smoking gun that workers were busy and silent for two consecutive minutes.
- **~61 s: CUDA-graph memory profiling** — a complete dry rehearsal of graph capture (9 PIECEWISE + 8 FULL + 8 dspark + 9 DFlash shapes) whose *only* output is the number `0.64 GiB`, which then turned out to be wrong by 244% (`0.19 GiB actual`). **This is the largest single removable item inside the container.**
- **~16 s: indexer/pre-profiling setup.**
- **4.22 s: FlashInfer autotuning** (6 new configs — this run was cold for autotune too).
- **2.80 s: post-load handoff.**

---

## 3. Q2 — Every piece of "warm" state, classified

| State | (a) Where it physically lives | (b) Capturable in an OCI layer? | (c) Seconds in this run |
|---|---|---|---|
| **torch.compile / TorchInductor cache** (Dynamo-transformed bytecode, FX graphs, Inductor `.so`/`.cubin`) | Files on disk: `/cache/jit/cu133-torch213-vllmd6cf36ae0d-…/vllm/torch_compile_cache/618cceda8d/rank_0_0/backbone` | **YES.** vLLM docs: "the cache directory can be copied between machines or **baked into a container image**" | **13.01 s** (`monitor.py:53`); 10.95 s wall |
| **vLLM AOT compile artifact** | File: `…/torch_compile_cache/torch_aot_compile/<sha256>/rank_0_0/model` | **YES** | included in the 13.01 s |
| **Triton / TileLang / CuTeDSL / DeepGEMM JIT kernel cache** | Files under `/cache/jit/…` | **YES** (cubins are files) | ~2–4 s observed; unknown share of the ~85 s block |
| **FlashInfer autotune configs** | File: `…/flashinfer-autotune/<hash>/autotune_configs.json` | **YES** | **4.22 s** |
| **Tokenizer artifacts / HF config** | Files, already in the image | already baked | ~0 (the 27 s is CPU parsing + `trust_remote_code` execution, not I/O) |
| **KV-cache sizing decision** (peak activation, available bytes) | A *measurement*, not an artifact — but pinnable as a config value | **Indirectly YES** — bake `--kv-cache-memory-bytes=9820551680` into the image/env | **~61 s** of profiling, + part of the dummy run |
| **CPU page cache of weight files** | Guest kernel page cache (RAM) | **NO.** A layer puts bytes on *disk*. Nothing in the OCI format warms RAM. | governs whether Phase B is 24.71 s or ~90 s (§6) |
| **Model weights in VRAM** | GPU HBM, inside a CUDA context | **NO** | **24.71 s** (2 × 80.99 GiB) |
| **KV cache allocation** | GPU HBM, `cudaMalloc`'d at init | **NO** | 0.74 s allocation |
| **CUDA graphs** (`cudaGraph_t` / `cudaGraphExec_t`) | Driver-side objects in the CUDA context. Nodes embed **actual device pointers in kernel argument buffers** and **kernel function handles** resolved against cubins lazily loaded into this context. | **NO — and not into a VM snapshot either.** No CUDA API serialises them. | **17.82 s** |
| **CUDA graph memory pool** | GPU HBM (`0.19 GiB`) | **NO** | inside the 17.82 s |
| **NCCL communicators / topology** | Process memory + GPU memory + driver handles; `ncclUniqueId` is per-run; rendezvous via `file:///tmp/vllm_dist_<uuid>` | **NO** | **1.32 s** |
| **CUDA context, module/cubin load state, stream state** | NVIDIA driver kernel + user state | **NO** | part of the ~85 s block |
| **Python interpreter + `torch` import state** (3 process generations) | Process RSS | **NO** (a CRIU/VM snapshot *could*) | **~26 s** |

**Summary of column (c):** bakeable = **13.01 s certain**, **~17–21 s optimistic**. Non-bakeable = everything else.

### The size of the artifact is itself the proof

The captured warm layer is **91,125,760 bytes uncompressed (15,726,145 compressed)**. The GPU state you would need to skip Phase B and C is **80.99 GiB per GPU × 2 = 161.98 GiB**. The layer is **1/1,900th** the size. A 91 MB tarball is exactly the right size for "a handful of compiled kernels and a 6-entry JSON", and physically cannot contain a CUDA graph, a KV cache, or a weight tensor.

> **Verification item (not confirmed):** vLLM's compile cache is **per-rank** — the log shows `rank_0_0`. Rank 1 writes `rank_1_0`. If the baked layer captured only one rank's subtree, or if the cache hash differs between ranks, **rank 1 recompiles and the two ranks are barriered together, so you get zero benefit**. Worth checking that the layer contains both `rank_0_0` and `rank_1_0`. vLLM docs also recommend `VLLM_FORCE_AOT_LOAD=1` "to ensure cached artifacts are used rather than silently recompiling on cache misses."

---

## 4. Q3 — "Is the limitation that this isn't a VM image, just an OCI?"

Answering this in three layers, because the intuition is right but the conclusion doesn't follow.

### 4.1 What an OCI image actually is

An OCI image is a JSON manifest plus an ordered list of **tar archives**. The spec is unambiguous: layers use media types `application/vnd.oci.image.layer.v1.tar{,+gzip,+zstd}` and "Layer Changesets … MUST be packaged in tar archive." A layer expresses exactly three things: files added, files modified, and files deleted (via `.wh.` whiteout entries), with permissions, ownership, mtimes and xattrs.

There is no field, no media type, and no extension point for a process, a memory page, a file descriptor, or a device handle. **So: anything that exists as a file can be baked. Anything that exists only as live state cannot.** That part of the hypothesis is exactly correct, and it is precisely why the bake recovered the compile caches (files) and nothing else.

### 4.2 Why a VM image would not have helped either

A VM snapshot (QEMU `savevm`, or the live-migration state stream) captures guest RAM, vCPU register state, and the state of **emulated** devices. Two independent reasons that does not solve this problem:

1. **The expensive state is not in guest RAM.** The 80.99 GiB per GPU lives in HBM on the card, and the CUDA graphs live in the NVIDIA driver's per-context bookkeeping. Guest RAM contains pointers to those things, not the things.

2. **These GPUs cannot be snapshotted by QEMU at all.** Read-only inspection of the guest shows raw PCIe passthrough, not vGPU:

   ```
   06:00.0 VGA compatible controller [0300]: NVIDIA Corporation Device [10de:2bb1] (rev a1)
   07:00.0 Audio device [0403]: NVIDIA Corporation Device [10de:22e8] (rev a1)
   08:00.0 VGA compatible controller [0300]: NVIDIA Corporation Device [10de:2bb1] (rev a1)
   09:00.0 Audio device [0403]: NVIDIA Corporation Device [10de:22e8] (rev a1)
   NVRM version: NVIDIA UNIX Open Kernel Module for x86_64  610.43.02
   ```

   The guest owns the physical devices through VFIO. QEMU refuses to snapshot or live-migrate a VM with an assigned VFIO device unless the device implements the VFIO migration protocol — which NVIDIA ships for vGPU/GRID, not for a passed-through workstation card. So `virsh save` on this guest would fail, not produce a slow-but-working snapshot.

**Conclusion: "it's OCI, not a VM" is the right diagnosis of *why files-only*, but "make it a VM image" is not the remedy.** The remedy, if there is one, is at a different layer entirely.

### 4.3 What *does* capture GPU state: `cuda-checkpoint` + CRIU

The one mechanism that captures GPU device state is NVIDIA's CUDA checkpoint API, exposed as the `cuda-checkpoint` CLI and the `cuCheckpointProcess*` driver APIs.

**How it works** (per NVIDIA's own description): on suspend it "locks GPU APIs, completes submitted work, copies device memory to host RAM, and releases GPU resources" so that "the process no longer directly refers to any GPU hardware at the OS level." CRIU then dumps the (now GPU-free) process tree — including those host allocations — to disk. On restore, CRIU restores the CPU state and `cuda-checkpoint` "re-acquires GPUs, copies device memory back from host RAM to GPU, and restores CUDA objects." Device memory is "copied to the host, into allocations managed by the CUDA driver" — **not to files** — which is why host RAM ≥ GPU memory in use is a hard requirement.

**Documented constraints:**

| Constraint | Source | Status on this box |
|---|---|---|
| Linux, x86_64 (ARM from driver 595+) | cuda-checkpoint README | ✅ |
| Driver ≥ 550; **≥ 570 for CRIU 4.0+ integration**; ≥ 580 for GPU migration & container partial passthrough; **≥ 610 for `cuIpcGetMemHandle`-based CUDA IPC** | cuda-checkpoint README | ✅ **610.43.02** — the newest tier |
| No UVM managed memory | cuda-checkpoint README | needs audit (PyTorch normally doesn't use UVM) |
| No IPC memory from `cuMemExportToShareableHandle()` | cuda-checkpoint README | ⚠️ see below |
| No MIG, no MPS | CRIU GPU_Checkpointing | ✅ not in use |
| Restore requires "a system with similar GPUs and same GPU count … same chip type … enough memory" | CRIU GPU_Checkpointing | fine for a fixed appliance |
| Host RAM ≥ GPU memory used | vLLM RFC #34303 | ⚠️ guest has **251 GiB**, needs **162 GiB** — tight but feasible |
| CRIU ≥ 4.0 for disk persistence | vLLM RFC #34303 | ❌ neither `criu` nor `cuda-checkpoint` is installed on the guest |

**Does it work with PCIe-passthrough GPUs in a VM?** *No documentation states either way — this is my inference, flagged as such.* The mechanism is entirely guest-local: a userspace binary talking to the guest's own NVIDIA driver, which owns real hardware via VFIO. Nothing in the suspend/restore path requires host or hypervisor cooperation, and the guest reports a normal `/proc/driver/nvidia/version` and full CUDA functionality. I would expect it to behave exactly as on bare metal. The one genuine unknown is whether the **open kernel module** build (`NVIDIA UNIX Open Kernel Module … 610.43.02`) carries the checkpoint support; NVIDIA documents the feature against driver *branches*, not module flavours. **This is cheap to test and should be tested before any design work.**

**Does it work with multi-GPU TP2 and NCCL?** This is the real obstacle, and the literature is consistent and discouraging:

- vLLM RFC #34303 (Feb 2026): *"CUDA checkpoint operates on the entire process — all GPU resources including NCCL buffers are released, requiring NCCL re-initialization on resume."* And, flagged as an open question: *"CUDA graphs containing NCCL collectives embed references to old `ncclComm_t` handles. After NCCL rebuild, these are stale — such graphs likely need re-capture even with CUDA checkpoint."*
- Foundry (Apr 2026), on why they excluded it from multi-GPU benchmarks: *"CUDA-checkpoint does not support the IPC memory required by communication kernels (e.g., DeepEP) … and its restore latency grows disproportionately for multi-GPU data-parallel engines, making it less efficient than launching multiple independent single-GPU instances. We therefore compare with it only on single-GPU settings."*
- Foundry related work: *"the current implementation still lacks support for IPC memory and therefore cannot be directly applied to multi-GPU distributed inference."*

This appliance is squarely in the difficult case: TP2 with `--compilation-config {"cudagraph_mode":"FULL_AND_PIECEWISE","custom_ops":["all"]}` and `Enabled custom fusions: norm_quant, act_quant, allreduce_rms` — i.e. **fused all-reduce is inside the captured FULL graphs**, exactly the "stale `ncclComm_t` inside a graph" scenario. And the all-reduce dispatch order is `['B12X_PCIE_ONESHOT_DMA', 'PYNCCL']`, where a peer-to-peer DMA path very likely uses CUDA IPC handles.

*Two speculative counterweights, flagged:* (i) driver **610** added `cuIpcGetMemHandle`-based IPC support to `cuda-checkpoint`, and this guest runs 610.43.02 — the IPC objection may be a version artefact of the papers, which used drivers 550–590. (ii) NCCL init here is only **1.32 s**, so even a full communicator rebuild is cheap; the cost, if any, is re-capturing graphs (17.82 s), not re-initialising NCCL.

**Measured restore numbers from the literature, for calibration:**

| System | Configuration | Restore time | vs. cold |
|---|---|---:|---|
| CUDA-checkpoint + CRIU (Foundry's measurement) | single GPU, **weights and KV cache released before checkpoint** | 5.7–6.1 s | 4.9–7.9× faster |
| Modal GPU memory snapshots (production, "alpha") | vLLM + Qwen2.5-0.5B | 5 s | 45 s cold |
| Modal | ViT with `torch.compile` | 2.25 s | 8.5 s cold |
| Cerebrium (reported) | 9 GiB checkpoint | 2.25 s from S3 / 9 s from local NVMe | ~50 s cold |
| Foundry (graph materialisation only) | Qwen3-235B-A22B EP8 | **3.9 s** | **650 s cold — 99% reduction** |

Note the asterisk on the CUDA-checkpoint row: Foundry deliberately **released the weights first** to avoid "storing the whole GPU memory (141 GB per H200)". A checkpoint of *this* appliance with weights resident would be ~170 GB. **You would have replaced a 156.3 GB image pull with a ~170 GB checkpoint restore.** That is the crux of §7.

---

## 5. Q4 — Is there a disk-serialisable graph mechanism for this runtime?

### 5.1 What vLLM does and does not persist

| Artifact | Persisted to disk? | Evidence |
|---|---|---|
| Inductor/Dynamo compilation | **Yes** | `VLLM_CACHE_ROOT` (default `~/.cache/vllm`), `torch_compile_cache/`. Docs: *"you can directly copy the whole `~/.cache/vllm/torch_compile_cache` directory in your deployment scenario to save a great amount of compilation time"* and *"the cache directory can be copied between machines or baked into a container image."* With a warm cache, *"Inductor compilation is completely bypassed, and we will load from disk to read the compilation artifact."* |
| AOT-compiled function | **Yes** | `decorators.py:708 saved AOT compiled function to …/torch_aot_compile/<sha256>/rank_0_0/model`; force with `VLLM_FORCE_AOT_LOAD=1` |
| FlashInfer autotune configs | **Yes** | `autotune_configs.json`; log reports `(6 new, 0 from previous config)` |
| **CUDA graphs** | **NO** | No flag, no cache path, no API. The design doc states capture happens at init: *"The CUDA Graphs capturing happens when the runner first calls the model forward (using `_dummy_run`) with a non-`NONE` runtime mode"*, for *"each capture size"*. |
| KV cache allocation | No — but its *size* can be pinned | `--kv-cache-memory-bytes` |

### 5.2 Why CUDA graphs cannot be serialised — the mechanism, precisely

The CUDA Runtime/Driver Graph Management API provides create, instantiate, launch, update, clone, destroy, and `cudaGraphDebugDotPrint`. **There is no save and no load.** This is not an oversight. Foundry's abstract states the reason better than I can:

> *"CUDA graphs cannot be naively serialized: beyond graph topology, they are tightly coupled to execution context, including device addresses embedded in kernel arguments and kernel code lazily loaded during warmup."*

and in the introduction:

> *"a CUDA graph is not merely a topology description; it is tightly coupled to the execution context in which it was captured. In particular, graph nodes may reference device-side resources, including memory pointers embedded in kernel arguments and kernel function handles resolved by the CUDA runtime. These context-dependent references make CUDA graphs inherently non-portable and prevent straightforward serialization."*

In plain terms: a captured graph is not a recipe, it is a **pre-filled launch table**. The literal 64-bit VRAM address of every tensor is already written into each kernel's argument buffer, and each node points at a function handle valid only in the CUDA context that loaded that cubin. Ship it to a new process and every pointer and every handle is meaningless. You could bake the *bytes* of such a structure into an OCI layer trivially — they're just bytes — and they would be useless on load. **This is why "pre-baking unextracted graphs" saves nothing: the problem is not that OCI can't carry the bytes, it's that the bytes are only meaningful inside the process that made them.**

### 5.3 Foundry: the mechanism does exist — but not for you

Foundry (Liu, Wu, Yao, Zhuo, Stoica, Mao — Michigan/Berkeley/Duke, arXiv 2604.06664, 8 Apr 2026, open-sourced) is exactly the "disk-serialisable graph mechanism" in question. It persists graph topology **and** execution context by hooking the CUDA driver, enforcing deterministic memory layouts via the VMM APIs, extracting and repacking the kernel binaries, and templating shared topologies. Results: **Qwen3-235B-A22B EP8 from 650 s to 3.9 s (99%)**; Qwen3-30B-A3B EP2–EP8 from 112–154 s to 2.7–2.8 s. It beats CUDA-checkpoint by 2.6–4.4× and produces 1.1–2.2 GB archives vs. 3.7–6.6 GB. Crucially it *does* handle distributed serving: *"Foundry further enables a single-GPU offline capture to generate templates for multi-GPU deployments by patching only rank-dependent communication state."*

**Why it doesn't help here:**

1. It is a research prototype against **vLLM v0.11.2, PyTorch 2.9, driver 590.48, CUDA 13.1**. This appliance runs a proprietary derivative (`0.26.1rc0+infernal.invocation…`) with B12X kernels, TileLang JIT, DSpark speculative decoding and a custom `B12X_MLA_SPARSE` attention backend.
2. **Foundry's headline wins come from configurations capturing 512 graphs.** This appliance sets `--max-cudagraph-capture-size 48` and captures **17** (9 PIECEWISE + 8 FULL, plus 8 dspark). That optimisation has already been made. Capture is 17.82 s, not 10 minutes.

So the ceiling for a Foundry-class approach here is the 17.82 s capture plus, at best, part of the ~61 s profiling — against a substantial integration effort on a closed fork.

### 5.4 Verdict on the agent's claim at `2026-08-28T10:01:52.293Z`

> *"It may eliminate kernel/JIT compilation, but it will not eliminate weight transfer into VRAM or CUDA graph capture unless this particular runtime provides a disk-serializable graph mechanism."*

**Verified — the claim is correct on every clause**, and the current documentation supports it:

- ✅ *eliminates kernel/JIT compilation* — vLLM docs explicitly endorse baking `VLLM_CACHE_ROOT` into a container image; the measured effect is 13.01 s.
- ✅ *will not eliminate weight transfer into VRAM* — no filesystem artifact can put bytes in HBM; the 24.71 s stands.
- ✅ *will not eliminate CUDA graph capture* — confirmed by the absence of any serialisation API in CUDA, by vLLM's design doc, and by Foundry's existence.
- ✅ *"unless this runtime provides a disk-serializable graph mechanism"* — correctly hedged. Such a mechanism now exists in the literature; it is not in vLLM upstream and not in this fork.

**Two refinements I would add:**

1. The claim is *directionally right but understates the futility*. Even the part it concedes is achievable — eliminating compilation — is 13.01 s of a 212.68 s engine init (6.1%) and 1.2% of the 1,124 s total. The claim implicitly frames compilation as the meaningful prize; it isn't.
2. The claim omits the ~61 s CUDA-graph memory-profiling pass, which is neither compilation nor capture, is larger than both combined, and **is removable by configuration** — no baking, no checkpointing, just `--kv-cache-memory-bytes=9820551680` and/or `VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=0`. vLLM's optimization guide is explicit: *"Skip memory profiling with `--kv-cache-memory`. On startup, vLLM logs the exact `--kv-cache-memory` value that reproduces the current allocation. Passing it back on the next boot skips the memory-profiling measurement and the CUDA-graph memory estimation pass."* The runtime printed the value for you at `04:19:58.175`.

### 5.5 Other documented levers in this runtime

| Lever | Documented effect | Cost |
|---|---|---|
| `--kv-cache-memory-bytes=9820551680` | skips memory-profiling measurement **and** the CUDA-graph memory estimation pass | KV cache is fixed, not measured; too low caps concurrency, too high fails at alloc |
| `VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=0` | disables the ~61 s estimation pass; log says compensate with `--gpu-memory-utilization 0.9817` | slightly less precise headroom (and the estimate was 244% wrong anyway) |
| `VLLM_FORCE_AOT_LOAD=1` | ensures cached artifacts are used rather than silently recompiling on a cache miss | fails loudly instead of degrading silently — desirable |
| `--enforce-eager` | *"Skips both compilation and CUDA-graph capture for the fastest possible startup"* | **loses decode throughput** — not recommended for an inference appliance |
| `-O0` | *"fastest startup time, but lowest performance"* | same objection |
| `--max-cudagraph-capture-size 48` | **already set** — this is why capture is 18 s, not minutes | — |

---

## 6. Q5 — Weight loading: 24.71 s, and why 3.3 GB/s is the wrong number

### The rate is 2× better than stated

`Model loading took 80.99 GiB and 25.14 seconds` is logged **per rank**, and both ranks ran concurrently (`Worker_TP1` at `04:16:39.388`, `Worker_TP0` at `04:16:39.406`). Aggregate: **161.98 GiB into VRAM in 24.71 s = 6.56 GiB/s = 7.04 GB/s.**

### And the file-read rate is higher still

The 24.71 s window contains three distinct things, only ~19.3 s of which is reading weights:

```
Loading safetensors using InstantTensor loader: 9% Completed | 13.3G/155G [00:01<00:10, 14.3GB/s]
[default_loader.py:497] Loading weights took 10.39 seconds     ← backbone
[b12x_moe.py:842] B12X MoE force-A8 enabled: using quant_mode=w4a8_mx for E8M0 FP4 weights.
[dspark.py:576] DSpark draft model loaded: 97 params
[default_loader.py:497] Loading weights took 8.92 seconds      ← DSpark draft / MTP head
```

The InstantTensor progress bar reports **14.3 GB/s** with a 10-second ETA on a 155 GB checkpoint. The remaining ~5 s is MoE quantisation prep (`w4a8_mx` for E8M0 FP4 weights) and model construction.

### It is reading from page cache, not disk

Read-only inspection of the guest:

```
              total  used  free  shared  buff/cache  available
Mem:            251     9     9       0         235        242
/dev/vdb        3.0T  1.2T  1.9T  39%  /var/lib/docker
Storage Driver: overlayfs   (Docker 29.7.2)
```

**235 GiB of the guest's 251 GiB is page cache.** The 577 s extraction had just written ~155–200 GB into `/var/lib/docker` on `vdb` (a 3 TB virtio-blk device), finishing roughly 67 s before the loader started. 14+ GB/s is far above what a single sequential reader gets from virtio-blk over NVMe (typically 2–7 GB/s) and is entirely consistent with page-cache reads.

**This produces an ironic dependency: the 577 s extraction is what makes the 24.71 s load possible.** Any optimisation that stops writing 155 GB through the page cache immediately before startup will make Phase B *slower* unless weights are pre-warmed some other way. Budget for that.

### Could it be faster, and does baking change it?

- **Ceiling:** PCIe Gen5 x16 is ~64 GB/s theoretical, ~50 GB/s practical host-to-device. 81 GiB per GPU at 40 GB/s is ~2.2 s. So the load runs ~10× off the bus ceiling — it is bound by host-side read plus dequant/layout work, not by PCIe. RDMA peer-transfer approaches cited by Foundry load 1T-parameter models in under 2 s.
- **Does baking change it? No.** The weights are *already* baked — they are the 156.3 GB blob. A warm `/cache` layer touches none of this. The only filesystem-level change that matters is moving weights *out* of the image onto a persistent volume, which attacks the 577 s, not the 24.71 s.
- **Is it worth optimising? No.** 24.71 s is **2.2%** of 1,124.49 s. Even reducing it to zero is worth less than fixing the 101.74 s of orchestration dead time.

`instanttensor BUFFERED` is doing its job well. Leave it alone.

---

## 7. Q6 — The honest ceiling

### 7.1 What a filesystem-only bake can remove

| Item | Seconds | Confidence |
|---|---:|---|
| `torch.compile` / Inductor / AOT | 13.01 | **Documented + measured.** `monitor.py:53` reports it; vLLM docs confirm a warm cache bypasses Inductor entirely. |
| FlashInfer autotune | 4.22 | **Measured.** `(6 new, 0 from previous config)` proves the run was cold; a warm cache makes it a JSON read. |
| TileLang JIT (2 kernels × 2 ranks) | ~2–4 | **Observed** compile spans; cubins are files, so cacheable. |
| **Conservative total** | **~17–19 s** | **1.5–1.7% of 1,124.49 s** |
| Unlogged JIT inside the ~85 s block | 0–20 | **Speculative.** Argues *against*: the layer is only 91.1 MB, and the block demonstrably contains real GPU dummy-forward work, not just compilation. |
| **Speculative optimistic total** | **~40 s** | **3.6%** — I would not plan against this |

**This matches the owner's measured ~13 s.** The bake is not underperforming; it is at its structural limit.

### 7.2 What configuration alone can remove (no baking, no checkpointing)

| Lever | Seconds | Confidence |
|---|---:|---|
| `--kv-cache-memory-bytes=9820551680` + `VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=0` — removes the CUDA-graph memory estimation pass and the memory-profiling measurement | **55–75** | **Documented.** vLLM optimization guide states both are skipped; the ~61 s profiling block is directly measured; part of the ~16 s pre-profiling and some of the ~85 s dummy-run block should also go. |
| Fix the ready→first-request gap | **~100** | **Measured.** Pure harness scheduling. |
| **Subtotal, config only** | **~155–175 s (14–16%)** | Higher confidence and lower effort than anything involving graphs |

### 7.3 What a process/device checkpoint could theoretically remove

A working `cuda-checkpoint` + CRIU restore replaces everything from container start to ready: **300.47 s**.

But be numerate about what restore costs *here*:

- The checkpoint must carry 161.98 GiB of VRAM. `cuda-checkpoint` stages it through **host RAM**; the guest has 251 GiB, so it fits — barely.
- CRIU must write that ~170 GB to disk and read it back. At page-cache speed ~12 s; at virtio-blk NVMe speed (~2 GB/s) **~85 s**.
- Then ~162 GiB host→device at 20–40 GB/s: **4–8 s**.
- Plus NCCL re-init (~1.3 s here) and, per the vLLM RFC's open question, **probable re-capture of the FULL graphs containing fused all-reduce (17.82 s)**.

**Realistic restore: ~25–100 s**, replacing 300.47 s ⇒ **net 200–275 s saved (18–24% of total)** — *conditional on* the multi-GPU/IPC obstacles being solvable on driver 610, which is unproven.

**And here is the sting:** you would have traded a 156.3 GB image transfer + extraction for a ~170 GB checkpoint transfer + restore. **Process checkpointing does not beat "stop shipping the weights inside the image."** It is a strictly worse version of the same idea unless the checkpoint stays resident on local NVMe and the image does not.

### 7.4 Full ledger

| Lever | Removes (s) | % of 1,124.49 | Evidence class |
|---|---:|---:|---|
| **Weights out of the image** (persistent volume / pre-staged NVMe) — kills most of extraction *and* blob transfer | **~600–690** | **53–61%** | Measured phases; mechanism obvious |
| zstd layers instead of gzip (AWS: up to 27% startup reduction; zstd >3× faster to decompress) or `pigz` / containerd `unpacking_mode = "parallel"` | 150–350 | 13–31% | Documented, well-attested; alternative if weights must stay in the image |
| **Fix ready→first-request dead time** | **~100** | **9.0%** | Measured directly from the logs |
| `--kv-cache-memory-bytes` + disable cudagraph estimation | 55–75 | 5–7% | Documented in vLLM optimization guide |
| Pre-warmed worker processes (removes triple `import torch`) | ~26 | 2.3% | Measured; Foundry §2 notes this is standard practice |
| **Bake the `/cache` layer (what was done)** | **13–19** | **1.2–1.7%** | **Measured — already realised** |
| Foundry-class graph materialisation | 18–80 | 1.6–7% | Research prototype; not available for this fork |
| CUDA-checkpoint/CRIU restore | 200–275 | 18–24% | Speculative for TP2 + fused-allreduce graphs; large storage cost |

---

## 8. Required conclusion

### "Why would pre-baking unextracted graphs not save any time — is that because this isn't a VM image, just an OCI?"

**Short answer: the OCI observation is correct but incomplete, and the graphs were never the prize.**

**The long answer, for an engineer who doesn't know vLLM internals:**

An OCI image is a stack of tar files. That is the whole format. It can hold anything that is a file, and it holds nothing else — no processes, no memory, no open devices. So the rule for "what can be pre-baked" is simply: *does this thing exist as a file when the server is warm?* Run that test over the startup work and you get a clean split. The compiled kernels do exist as files, in `/cache/jit/…/torch_compile_cache/…`; they were baked, and they are worth **13.01 seconds**. The FlashInfer autotune table is a JSON file; worth **4.2 seconds**. And that's the list. 91 MB of layer, ~17 seconds of value. **The bake did not underperform — it hit its ceiling.**

Now, the natural next thought is the one you had: *if the format is the constraint, use a format that captures memory — a VM image.* That fails for two independent reasons. First, the state you want isn't in memory. When the server is warm, 80.99 GiB per GPU sits in **HBM on the card**, and the CUDA graphs live inside the NVIDIA driver's private bookkeeping for that process's GPU context. A VM snapshot captures guest RAM and emulated device state; it does not reach inside a graphics card. Second, and more bluntly: these GPUs are raw PCIe passthrough — the guest owns the physical hardware through VFIO — and QEMU cannot snapshot or live-migrate a VM with an assigned VFIO device at all. `virsh save` on this guest would refuse.

CUDA graphs deserve their own paragraph because they are the hardest case and the most counter-intuitive. A CUDA graph is *not* a description of work to do. It is a **pre-filled launch table** in which the actual 64-bit VRAM addresses of your tensors have already been written into each kernel's argument buffer, and each node points at a GPU function handle that is only meaningful in the CUDA context that loaded that binary. Restore that structure in a fresh process and every pointer and every handle is garbage. This is why the CUDA API has `cudaGraphCreate`, `cudaGraphInstantiate`, `cudaGraphLaunch` — and no `cudaGraphSave`. So: you *could* stuff the bytes of a captured graph into an OCI layer with no trouble at all. They would simply not work. **The limitation is not the container format; the container format would happily carry the bytes. The limitation is that the bytes are only meaningful inside the process that produced them.** Research systems (Foundry, Apr 2026) get around this by hooking the driver, forcing deterministic memory layouts so the addresses come back identical, and repacking the kernel binaries — which is exactly how much machinery it takes.

**But here is the thing that actually matters.** For this appliance the whole question is a red herring, because graph capture is **17.82 seconds** and `torch.compile` is **13.01 seconds** — together **2.8% of the 1,124-second cold start**. The runtime says so itself in one line:

> `init engine (profile, create kv cache, warmup model) took 212.68 s (compilation: 13.01 s)`

Six percent. And the reason capture is cheap is that someone already set `--max-cudagraph-capture-size 48`, so only 17 graphs get captured instead of the hundreds that make graph capture dominate startup in the published literature. **That optimisation has already been made.** There is no hidden ten-minute graph-capture problem here waiting to be pre-baked away.

### So what *is* the highest-leverage lever?

**Image extraction: 577.02 seconds — 51.3% of the entire cold start.** It is more than the other six measured phases combined. It is 32× the graph capture. And what it is doing is gzip-inflating ~155 GB of model weights out of tar archives, single-threaded, onto a virtio disk — weights that then get read straight back off that disk 67 seconds later.

Two fixes, in order of leverage:

1. **Take the weights out of the image.** Serve them from a persistent volume or pre-staged local NVMe and let the image carry only the ~1 GB runtime. This collapses the 577.02 s extraction *and*, on repeat starts, the 116.06 s blob transfer. **~690 s, 61% of the cold start.** *Caveat established in §6: today's fast 24.71 s weight load depends on the extraction having just warmed the page cache. Removing the extraction without a pre-warm will make Phase B slower — budget ~40–80 s back unless weights are pre-faulted.*
2. **If the weights must stay in the image, stop using gzip.** zstd decompresses >3× faster than gzip; AWS measured up to 27% startup reduction on Fargate with the largest images benefiting most. `pigz` on the host is used automatically by containerd if installed, and containerd supports `unpacking_mode = "parallel"`. Any of these attacks a 577-second, single-threaded, CPU-bound phase.

**Then, in descending order:**

3. **The 101.74 s of dead time between "ready" and the first request** (9.0%). This is the harness not asking, not the appliance not being ready. It is free.
4. **`--kv-cache-memory-bytes=9820551680` plus `VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=0`** (5–7%). The runtime printed both values for you at `04:19:58.175`, and vLLM's optimization guide documents that passing `--kv-cache-memory` "skips the memory-profiling measurement and the CUDA-graph memory estimation pass." This kills a ~61 s dry rehearsal of graph capture whose only output was an estimate that turned out to be **244% wrong** (`0.64 GiB estimated, 0.19 GiB actual`).

Those four levers total roughly **740–870 seconds — 66–77% of the cold start — and not one of them involves graphs, checkpointing, or the container image format.**

The bake is not the problem. The bake is finished, correct, and at its ceiling. The problem is that you are shipping 156 GB through a single-threaded decompressor and then waiting 100 seconds to ask the first question.

---

## 9. Speculation register

Explicitly flagged, in order of how much weight I would put on it:

| Claim | Status |
|---|---|
| The bakeable ceiling is 13–19 s | **Measured.** Direct from `monitor.py:53`, the autotune log, and the TileLang spans. |
| The 101.74 s residual is ready→first-request dead time | **Measured** to 0.07 s from the logs. |
| The ~61 s CUDA-graph memory profiling is removable by config | **Documented** in vLLM's optimization guide + the runtime's own log line. |
| Phase B reads from page cache, not disk | **Strong inference.** 235 GiB buff/cache + 14.3 GB/s reported rate + extraction finishing 67 s earlier. Not directly instrumented. |
| The ~85 s block is JIT warmup + memory-profiling dummy forward | **Inference** from surrounding log lines (TileLang, `enable_cutedsl_warmup`, `enable_jit_warmup`, two 60-s `shm_broadcast` timeouts). The block itself is unlogged. |
| The C4/C5 boundary (~`04:18:34`) | **Estimated.** tqdm bars carry no Docker timestamp; bounded by `04:18:40.54` and `04:19:35.39` plus the bars' own elapsed times. |
| `cuda-checkpoint` works under VFIO passthrough | **Undocumented — my inference.** Mechanism is guest-local; guest has a real driver and real devices. Cheap to test; test before designing. |
| Driver 610's `cuIpcGetMemHandle` support may resolve the multi-GPU IPC objection | **Speculative.** The papers used drivers 550–590; the objection may be stale. Unverified. |
| Whether the baked layer contains **both** `rank_0_0` and `rank_1_0` compile caches | **Unverified — and material.** If only one rank's cache is present, the barriered ranks give you zero benefit. |
| CUDA-checkpoint restore for this appliance would be 25–100 s | **Modelled**, not measured. Built from documented per-GB rates; no one has published a TP2-with-fused-allreduce number. |
| Removing extraction will slow Phase B | **Inference** from the page-cache finding. Should be budgeted, then measured. |

---

## 10. Sources

**Specifications and primary documentation**
- OCI Image Layer specification — https://github.com/opencontainers/image-spec/blob/main/layer.md
- NVIDIA `cuda-checkpoint` — https://github.com/NVIDIA/cuda-checkpoint
- CUDA Driver API, checkpoint group (`cuCheckpointProcess*`) — https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__CHECKPOINT.html
- CUDA Runtime API, Graph Management (note the absence of any save/load) — https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART__GRAPH.html
- CUDA Programming Guide, CUDA Graphs — https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/cuda-graphs.html
- CRIU GPU Checkpointing — https://www.criu.org/GPU_Checkpointing
- CRIU CUDA plugin source — https://github.com/checkpoint-restore/criu/tree/criu-dev/plugins/cuda
- NVIDIA, "Checkpointing CUDA Applications with CRIU" — https://developer.nvidia.com/blog/checkpointing-cuda-applications-with-criu

**vLLM**
- torch.compile integration (cache paths, cross-machine copy, baking into an image) — https://docs.vllm.ai/en/latest/design/torch_compile/
- CUDA Graphs design (PIECEWISE / FULL / FULL_AND_PIECEWISE, capture at init via `_dummy_run`) — https://docs.vllm.ai/en/stable/design/cuda_graphs/
- Optimization and Tuning (`--kv-cache-memory`, `VLLM_FORCE_AOT_LOAD`, `--enforce-eager`, `-O0`) — https://docs.vllm.ai/en/stable/configuration/optimization/
- vLLM blog, "Introduction to torch.compile and How It Works with vLLM" — https://blog.vllm.ai/2025/08/20/torch-compile.html
- RFC #34303, "CUDA Checkpoint/Restore for Near-Zero Cold Starts" — https://github.com/vllm-project/vllm/issues/34303
- Issue #33930, "GPU Memory Snapshotting to reduce cold starts" — https://github.com/vllm-project/vllm/issues/33930
- Issue #45178, `VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS` overestimates memory — https://github.com/vllm-project/vllm/issues/45178
- Issue #16501, compile caching opt-out by default — https://github.com/vllm-project/vllm/issues/16501

**Papers**
- Liu, Wu, Yao, Zhuo, Stoica, Mao. *Foundry: Template-Based CUDA Graph Context Materialization for Fast LLM Serving Cold Start*, arXiv:2604.06664 (8 Apr 2026) — https://arxiv.org/abs/2604.06664 · code: https://github.com/foundry-org/foundry
- Kabakibo, Trivedi, Wang. *Breaking the Ice: Analyzing Cold Start Latency in vLLM*, arXiv:2606.07362v3 (29 Jun 2026) — https://arxiv.org/abs/2606.07362 · tooling: https://github.com/upb-cn/vllm-startup-profiler
- *CRIUgpu: Transparent Checkpointing of GPU-Accelerated Workloads*, arXiv:2502.16631 — https://arxiv.org/abs/2502.16631

**Production GPU snapshotting**
- Modal, "GPU Memory Snapshots: Supercharging sub-second startup" — https://modal.com/blog/gpu-mem-snapshots
- Modal, "Memory snapshots: Checkpoint/restore for sub-second startup" — https://modal.com/blog/mem-snapshots
- Cerebrium, "Reducing GPU Cold Starts with Memory Snapshots" — https://cerebrium.ai/blog/reducing-gpu-cold-starts-with-memory-snapshots-restoring-cuda-workloads-in-second
- Cedana, "Cedana vs. CRIUgpu for GPU Checkpoint/Restore" — https://docs.cedana.ai/articles/cedana-vs.-criu-cuda-for-gpu-checkpoint-restore

**Image pull / extraction**
- containerd #13559, "End-to-end image pull duration is often dominated by gzip decompression" — https://github.com/containerd/containerd/issues/13559
- containerd #8881, "Parallel Container Layer Unpacking" — https://github.com/containerd/containerd/issues/8881
- AWS, "Reducing AWS Fargate Startup Times with zstd Compressed Container Images" — https://aws.amazon.com/blogs/containers/reducing-aws-fargate-startup-times-with-zstd-compressed-container-images/
- Depot, "Building Images: Gzip vs Zstd" — https://depot.dev/blog/building-images-gzip-vs-zstd
- vLLM #28656, "Investigate and Implement Zstd Compression for Docker Images" — https://github.com/vllm-project/vllm/issues/28656

**Primary measured data**
- Codex transcript `C:\Users\pmacl\.codex\sessions\2026\08\26\rollout-2026-08-26T11-08-50-01a03ed4-d36a-7333-9548-7b7d8fc6ee32.jsonl` — reconstructed container log, `2026-08-29T04:15:15.29Z` → `04:22:14.34Z`
- Read-only host/guest inspection via `ssh bloodarrow` → `ssh ubuntu@192.168.122.248`: `free -g`, `nproc`, `nvidia-smi`, `/proc/driver/nvidia/version`, `lsblk`, `df`, `lspci -nn`, `docker info`, `docker system df`
