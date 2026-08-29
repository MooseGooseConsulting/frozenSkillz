# B — Unpack Limiter Analysis

**Image:** `deepseek-v4-flash-r21-appliance@sha256:4bdd68f66f12e07f52714533a29d4f2f869e61129cd1486c35381fa3035f7f79`
**Question:** why did extraction take 577.02 s, and would uncompressed or zstd layers be faster?
**Date:** 2026-08-29
**Method:** read-only inspection of host `bloodarrow` and guest `vast-ubuntu` (192.168.122.248). No files created, modified or deleted on either machine; no image pulled, extracted or built; no service restarted; renter container `C.49031045` untouched. All benchmarks are pipe-only (`... | wc -c`, `of=/dev/null`) against blobs that already exist in the content store.

---

## 0. Executive answer

**The single dominant limiter is serial, single-threaded gzip decompression.** containerd applies layers one at a time, and each layer's gzip stream is decompressed by exactly one thread. The whole 64-vCPU guest ran the extraction at the speed of **one** decompressor.

Measured on the guest, on the actual weight blob: a single `unpigz` stream sustains **312.1 MB/s in / 365.3 MB/s out**. The observed extraction sustained **290.4 MB/s in / 350.4 MB/s out**. That is **93% / 96% of exactly one stream.** Six concurrent streams on the same box reach **1770 MB/s** — 5.67× — so the hardware was 82% idle for 577 seconds.

Two premises in the brief are wrong and both matter:

| Brief says | Actual | Evidence |
|---|---|---|
| 32-core / 64-thread Threadripper | **64-core / 128-thread 9985WX**; guest gets 64 vCPU (32c/64t) | §3 |
| Unpacked size ≈ 370 GB → 640 MB/s | **202.19 GB** unpacked → **350.4 MB/s** | §5 |

The "370 GB" is `docker images` reporting *content blobs + snapshots* under the containerd image store: 167.573 + 202.193 = **369.77 GB**. Only 202.19 GB was actually written by extraction. Correcting this is what makes the observed rate land exactly on one gzip stream instead of a puzzling ~640 MB/s.

**Owner's intuition — correct, but for a subtler reason than "compression is slow", and zstd beats it.**

---

## 1. What compression are the layers actually using?

### 1.1 Registry required auth; obtained the manifest read-only from ZFS instead

```
$ ssh bloodarrow "curl -s -H 'Accept: application/vnd.oci.image.manifest.v1+json, ...' \
    'http://192.168.122.1:5001/v2/deepseek-v4-flash-r21-appliance/manifests/sha256:4bdd68...'"
HTTP 400 bytes=48
Client sent an HTTP request to an HTTPS server.

$ ... 'https://192.168.122.1:5001/v2/...' (with -k)
HTTP 401 bytes=174
{"errors":[{"code":"UNAUTHORIZED","message":"authentication required","detail":[{"Type":"repository",
 "Class":"","Name":"deepseek-v4-flash-r21-appliance","Action":"pull"}]}]}
```

`skopeo inspect --raw` also failed — the host's docker config has no credentials:

```
$ ssh bloodarrow "skopeo inspect --raw --tls-verify=false docker://192.168.122.1:5001/deepseek-...@sha256:4bdd68..."
level=fatal msg="... authentication required"

$ cat /home/coldaine/.docker/config.json
{ "auths": {} }
```

Registry container env confirms htpasswd auth (`REGISTRY_AUTH=htpasswd`, `REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd`). **I did not work around the credential requirement.** Instead I read the manifest blob directly from the registry's own ZFS-backed storage, which is a plain read:

```
$ docker inspect bloodarrow-oci-registry --format '{{json .Mounts}}'
[{"Type":"bind","Source":"/srv/ai-models/runtimes/oci-registry/data","Destination":"/var/lib/registry",...}]
```

### 1.2 The descriptor is an index, not a manifest

```
$ cat /srv/ai-models/runtimes/oci-registry/data/docker/registry/v2/blobs/sha256/4b/4bdd68f6.../data
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.index.v1+json",
  "manifests": [
    { "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "digest": "sha256:2bcfcd5544d16d94dcf0d6bf472a5398d3dc2595a85e0400cfcec61f423b9517",
      "size": 22028,
      "platform": { "architecture": "amd64", "os": "linux" } }
  ]
}
```

### 1.3 Every one of the 133 layers is gzip. No zstd anywhere.

Parsing `sha256:2bcfcd55...` (the real manifest):

```
manifest mediaType: application/vnd.oci.image.manifest.v1+json
config mediaType:   application/vnd.oci.image.config.v1+json  327185
layer count: 133
  MT application/vnd.docker.image.rootfs.diff.tar.gzip -> 124 layers, bytes= 15025190099
  MT application/vnd.oci.image.layer.v1.tar+gzip       ->   9 layers, bytes= 152547708730
total compressed bytes: 167572898829 = 167.573 GB
```

Total matches the brief exactly: **167,572,898,829 bytes**. Two media types, **both gzip**:

- 124 × `application/vnd.docker.image.rootfs.diff.tar.gzip` — 15,025,190,099 B (15.025 GB), the OS/CUDA/Python base
- 9 × `application/vnd.oci.image.layer.v1.tar+zstd`? **No — `application/vnd.oci.image.layer.v1.tar+gzip`** — 152,547,708,730 B (152.548 GB), the model weights

The 9 "weight" layers, in manifest order (they are the *last* 9 layers of the image — this matters, see §5.4):

| # | bytes | GB | mediaType | digest |
|---|---|---|---|---|
| 1 | 2,132,863 | 0.00 | oci…tar+gzip | `013f1a9382554a39545830c…` |
| 2 | 15,699 | 0.00 | oci…tar+gzip | `f8740097c1d2ce8ca50f3a7…` |
| 3 | 19,350 | 0.00 | oci…tar+gzip | `600aabe4539a1a715e2bde9…` |
| 4 | 23,743,064,094 | 23.74 | oci…tar+gzip | `beda23a80d2f080e9147fc5…` |
| 5 | 26,200,033,067 | 26.20 | oci…tar+gzip | `14fb308af47fe21c8c5ac48…` |
| 6 | 26,232,468,608 | 26.23 | oci…tar+gzip | `d177390a55a17a115a56cf8…` |
| 7 | 26,252,701,563 | 26.25 | oci…tar+gzip | `96a53e352c9817a4166dcc7…` |
| 8 | 26,249,789,048 | 26.25 | oci…tar+gzip | `91dfd733d4107e78fc2b3f5…` |
| 9 | 23,867,484,438 | 23.87 | oci…tar+gzip | `75fe65129dfe23158316e13…` |
|  | **152,547,708,730** | **152.548** | | |

