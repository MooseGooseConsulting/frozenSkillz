# Blood Arrow cold-start telemetry audit — runs 1 & 2

**Scope:** what telemetry exists, whether run 1's startup was clean or hiding errors/retries, and what
instrumentation is missing.
**Method:** read-only. Host artifacts under `/srv/ai-models/runtime-state/serving/cold-start/` were read
and copied locally; the Codex transcript
`rollout-2026-08-26T11-08-50-01a03ed4-d36a-7333-9548-7b7d8fc6ee32.jsonl` (31.5 MB, 8,562 records) was
parsed. No writes, no restarts, no `vastai` state changes. Container `C.49031045` was not touched.

**Two headline corrections to the brief, up front:**

1. **Raw container logs *were* saved to disk.** The brief said run 1's directory contained only
   `cold-measurements.json`, `first-inference-response.json`, `warm-cache-publication.json`. In fact it
   contains **18 files including `container.log` (54,527 bytes, 223 lines)** — the complete
   `docker logs --timestamps` of the vLLM container from first line to post-inference. No transcript
   archaeology was needed for run 1. This is the single most important finding in this report.
2. **Run 1 contained exactly one retry, and it was a harness port bug, not a server error.** Details in
   §3.2.

---

## 1. Inventory — what actually exists

### 1.1 Full tree

```
/srv/ai-models/runtime-state/serving/cold-start/
├── 20260829T040311Z-r21-cold1/        <- RUN 1 (contract 49089274)  — 18 files
├── 20260829T043908Z-r21-warm-cold2/   <- RUN 2 (contract 49091846)  —  5 files
└── native-codex-*.{jsonl,txt}         <- 10 files, Aug 28 01:30–02:29, a SEPARATE earlier
                                          Codex-driven registry/pull exercise. Not cold-start
                                          run telemetry. Ignored for this audit.
```

### 1.2 Run 1 — `20260829T040311Z-r21-cold1/` (contract 49089274)

| File | Size (B) | mtime (host local) | What it captures |
|---|---:|---|---|
| **`container.log`** | **54,527** | 2026-08-28 23:23:21 | **Full `docker logs --timestamps C.49089274`.** 223 lines, `04:15:15.292` → `04:22:14.342`. The complete vLLM startup + the inference. |
| `registry.log` | 112,697 | 23:23:28 | `docker logs --timestamps bloodarrow-oci-registry --since 04:03:13Z`. Blob-by-blob serving record. |
| `cold-measurements.json` | 2,833 | 23:30:19 | Derived summary: 12 phase timestamps, 12 durations, registry/storage/runtime/inference rollups. |
| `timestamps.tsv` | 570 | 23:21:58 | 13 phase markers. **Note: 9 of the 13 were hardcoded string literals in the shell script**, not measured live (see §6.4). |
| `first-inference-response.json` | 858 | 23:21:58 | Raw JSON body of the single chat completion. |
| `container-inspect-sanitized.json` | 19,092 | 23:23:20 | `docker inspect` — keys `Id, Created, Image, Path, Args, Mounts, State, HostConfig, NetworkSettings, Config`. |
| `docker-diff-running.txt` | 572,965 | 23:23:28 | `docker diff` of the running container (writable-layer churn). |
| `docker-diff-stopped.txt` | 572,965 | 23:25:37 | Same, post-stop. Byte-identical size — no post-stop churn. |
| `cache-inventory.txt` | 733,611 | 23:23:21 | File listing of the JIT/compile cache. |
| `cache-du-bytes.txt` | 19,470 | 23:23:21 | Per-directory byte sizes under `/cache/jit/...`. |
| `cache-tar-paths.txt` | 700,803 | 23:25:29 | Paths inside `cache-layer-source.tar`. |
| `cache-layer-source.tar` | 698,293,248 | 23:24:34 | Full `/cache` capture (~698 MB). |
| `cache-layer-r21-generated.tar` | 91,125,760 | 23:28:09 | Refined cache layer actually published (~91 MB). |
| `cache-layer-r21-generated-paths.txt` | 466,348 | 23:28:09 | Paths inside the refined layer. |
| `warm-cache-publication.json` | 1,649 | 23:30:47 | Result of publishing the warm-cache image (`status: published-and-verified`). |
| `preflight.json` | 3,905 | 23:03:12 | Pre-run vast.ai offer snapshot + `gpu_state` + `docker_used_bytes`. |
| `create-response.json` | 50 | 23:06:38 | `{"new_contract": 49089274, "success": true}` |
| `post-inference-host-state.txt` | 211 | 23:23:28 | `df` of `/var/lib/docker` + **two** `nvidia-smi` rows. |

### 1.3 Run 2 — `20260829T043908Z-r21-warm-cold2/` (contract 49091846)

| File | Size (B) | What it captures |
|---|---:|---|
| `preflight.json` | 3,997 | Pre-run offer snapshot. `docker_used_bytes: 951293042688`. |
| `create-response-sanitized.json` | 42 | `{\ success\:true,\new_contract\:49091846}` (escaping mangled by the capture path). |
| `monitor.tsv` | 1,752 | 40 poll rows, ~16 s apart, `04:41:33.698Z` → `04:51:58.327Z`. Columns: `timestamp_utc, actual_status, container_state, mapped_port, health_code`. |
| `timestamps.tsv` | 41 | **One line only:** `monitor_started  2026-08-29T04:41:33.696Z` |
| `instance-latest-sanitized.json` | 511 | Final instance state. |

### 1.4 Direct answer: were raw container logs saved?

- **Run 1: YES.** `container.log` is a complete, timestamped, unfiltered `docker logs` capture. It was
  written by the command at transcript line 7588 (`2026-08-29T04:23:19.468Z`):

  ```
  ssh -o BatchMode=yes "$guest" "/usr/bin/docker logs --timestamps C.49089274 2>&1" < /dev/null > "$run_dir/container.log"
  docker logs --since 2026-08-29T04:03:13Z --timestamps bloodarrow-oci-registry > "$run_dir/registry.log" 2>&1
  ```

- **Run 2: NO — and there was nothing to capture.** A `find` across the whole cold-start tree returns
  only three log-ish files, all in run 1's directory:

  ```
  /srv/.../20260829T040311Z-r21-cold1/container-inspect-sanitized.json
  /srv/.../20260829T040311Z-r21-cold1/container.log
  /srv/.../20260829T040311Z-r21-cold1/registry.log
  ```

  Run 2's container **never started** — `instance-latest-sanitized.json` records
  `"actual_status":"created","cur_state":"stopped","intended_status":"stopped"`. There were no container
  logs in existence to save. The gap is not that logs were lost; it is that **run 2 produced no startup
  evidence whatsoever**, and the harness captured no `docker events` or `docker inspect` to bound the
  container-create moment more tightly than a 16-second poll.

---

## 2. Run 1 container log timeline

Contract `49089274`. Container started `04:15:13.870Z`, endpoint ready `04:20:14.338Z`, inference
completed `04:21:58.007Z`. All times below are the container log's own `docker logs --timestamps`
prefixes (UTC).

### 2.1 Whole-run phase budget (contract → first inference complete = 1,124.49 s)

| Phase | Window | Duration | Share |
|---|---|---:|---:|
| Contract created → first registry manifest request | 04:03:13.518 → 04:03:34.627 | 21.11 s | 1.9% |
| Blob transfer (52 GETs, 156.30 GB, 1.347 GB/s) | 04:03:34.627 → 04:05:30.771 | 116.06 s | 10.3% |
| **Image extraction / unpack** | 04:05:30.771 → 04:15:07.790 | **577.02 s** | **51.3%** |
| Container create → start | 04:15:07.790 → 04:15:13.870 | 6.08 s | 0.5% |
| Container start → model load start (python import, engine init) | 04:15:13.870 → 04:16:14.700 | 60.83 s | 5.4% |
| Model load (weights) | 04:16:14.700 → 04:16:39.406 | 24.71 s | 2.2% |
| **Load done → graph capture done** | 04:16:39.406 → 04:19:58.175 | **198.77 s** | **17.7%** |
| Graph capture done → endpoint ready | 04:19:58.175 → 04:20:14.338 | 16.16 s | 1.4% |
| Ready → inference requested (harness lag + failed attempt) | 04:20:14.338 → 04:21:55.998 | 101.66 s | 9.0% |
| Inference | 04:21:55.998 → 04:21:58.007 | 2.01 s | 0.2% |
| **Total** | | **1,124.49 s** | 100% |

The dominant cost of a Blood Arrow cold start is **image extraction (51%)**, not model loading and not
graph capture. That phase has *zero* instrumentation (§6.2).

### 2.2 Chronological log table — container start to endpoint ready