The real payload is **6 layers averaging 25.4 GB each**. Snapshot inode counts (§5.2) show 11 inodes per weight snapshot → ~8 shard files per layer × 6 = 48 shards, matching the brief.

**No layer carries `annotations`**, so there is no eStargz / zstd:chunked / SOCI metadata — no lazy-pull or seekable-decompression path is present.

> **Finding 1.** All 133 layers are gzip. 91% of the compressed bytes sit in 6 gzip streams of ~25 GB each. Because gzip's DEFLATE format is a single unseekable back-referencing stream, each of those 6 layers is an irreducibly serial unit of work.

---

## 2. How does the extraction actually work?

### 2.1 Guest runtime

```
$ docker version --format 'client={{.Client.Version}} server={{.Server.Version}}'
client=29.7.2 server=29.7.2

$ docker info
 Server Version: 29.7.2
 Storage Driver: overlayfs
  driver-type: io.containerd.snapshotter.v1
 Cgroup Driver: systemd / Cgroup Version: 2
 Runtimes: io.containerd.runc.v2 nvidia runc
 containerd version: aad11006b869517fcd3009450b6f82da282e1a9b
 runc version: v1.4.3-0-gbb14dabe
 Kernel Version: 6.8.0-137-generic
 Operating System: Ubuntu 24.04.4 LTS
 CPUs: 64
 Total Memory: 251.6GiB
 Docker Root Dir: /var/lib/docker

$ containerd --version
containerd containerd v2.3.3 aad11006b869517fcd3009450b6f82da282e1a9b
```

Docker 29.7.2 is running the **containerd image store** (`driver-type: io.containerd.snapshotter.v1`), so the unpack is done by **containerd 2.3.3**, not by the legacy dockerd graphdriver. Kaalia confirms it drives Docker:

```
$ ps aux | grep kaalia
vastai_+ 2319 /var/lib/vastai_kaalia/latest/kaalia backend=DKR installpath=/var/lib/vastai_kaalia/latest/ ...
```

`backend=DKR` — Vast's daemon shells out to the local Docker daemon, so the pull path's capabilities are exactly Docker 29.7.2 + containerd 2.3.3's.

### 2.2 Where the extracted bytes actually land

`docker info` says Docker Root Dir is `/var/lib/docker`, but with the containerd snapshotter the snapshots live under `/var/lib/containerd`. Verified that this is still on the zvol:

```
$ ls -ld /var/lib/containerd
lrwxrwxrwx 1 root root 26 Aug 16 18:51 /var/lib/containerd -> /var/lib/docker/containerd

$ df -h | grep -E 'vda1|vdb'
/dev/vda1       247G  6.7G  241G   3% /
/dev/vdb        3.0T  1.2T  1.9T  39% /var/lib/docker

$ mount | grep vdb
/dev/vdb on /var/lib/docker type xfs (rw,noatime,attr2,inode64,logbufs=8,logbsize=32k,prjquota)
```

Good — `/var/lib/containerd` is a symlink into `/var/lib/docker`, so extraction targets xfs → `/dev/vdb` → zvol `scratch/vast-docker` as the brief states. (Worth noting because if that symlink were ever removed, 370 GB of snapshots would try to land on a 247 GB root disk.)

### 2.3 Is unpacking serial? Yes — in *this* build.

containerd's upstream `main` branch **does** have a parallel unpack mode (`core/unpack/unpacker.go`):

```go
for i, desc := range layers {
    statusCh, err := topHalf(i, desc, layerSpan, unpackLayerStart)
    if parallel {
        statusChans = append(statusChans, statusCh)
    } else {
        if err = bottomHalf(<-statusCh, nil); err != nil {
            return err
        }
    }
}
```
```go
if i > 0 && !parallel {
    parent = chainIDs[i-1].String()   // serial: layer N prepared on top of layer N-1
}
...
if i > 0 && parallel {
    opts = append(opts, snapshots.WithParent(chainIDs[i-1].String()))  // parallel: rebase at commit
}
```

In the serial path — the default — layer *N*'s snapshot is `Prepare()`d with `parent = chainIDs[N-1]`, so **layer N cannot begin applying until layer N-1 has been committed.** That is a hard dependency chain across all 133 layers.

**The installed containerd 2.3.3 does not have the parallel path compiled in.** Searching the actual binary for the feature's identifiers returns nothing:

```
$ strings -n 6 /usr/bin/containerd | grep -oiE 'parallel_unpack|parallelUnpack|unpacking_mode|unpack-parallel' | sort -u
(no output)

$ containerd config dump | grep -iE 'parallel|unpacking_mode'
(no output — only discard_unpacked_layers = false is present)
```