| Time (UTC) | Source | Event |
|---|---|---|
| 04:15:15.292 | entrypoint | `DS4 launch: mode=dspark depth=fixed capacity_activation=disabled backend=b12x-a8-dglin allreduce=b12x b12x_dma=0 indexer=b12x tp=2 dcp=1 max_seqs=8 graph=48 load_format=instanttensor instanttensor_backend=BUFFERED native_l2=0 allocator=expandable_segments:True model=/models/ds4` |
| 04:15:15.292 | entrypoint | `Process-group interfaces: GLOO_SOCKET_IFNAME=lo NCCL_SOCKET_IFNAME=lo` |
| 04:15:15.292 | entrypoint | Full `vllm serve` command line (TP2, `--kv-cache-dtype fp8`, `--max-model-len 1048576`, `--load-format instanttensor`, dspark spec-decode w/ 5 draft tokens, `B12X_MLA_SPARSE` attention) |
| 04:15:22.159 | torch pid=1 | `W0829 ... torch/utils/_pytree.py:630] <enum 'KernelPreference'> ... deprecated` |
| 04:15:27.533 | APIServer | vLLM banner, `version 0.26.1rc0+infernal.invocation.cu133.r21.vllmd6cf36a.b12xf6dc512` |
| 04:15:27.537 | APIServer | 5× `WARNING [envs.py:2544] Unknown vLLM environment variable detected: ...` |
| 04:15:27.542 | APIServer | `Detected quantization_config.scale_fmt=ue8m0; enabling UE8M0 for DeepGEMM.` |
| 04:15:36.892 | APIServer | **Tokenizer/arch resolve:** `Resolved architecture: DeepseekV4ForCausalLM`; `Using max model len 1048576` |
| 04:15:37.179 | APIServer | `Using fp8 data type to store kv cache. ... it may cause accuracy drop without a proper scaling factor` |
| 04:15:46.058 | APIServer | `Resolved architecture: DeepSeekV4MTPModel` (draft model) |
| 04:15:55.006 | APIServer | `Chunked prefill is enabled with max_num_batched_tokens=4096.` |
| 04:16:04.128 | EngineCore pid=374 | `Initializing a V1 LLM engine ... tensor_parallel_size=2 ... kv_cache_dtype=fp8 ...` |
| 04:16:04.128 | EngineCore | **Worker spawn:** `DP group leader: node_rank=0, master_addr=127.0.0.1, mq_connect_ip=172.17.0.3 (local), world_size=2, local_world_size=2` |
| 04:16:12.466 | Worker pid=400 | **Distributed init:** `world_size=2 rank=0 local_rank=0 distributed_init_method=file:///tmp/vllm_dist_3a73081ec90944d98b811264454a2df2 backend=nccl` |
| 04:16:12.551 | Worker pid=401 | same, `rank=1` |
| 04:16:12.590 | Worker 401 | **NCCL:** `Found nccl from environment variable VLLM_NCCL_SO_PATH=/opt/local-inference/nccl/lib/libnccl.so.2.31.2` |
| 04:16:12.599 | Worker 400 | `vLLM is using nccl==2.31.2` |
| 04:16:12.992 | Workers 400/401 | `WARNING [symm_mem.py:101] SymmMemCommunicator: native P2P atomics are not supported between devices [0, 1], communicator is not available.` |
| 04:16:13.080 | Workers | `B12X selected a 524288-byte PCIe all-reduce limit for TP2; the vLLM default is 86016 bytes.` |
| 04:16:13.736 | Worker 400 | `Using ['B12X_PCIE_ONESHOT_DMA', 'PYNCCL'] all-reduce backends ... for group 'tp:0'` |
| 04:16:13.792 | Worker 400 | `rank 0 in world size 2 is assigned as DP rank 0, PP rank 0, PCP rank 0, TP rank 0, EP rank 0` |
| **04:16:14.700** | Worker_TP0 | **`Loading model from scratch...`** ← `model_load_started` |
| 04:16:14.703 | Worker_TP0 | `DeepSeek V4 b12x mHC enabled.` / `expert_dtype resolved to 'fp4'` |
| 04:16:14.821 | Worker_TP0 | `Using DeepSeek's fp8_ds_mla KV cache format.` |
| 04:16:15.029 | Worker_TP0 | `Using 'B12X' Mxfp4 MoE backend.` |
| 04:16:16.606 → 04:16:25.831 | Worker_TP0 | **Main weights:** `Loading safetensors using InstantTensor loader: 0% → 100% Completed \| 155G/155G [00:09<00:00, 18.1GB/s]` |
| **04:16:25.978** | Worker_TP0 | **`Loading weights took 10.39 seconds`** ← `weights_loaded` |
| 04:16:27.169 | Worker_TP0 | `WARNING [b12x_moe.py:842] B12X MoE force-A8 enabled: using quant_mode=w4a8_mx for E8M0 FP4 weights.` |
| 04:16:28.952 | Workers | `Using Eagle3 auxiliary layers from config: (41, 42, 43)` |
| 04:16:29.030 | Workers 400/401 | `WARNING [vllm.py:2625] `torch.compile` is turned on, but the model /models/ds4 does not support it.` |
| 04:16:30.154 → 04:16:37.946 | Worker_TP0 | **Draft weights:** second `InstantTensor` pass, `100% \| 155G/155G [00:07<00:00, 21.4GB/s]` |
| 04:16:38.054 | Worker_TP0 | `DSpark draft model loaded: 97 params` / `Loading weights took 8.92 seconds` |
| 04:16:39.388 | Worker_TP1 | `Model loading took 80.99 GiB and 25.139530 seconds` |
| **04:16:39.406** | Worker_TP0 | **`Model loading took 80.99 GiB and 25.141342 seconds`** ← `model_load_completed` |
| 04:16:39.432 | EngineCore | `WARNING [torch_utils.py:251] OMP_NUM_THREADS=2 is set; leaving Torch threads at 2 for serving.` |
| 04:16:42.213 | Worker_TP0 | `Using cache directory: /cache/jit/cu133-torch213-vllmd6cf36ae0d-b12xf6dc512eb1-lmcachee045d729bc/vllm/torch_compile_cache/618cceda8d/rank_0_0/backbone for vLLM's torch.compile` |
| 04:16:42.213 | Worker_TP0 | `Dynamo bytecode transform time: 2.06 s` |
| 04:16:51.919 | Worker_TP0 | `Compiling a graph for compile range (1, 4096) takes 8.53 s` |
| 04:16:53.144 | Worker_TP0 | `collected artifacts: 44 entries, 44 artifacts, 7801534 bytes total` |
| **04:16:53.162** | Worker_TP0 | **`torch.compile took 13.01 s in total`** ← `torch_compile_completed` |
| 04:17:14–15 | Worker_TP0 | `TileLang begins to compile kernel `hc_head_fuse_tilelang`` … `TileLang completes` |
| **04:17:16.215** | Worker_TP0 | **`Initial profiling/warmup run took 23.05 s`** |
| 04:17:25.411 / 04:17:26.300 | TileLang | `Warning: T.vectorized loop over `i_hci` with extent 4 is lowered as a serial loop because TileLang could not find a valid vectorization plan.` (×2) |
| 04:17:28.137 | Worker_TP0 | `TileLang completes to compile kernel `mhc_post_tilelang`` ; `Profiled V1 prompt-logprobs workspace with chunk size 1024` |
| 04:17:29.612 | Worker_TP0 | `Warming up DeepSeek V4 mHC kernels for token sizes: [1, 2, 4, 8, 16, 24, 32, 40, 48, 64, 128, ... ]` |
| **04:17:31.807** | Worker_TP0 | **`DeepSeek V4 mHC warmup finished in 2.19 seconds.`** |
| 04:17:31.941 | Worker_TP0 | `Warming up ll_bf16 router GEMM kernels for shapes: ((4096, 256),).` |
| 04:17:40.483 | EngineCore | `INFO [shm_broadcast.py:801] No available shared memory broadcast block found in 60 seconds. This typically happens when some processes are hanging or doing some time-consuming work (e.g. compilation, weight/kv cache quantization).` |
| ~04:17:33.6 → **04:18:14.646** | Worker_TP0 | **`DeepGEMM warmup: 100%\|██████████\| 888/888 [00:41<00:00, 21.15it/s]`** |
| 04:18:15.995 | Worker_TP0 | `Warmed up 3 B12X MoE dynamic launch variant(s) across 1 expert signature(s).` |
| 04:18:15.998 | Worker_TP0 | `Deferring runtime-dependent kernel warmup until KV cache initialization.` |
| 04:18:18.025 | Worker_TP0 | `DSA indexer decode path: use_flattening=False use_varlen=False (next_n=6, use_fp4_indexer_cache=False)` |
| 04:18:40.544 | EngineCore | Second `No available shared memory broadcast block found in 60 seconds` |
| ~04:18:32.7 → **04:18:55.746** | Worker_TP0 | **`Profiling CUDA graph memory (PIECEWISE): 100%\|██████████\| 9/9 [00:23<00:00, 2.62s/it]`** |
| ~04:18:55.7 → **04:19:25.020** | Worker_TP0 | **`Profiling CUDA graph memory (FULL): 100%\|██████████\| 8/8 [00:29<00:00, 3.66s/it]`** |
| 04:19:24.238 / 04:19:25.020 | Workers | `Capturing model for DSpark speculator...` |
| 04:19:34.593 | Worker_TP0 | `Capturing dspark CUDA graphs (FULL): 100%\|██████████\| 8/8 [00:09<00:00, 1.20s/it]` |
| 04:19:34.625 | Worker_TP0 | `Capturing DFlash context-KV CUDA graphs (FULL): 100%\|██████████\| 9/9 [00:00<00:00, 374.18it/s]` |
| 04:19:35.383 | Worker_TP0 | `torch/distributed/c10d_logger.py:83: UserWarning: barrier(): using the device under current context.` |
| 04:19:35.389 | Workers | `Estimated MRV2 CUDA graph memory: 0.64 GiB total (0.31 GiB retained in the reusable pool)` |
| **04:19:35.389** | Worker_TP0 | **`Available KV cache memory: 8.28 GiB`** |
| **04:19:35.398** | EngineCore | **`GPU KV cache size: 1,249,001 tokens, Maximum concurrency for 1,048,576 tokens per request: 1.19x`** |
| 04:19:36.127 | Worker_TP0 | `Using FlashInfer autotune cache file: /cache/jit/.../flashinfer-autotune/e3471a6.../autotune_configs.json` ; `[Autotuner]: Autotuning process starts ...` |
| 04:19:40.195 | Workers | `[AutoTuner]: Tuning sparse_mla_sm120_decode_dsv4: 100%\|██████████\| 6/6 [00:03<00:00, 1.69profile/s]` |
| **04:19:40.346** | Worker_TP0 | **`[Autotuner]: Saved 6 configs to ...autotune_configs.json (6 new, 0 from prior)`** ← proves the JIT cache was **cold** |
| ~04:19:41.9 → 04:19:45.883 | Worker_TP0 | `Capturing CUDA graphs (PIECEWISE): 100%\|██████████\| 9/9 [00:04<00:00, 1.85it/s]` |
| ~04:19:46.7 → 04:19:57.689 | Worker_TP0 | `Capturing CUDA graphs (FULL): 100%\|██████████\| 8/8 [00:11<00:00, 1.48s/it]` |
| 04:19:58.155 | Worker_TP0 | `Capturing dspark CUDA graphs (FULL): 100%\|██████████\| 8/8 [00:00<00:00, 19.55it/s]` |
| **04:19:58.175** | Workers | **`Graph capturing finished in 18 secs, took 0.19 GiB`** ← `graph_capture_completed` |
| 04:19:58.175 | Workers | `CUDA graph pool memory: 0.19 GiB (actual), 0.64 GiB (estimated), difference: 0.45 GiB (244.2%).` |
| 04:19:58.175 | Workers | `Free memory on device (93.83/95.01 GiB) on startup. ... Actual usage is 82.69 GiB for consumed memory (weights + non-torch), 1.66 GiB for peak activation, and 0.19 GiB for CUDAGraph memory.` |
| 04:20:11.427 | Workers | `Kernel JIT monitor activated; monitored JIT compilations during inference will use mode=warn.` |
| **04:20:12.109** | EngineCore | **`init engine (profile, create kv cache, warmup model) took 212.68 s (compilation: 13.01 s)`** |
| 04:20:13.680 | APIServer | `Supported tasks: ['generate']` |
| 04:20:13.821 | APIServer | `"auto" tool choice has been enabled.` |
| 04:20:13.831 | APIServer | `WARNING [model.py:1723] Default vLLM sampling parameters have been overridden by the model's `generation_config.json`: `{'temperature': 1.0, 'top_p': 1.0}`.` |
| 04:20:13.845 | APIServer | `Starting vLLM server on http://0.0.0.0:8000` + 30 route lines |
| 04:20:13.860 | APIServer | `INFO: Started server process [1]` / `INFO: Waiting for application startup.` |
| **04:20:14.338** | APIServer | **`INFO: Application startup complete.`** ← `endpoint_ready` |
| 04:21:56.006 | APIServer | `INFO: 172.17.0.1:42720 - "GET /health HTTP/1.1" 200 OK` |
| 04:21:57.913 | Worker_TP0 | `WARNING [jit_monitor.py:135] Triton kernel JIT compilation during inference: _prepare_dflash_inputs_kernel. This causes a latency spike; consider extending warmup to cover this shape/config.` |
| 04:21:58.015 | APIServer | `INFO: 172.17.0.1:42736 - "POST /v1/chat/completions HTTP/1.1" 200 OK` |
| 04:22:04.341 | APIServer | `Engine 000: Avg prompt throughput: 9.1 tokens/s, Avg generation throughput: 2.1 tokens/s, Running: 0 reqs, Waiting: 0 reqs, GPU KV cache usage: 0.0%, Prefix cache hit rate: 0.0%` |
| 04:22:04.341 | APIServer | `SpecDecoding metrics: Mean acceptance length: 3.00, Current speculative depth: 5, Accepted throughput: 0.13 tokens/s, Drafted throughput: 0.32 tokens/s, Accepted: 14 tokens, Drafted: 35 tokens, Per-position acceptance rate: 0.714, 0.429, 0.286, 0.286, 0.286, Avg Draft acceptance rate: 40.0%` |
| 04:22:14.342 | APIServer | Final idle stats line. **End of container.log.** |

### 2.3 The ~168 s answer — accounting for the 198.77 s window

`model_load_completed` (04:16:39.406) → `graph_capture_completed` (04:19:58.175) = **198.769 s**, of which
13.01 s is `torch.compile` and 18 s is graph capture, leaving **167.76 s**. Every second of it is
accounted for below. Segments are contiguous and sum exactly to 198.769 s.

| # | Segment | Window | Duration | In the 168 s? |
|---:|---|---|---:|:---:|
| 1 | `torch.compile` (Dynamo 2.06 s + inductor 8.53 s + AOT artifact save) | 04:16:39.406 → 04:16:53.162 | 13.76 s | no (the 13.01 s) |
| 2 | **Initial profiling/warmup run** (incl. TileLang `hc_head_fuse` JIT) | 04:16:53.162 → 04:17:16.215 | **23.05 s** | ✔ |
| 3 | TileLang `mhc_post` JIT + prompt-logprobs workspace profiling + mHC warmup (2.19 s) | 04:17:16.215 → 04:17:31.807 | **15.59 s** | ✔ |
| 4 | ll_bf16 router GEMM warmup + **DeepGEMM warmup (888 kernels, 41 s)** + B12X MoE variants | 04:17:31.807 → 04:18:15.998 | **44.19 s** | ✔ |
| 5 | DSA indexer setup, IR-priority re-resolve, deferred-warmup bookkeeping (quiet) | 04:18:15.998 → ~04:18:32.75 | **16.75 s** | ✔ |
| 6 | **CUDA-graph memory *profiling* (PIECEWISE, 9 shapes)** | ~04:18:32.75 → 04:18:55.746 | **23.00 s** | ✔ |
| 7 | **CUDA-graph memory *profiling* (FULL, 8 shapes)** | 04:18:55.746 → 04:19:25.020 | **29.27 s** | ✔ |
| 8 | dspark speculator + DFlash profiling capture | 04:19:25.020 → 04:19:34.625 | **9.61 s** | ✔ |
| 9 | KV-cache sizing (8.28 GiB / 1,249,001 tokens) | 04:19:34.625 → 04:19:36.127 | **1.50 s** | ✔ |
| 10 | **FlashInfer autotune** (6 configs, cold miss) | 04:19:36.127 → 04:19:40.346 | **4.22 s** | ✔ |
| 11 | Idle gap + PIECEWISE graph capture begins | 04:19:40.346 → 04:19:45.883 | 5.54 s | partly |
| 12 | FULL capture (11 s) + dspark + DFlash capture | 04:19:45.883 → 04:19:58.175 | 12.29 s | no (the 18 s) |
| | **Total** | | **198.77 s** | |

Segments 2–10 sum to **167.18 s**, plus ~1.55 s of idle at the head of segment 11 = **~168.7 s**. That is
the missing time, and it is *entirely* kernel autotuning, warmup, and memory profiling.

**The two biggest single contributors:**