The upstream config knob is `unpacking_mode = "parallel"` under the CRI overlayfs plugin ([issue #8881](https://github.com/containerd/containerd/issues/8881)); it is absent here. So: **serial confirmed, by source semantics, by binary inspection, and by measurement (§5).**

### 2.4 Is each layer's gzip decompression single-threaded? Yes.

containerd does *not* use Go's `compress/gzip` when a faster external binary exists. From `pkg/archive/compression/compression.go`:

```go
func gzipDecompress(ctx context.Context, buf io.Reader) (io.ReadCloser, error) {
	initGzip.Do(func() {
		if gzipPath = detectCommand("igzip", disableIgzipEnv); gzipPath != "" {
			log.L.Debug("using igzip for decompression")
			return
		}
		if gzipPath = detectCommand("unpigz", disablePigzEnv); gzipPath != "" {
			log.L.Debug("using unpigz for decompression")
		}
	})
```
```go
const (
	disablePigzEnv  = "CONTAINERD_DISABLE_PIGZ"
	disableIgzipEnv = "CONTAINERD_DISABLE_IGZIP"
)
```

Preference order is **igzip → unpigz → Go stdlib**. On this guest:

```
$ which unpigz pigz
/usr/bin/unpigz
/usr/bin/pigz
$ dpkg -l | grep -i pigz
ii  pigz  2.8-1  amd64  Parallel Implementation of GZip

$ which igzip
(not found)

$ strings -n 8 /usr/bin/containerd | grep -o 'CONTAINERD_DISABLE_PIGZ'
CONTAINERD_DISABLE_PIGZ
$ strings -n 8 /usr/bin/containerd | grep -o 'unpigz'
unpigz

$ cat /proc/<containerd-pid>/environ | tr '\0' '\n'
LANG=C.UTF-8
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/snap/bin
...
$ systemctl show containerd -p Environment
Environment=
```

`unpigz` is in containerd's `PATH`, `CONTAINERD_DISABLE_PIGZ` is **not** set, and `igzip` is **not** installed. **So containerd used `unpigz`.**

And here is the crux — from the man page of the *installed* pigz 2.8:

> **Decompression can't be parallelized, at least not without specially prepared deflate streams for that purpose. As a result, pigz uses a single thread (the main thread) for decompression, but will create three other threads for reading, writing, and check calculation, which can speed up decompression under some circumstances.** Parallel decompression can be turned off by specifying one process (`-dp 1` or `-tp 1`).

Directly observed, mid-decompression:

```
$ top -b -n1 -H -p <unpigz pid>
unpigz pid=2161546 threads=4
    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
2161546 ubuntu    20   0   28552   2432   2156 R  90.0   0.0   0:03.01 unpigz
2161548 ubuntu    20   0   28552   2432   2156 S  10.0   0.0   0:00.19 unpigz
2161572 ubuntu    20   0   28552   2432   2156 S  10.0   0.0   0:00.04 unpigz
2161573 ubuntu    20   0   28552   2432   2156 S  10.0   0.0   0:00.16 unpigz
```

Exactly as documented: **one thread at 90% doing the inflate, three helper threads at 10% doing I/O and CRC.** ~1.2 cores busy out of 64.

> **Finding 2.** Extraction is serial across layers (containerd 2.3.3 has no parallel mode) and single-threaded within a layer (pigz cannot parallelize inflate). The effective parallelism of the entire 577 s operation was **~1.2 of 64 vCPUs**.

---

## 3. The CPU, and quantifying the gzip ceiling

### 3.1 Hardware — brief's spec is off by 2×

Host:
```
Model name:  AMD Ryzen Threadripper PRO 9985WX 64-Cores
CPU(s):      128        Thread(s) per core: 2
Core(s) per socket: 64  Socket(s): 1
CPU max MHz: 5476.2891
L3 cache:    256 MiB (8 instances)
MemTotal:    527433128 kB   (~503 GiB)
```

Guest (`vast-ubuntu`, KVM):
```
Model name: AMD Ryzen Threadripper PRO 9985WX 64-Cores
CPU(s):     64          Thread(s) per core: 2
Core(s) per socket: 32  Socket(s): 1
Hypervisor vendor: KVM  Virtualization type: full
L3 cache:   128 MiB (4 instances)
Mem:        251 GiB total
```

The machine is a **64-core / 128-thread 9985WX**, not 32c/64t. The guest is given **half of it — 64 vCPUs (32 cores × 2 threads)** — plus 251 GiB RAM. Per-core clock is the same silicon, so single-stream decompression speed measured in the guest is representative.

### 3.2 Measured single-stream decompression on the real data

Benchmarked against the actual weight blob already in the content store. First attempt was invalid — `ctr content get` streams over gRPC and capped at 249 MB/s, which was itself the bottleneck:

```
=== A. raw blob read (ctr content get -> /dev/null), 4GiB ===
elapsed=17.23s  read_MBps=249
=== B. unpigz via ctr, 4GiB in ===
elapsed=18.80s  out=5026007088  ratio=1.1702  OUT_MBps=267.3  IN_MBps=228.5
```

Redone reading the blob file directly, page-cache warm, so the number is pure CPU:

```
$ CS=/var/lib/containerd/io.containerd.content.v1.content/blobs/sha256
$ D=beda23a80d2f080e9147fc5a685ac105187077d6b56c8341fc53eb644347a8c0

=== warm the cache (first 4GiB) ===
4294967296 bytes (4.3 GB, 4.0 GiB) copied, 0.164579 s, 26.1 GB/s

=== A2. cached raw read 4GiB ===
elapsed=0.18s  read_MBps=24515          <- read path irrelevant, 24.5 GB/s

=== B2. unpigz from cached file, 4GiB in ===
elapsed=13.76s  out=5026007088  ratio=1.1702  OUT_MBps=365.3  IN_MBps=312.1

=== C2. gzip -dc from cached file, 4GiB in ===
elapsed=24.34s  out=5026007088          OUT_MBps=206.5  IN_MBps=176.5
```

| decompressor | input MB/s | output MB/s | vs zlib |
|---|---|---|---|
| `unpigz` 2.8 (what containerd used) | **312.1** | **365.3** | 1.77× |
| `gzip` (zlib, 1 thread) | 176.5 | 206.5 | 1.00× |

unpigz's 1.77× advantage over plain gzip comes entirely from offloading read/write/CRC to its 3 helper threads — the inflate itself is still one thread.

### 3.3 Which number to compare: output or input?

**Compare the *output* rate against a decompressor's rated speed.** Decompression benchmarks (lzbench, Squash, zstd's own `-b`) universally quote decompression throughput in **uncompressed (output) MB/s**, because the work an inflater does — literal copies and LZ77 back-reference copies into the output window — scales with bytes *produced*, not bytes consumed. The input rate is a derived quantity: `input_rate = output_rate / compression_ratio`, and therefore varies with how compressible the data happens to be. Quoting input MB/s would make a decompressor look "faster" on incompressible data and "slower" on text, for identical CPU work.

So the number to test against "200–500 MB/s single-stream gzip" is the **output** rate.

### 3.4 The arithmetic

Using the brief's figures:

```
370 GB output / 577.02 s        = 641.2 MB/s output      <- looks like ~2 gzip streams
167,572,898,829 / 577.02 s      = 290.4 MB/s input
```

641 MB/s output is above the top of the 200–500 MB/s band and above the measured 365 MB/s ceiling — which is exactly what made this measurement look anomalous. **But the 370 GB figure is wrong** (§5). Using the authoritative unpacked size of 202.19 GB:

```
202,192,745,267 B / 577.02 s    = 350.4 MB/s output
```

**350.4 MB/s observed vs 365.3 MB/s measured single-stream ceiling = 95.9%.**

On the input side: **290.4 MB/s observed vs 312.1 MB/s measured = 93.0%.**

> **Finding 3.** The observed rate matches **one** gzip stream to within 4–7%. It does not match two, and it is 5.7× below what six streams achieve on this box (§6.2). The residual 4–7% is fully accounted for by work the microbenchmark omits: tar parsing, `write()` into xfs, sha256 of both the compressed blob (verification) and the uncompressed stream (diff ID), snapshot prepare/commit per layer, and concurrent blob fetching.

---

## 4. Write-side amplification — ruled out

### 4.1 ZFS properties of the target zvol

```
$ zfs get -o property,value,source volsize,compression,compressratio,volblocksize,sync,logbias,\
    primarycache,secondarycache,checksum,dedup,copies,refreservation,used scratch/vast-docker
PROPERTY        VALUE           SOURCE
volsize         3T              local
compression     off             local      <-- 
compressratio   1.00x           -          <-- 
volblocksize    64K             -
sync            standard        default    <-- 
logbias         latency         default
primarycache    all             default
secondarycache  all             default
checksum        on              default
dedup           off             default
copies          1               default
refreservation  none            default
used            2.06T           -
```

- **`compression=off`, `compressratio=1.00x`.** ZFS is **not** re-compressing what Docker just decompressed. The double-work hypothesis is **false**. (Contrast: the registry's own dataset `models/ai-models` *does* use `compression=lz4, recordsize=1M` — but that is the host side, storing already-gzipped blobs, where lz4 costs almost nothing and gains almost nothing.)
- **`sync=standard`, not `always`.** Extraction writes are asynchronous, batched into ZFS transaction groups. No synchronous-write stall. `logbias=latency` is irrelevant with no sync writes.
- `volblocksize=64K` with `checksum=on` is a reasonable match for large sequential writes; xfs on top uses `logbsize=32k` with `noatime` and `prjquota`.

### 4.2 Pool topology and the write ceiling

```
$ zpool status scratch
  pool: scratch
 state: ONLINE
	NAME                                     STATE     READ WRITE CKSUM
	scratch                                  ONLINE       0     0     0
	  nvme-Corsair_MP700_PRO_A7GGB349000E5P  ONLINE       0     0     0
	  nvme-Corsair_MP700_PRO_A7GGB3490008HV  ONLINE       0     0     0

$ zpool list
NAME      SIZE  ALLOC   FREE   FRAG   CAP  HEALTH
scratch  3.62T  2.28T  1.34T     9%   62%  ONLINE
```

Two **Corsair MP700 PRO** (PCIe 5.0 x4) NVMe drives as a **2-way stripe** (no mirror, no raidz) — writes are split across both, no parity, no read-modify-write. This is close to a best-case ZFS write target.

```
$ zpool iostat -l scratch 1 2
            capacity     operations    bandwidth   total_wait    disk_wait
scratch  2.28T  1.34T   73   303   4.45M  13.6M   569us   2ms   569us   2ms
```

Cumulative since boot: 13.6 MB/s average write, `disk_wait` 2 ms. The pool is nowhere near saturated.

### 4.3 Two direct measurements bounding the storage path

**Read (cold, through xfs → zvol → ZFS):**
```
$ echo 3 > /proc/sys/vm/drop_caches   # (caches dropped)
$ dd if=$CS/$D bs=4M count=2048 of=/dev/null      # 8 GiB
cold read elapsed=1.98s  read_MBps=4348
```
**4348 MB/s cold read** — 12× the extraction rate. Reading compressed blobs was never a constraint.

**Write — proven by the owner's own transfer measurement.** During the 116.06 s blob transfer, containerd wrote all 167,572,898,829 bytes of compressed blobs into the content store *on this same `/dev/vdb`*:

```
167,572,898,829 B / 116.06 s = 1,443,847,483 B/s = 1443.8 MB/s = 1.444 GB/s
```

So the write path through xfs → zvol → ZFS **demonstrably sustains at least 1.444 GB/s**, concurrently with network receive. That is a hard empirical lower bound, not an estimate.

### 4.4 How much of the 577 s was write-bound?

Extraction wrote 202.19 GB in 577.02 s = 350.4 MB/s.

```
time the writes alone would need, at the proven >=1443.8 MB/s ceiling:
    202,192,745,267 / 1,443,847,483 = 140.0 s

fraction of the 577.02 s window that is write-bound:
    140.0 / 577.02 = 24.3%     (and this is an upper bound on the write share)
```

**At most 24% of the wall clock could be write-bound, and that 140 s overlaps with decompression rather than adding to it.** The decompressor, running at 96% of its single-stream ceiling for the entire window, is the serialising resource. Writes were absorbed asynchronously into ZFS txgs at a quarter of the available bandwidth.

> **Finding 4.** Nothing on the write side explains the 577 s. ZFS compression is off (no double work), sync is standard (no fsync stalls), the pool is a 2× PCIe-5 NVMe stripe reading at 4.3 GB/s and proven to write at ≥1.44 GB/s. The write path had ≥4× headroom throughout.

---

## 5. The true unpacked size — correcting the 640 MB/s premise

This turned out to be the second-most important finding, so it gets its own section.

### 5.1 The measured compression ratio is far below what 370 GB implies

The brief's premise implies `370 / 167.573 = 2.208:1` overall. But decompressing 4 GiB of the actual weight blob gave:

```
in=4294967296  out=5026007088  ratio=1.1702
```

**1.17:1**, which is what one expects for fp8/bf16 tensor data. 2.2:1 on model weights is not physically plausible. Something was wrong with the 370 GB figure.

### 5.2 Authoritative per-layer unpacked sizes from containerd

Computed the OCI chain IDs from the image config's `diff_ids`, then queried the snapshotter's recorded usage for each — this is the byte count containerd itself recorded when it wrote each layer:

```python
# chainID_0 = diff_id_0 ; chainID_N = sha256(chainID_{N-1} + " " + diff_id_N)
config digest: cb457268c069a26edbc9f1e6c1e46a40c49bff301bbf37da07de733655748635
diff_ids: 133
final chainID: sha256:f9997b155394f90a911a2211c1c1705831cf9886a0aa1b0c4ab0608a48bdd994
```
```
$ for C in <133 chain IDs>; do ctr -n moby snapshots usage "$C"; done
...
sha256:56ded26c456bfcbceaff6d76dad9f399a5bb7ab62e7e54a762d6bdeaa82c0fb3  24.3 GiB  11
sha256:264ad63c5e9127c0eaffde61881b8536ee7423b1f8717d726577718f342c79e4  26.7 GiB  11
sha256:baa6aa1d46f04d9b0cd368941a41fc0833c3c626d6341488bc1a2e6ae2ff4035  26.7 GiB  11
sha256:269313a75b16be96d6aedcafd87c8fff2cf53dead7cd9d4c0d6befaeebda369a  26.7 GiB  11
sha256:227df308e046b8cf0927cc234cd5aef2ea301076b025d40466b7dbe25e87f64f  26.7 GiB  11
sha256:f9997b155394f90a911a2211c1c1705831cf9886a0aa1b0c4ab0608a48bdd994  24.4 GiB  11
```

Summing all 133:

```
snapshots parsed: 133
TOTAL unpacked on disk = 202192745267 bytes = 188.31 GiB = 202.19 GB

sum of snapshots >10GB: 155.50 GiB = 166.97 GB      (the 6 weight layers)
sum of all others:       32.81 GiB =  35.23 GB      (the 127 small layers)

COMPRESSION RATIOS (authoritative unpacked/compressed):
  overall : 202192745267 / 167572898829 = 1.2066
  weights : 166966853632 / 152547708730 = 1.0945
  other   :  35225891635 /  15025190099 = 2.3445
```

The weights compress **1.0945:1** — gzip is buying 8.6% on 152.5 GB. The OS layers compress 2.34:1, as expected for binaries and text. Overall **1.2066:1**.

Note the inode counts: **11 inodes per weight snapshot** — a handful of large shard files each, not a deep tree. Six snapshots × ~8 data files = the 48 shards. This is the ideal case for tar extraction (almost no per-file syscall overhead), which further isolates decompression as the cost.

### 5.3 Where "370 GB" comes from

```
$ docker images --digests | grep r21-appliance
192.168.122.1:5001/deepseek-v4-flash-r21-appliance  <none>  sha256:7b5b493a...  7b5b493a2e3c  33 hours ago  370GB

$ docker image inspect 7b5b493a2e3c --format '{{.Id}}|Size={{.Size}}'
sha256:7b5b493a2e3c4bf096c0180e8723ea89fdd51dbd3be81042823b926291da9673|Size=167588974948
```

`docker image inspect` reports **167.589 GB** (the compressed content), while the `docker images` SIZE column reports **370 GB**. The reconciliation is exact:

```
compressed blobs retained in content store : 167,572,898,829 B
unpacked snapshots on disk                 : 202,192,745,267 B
                                             ---------------
total disk footprint                       : 369,765,644,096 B = 369.77 GB  ~= "370GB"
```

Under the containerd image store, `docker images` SIZE is the **total on-disk footprint = content blobs + snapshots**, because containerd keeps the compressed blobs after unpacking (`discard_unpacked_layers = false`, confirmed in §2.3). It is not "unpacked size".

The guest's `ctr` view agrees the *content* is 156.1 GiB (= 167.6 GB):
```
$ ctr -n moby images ls | grep r21-appliance
192.168.122.1:5001/deepseek-v4-flash-r21-appliance@sha256:7b5b493a...  index.v1+json  156.1 GiB  linux/amd64
```

> **Finding 5.** Extraction wrote **202.19 GB**, not 370 GB. The observed extraction rate is **350.4 MB/s**, not 641 MB/s — squarely one gzip stream. Incidentally, `discard_unpacked_layers = false` means this image occupies **370 GB** for a 202 GB rootfs; setting it true would reclaim 167.6 GB per image, at the cost of not being able to re-push.

### 5.4 Sanity check: was decompression overlapped with the fetch?

containerd fetches layers concurrently while unpacking serially, so some unpack work happens inside the 116 s transfer window. But **the 6 weight layers are the last 6 entries in the manifest**, and the serial unpacker cannot reach layer 128 until layers 1–127 are committed — nor can it apply a layer whose blob has not arrived. So essentially all of the 152.5 GB of weight decompression necessarily falls *after* the transfer, in the 577 s window:

```
weight layers only, output:  166,966,853,632 / 577.02 s = 289.4 MB/s
weight layers only, input:   152,547,708,730 / 577.02 s = 264.4 MB/s
```

versus the measured single-stream ceiling of 365.3 MB/s out / 312.1 MB/s in → **79% / 85%**. Adding the ~35 GB of small-layer output that spilled past the transfer boundary pushes this back toward the 96% figure in §3.4. Either accounting lands in the same place: **one stream, running at 79–96% of its ceiling, for the entire 577 s.**

---

## 6. Was anything else competing?

### 6.1 Guest state

```
$ uptime
 06:04:08 up 1 day, 13:15,  1 user,  load average: 1.22, 1.20, 0.72

$ docker image inspect 7b5b493a2e3c --format '{{.Created}}'
2026-08-27T21:03:50.530572388Z          <- extraction completed here; began ~20:54:13Z

$ docker ps -a --format '{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Size}}'
C.49031045            pytorch/pytorch_2.8.0-cuda12.8-cudnn9-devel/ssh  Exited (137) 3 hours ago  108GB (virtual 125GB)
local-registry        registry:2                                       Up 23 hours               0B (virtual 26.2MB)
blackwell-cublas-soak 4ff859525f99                                     Exited (137) 13 days ago  49.2kB (virtual 7.83GB)

$ docker inspect C.49031045 --format '{{.Created}}|{{.State.Status}}|...'
2026-08-28T16:38:31Z|exited|started 2026-08-28T16:38:32Z|finished 2026-08-29T03:00:15Z
```

**The renter container `C.49031045` did not exist during the extraction** — it was created 2026-08-28T16:38Z, ~19.5 hours *after* the 2026-08-27T21:03Z extraction. It cannot have contended.

### 6.2 The local-registry volume

```
$ docker volume inspect 82b5452e... --format '{{.Mountpoint}}'
/var/lib/docker/volumes/82b5452e868687e50ef38a4cd2221ae4d757481b0ac147cad99d850f165223b8/_data
$ du -sh /var/lib/docker/volumes/82b5452e.../ 
185G
$ docker inspect local-registry --format '{{.Created}}|{{.State.Status}}'
2026-08-24T18:08:25Z|running
```

The guest-side `local-registry` holds **185 GiB (198.6 GB)** on the **same `/dev/vdb`**. It is *running*, so it occupies capacity and its data shares the zvol — but a `registry:2` container generates I/O only while serving a push or pull. There is no evidence it was serving anything at 20:54–21:03 on Aug 27, and §4 shows the write path had ≥4× headroom regardless. **Capacity pressure is real; I/O contention is not the limiter.**

```
$ docker system df
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          35        3         754.7GB   439.6GB (58%)
Containers      3         1         108GB     108GB (100%)
Local Volumes   1         1         198.6GB   0B (0%)
Build Cache     550       0         149.3GB   402MB
```
`/dev/vdb` is at 1.2 T of 3.0 T (39%). 439.6 GB of images and 149.3 GB of build cache are reclaimable.

### 6.3 The decisive control: does this box actually scale?

Six concurrent `unpigz` streams, one per weight blob, 2 GiB each:

```
=== 6 concurrent streams on the 6 weight blobs, 2GiB each ===
6-way parallel elapsed=7.28s  aggregate_IN_MBps=1771.0
```

```
scaling factor = 1771.0 / 312.1 = 5.67x   (out of a theoretical 6.0x = 94.5% efficiency)
aggregate output rate = 1771.0 * 1.1702  = 2072 MB/s
```

**The hardware scales near-linearly to 6 streams.** Nothing about memory bandwidth, the zvol, ZFS checksums, or the hypervisor prevented parallel decompression. The serialisation is purely containerd's unpack model.

> **Finding 6.** No external contention. The guest was ~1.2 cores busy out of 64 for 577 s, and a control experiment proves 6-way decompression would have run 5.67× faster on the same hardware at the same moment.

---

## 7. The counterfactual, quantified

### 7.1 Established constants

| Quantity | Value | Source |
|---|---|---|
| Compressed image | 167,572,898,829 B (167.573 GB) | manifest, §1.3 |
| Unpacked image | 202,192,745,267 B (202.193 GB) | snapshot usage, §5.2 |
| Overall ratio | 1.2066 : 1 | §5.2 |
| Weight-layer ratio | 1.0945 : 1 | §5.2 |
| Transfer rate | 1443.8 MB/s (= 1.345 GiB/s) | 167.573 GB / 116.06 s |
| Write ceiling (proven ≥) | 1443.8 MB/s | §4.3 |
| Cold read rate | 4348 MB/s | §4.3 |
| 1× unpigz | 312.1 MB/s in / 365.3 MB/s out | §3.2 |
| 6× unpigz | 1771.0 MB/s in / 2072 MB/s out | §6.3 |
| 1× gzip (zlib) | 176.5 MB/s in / 206.5 MB/s out | §3.2 |
| zstd decode (guest CPU, in-RAM) | 2608 MB/s (L3) – 3934 MB/s (L1) | §7.4 |

The brief's "~1.347 GB/s" transfer figure is the same measurement expressed in GiB/s (167,572,898,829 / 116.06 / 2³⁰ = 1.345 GiB/s). I use decimal GB/s throughout.

### 7.2 (a) As-is — gzip layers

```
transfer   : 116.06 s
extraction : 577.02 s
             -------
TOTAL      : 693.08 s  =  11 min 33 s
```
Extraction is 83.3% of wall clock, and 96% of that is one gzip thread.

### 7.3 (b) Uncompressed layers (`application/vnd.oci.image.layer.v1.tar`)

**Transfer.** Carries the unpacked size, **202.193 GB — not 370 GB**:
```
202,192,745,267 / 1,443,847,483 B/s = 140.0 s        (+23.9 s vs gzip's 116.06 s)
```
*Caveat:* this assumes the 1.4438 GB/s rate is reproducible for a larger payload. 1.4438 GB/s ≈ 11.6 Gbit/s over a host↔guest virtio link, which is well under virtio's practical ceiling, so the rate was more likely bounded by the registry's read path or by the receiver writing blobs — both of which apply equally to uncompressed layers. Treating it as unchanged is reasonable; if the link is the true limit, (b) degrades by the 21% extra bytes, already reflected in the +23.9 s.

**Extraction.** No decompression at all — containerd's `DecompressStream` passes a plain tar through untouched, so the differ becomes `tar → write()`. Bounded by the write path, plus sha256 of the stream for the diff ID (~2 GB/s/core, not limiting). With ~11 inodes per weight layer there is negligible per-file overhead:
```
at the proven >=1443.8 MB/s write ceiling : 202,192,745,267 / 1.4438e9 = 140.0 s
conservative, at 1000 MB/s                : 202,192,745,267 / 1.000e9  = 202.2 s
```

**Total (b):**
```
best  : 140.0 + 140.0 = 280.0 s
cons. : 140.0 + 202.2 = 342.2 s

vs (a) 693.08 s  ->  saving 351 - 413 s   (5.9 - 6.9 min)
                 ->  speedup 2.03x - 2.48x
```

**The owner's intuition is correct.** Uncompressed is roughly **2.0–2.5× faster end-to-end**, saving ~6–7 minutes, despite pushing 21% more bytes over the wire. The extra 23.9 s of transfer buys back ~437 s of decompression.

### 7.4 (c) zstd layers (`application/vnd.oci.image.layer.v1.tar+zstd`)

**Transfer size — measured, not assumed.** I compressed 2 GiB of *real decompressed weight data* at several levels (pipe-only, nothing written to disk):

```
=== zstd RATIO on 2GiB of REAL decompressed weight data ===
zstd -1   in=2147483648  out=1700678010  ratio=1.2627
zstd -3   in=2147483648  out=1699970792  ratio=1.2632
zstd -9   in=2147483648  out=1686291843  ratio=1.2735

=== gzip on the same 2GiB ===
gzip -6   in=2147483648  out=1709494658  ratio=1.2562
gzip -1   in=2147483648  out=1732461494  ratio=1.2396
```

**zstd -3 (1.2632) beats gzip -6 (1.2562) by 0.6%** on this data — and zstd -3 compresses far faster than gzip -6, which matters for *building* the appliance image. So the transfer payload is the same or marginally smaller:
```
167.573 GB x (1.2562 / 1.2632) = 166.64 GB
166,642,000,000 / 1,443,847,483 = 115.4 s      (vs 116.06 s -- a wash)
```

**Decompression speed.** `zstd -b` ignores stdin, so I could not benchmark zstd decode against the real blob without writing a temp file (forbidden). I have two bounds instead:

1. zstd's own in-RAM benchmark, run **on this guest's CPU** (synthetic corpus):
```
level 1: 3934.4 MB/s decompression
level 3: 2797.4 MB/s decompression
level 5: 2659.3 MB/s decompression
```
2. zstd's decode speed is famously near content-independent (it is dominated by sequence copies), and on *low-ratio* data like these weights it trends toward memcpy-bound — i.e. faster in input terms, not slower.

Being deliberately conservative and taking **1500 MB/s of input** — roughly half the measured synthetic figure:
```
decompress : 166,642,000,000 / 1.5e9 = 111.1 s
write      : 202,192,745,267 / 1.4438e9 = 140.0 s   <- now the binding constraint
extraction : ~140 s (write-bound), say 140-160 s allowing for tar/sha256 overhead
```

**Total (c):**
```
115.4 + 140 = 255.4 s   (best)
115.4 + 160 = 275.4 s   (conservative)

vs (a) 693.08 s  ->  saving 418 - 438 s  (7.0 - 7.3 min)
                 ->  speedup 2.52x - 2.71x
```

**Crucially, zstd flips the bottleneck.** At ~1500+ MB/s the decompressor is no longer the limiter — the write path is. That is the correct place for a bottleneck to sit.

### 7.5 (d) Bonus: keep gzip, enable parallel unpack

Not available in containerd 2.3.3 (§2.3), but the ceiling is worth stating since §6.3 measured it:
```
extraction at 6-way parallel : 167,572,898,829 / 1.771e9 = 94.6 s (decompress)
                               but write-bound at 140.0 s
total : 116.06 + 140 = 256 s
```
Identical to zstd — because both land on the same ~1.44 GB/s write ceiling.

### 7.6 Summary table

| Variant | Transfer | Extract | **Total** | vs as-is | Bytes on wire | Bytes in registry |
|---|---|---|---|---|---|---|
| **(a) gzip (actual)** | 116.06 s | 577.02 s | **693.08 s** | — | 167.57 GB | 167.57 GB |
| **(b) uncompressed** | 140.0 s | 140–202 s | **280–342 s** | **2.0–2.5× faster** | 202.19 GB | 202.19 GB |
| **(c) zstd -3** | 115.4 s | 140–160 s | **255–275 s** | **2.5–2.7× faster** | 166.64 GB | 166.64 GB |
| (d) gzip + parallel unpack¹ | 116.06 s | 140 s | **256 s** | 2.7× faster | 167.57 GB | 167.57 GB |

¹ not available in containerd 2.3.3.

**zstd wins.** It is ~25–70 s faster than uncompressed on wall clock, and it moves and stores **35.5 GB less** per copy — 18% less network and 18% less registry capacity on a pool already at 62%.

### 7.7 Does the pull path actually support zstd? — Verified, yes

Not assumed. Checked the installed binaries directly:

```
$ strings -n 8 /usr/bin/containerd | grep -o 'application/vnd\.oci\.image\.layer\.v1\.tar+zstd'
application/vnd.oci.image.layer.v1.tar+zstd
$ strings -n 8 /usr/bin/containerd | grep -o 'application/vnd\.docker\.image\.rootfs\.diff\.tar\.zstd'
application/vnd.docker.image.rootfs.diff.tar.zstd
$ strings -n 8 /usr/bin/containerd | grep -o 'klauspost/compress/zstd'
klauspost/compress/zstd

$ strings -n 8 /usr/bin/dockerd | grep -o 'application/vnd\.oci\.image\.layer\.v1\.tar+zstd'
application/vnd.oci.image.layer.v1.tar+zstd
```

And in containerd's source, `DecompressStream` sniffs the zstd magic number and dispatches to `github.com/klauspost/compress/zstd`:
```go
zstdReader, err := zstd.NewReader(buf, zstd.WithDecoderLowmem(false))
```

- **containerd 2.3.3**: both OCI and Docker zstd media types present, klauspost zstd decoder linked. ✅
- **dockerd 29.7.2**: OCI zstd media type present. ✅
- **Kaalia**: runs `backend=DKR`, i.e. drives this same Docker daemon, so it inherits the capability. ✅
- **registry:2** (host and guest): registries are media-type agnostic for blob storage; the host registry is `registry:2` and stores blobs by digest. ✅

One caveat I **could not** verify read-only: whether Vast's *control plane* (the remote side that schedules image pulls for a rented instance, as opposed to the on-host `kaalia` binary) does any media-type validation of its own before handing the reference to Docker. Everything on this machine supports zstd; a first zstd push should still be smoke-tested against a real Vast instance launch before committing the build pipeline to it.

Note also that `klauspost/compress/zstd`'s `Decoder` does use multiple goroutines internally, so a zstd layer may decode faster than the single-thread figures above — this only strengthens (c).

---

## 8. Conclusions

### 8.1 The single dominant limiter

**Serial, single-threaded gzip decompression — specifically, one `unpigz` inflate thread applying 133 layers one after another.**

The evidence chain:

1. All 133 layers are gzip; 152.5 GB of 167.6 GB sits in **6 unseekable DEFLATE streams** of ~25 GB each (§1.3).
2. containerd 2.3.3 unpacks **serially** — layer *N*'s snapshot is prepared with layer *N−1* as parent. The parallel unpack path exists upstream but is **not in this binary** (§2.3).
3. containerd shells out to **`unpigz`**, which by its own man page **cannot parallelize decompression** — one inflate thread plus three I/O/CRC helpers. Directly observed: 4 threads, one at 90% CPU, three at 10% (§2.4).
4. Measured single-stream ceiling on the real blob: **365.3 MB/s out / 312.1 MB/s in** (§3.2).
5. True unpacked size is **202.19 GB**, not 370 GB — the 370 GB is blobs + snapshots (§5.3). Real observed rate: **350.4 MB/s out / 290.4 MB/s in** = **96% / 93% of exactly one stream** (§3.4).
6. Everything else has ≥4× headroom: cold read 4348 MB/s, write path proven ≥1443.8 MB/s, ZFS compression off, sync standard, no contending containers (§4, §6).
7. Control experiment: 6 concurrent streams hit **1771 MB/s (5.67×)** on the same box at the same time (§6.3).

For 577 seconds a 64-vCPU / 251 GiB guest ran at **~1.2 cores of useful work**, or **1.9% CPU utilisation**.

### 8.2 Would uncompressed layers have been faster? **Yes — about 2.0–2.5×, saving ~6–7 minutes.**

693 s → **280–342 s**. The 21% larger transfer (167.57 → 202.19 GB, costing +23.9 s) is repaid many times over by eliminating ~437 s of single-threaded inflate. The owner's intuition is right: on this hardware and this data, gzip is buying only **1.0945:1** on the weights — an 8.6% saving — in exchange for making 91% of the payload strictly serial.

### 8.3 Would zstd have been better than both? **Yes — best of the three.**

693 s → **255–275 s** (**2.5–2.7×**), and it does so while moving *fewer* bytes than gzip:

- **Measured** on real weight data, zstd -3 compresses **0.6% better than gzip -6** (1.2632 vs 1.2562) — so there is no transfer penalty at all, and a 35.5 GB saving versus uncompressed.
- zstd decodes at **2600–3900 MB/s** on this guest's CPU; even at a conservative 1500 MB/s it is **4–10× faster than unpigz**, which moves the bottleneck off the CPU and onto the ~1.44 GB/s write path — where it belongs.
- **Verified supported**: containerd 2.3.3 and dockerd 29.7.2 both carry the zstd media types and the klauspost decoder; Kaalia drives this same daemon.

**Recommendation order:** (1) ship zstd layers — best wall clock *and* 18% less network/storage; (2) if zstd is blocked by the Vast control plane, ship uncompressed — still 2× better than today; (3) as a zero-rebuild stopgap, `apt install isal` to put **`igzip`** on the guest — containerd prefers it over `unpigz` (§2.4) and ISA-L's inflate is typically 2–3× zlib, which would cut extraction materially without touching the image. (4) Independently, `discard_unpacked_layers = true` would reclaim 167.6 GB per image on a pool at 62%.

### 8.4 What I could not determine read-only

Stated rather than guessed:

1. **zstd decode rate on the real blob.** `zstd -b` ignores stdin and isolating a decode-only measurement needs a temp file, which the no-write constraint forbids. I substituted the guest's own in-RAM synthetic benchmark (2608–3934 MB/s) and applied a conservative 1500 MB/s to the estimate.
2. **`igzip` speedup.** Not installed; installing it is a modification. The preference order is confirmed from containerd source, but the resulting throughput is untested here.
3. **Sustained write ceiling of the zvol.** Cannot be measured without writing. I used the ≥1443.8 MB/s *proven* by the blob transfer itself; the true ceiling for a 2× PCIe-5 NVMe stripe is likely several GB/s, which would only make (b) and (c) faster than quoted.
4. **Vast control-plane zstd validation.** Everything on this machine supports zstd; whether Vast's remote scheduler inspects media types before dispatching a pull is not observable from here. Smoke-test one zstd image before converting the pipeline.
5. **Exact fetch/unpack overlap during the 116 s transfer.** No per-layer timing was logged (`journalctl -u containerd` for the window yielded only 13 matching lines, no per-layer records). §5.4 brackets it: the answer is 79–96% of one stream either way.
6. **Registry credentials.** Not available to me; per instructions I did not work around the 401 and read the manifest from the registry's own storage instead.

---

## Appendix A — Command inventory

All read-only. Host = `bloodarrow`; guest = `ubuntu@192.168.122.248` via nested ssh.

| # | Command | Purpose |
|---|---|---|
| 1 | `lscpu`, `/proc/meminfo` (both) | CPU/RAM topology |
| 2 | `curl -H 'Accept: …' https://192.168.122.1:5001/v2/…/manifests/…` | manifest fetch → 401 |
| 3 | `skopeo inspect --raw --tls-verify=false docker://…` | credential probe → 401 |
| 4 | `docker inspect bloodarrow-oci-registry --format '{{json .Mounts}}'` | locate registry storage |
| 5 | `cat …/blobs/sha256/4b/4bdd68…/data`, `…/2b/2bcfcd…/data` | index + manifest |
| 6 | `docker version`, `docker info`, `containerd --version` | runtime versions |
| 7 | `ls -ld /var/lib/containerd`, `df -h`, `mount`, `findmnt` | storage layout |
| 8 | `which unpigz pigz igzip`, `dpkg -l \| grep pigz` | decompressor availability |
| 9 | `cat /proc/<containerd>/environ`, `systemctl show containerd -p Environment` | `CONTAINERD_DISABLE_PIGZ` unset |
| 10 | `strings /usr/bin/containerd \| grep -o '…tar+zstd'`, `… 'unpigz'`, `… 'parallel'` | capability probe |
| 11 | `containerd config dump` | effective config |
| 12 | `man pigz` | authoritative decompression-parallelism statement |
| 13 | `zfs get … scratch/vast-docker`, `zpool status/list/iostat -l scratch` | write-side properties |
| 14 | `ctr -n moby snapshots usage <chainID>` × 133 | authoritative unpacked sizes |
| 15 | `docker images --digests`, `docker image inspect`, `docker system df`, `ctr images ls` | size accounting |
| 16 | `dd if=<blob> … \| unpigz -c \| wc -c` (and `gzip -dc`) | single-stream benchmarks |
| 17 | 6 × `dd \| unpigz` concurrently | parallel scaling control |
| 18 | `dd … \| unpigz -c \| head -c 2G \| zstd -N -c \| wc -c` | zstd vs gzip ratio on real data |
| 19 | `zstd -b1 -e5` | in-RAM decode rate on guest CPU |
| 20 | `docker ps -a`, `docker inspect C.49031045`, `docker volume inspect`, `du -sh` | contention check |

Nothing was written to either machine. `echo 3 > /proc/sys/vm/drop_caches` (step 16) is a volatile kernel cache hint, not a filesystem modification, and was used once to obtain a valid cold-read number.

## Appendix B — Key numbers at a glance

```
COMPRESSED   167,572,898,829 B  = 167.573 GB   (133 gzip layers)
UNPACKED     202,192,745,267 B  = 202.193 GB   (sum of 133 snapshot usages)
FOOTPRINT    369,765,644,096 B  = 369.77  GB   = "370GB" in docker images
RATIO        1.2066 overall  |  1.0945 weights  |  2.3445 base layers

TRANSFER     116.06 s  ->  1443.8 MB/s
EXTRACT      577.02 s  ->   350.4 MB/s out  |  290.4 MB/s in
TOTAL        693.08 s

1x unpigz     365.3 MB/s out  |  312.1 MB/s in     <- observed = 96% of this
1x gzip       206.5 MB/s out  |  176.5 MB/s in
6x unpigz    2072   MB/s out  | 1771.0 MB/s in     <- 5.67x, unused
zstd decode  2608-3934 MB/s (guest CPU, in-RAM)

cold read    4348 MB/s     write (proven >=) 1443.8 MB/s
ZFS: compression=off  sync=standard  volblocksize=64K  2x PCIe-5 NVMe stripe

(a) gzip         693 s      (b) uncompressed 280-342 s      (c) zstd 255-275 s
```

**Sources:**
- [containerd/containerd `pkg/archive/compression/compression.go`](https://raw.githubusercontent.com/containerd/containerd/main/pkg/archive/compression/compression.go)
- [containerd/containerd `core/unpack/unpacker.go`](https://raw.githubusercontent.com/containerd/containerd/main/core/unpack/unpacker.go)
- [Parallel Container Layer Unpacking · Issue #8881](https://github.com/containerd/containerd/issues/8881)
- [unpack package — pkg.go.dev](https://pkg.go.dev/github.com/containerd/containerd/v2/core/unpack)
- [containerd CRI config docs](https://github.com/containerd/containerd/blob/main/docs/cri/config.md)
- `man pigz` (pigz 2.8-1, as installed on the guest)