1. **CUDA-graph memory profiling — 61.9 s** (segments 6+7+8). This is *not* graph capture; it is vLLM
   running each of 17 batch shapes to measure peak memory before deciding the KV-cache size. It costs
   3.4× more than the actual capture (18 s) and 4.8× more than `torch.compile` (13.01 s). Note the
   estimate it produced was badly wrong — `0.19 GiB (actual), 0.64 GiB (estimated), difference: 0.45 GiB
   (244.2%)` — so ~0.45 GiB of KV cache was left on the table for a minute of profiling.
2. **DeepGEMM warmup — 41 s** for 888 kernels (segment 4).

Together those two are **103 s of the 168 s**. Both are JIT/autotune work whose outputs land in
`/cache/jit/...`, i.e. exactly what the warm-cache layer published in `warm-cache-publication.json`
(`cache_source_bytes: 91125760`, `cache_entries: 2732`) is meant to eliminate on a subsequent run. **We
have no measurement proving it does**, because run 2 never started (§5).

The `Saved 6 configs ... (6 new, 0 from prior)` line at 04:19:40.346 is independent confirmation that run
1's JIT cache started genuinely cold.

**Cross-check:** `init engine ... took 212.68 s` at 04:20:12.109 back-computes to 04:16:39.43 — exactly
`model_load_completed`. The extra 13.93 s beyond graph-capture-done is the JIT-monitor activation and
final engine setup. The numbers are internally consistent.

---

## 3. Errors, warnings, retries, fallbacks

### 3.1 The direct answer to "for all I know that loading is taking a long time because we're hitting a ton of errors"

**No. It is not.** Keyword counts across all 223 lines of `container.log`:

| Pattern | Hits |
|---|---:|
| `ERROR` | **0** |
| `Traceback` | **0** |
| `Exception` | **0** |
| `retry` / `retrying` | **0** |
| `failed` / `Failed` | **0** |
| `fallback` | **0** |
| `OOM` | **0** |
| `CUDA error` | **0** |
| `timeout` | **0** |
| `abort` / `Killed` | **0** |
| `WARNING` | 17 |
| `deprecat` | 8 |
| `NCCL` | 7 (all normal init) |

There is **not one error, exception, stack trace, retry, or fallback anywhere in the container's output.**
The long startup is not error-driven. It is 103 s of kernel autotune + memory profiling (§2.3) on top of
a 577 s image unpack (§2.1) — all of it *expected work*, none of it failure recovery.

### 3.2 The one real retry — and it was on the client side

At `2026-08-29T04:21:11.929Z` (transcript line 7550) the harness ran an inference script that targeted
**port 8000 on the guest**:

```
health_code=$(ssh ... "curl -sS -o /dev/null -w '%{http_code}' --max-time 10 http://127.0.0.1:8000/health")
```

It failed (transcript line 7551, `04:21:13.562Z`):

```
Secrets: 1 loaded
curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
```

The retry at `04:21:54.712Z` (line 7570) added `host_port=20083` and succeeded. The container publishes
`8000` to a **mapped** host port; the first script guessed the container-internal port.

**Critically, this never reached the server.** `container.log`'s first request line is at
`04:21:56.005` (`GET /health 200`) — there is no 04:21:11–13 entry at all. The failure was purely
harness-side, and it explains most of the 101.66 s "ready → inference requested" gap in §2.1.

### 3.3 Every warning, with an assessment

All 17 `WARNING`/`W0829`/`UserWarning` lines, verbatim and classified. **None indicate a fault.**

| Line | Warning | Assessment |
|---:|---|---|
| 4, 5, 28, 29, 32, 33, 34, 35 | `W0829 ... torch/utils/_pytree.py:630] <enum 'KernelPreference'> is an Enum subclass and is now natively supported by torch.compile as an opaque value type. Calling register_constant() on Enum subclasses is deprecated and will be an error in a future release.` (and `ScaleCalculationMode`) | Upstream PyTorch deprecation, emitted once per process (pids 1, 374, 400, 401). Cosmetic. |
| 13–17 | `WARNING [envs.py:2544] Unknown vLLM environment variable detected: VLLM_DSPARK_CAPACITY_LOG_INTERVAL / VLLM_SOURCE_DIR / VLLM_DSPARK_STS_LOG_INTERVAL / VLLM_DSPARK_TP_CHECK / VLLM_SOURCE_OVERLAY_ACTIVE` | Custom appliance env vars vLLM doesn't recognise. Expected for this fork. Worth confirming they're consumed by *something* — otherwise they're dead config. |
| 26, 80, 178 | `WARNING [vllm.py:1870] max_num_scheduled_tokens is set to 4064 based on the speculative decoding settings. This may lead to suboptimal performance. Consider increasing max_num_batched_tokens ...` | Genuine tuning advice: `--max-num-batched-tokens 4096` minus draft slots = 4064. A perf note, not a fault. |
| 41, 42 | `WARNING [symm_mem.py:101] SymmMemCommunicator: native P2P atomics are not supported between devices [0, 1], communicator is not available.` | Hardware fact — these are PCIe RTX PRO 6000s with `bw_nvlink: 0.0`. vLLM correctly selects `B12X_PCIE_ONESHOT_DMA` + `PYNCCL` instead. A capability probe, not an error. |
| 76 | `WARNING [b12x_moe.py:842] B12X MoE force-A8 enabled: using quant_mode=w4a8_mx for E8M0 FP4 weights.` | Intentional appliance behaviour. |
| 83, 84 | ``WARNING [vllm.py:2625] `torch.compile` is turned on, but the model /models/ds4 does not support it.`` | **Cosmetic and misleading** — `torch.compile` demonstrably *did* run 22 s later (`torch.compile took 13.01 s in total`, 44 artifacts saved). This is a stale support-matrix check in the fork. |
| 100, 175 | `WARNING [torch_utils.py:251] OMP_NUM_THREADS=2 is set; leaving Torch threads at 2 for serving. Multi-threaded torch CPU ops during serving can degrade performance through spin-wait contention and cgroup CPU-quota throttling.` | Deliberate; the message says it is leaving the setting alone. |
| 112, 113 | ``Warning: T.vectorized loop over `i_hci` with extent 4 is lowered as a serial loop because TileLang could not find a valid vectorization plan.`` | TileLang codegen quality note. Minor perf, not correctness. |
| 143 | `torch/distributed/c10d_logger.py:83: UserWarning: barrier(): using the device under current context.` | Standard PyTorch nag. |
| 182 | ``WARNING [model.py:1723] Default vLLM sampling parameters have been overridden by the model's `generation_config.json`: `{'temperature': 1.0, 'top_p': 1.0}`.`` | Informational. The request set `temperature: 0` explicitly, so this did not affect the test. |
| 219 | `WARNING [jit_monitor.py:135] Triton kernel JIT compilation during inference: _prepare_dflash_inputs_kernel. This causes a latency spike; consider extending warmup to cover this shape/config.` | **The one actionable warmup gap.** A kernel was JIT'd *during* the first inference — part of why it took 2.009 s. Extending warmup to cover this shape would cut first-token latency. |

### 3.4 Two lines that look alarming but are not

```
04:17:40.483 (EngineCore pid=374) INFO [shm_broadcast.py:801] No available shared memory broadcast block
  found in 60 seconds. This typically happens when some processes are hanging or doing some
  time-consuming work (e.g. compilation, weight/kv cache quantization).
04:18:40.544 (EngineCore pid=374) INFO [shm_broadcast.py:801] (same)
```

These are **`INFO`, not warnings**, and they contain the word "hanging" only as an explanatory hint. They
fire at 04:17:40 and 04:18:40 — precisely during the DeepGEMM warmup (04:17:33–04:18:15) and the
CUDA-graph memory profiling (04:18:32–04:19:25). EngineCore is simply noting that its workers were busy
for >60 s. This is the *expected* signature of the long warmup, not evidence of a stall.

### 3.5 LMCache

`grep -c "LMCache"` = **0**. The string `lmcache` appears only inside build-fingerprint paths
(`/cache/jit/cu133-torch213-...-lmcachee045d729bc/`) and in the published entrypoint
(`"/usr/local/bin/lmcache-mp-wrapper.sh"` in `warm-cache-publication.json`). **LMCache emitted no init
line and no log output at all during run 1.** Whether it is active and silent, or inert, cannot be
determined from this log — flagging as undetermined (§7).

---

## 4. Was the inference genuine?

### 4.1 The actual request

Recovered from the transcript (line 7570, `04:21:54.712Z`) — this is the exact payload:

```json
{"model":"DeepSeek-V4-Flash-0731",
 "messages":[{"role":"user","content":"Reply with exactly: cold-start-ok"}],
 "max_tokens":64,
 "temperature":0}
```

Delivered base64-encoded over nested SSH (host → guest → `curl` to `127.0.0.1:20083`).

So yes — **the content `"cold-start-ok"` was dictated by the prompt.** On its face this is an echo test,
and the owner's instinct to be suspicious is correct.

### 4.2 But the evidence goes further than an echo

Four independent signals in the saved artifacts show a real forward pass through the real weights:

**(a) The model produced reasoning that is nowhere in the prompt.** `first-inference-response.json`
contains:

```json
"reasoning": "We need to reply exactly with \"cold-start-ok\". No extra."
```

That sentence is generated text. A stub, proxy, or echo endpoint cannot invent it. It also explains the
token accounting: `completion_tokens: 21` for a 3-token answer — ~15 tokens of reasoning + ~6 of content.
(`--default-chat-template-kwargs.thinking=true` and `reasoning_effort=high` were set at launch.)

**(b) Speculative decoding metrics show a real draft/target token distribution:**

```
SpecDecoding metrics: Mean acceptance length: 3.00, Current speculative depth: 5,
Accepted: 14 tokens, Drafted: 35 tokens,
Per-position acceptance rate: 0.714, 0.429, 0.286, 0.286, 0.286, Avg Draft acceptance rate: 40.0%
```

Two separate models (target + dspark draft) agreed and disagreed position-by-position. This cannot be
faked by an echo.

**(c) A real attention kernel was JIT-compiled mid-request:**

```
04:21:57.913 WARNING [jit_monitor.py:135] Triton kernel JIT compilation during inference:
  _prepare_dflash_inputs_kernel. This causes a latency spike;
```

**(d) Engine throughput was recorded:** `Avg prompt throughput: 9.1 tokens/s, Avg generation throughput:
2.1 tokens/s`, and GPU memory settled at `95524 MiB / 97887 MiB` on both GPUs.

### 4.3 A telemetry bug that hid the best evidence

The extraction `jq` asked for the wrong field:

```
... finish_reason:.choices[0].finish_reason, content:.choices[0].message.content,
    reasoning_content:.choices[0].message.reasoning_content, usage:.usage
```

The API returns the key as **`reasoning`**, not `reasoning_content`. So the run summary recorded
`"reasoning_content":null` and the strongest proof that the model genuinely generated was discarded from
the summary — it survives only because the full body was also written to
`first-inference-response.json`. Trivial one-character-class fix; see §6.6.

### 4.4 Was there a second or longer inference? No.

An exhaustive scan of all 8,562 transcript records found **exactly two** commands containing
`/v1/chat/completions`, both carrying the **identical** payload: line 7550 (`04:21:11.929Z`, failed on
port 8000) and line 7570 (`04:21:54.712Z`, succeeded on port 20083). `container.log` independently
confirms only one `POST /v1/chat/completions` ever reached the server, and the engine returned to
`Running: 0 reqs, Waiting: 0 reqs` and idled until the log ends.

### 4.5 Honest verdict on inference validity

**Proven:** the model was loaded onto both GPUs, ran a genuine autoregressive forward pass through the
real weights with speculative decoding active, and returned a well-formed OpenAI-schema response with a
generated reasoning trace. This is materially more than "a port answered."

**Not proven:**

- **Numerical/output quality.** One 21-token instruction-following echo at `temperature: 0` cannot detect
  quantization damage. The stack is aggressive: `fp8` KV cache, `fp4` experts, `w4a8_mx` MoE quant. The
  log itself warns at 04:15:37.179: *"Using fp8 data type to store kv cache ... it may cause accuracy
  drop without a proper scaling factor."* Nothing here tests that.
- **Long context.** `--max-model-len 1048576` was configured but only **91 prompt tokens** were
  exercised. And KV cache is tight: `Maximum concurrency for 1,048,576 tokens per request: 1.19x` — a
  single max-length request nearly exhausts the cache. Completely untested.
- **Throughput / concurrency.** `--max-num-seqs 8` never exercised. The 2.1 tok/s figure is dominated by
  the mid-request JIT spike and is not a performance measurement.
- **Parser correctness.** `--reasoning-parser deepseek_v4` and `--tool-call-parser deepseek_v4` were
  enabled, yet reasoning came back under `reasoning` while the harness expected `reasoning_content`. That
  mismatch is unexplained and may indicate the reasoning parser is not mapping as expected (§7).

---

## 5. Run 2 telemetry (contract 49091846)

### 5.1 What exists

Five files, no logs. `monitor.tsv` is the only time series: 40 rows, ~16 s apart, `04:41:33.698Z` →
`04:51:58.327Z`. Its `mapped_port` and `health_code` columns are **empty on every single row** — the
schema anticipated a serving container that never materialised.

### 5.2 Reconstructed timeline

| Time (UTC) | Event | Source |
|---|---|---|
| 04:39:10 | Preflight snapshot; `docker_used_bytes: 951293042688` | `preflight.json` |
| ~04:39:10 | Contract 49091846 created | `create-response-sanitized.json` |
| 04:40:12.163 – 04:41:19.415 | Blob serving; largest single blob `26249789048` B at 04:41:14.917 | host registry log |
| **04:41:19.415** | **Last blob completed** (verified directly, not assumed) | host registry log |
| 04:41:33.696 | `monitor_started` | `timestamps.tsv` |
| 04:41:33.698 → 04:50:52.877 | 36 consecutive rows: `actual_status=loading`, `container_state=absent` | `monitor.tsv` |
| **[04:50:52.877, 04:51:08.901]** | **Container first observed as `created`** — true creation bounded to this 16 s window | `monitor.tsv` |
| 04:51:08.901 / 04:51:25.315 / 04:51:42.024 | `actual_status=loading`, `container_state=created` | `monitor.tsv` |
| 04:51:58.327 | `actual_status` finally flips to `created` — last row | `monitor.tsv` |
| ~04:52 | Destroyed | — |

Final state: `"actual_status":"created","cur_state":"stopped","intended_status":"stopped"`,
`"status_msg":"Successfully loaded ...@sha256:7b5b493a..."`. The image loaded fine. **The container was
never started, so no vLLM process ever ran and no container log exists.**

### 5.3 Correcting the ~639 s extraction figure

The 639 s figure reproduces as `04:41:19.415 → 04:51:58.327 = 638.91 s`. **But that endpoint is the wrong
one.** It measures to the vast.ai `actual_status` field flip, which lags the real container-create event.
`container_state` — the direct observation — had already shown `created` at 04:51:08.901.

| Measurement | Value |
|---|---|
| Quoted figure (to `actual_status` flip) | 638.9 s |
| **True extraction (to `container_state=created`)** | **573.5 s – 589.5 s** (16 s poll resolution) |
| vast.ai status-propagation lag included in the quoted figure | ~49 – 65 s |
| Run 1's directly-measured equivalent (`last_blob_to_container_created`) | **577.02 s** |

**So the 639 s figure overstates extraction by roughly 50–65 s, and should be restated as ~577 s ± 8 s.**

This matters for the warm-cache thesis: run 2's true extraction (573–590 s) is **statistically
indistinguishable from run 1's 577.02 s.** That is the expected result — the published warm-cache layer is
only 91,125,760 B uncompressed / 15,726,145 B compressed against ~156 GB of model weights, so it cannot
move extraction time. **The warm cache was never expected to help here, and the data confirms it did
not.** Its value would be in eliminating the ~103 s of JIT/autotune warmup inside the 198.77 s window —
and **run 2 produced no evidence on that question at all**, because the container never started.

### 5.4 Container logs for run 2

**None. Zero.** Confirmed by directory listing and by a `find` across the whole cold-start tree. Not a
capture failure — there was no running container to log.

---

## 6. What instrumentation is missing

Ordered by how much darkness each one removes. None of these require touching the `vast-ubuntu` VM's
lifecycle; where a change needs an image rebuild it is flagged explicitly.

### 6.1 Capture logs on *every* run, including aborted ones — **highest value, zero cost**

Run 1 got a full `container.log`; run 2 got nothing. The capture was ad-hoc (a command the agent
happened to type at 04:23:19, eight minutes after the fact), not part of a teardown path. Make it
unconditional, before destroy:

```
docker logs --timestamps <cid>            > $run_dir/container.log 2>&1 || true
docker inspect <cid>                      > $run_dir/container-inspect.json 2>&1 || true
docker events --since <t0> --until <t1>   > $run_dir/docker-events.jsonl 2>&1 || true
```

`docker events` alone would have replaced run 2's entire 16 s-resolution guess with an exact
`create`/`start`/`die` timestamp. Host-side only; no VM change.

### 6.2 Sample during the 577 s extraction — **the biggest black box**

Extraction is **51% of total cold start** and has exactly two data points: start and end. We cannot say
whether it is CPU-bound (decompression) or IO-bound (disk write), so we cannot say what would fix it.
From last-blob until `container_state=created`, sample every 2 s into a TSV:

```
date -u +%FT%T.%3NZ, df --output=used /var/lib/docker, iostat -x 1 1 (or zpool iostat 1 1),
  cat /proc/loadavg, ps -eo pcpu,comm --sort=-pcpu | head -5
```

Host/guest-side sampler; no VM lifecycle change.

### 6.3 `nvidia-smi` time series — currently only 2 samples, both post-inference

`post-inference-host-state.txt` has two rows (`0, 95524, 97887, 0, 40, 20.51` / `1, 95524, 97887, 0, 35,
19.93`). We cannot see when the 80.99 GiB/worker was allocated, nor GPU utilisation across the 62 s of
CUDA-graph memory profiling — which would tell us whether that phase is GPU-bound or serialised CPU
overhead. Run from container start to endpoint-ready:

```
nvidia-smi --query-gpu=timestamp,index,memory.used,utilization.gpu,power.draw,clocks.sm \
           --format=csv -l 2 > $run_dir/nvidia-smi.csv
```

### 6.4 Emit phase markers from inside the container — stop reconstructing them

This is the core of the owner's "transcript archaeology" complaint. Run 1's `timestamps.tsv` looks like
measured telemetry but 9 of its 13 rows were **hardcoded string literals inside the shell script**:

```
printf 'contract_created\t2026-08-29T04:03:13.518Z\ncontainer_created\t2026-08-29T04:15:07.790Z\n
container_started\t2026-08-29T04:15:13.870Z\nmodel_load_started\t2026-08-29T04:16:14.700Z\n...'
```

Those values were read off `container.log` by hand and pasted in. Only the four `health_*`/`inference_*`
rows were measured live. Two fixes, either works:

- *No rebuild:* derive `timestamps.tsv` from `container.log` with a committed grep/awk script, so the
  provenance is a reproducible transform rather than a paste.
- *Better, needs an r22 image rebuild:* have the entrypoint emit
  `PHASE <name> $(date -u +%FT%T.%3NZ)` around each stage. **This is a build change, not a VM lifecycle
  change** — but flagging it since it requires reissuing the appliance image.

### 6.5 Per-phase timing that the log makes you compute by hand

vLLM reports `torch.compile took 13.01 s`, `Graph capturing finished in 18 secs`, and `init engine ...
212.68 s` — but the 62 s of CUDA-graph memory profiling and the 41 s DeepGEMM warmup have **no summary
line at all**. I had to recover them by parsing tqdm bars' elapsed fields and subtracting. A small
post-processing script over `container.log` that emits a phase-duration table would make §2.3 a
one-command output instead of an investigation.

### 6.6 Fix the `jq` field name

```
-  reasoning_content:.choices[0].message.reasoning_content
+  reasoning:(.choices[0].message.reasoning // .choices[0].message.reasoning_content)
```

One line; recovers the single best proof of genuine generation (§4.3).

### 6.7 Record the mapped host port at create time

The one retry in run 1 (§3.2) happened because the inference script assumed port 8000. Write the mapped
port to `$run_dir/mapped-port.txt` when the container is created and have the inference script read it.
Also populate `monitor.tsv`'s already-existing but perpetually-empty `mapped_port` and `health_code`
columns.

### 6.8 Add a real validation inference

`"Reply with exactly: cold-start-ok"` proves liveness, not correctness. Add a second request with a
verifiable non-echo answer and a ~200-token generation, and record tokens/s:

- a short arithmetic or factual question whose answer is checkable;
- a `/metrics` scrape at endpoint-ready and again after inference;
- optionally a long-context probe, since `--max-model-len 1048576` is entirely untested and the KV cache
  only supports `1.19x` concurrency at that length.

### 6.9 Snapshot the JIT cache before the run

We know run 1 started cold only *incidentally*, from `Saved 6 configs ... (6 new, 0 from prior)`. A
`du -sb /cache/jit` before and after makes warm-vs-cold explicit — and it is the only way to
quantitatively prove whether the published warm-cache layer actually eliminates the ~103 s of
autotune/warmup, which is the whole point of `warm-cache-publication.json`.

### 6.10 Tighten the poll interval

`monitor.tsv`'s 16 s cadence is what forced the ±8 s uncertainty in §5.3. Drop to ~3 s. Cheap, and it
would have resolved run 2's container-create moment exactly. Keep run 2's *shape* (both `actual_status`
and `container_state`) and apply it to run 1's directory too — right now the two runs have incompatible
schemas.

---

## 7. What I could not determine read-only

- **Run 2's exact container-create time.** Bounded to `[04:50:52.877, 04:51:08.901]` only. No
  `docker events` was captured and the container is destroyed.
- **Whether the 577 s extraction is CPU- or IO-bound.** No CPU, disk, or IO sampling exists for that
  window in either run. This is the single most consequential unknown, since it is half of cold start.
- **Whether LMCache is active.** Zero LMCache log output in run 1 despite `lmcache-mp-wrapper.sh` being
  the published entrypoint. Cannot distinguish "active and silent" from "inert" from the log alone.
- **Why `reasoning` came back instead of `reasoning_content`** despite `--reasoning-parser deepseek_v4`.
  Could be correct fork behaviour or a parser mismatch; needs a second request to characterise.
- **The 16.75 s quiet gap at 04:18:16 – 04:18:32.75** (§2.3 segment 5). No log lines at all. Presumably
  deferred-warmup bookkeeping, but unobservable without §6.3's GPU sampling.
- **Whether the warm-cache layer actually shortens the 198.77 s window.** Run 2 never started. This is
  the central open question and it remains completely unanswered.
- **Model output quality under fp8 KV / fp4 experts / w4a8_mx.** One echo test cannot establish it.

---

## 8. Required conclusions

### Was run 1 clean, or error-laden?

**Clean.** Emphatically so. Across all 223 lines of `container.log` there are **zero** errors, zero
tracebacks, zero exceptions, zero retries, zero fallbacks, zero OOMs, zero CUDA errors, and zero timeouts.
The 17 warnings are deprecation nags, hardware-capability probes (`native P2P atomics are not
supported` — correct for PCIe cards with no NVLink), intentional appliance settings, and two genuinely
useful perf hints (`max_num_scheduled_tokens is set to 4064`, and the `_prepare_dflash_inputs_kernel`
JIT-during-inference warning). The two `shm_broadcast` messages that mention "hanging" are `INFO`-level
and fire exactly during the known-long warmup phases — they are the *expected* signature of that work,
not a stall.

**The slow startup is fully explained by work, not failure:** 577 s of image extraction (51% of the
total), then 103 s of CUDA-graph memory profiling plus DeepGEMM kernel warmup inside the 198.77 s window,
on a cold JIT cache. Every second of that 198.77 s window is accounted for in §2.3, and the arithmetic
closes exactly against vLLM's own `init engine ... took 212.68 s`.

*One caveat, stated plainly:* run 1 did contain a single failed attempt and retry — but it was
**harness-side**, an inference script that targeted port 8000 instead of the mapped port 20083. It never
reached the container (no corresponding entry in `container.log`) and cost ~44 s of the gap between
endpoint-ready and first inference. The *container* was clean; the *harness* had one bug.

### Do we know the model was serving validly, or only that a port answered?

**Meaningfully more than "a port answered" — but short of "serving validly" in any quality sense.**

We know a real forward pass happened: the model emitted a reasoning trace that appears nowhere in the
prompt (`"We need to reply exactly with \"cold-start-ok\". No extra."`), speculative decoding produced a
genuine per-position acceptance distribution (`0.714, 0.429, 0.286, 0.286, 0.286`, 14 accepted of 35
drafted), a Triton attention kernel JIT-compiled mid-request, and 80.99 GiB of weights per worker were
resident on both GPUs. No echo, proxy, or stub could produce that.

But the test was `"Reply with exactly: cold-start-ok"` — the content was dictated by the prompt, it was
the *only* inference of the entire session, and it exercised 91 of 1,048,576 available context tokens.
Given an fp8 KV cache (which the log itself warns "may cause accuracy drop without a proper scaling
factor"), fp4 experts, and w4a8_mx MoE quantization, **we have liveness and plumbing correctness, not
output correctness.** §6.8 is the fix and it is cheap.

---

*Sources: `/srv/ai-models/runtime-state/serving/cold-start/{20260829T040311Z-r21-cold1,20260829T043908Z-r21-warm-cold2}/`
(read-only); host registry container log (read-only `docker logs`);
`~/.codex/sessions/2026/08/26/rollout-2026-08-26T11-08-50-01a03ed4-d36a-7333-9548-7b7d8fc6ee32.jsonl`
(8,562 records parsed). No writes, restarts, or `vastai` state changes were made; container `C.49031045`
was not touched.*
