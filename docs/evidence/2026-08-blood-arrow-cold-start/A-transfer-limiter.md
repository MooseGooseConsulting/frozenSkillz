# What limited the OCI registry pull to ~1.35 GB/s

**Target measurement:** Run 1 pulled **156.32 GB of blobs in 116.06 s** = **1.3467 GB/s** = **10.774 Gbit/s**.

**Verdict up front:** The primary limiter is the **single-queue virtio-net NIC on `vast-ubuntu`, served by exactly one `vhost-net` kernel thread**. The traffic did **NOT** touch a physical network — it could not have, because the only live physical port on the box negotiated at **2.5 Gb/s**, which is 4.3x *slower* than the measured transfer.

Investigation performed 2026-08-29 against host `bloodarrow` (Linux 7.1.8-zen1-3-zen) and guest `vast-ubuntu` (192.168.122.248). Everything below is read-only: `ip`, `tc`, `virsh dumpxml`, `ps`, `ethtool`, `docker inspect`, `zpool`/`zfs get`, and `/proc` + `/sys` counters. Nothing was created, modified, restarted, or reconfigured. The renter container `C.49031045` was never touched.

---

## 0. Executive summary of the ranking

| # | Candidate limiter | Verdict | Headroom / load at 1.3467 GB/s |
|---|---|---|---|
| 1 | **virtio-net single queue / single `vhost-net` thread** | **PRIMARY** | one thread at ~50-89% of one core; **cannot scale out** |
| 2 | Gzip decompression (pigz, 1.91-2.00x expansion) | Plausible co-limiter, **unresolved read-only** | ~857 MB/s inflate output per stream needed |
| 3 | Docker `max-concurrent-downloads = 3` | Contributing multiplier, not the wall | forces exactly 3 streams x 449 MB/s |
| 4 | MTU 1500 on the virtual path | Secondary contributor | TSO/GSO/GRO all working; still per-1500B copy cost in vhost |
| 5 | Registry process / TLS single-core | **Ruled out** | registry used 0.84 core-equivalents across 60 threads, no cgroup cap |
| 6 | ZFS read from `models` | **Ruled out** | ~5-13% of a 2x Gen5 NVMe stripe |
| 7 | **Physical 10 GbE in the path** | **RULED OUT — categorically** | no physical NIC is enslaved to `virbr0`; only live port is 2.5 Gb/s |
| 8 | tc / QoS shaping on `virbr0` | **Ruled out** | HTB root qdisc with **zero classes** (libvirt default shell) |
| 9 | `docker-proxy` userspace relay | **Ruled out** | in-kernel DNAT rule matches; proxy holds listen-fd only |
| 10 | TCP window / packet loss | **Ruled out** | 6 MiB rmem vs ~75 KB BDP; 111 retransmits lifetime |

---

## 1. The actual network path

### 1.1 Which interface owns 192.168.122.1

```
$ ip -o addr show | grep -F '192.168.122.1'
6: virbr0    inet 192.168.122.1/24 brd 192.168.122.255 scope global virbr0

$ ip route get 192.168.122.248
192.168.122.248 dev virbr0 src 192.168.122.1 uid 1000
    cache
```

`192.168.122.1` is **`virbr0`**, the stock libvirt `default` NAT network bridge. The route to the guest goes out `virbr0`. No gateway, no next hop — it is a directly attached L2 segment.

### 1.2 What is enslaved to virbr0

```
$ bridge link show
3: enp212s0f0np0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 hwmode VEPA
4: enp212s0f1np1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 hwmode VEPA
10: vnet0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 master virbr0 state forwarding priority 32 cost 2
18: veth35e3cfa@...: mtu 1500 master br-3f4a98f1a487 state forwarding
19: veth5b81149@...: mtu 1500 master br-6c557f259649 state forwarding
20: veth64eb5e4@...: mtu 1500 master br-a0b1f880f8df state forwarding
21: veth4ca8805@...: mtu 1500 master br-a0b1f880f8df state forwarding
341: veth9ac0f23@...: mtu 1500 master br-d2506ec10d64 state forwarding
342: veth42b097f@...: mtu 1500 master br-d2506ec10d64 state forwarding
664: veth74927f5@...: mtu 1500 master docker0 state forwarding
```

Read the `master` field. **The only port whose master is `virbr0` is `vnet0`** — the VM's tap device. The two physical `enp212s0f*` lines carry no `master` at all; they are listed because `bridge link show` enumerates every device with a bridge-capable link layer, and `hwmode VEPA` is the default readout for an unenslaved i40e port. They are **not** bridge members.

Corroborated by the `ip -d link` dump: `virbr0` reports `fdb_n_learned 1` (one learned MAC — the guest's), and only `vnet0` carries the `bridge_slave ... designated_bridge 8000.52:54:0:54:77:37` attributes matching `virbr0`'s bridge id.

### 1.3 The physical NICs carried nothing

```
$ for i in enp212s0f0np0 enp212s0f1np1 enp52s0u8u5c2; do ...; done

--- enp212s0f0np0 ---            (i40e, PCI 0000:d4:00.0)
    Speed: Unknown!
    Duplex: Unknown! (255)
    Link detected: no
rx_bytes=0 tx_bytes=0

--- enp212s0f1np1 ---            (i40e, PCI 0000:d4:00.1)
    Speed: 2500Mb/s
    Duplex: Full
    Link detected: yes
rx_bytes=617584005530 tx_bytes=34537180916

--- enp52s0u8u5c2 ---            (cdc_ether, USB)
    Speed: Unknown!
    Link detected: yes
rx_bytes=795362 tx_bytes=3382150
```

- `enp212s0f0np0`: **no carrier, and 0 bytes received and 0 bytes transmitted in the entire uptime.** No cable. It also hosts `vlan30` (LOWERLAYERDOWN) and `macvtap0`/`macvtap1` for the two Talos VMs — all dead (`macvtap0 rx=0 tx=0`, `macvtap1 rx=0 tx=0`).
- `enp212s0f1np1`: up, but at **2500 Mb/s**, on `192.168.0.253/24` — a *different subnet* from `192.168.122.0/24`. It is the host's LAN uplink.
- USB NIC: 4 MB lifetime. Irrelevant.

### 1.4 The arithmetic that settles the owner's fear

The measured pull rate was **1.3467 GB/s = 10.774 Gbit/s**.

The fastest physical link on this machine is `enp212s0f1np1` at **2500 Mb/s = 2.5 Gbit/s = 0.3125 GB/s**.

```
1.3467 GB/s  /  0.3125 GB/s  =  4.31x
```

**The pull ran 4.31x faster than the only live physical port can transmit.** It is arithmetically impossible for that traffic to have crossed a wire. There is not a single 10 GbE link *up* on this box — the resemblance between 10.774 Gbit/s and 10 GbE line rate is a coincidence.

### 1.5 The full data path (all in-kernel, all virtual)

```
registry:2 process (PID 1445779, netns of container 12eb788604ea, 172.17.0.2)
  -> container eth0
  -> veth74927f5                 (host side of the veth pair)
  -> docker0 bridge              (172.17.0.1/16)
  -> host IP forwarding + conntrack + netfilter DNAT
  -> virbr0 bridge               (192.168.122.1/24)
  -> vnet0 tap                   (tun/tap, vnet_hdr on)
  -> vhost-net kernel thread     "vhost-7829", TID 7842   <<== THE BOTTLENECK
  -> virtio-net-pci ring         (single queue pair)
  -> guest enp1s0                (192.168.122.248)
```

Two software bridges and one NAT hop, zero physical NICs.

### 1.6 The libvirt `<interface>` element, in full

```xml
<interface type='network'>
  <mac address='52:54:00:38:26:8a'/>
  <source network='default' portid='2efe4e55-61bb-4668-8a3b-2a503d774646' bridge='virbr0'/>
  <target dev='vnet0'/>
  <model type='virtio'/>
  <alias name='net0'/>
  <address type='pci' domain='0x0000' bus='0x01' slot='0x00' function='0x0'/>
</interface>
```

Note what is **absent**:

- **No `<driver>` element at all.** No `name='vhost'`, no `queues='N'`, no `txmode`. libvirt therefore uses vhost-net (its default when available) with the default **one** queue pair.
- No `<bandwidth>` element — so libvirt applied no QoS.
- `<model type='virtio'/>` — good choice, but single-queue.

### 1.7 `virbr0`'s HTB qdisc is NOT a rate limiter

`ip -d link` shows `virbr0: ... qdisc htb`. That looks alarming. It is not:

```
$ tc -s qdisc show dev virbr0
qdisc htb 1: root refcnt 2 r2q 10 default 0x2 direct_packets_stat 102698820 direct_qlen 1000
 Sent 690723409496 bytes 458886384 pkt (dropped 0, overlimits 0 requeues 0)
 backlog 0b 0p requeues 0

$ tc -s class show dev virbr0
                                   <-- EMPTY. Zero classes.

$ tc filter show dev virbr0
filter parent 1: protocol ip pref 2 u32 chain 0 fh 800::800 order 2048 key ht 800 bkt 0 terminal flowid not_in_hw
  match 00000044/0000ffff at 20
    action order 1: csum (iph, udp) action pass
```

- **Zero HTB classes exist.** With no classes, every packet takes HTB's *direct* path — `direct_packets_stat 102698820` accounts for essentially all 102.7 M packets. Unclassified traffic in HTB is not shaped at all; it is passed straight through at `direct_qlen`.
- `dropped 0, overlimits 0` — HTB never throttled anything, not once.
- The single filter is libvirt's standard DHCP checksum-fixup: `match 00000044/0000ffff at 20` is UDP destination port `0x0044` = **68** (DHCP client). It rewrites checksums for DHCP offers to the guest. Nothing to do with bulk data.

libvirt installs this HTB shell on every `virbr*` unconditionally. **No shaping. Ruled out.**

### 1.8 MTU and offloads, both ends

Host side:

```
virbr0:  mtu 1500   maxmtu 65535
vnet0:   mtu 1500   maxmtu 65521   tun type tap pi off vnet_hdr on
```

Guest side:

```
$ ethtool -i enp1s0
driver: virtio_net
version: 1.0.0
bus-info: 0000:01:00.0

$ ethtool enp1s0
    Speed: Unknown!
    Duplex: Unknown! (255)
    Link detected: yes

$ ip -o link show enp1s0
2: enp1s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000
```

**On `Speed: Unknown!` / `Duplex: Unknown! (255)`:** this is expected and carries **no information**. virtio-net is a paravirtual device with no PHY; the driver reports `SPEED_UNKNOWN`/`DUPLEX_UNKNOWN` unless QEMU was given explicit `speed=`/`duplex=` properties (it was not). Do **not** read this as a misconfiguration, and do not read it as evidence of any particular link rate. The virtual link has no nominal rate at all — its throughput is purely a function of how fast the vhost thread can move descriptors.

Offloads (guest):

```
rx-checksumming: on [fixed]
tx-checksumming: on
scatter-gather: on
tcp-segmentation-offload: on
        tx-tcp-segmentation: on
generic-segmentation-offload: on
generic-receive-offload: on
large-receive-offload: off [fixed]
rx-gro-hw: on
```

**All the offloads that matter are on.** TSO, GSO, GRO, hardware GRO, and both checksum directions. Offloads are not the problem.

Ring sizes:

```
$ ethtool -g enp1s0
Pre-set maximums:  RX 256   TX 256
Current:           RX 256   TX 256
```

256 descriptors is the virtio maximum here and is already at max.

### 1.9 Proof that large frames survive the whole path

This matters because it isolates *where* the MTU-1500 cost is actually paid. Byte and packet counters at five points:

| Point | bytes | packets | bytes/packet |
|---|---:|---:|---:|
| registry container `eth0` TX | 313,468,814,588 | 6,157,780 | **50,906** |
| host `veth74927f5` RX | 313,468,814,588 | 6,157,780 | 50,906 |
| host `virbr0` TX (sysfs) | 667,215,430,523 | 102,699,372 | 6,498 |
| host `vnet0` TX (sysfs) | 667,220,336,191 | 102,775,027 | 6,492 |
| guest `enp1s0` RX | 667,220,426,908 | 102,775,399 | 6,492 |

`virbr0` TX packets (102,699,372) ~= `vnet0` TX packets (102,775,027) ~= guest `enp1s0` RX packets (102,775,399). **Identical to within 0.07%.** No skb is being split anywhere between the bridge and the guest. GSO super-frames pass through intact.

Cross-check against tc, which counts GSO *segments* rather than skbs (`qdisc_bstats` uses `gso_segs`):

```
tc  virbr0:  690,723,409,496 bytes / 458,886,384 "pkt"  = 1,505 bytes per SEGMENT
sysfs virbr0: 667,215,430,523 bytes / 102,699,372 pkts  = 6,498 bytes per SKB
458,886,384 / 102,699,372 = 4.468 segments per skb (all traffic, lifetime average)
```

Decomposing the 6,492 B/skb lifetime average at `vnet0`:
- registry share: 313.47 GB in 6.16 M skbs @ 50,906 B (~34 segments each)
- everything else: 667.22 - 313.47 = 353.75 GB in (102.78 - 6.16) = 96.62 M skbs @ **3,661 B**
- predicted segments: (6.16M x ~34) + (96.62M x ~2.44) = 209 M + 236 M = **445 M** vs the 459 M tc measured. Consistent.

**Conclusion:** the registry's traffic really does traverse the path as ~51 KB TSO super-frames. The MTU-1500 cost is therefore *not* paid in the host IP stack — it is paid inside vhost-net's copy loop and the guest's GRO reassembly. Raising MTU still helps, but less than a naive reading of "MTU 1500" would suggest.

### 1.10 `docker-proxy` is not in the data path

```
$ sudo iptables -t nat -S | grep 5001
-A DOCKER -d 192.168.122.1/32 ! -i docker0 -p tcp -m tcp --dport 5001 -j DNAT --to-destination 172.17.0.2:5000

$ ps -eo pid,args | grep docker-proxy
1445795 /usr/bin/docker-proxy -proto tcp -host-ip 192.168.122.1 -host-port 5001 -container-ip 172.17.0.2 -container-port 5000 -use-listen-fd

$ cat /proc/sys/net/netfilter/nf_conntrack_count /proc/sys/net/netfilter/nf_conntrack_max
147
262144
```

Guest packets arrive on `virbr0`, which satisfies `! -i docker0`, so the kernel DNAT rule matches and rewrites in-kernel. `docker-proxy` merely holds the listening socket (`-use-listen-fd`) as a fallback for hairpin/loopback cases. **No userspace relay, no splice() bottleneck.** conntrack at 147/262144 — zero table pressure.

### 1.11 Plain answer

> **Is any physical NIC in the path? NO.**
>
> The path is: container netns -> veth -> `docker0` -> in-kernel DNAT -> `virbr0` -> `vnet0` tap -> vhost-net -> virtio-net. Every hop is software. `virbr0` has exactly one member (`vnet0`, the VM tap) and no physical uplink. One of the two i40e ports has moved literally zero bytes since boot; the other is on a different subnet at 2.5 Gb/s, which is 4.3x too slow to have carried this transfer.

---

## 2. virtio-net configuration — the primary finding

### 2.1 Five independent confirmations of single-queue

**(a) libvirt XML** — the `<interface>` element (Section 1.6) has **no `<driver>` element whatsoever**, hence no `queues='N'`.

**(b) The QEMU command line** (PID 7829):

```
-netdev {"type":"tap","fd":"40","vhost":true,"vhostfd":"42","id":"hostnet0"}
-device {"driver":"virtio-net-pci","netdev":"hostnet0","id":"net0","mac":"52:54:00:38:26:8a","bus":"pci.1","addr":"0x0"}
```

This is the decisive artifact. A **multiqueue** virtio-net netdev looks like
`{"type":"tap","fds":"40:41:42:43",...,"vhostfds":"50:51:52:53",...}` (plural `fds`/`vhostfds`), and the device gains `"mq":true` plus `"vectors":2N+2`. Here there is a **single scalar `fd`**, a **single scalar `vhostfd`**, no `mq`, and no `vectors`. **One queue pair. Full stop.**

`"vhost":true` confirms vhost-net *is* engaged (the fast in-kernel datapath, not QEMU userspace emulation) — that part is configured correctly.

**(c) Exactly one vhost kernel thread exists for this domain:**

```
$ ps -eLo pid,tid,comm | grep vhost
   7772    7779 vhost-7772        (talos-worker-01)
   7801    7809 vhost-7801        (bloodarrow-control-plane-01)
   7829    7842 vhost-7829        (vast-ubuntu)   <<== one thread, total

$ for p in 7772 7801 7829; do ...count vhost threads...; done
pid 7772: 1
pid 7801: 1
pid 7829: 1
```

With N queues you get N vhost worker threads. There is **1**.

**(d) The guest agrees, and cannot be changed at runtime:**

```
$ ethtool -l enp1s0
Channel parameters for enp1s0:
Pre-set maximums:
RX:             n/a
TX:             n/a
Other:          n/a
Combined:       1
Current hardware settings:
RX:             n/a
TX:             n/a
Other:          n/a
Combined:       1
```

**`Combined: 1` is the *pre-set maximum*, not just the current setting.** The device was instantiated with one queue pair, so `ethtool -L` cannot raise it. Fixing this requires editing the domain XML and restarting the VM.

**(e) The guest's interrupt and softirq topology:**

```
$ grep -oE "virtio0-[a-z.0-9]+" /proc/interrupts
virtio0-config
virtio0-input.0
virtio0-output.0
```

Only `input.0` and `output.0` exist. A 4-queue NIC would show `input.0..input.3`. And each fires on exactly one vCPU:

```
virtio0-input.0    total=48,034,773 interrupts   cpus_with_nonzero_counts=1
virtio0-output.0   total=34,925,526 interrupts   cpus_with_nonzero_counts=1

$ grep NET_RX /proc/softirqs   (per-CPU counts, sorted descending)
49,898,587
33,751,250
 1,057,683
   667,760
   ... (remainder negligible)
```

Two CPUs carry 98%+ of all NET_RX softirq events; the counts match the two IRQ vectors almost exactly (49.9 M vs 48.0 M, 33.8 M vs 34.9 M).

### 2.2 vCPUs vs queues

```xml
<vcpu placement='static' cpuset='0-31,64-95'>64</vcpu>
<memory unit='KiB'>268435456</memory>      <!-- 256 GiB -->
<memoryBacking><locked/><source type='memfd'/><access mode='shared'/></memoryBacking>
```

Plus 64 explicit `<vcpupin>` entries pairing each vCPU to a physical thread (0/64, 1/65, 2/66, ...), i.e. deliberate SMT-sibling pinning. 4 `<hostdev>` entries (the passed-through GPUs).

```
Guest vCPUs:          64
virtio-net queues:     1
Ratio:              64:1
```

**The guest has 64 vCPUs and one network queue.** Every byte of inbound network traffic for a 64-vCPU, 256 GiB VM is funnelled through a single kernel thread on the host and a single softirq context in the guest.

### 2.3 The damning contrast: the disks *did* get multiqueue

```xml
<disk type='file' device='disk'>
  <driver name='qemu' type='qcow2' cache='none' io='native'/>
  <source file='/scratch/vast-ubuntu-vm/vast-ubuntu-os.qcow2' index='3'/>
  <target dev='vda' bus='virtio'/>
<disk type='block' device='disk'>
  <driver name='qemu' type='raw' cache='none' io='native' discard='unmap'/>
  <source dev='/dev/zvol/scratch/vast-docker' index='2'/>
  <target dev='vdb' bus='virtio'/>
```

Neither disk has a `queues=` attribute either — yet in the guest:

```
$ grep virtio /proc/interrupts
 43: virtio1-req.0    8800 on cpu0
 44: virtio1-req.1    3135 on cpu1
 45: virtio1-req.2    9469 on cpu2
 46: virtio1-req.3    3479 on cpu3
 47: virtio1-req.4   10399 on cpu4
 48: virtio1-req.5    3302 on cpu5
 49: virtio1-req.6    6128 on cpu6
 ...
```

**virtio-blk is multiqueue across many vCPUs; virtio-net is not.** This is not an inconsistency in the config — it is a difference in QEMU's defaults. QEMU **auto-scales `virtio-blk` `num-queues` to the vCPU count**, but `virtio-net` multiqueue must be **requested explicitly** via `queues=N`. The owner got MQ for free on storage and silently did not get it on the network. This is exactly the trap that produces a fast-disk / slow-network asymmetry on an otherwise well-tuned host.

### 2.4 vhost-net is enabled and healthy

```
$ lsmod | grep -E '^vhost|^tun|^tap'
vhost_net              40960  3
vhost                  81920  1 vhost_net
vhost_iotlb            16384  1 vhost
tap                    36864  6 macvtap,vhost_net
tun                    73728  7 vhost_net

$ taskset -pc 7842
pid 7842's current affinity list: 32-63,96-127
```

The vhost thread's affinity mask (`32-63,96-127`) is disjoint from the vCPU pin set (`0-31,64-95`), so the vhost thread never contends with a vCPU for a core. That is good tuning — and it means the thread had a full, uncontended physical core available. Its inability to go faster is a *single-thread* ceiling, not a scheduling artefact.

### 2.5 Quantifying the vhost thread

This is the core measurement of the whole investigation.

```
$ awk '{print "utime_ticks="$14" stime_ticks="$15" total_sec="($14+$15)/100}' /proc/7829/task/7842/stat
utime_ticks=0 stime_ticks=44618 total_sec=446.18
```

> **Methodological note.** My first attempt read `/proc/7842/stat` and got 100,751 CPU-seconds, which is wrong. When a TID is opened through the `/proc` **root** rather than `/proc/<pid>/task/<tid>/`, the kernel serves it via `proc_tgid_stat()` and reports **whole-thread-group** totals — i.e. all of QEMU's 64 vCPU threads. A 6-second delta confirmed the error (7,608 ticks = 12.7 cores, impossible for one thread). The correct path `/proc/7829/task/7842/stat` gives `utime=0` (as expected for a kernel task) and a 6-second delta of **0 ticks** while idle. All numbers below use the correct path.

Sanity check on the other two domains, whose networks are dead:

```
pid=7772 vhost_tid=7779 cpu_s=0.18     (macvtap0: rx=0 tx=0)
pid=7801 vhost_tid=7809 cpu_s=2.21     (macvtap1: rx=0 tx=0)
```

Near-zero CPU with near-zero traffic. The counter is genuinely traffic-driven, so `vast-ubuntu`'s 446.18 s is all real packet work.

**Bytes moved by that one thread over the VM's 133,589 s (37.1 h) uptime:**

```
vnet0 tx_bytes (host -> guest) =  667,220,336,191
vnet0 rx_bytes (guest -> host) =    8,786,496,722
                                 ----------------
total                          =  676,006,832,913 B  = 676.0 GB

vnet0 tx_packets = 102,775,027
vnet0 rx_packets =  53,117,582
                   -----------
total            = 155,892,609 packets

vnet0 rx_dropped = 0
vnet0 tx_dropped = 0
```

**Aggregate single-thread efficiency:**

```
676,006,832,913 B / 446.18 s = 1,515,101,600 B/s = 1.5151 GB per vhost-CPU-second
```

**Compare to the measurement:**

```
1.3467 GB/s observed  /  1.5151 GB per CPU-second  =  0.889
```

The pull ran at **88.9% of this thread's lifetime average byte-throughput**. Taken at face value, the single vhost thread was ~89% busy for the entire 116 s.

**Self-consistency check.** If the pull's per-byte vhost cost equalled the lifetime average, it should have consumed `156.32 / 1.5151 = 103.2` CPU-seconds. The pull is `156.32 / 676.0 = 23.1%` of all bytes the thread ever moved, and `103.2 / 446.18 = 23.1%` of all CPU it ever used. Those match exactly, which is what you would expect if this traffic class dominates the counter.

**Honest caveat — why 89% is an upper bound.** The 1.5151 GB/CPU-s figure blends traffic of very different shapes: the registry's 51 KB super-frames, 96.6 M "other" skbs averaging 3.66 KB, and 53.1 M guest->host ACKs averaging 165 B. Small packets cost far more CPU per byte, so the registry's own per-byte cost is *better* than the lifetime average. Modelling vhost cost as `CPU = a x packets + b x bytes` subject to

```
a x 155.89e6 + b x 676.0e9 = 446.18 s
```

and bracketing `a` (per-skb cost) with the guest's own independently measured 1.18 us/skb NAPI cost (Section 2.6):

| assumed a (us/skb) | implied b | implied copy rate | vhost load during the pull |
|---:|---:|---:|---:|
| 1.0 | 0.429 ns/B | 2.33 GB/s | **~71% of one core** |
| 1.5 | 0.314 ns/B | 3.18 GB/s | **~62% of one core** |
| 2.0 | 0.199 ns/B | 5.03 GB/s | **~53% of one core** |

(Pull cost = `a x (3.07M large skbs + ~12.1M ACKs) + b x 156.32 GB`, over 116.06 s.)

**So the defensible statement is: the single vhost-net thread ran at roughly 50-89% of one core during the pull — by a wide margin the most heavily loaded single-threaded resource anywhere in the path.** I could not pin the number precisely without a live test (Section 9).

Note also that for host->guest traffic **vhost-net always copies**: zero-copy (`experimental_zcopytx`) only ever applied to the guest->host direction and is disabled here. All 667.22 GB were memcpy'd into guest memory by this one thread, against a 256 GiB guest working set far larger than any cache.

### 2.6 The guest side is *not* the bottleneck

The guest has the mirror-image single-queue problem, so it is worth checking whether the guest's single NAPI CPU was the wall instead. It was not:

```
$ grep "^cpu[0-9]" /proc/stat | sort -k8 -nr | head -5 | cut -d" " -f1,8
cpu22 12170          <-- softirq jiffies
cpu0   2631
cpu23  1311
cpu1    392
cpu24   349
$ ... | tail -3
cpu35     2
cpu55     1
cpu45     1
```

`cpu22` carries essentially all of it: **12,170 jiffies = 121.70 CPU-seconds** of softirq, versus single-digit jiffies on most of the other 63 vCPUs. Textbook single-queue hot spot.

```
667,220,426,908 B received / 121.70 s = 5,482,502,275 B/s = 5.483 GB per softirq-CPU-second
1.3467 / 5.483 = 0.246
```

**`cpu22` was only ~25% busy at 1.3467 GB/s.** The guest can absorb roughly 5.5 GB/s on one core, because GRO hands it 6.5 KB (and for registry traffic, ~51 KB) frames. Per-skb cost in the guest: `121.70 s / 102.78 M skbs = 1.18 us/skb`.

So both ends are single-queue, but only the **host** end is near its limit — because the host end also pays the data copy.

---

## 3. Direct bridge measurement — **SKIPPED, and why**

**I did not run the authenticated blob GET. Per your instructions, I stopped rather than working around the credential problem.** Here is exactly what I found and where I stopped.

**The registry requires authentication:**

```
$ curl -sk -o /dev/null -w "http=%{http_code}\n" https://192.168.122.1:5001/v2/
http=401
```

**There is no non-TLS endpoint to compare against:**

```
$ ss -lntp | grep -E ':50[0-9][0-9]'
LISTEN 0  4096  192.168.122.1:5001  0.0.0.0:*
```

One listener, TLS only. The `REGISTRY_HTTP_TLS_CERTIFICATE` / `REGISTRY_HTTP_TLS_KEY` env vars confirm TLS termination is mandatory. So the "repeat over plain HTTP" comparison is not available at all.

**Credential search — everything I checked, and the result:**

| Location | Result |
|---|---|
| guest `/home/ubuntu/.docker/config.json` | does not exist |
| guest `/root/.docker/config.json` | **Permission denied** to the `ubuntu` account |
| guest `/home/*/.docker/config.json` | no matches (only `/home/ubuntu` exists) |
| guest `/etc/docker/config.json` | does not exist |
| guest `/etc/containerd/certs.d` | does not exist |
| guest `/etc/docker/daemon.json` | present, world-readable, contains only the nvidia runtime shim — no credentials |
| host `~coldaine/.docker/config.json` | present, 16 bytes, contents: `{ "auths": {} }` — **empty** |
| host `~/.config/containers/auth.json`, `/run/user/1000/containers/auth.json` | do not exist |
| host `/srv/ai-models/runtimes/oci-registry/auth/htpasswd` | readable, but **bcrypt hashes** — not reversible, cannot authenticate |

The only credential that exists is inside `/root/.docker/config.json` in the guest, which is **not plainly readable** — it requires privilege escalation to extract. **Per your instruction I did not `sudo`-read it.**

**Consequences — what this cost the investigation:**

1. No host-local (127.0.0.1 / 172.17.0.2) vs guest-side throughput comparison. That delta is the single cleanest way to isolate the virtio boundary from the registry/TLS/storage side, and I do not have it.
2. No 1-vs-3-vs-6 parallel-stream test. That is the *decisive* discriminator between an aggregate limiter (the shared vhost thread) and a per-stream limiter (decompression or per-connection TLS) — see Section 9.
3. The vhost load figure remains a modelled range (50-89%) rather than a direct measurement.

**What I substituted.** Rather than work around the credential, I derived equivalent evidence from kernel and process accounting that requires no authentication at all: lifetime CPU-seconds and byte/packet counters for the vhost thread (Section 2.5), for the guest's NAPI CPU (Section 2.6), and for the registry process itself (Section 4.2). These are weaker than a live A/B test but they are real measurements of the same quantities, and they cross-check each other.

**One thing I did read, and why it is not a secret:** I read the image **manifests** directly out of the registry's on-disk blob store (`/srv/ai-models/.../blobs/sha256/...`). These are the exact JSON documents that `GET /v2/<repo>/manifests/<ref>` would have returned — image metadata (layer digests, sizes, media types), not credentials. Reading them from disk instead of over HTTP is equivalent and purely read-only. That is what made Section 6 possible.

---

## 4. Is TLS the limiter? No — quantitatively ruled out

### 4.1 The CPU is extremely well equipped for TLS

```
$ lscpu
Model name:  AMD Ryzen Threadripper PRO 9985WX 64-Cores
CPU(s):      128        Core(s) per socket: 64      Thread(s) per core: 2
CPU max MHz: 5476.29
L3 cache:    256 MiB (8 instances)
NUMA node(s): 1          NUMA node0 CPU(s): 0-127

Crypto-relevant flags present: aes  pclmulqdq  vaes  vpclmulqdq  sha_ni
                               avx2  avx512f  avx512dq  avx512bw  avx512vl
MemTotal: 503.0 GiB
```

AES-NI **and** VAES (vectorised AES over AVX-512) **and** PCLMULQDQ/VPCLMULQDQ (GHASH) **and** SHA-NI. Go's `crypto/tls` uses the AES-GCM assembly path on this hardware; single-core AES-128-GCM runs in the **2-4 GB/s** range. Single socket, single NUMA node, so no cross-node penalty.

### 4.2 The registry has no CPU limit, and used almost none

```
$ docker inspect bloodarrow-oci-registry --format '...'
NanoCpus=0 CpuShares=0 CpuQuota=0 CpuPeriod=0 CpusetCpus= Memory=0 NetworkMode=bridge

$ cat /sys/fs/cgroup/system.slice/docker-12eb788604ea*.scope/cpu.max
max 100000
```

`cpu.max = max` — **no cgroup CPU ceiling.** No cpuset pinning, no shares weighting, no memory cap. The container can use all 128 threads.

```
$ RP=$(docker inspect -f '{{.State.Pid}}' bloodarrow-oci-registry)   # 1445779
$ awk '{print "utime_s="$14/100, "stime_s="$15/100, "total_s="($14+$15)/100}' /proc/$RP/stat
utime_s=110.27 stime_s=84.7 total_s=194.97

$ ls /proc/$RP/task | wc -l
60                                    # 60 OS threads

$ cat /proc/$RP/net/dev
  eth0: 15885492656 3053077 ... 313468814588 6157780 ...
        ^rx_bytes   ^rx_pkts     ^tx_bytes    ^tx_pkts

$ docker inspect -f '{{.State.StartedAt}}' bloodarrow-oci-registry
2026-08-28T07:29:06.96521479Z         # ~23 h before this investigation
```

**A beautiful corroboration falls out of this.** The registry has transmitted **313,468,814,588 B = 313.47 GB** since it started. The stated pull was 156.32 GB:

```
313.47 GB / 156.32 GB = 2.005
2 x 156.32 GB = 312.64 GB      (difference 0.83 GB = manifests, HEAD probes, other requests)
```

**The registry has served almost exactly two full pulls of this image** — Run 1 and Run 2. This independently confirms that 156.32 GB is the on-the-wire (compressed) byte count, and it means the registry's lifetime CPU counter cleanly covers exactly two instances of the workload under study.

**Registry efficiency:**

```
313,468,814,588 B / 194.97 CPU-s = 1,607,780,758 B/s = 1.6078 GB per CPU-second
```

That figure covers **everything** the registry does: file reads from ZFS, TLS record framing, AES-GCM encryption, HTTP/1.1 chunking, and all syscalls.

**Cost of one pull:**

```
156.32 GB / 1.6078 GB per CPU-s = 97.23 CPU-seconds
97.23 CPU-s / 116.06 s wall     = 0.838 core-equivalents
```

**The registry consumed 0.84 of one core's worth of CPU — spread across 60 threads and at least 3 concurrent download goroutines, on a machine with 128 hardware threads.** Per stream that is roughly **0.28 of a core**.

### 4.3 The single-TLS-stream question, answered

Your brief asked whether ~1.3 GB/s through one Go TLS process is "plausible-to-tight on one core". The answer is that **it was never on one core**:

- `registry:2` is Go. Each inbound HTTPS connection is served by its own goroutine, scheduled across `GOMAXPROCS` (128 here, uncapped). Three concurrent blob downloads = at least three independent TLS write paths on three different cores.
- Per stream the load was 449 MB/s. At 1.6078 GB/CPU-s that is **0.28 core**. At the AES-GCM-only rate of ~2-4 GB/s/core it is **~11-22% of a core**.
- Even the *aggregate* 1.3467 GB/s costs only 0.84 cores out of 128.

**TLS had roughly an order of magnitude of headroom. Ruled out.** The same reasoning rules out the registry Go process generally — it is not CPU-starved, not cgroup-throttled, and not single-threaded in any way that matters.

---

## 5. Is storage the limiter? No — an order of magnitude of headroom

### 5.1 Source pool: `models`

```
$ zpool status models
  pool: models
 state: ONLINE
config:
        NAME                                                           STATE
        models                                                         ONLINE
          nvme-Samsung_SSD_9100_PRO_with_Heatsink_4TB_S7ZRNJ0YB04493D  ONLINE
          nvme-Samsung_SSD_9100_PRO_4TB_S7YANJ0L207436B                ONLINE

$ zpool list
NAME      SIZE  ALLOC   FREE   FRAG    CAP   HEALTH
models   7.25T  2.89T  4.36T     1%    39%   ONLINE
scratch  3.62T  2.28T  1.34T     9%    62%   ONLINE
```

**Topology: two top-level single-disk vdevs = a 2-wide stripe.** No mirror, no raidz, so reads are spread across both devices with no parity overhead. (Worth flagging separately: this pool has **no redundancy** — a single NVMe failure loses 2.89 TB. Not a performance issue, but the owner should know.)

PCIe link state:

```
nvme2 | Samsung SSD 9100 PRO 4TB               | 32.0 GT/s PCIe x4
nvme3 | Samsung SSD 9100 PRO with Heatsink 4TB | 32.0 GT/s PCIe x4
```

**32 GT/s x4 = PCIe Gen5 x4, fully negotiated on both.** Raw lane bandwidth ~15.75 GB/s each. The Samsung 9100 PRO is rated ~14.8 GB/s sequential read.

```
Theoretical stripe read ceiling:  2 x ~14.8 GB/s  ~= 29 GB/s
Realistic ZFS sequential read:    ~10-20 GB/s
Required for the pull:            1.3467 GB/s
Utilisation:                      ~5-13%
```

Lifetime IO confirms the stripe is balanced and the disks are being used:

```
nvme2n1 read_GB=2330.62 written_GB=176.87
nvme3n1 read_GB=2332.96 written_GB=176.86     <- within 0.1% of each other
```

### 5.2 Dataset tuning is already correct

```
$ zfs get -H compression,recordsize,primarycache,secondarycache,atime,sync,logbias models/ai-models
models/ai-models  compression     lz4       local
models/ai-models  recordsize      1M        local
models/ai-models  primarycache    all       default
models/ai-models  secondarycache  all       default
models/ai-models  atime           off       local
models/ai-models  sync            standard  default
models/ai-models  logbias         latency   default
models/ai-models  used            3.20T
models/ai-models  compressratio   1.02x
```

- `recordsize=1M` — ideal for multi-GB blobs; minimises per-record overhead.
- `atime=off` — no metadata writes on read.
- `compressratio 1.02x` — the blobs are **already gzip-compressed**, so lz4 correctly gives up almost immediately (early-abort). **ZFS decompression costs essentially nothing on the read path.**

### 5.3 ARC vs disk: it was mostly disk, and that's fine

```
$ grep -E '^(size|c|c_max|c_min)' /proc/spl/kstat/zfs/arcstats
c        4  34359738368
c_max    4  34359738368     = 32.0 GiB
c_min    4   2147483648
size     4  32478309600     = 30.2 GiB (later sample: 32.0 GiB)

MemTotal = 503.0 GiB
```

**ARC is capped at 32.0 GiB and is sitting full at its cap, on a host with 503 GiB of RAM — just 6.4% of physical memory.**

```
Pull size:      156.32 GB
ARC c_max:       34.36 GB
Ratio:            4.55x
```

The working set is **4.55x larger than the entire ARC**, and the six ~25 GB layers each individually approach it. **The bulk of the 156.32 GB was read from NVMe, not from cache.**

```
$ grep -E 'prefetch_data' /proc/spl/kstat/zfs/arcstats
prefetch_data_hits      4   1088919
prefetch_data_misses    4  11463232
```

The 10.5:1 prefetch miss ratio is the signature of large streaming reads pulling fresh data off disk — consistent with serving multi-GB blobs from a 3.2 TB dataset through a 32 GiB cache.

**This does not matter.** Even entirely from disk, 1.3467 GB/s is ~5-13% of the stripe's capability. **Storage is ruled out.**

(Side note for the owner: `c_max = 32 GiB` on a 503 GiB host is very conservative. Raising it would not fix the 1.35 GB/s ceiling — the bottleneck is downstream — but it would help repeat pulls of the same image.)

### 5.4 Destination pool: `scratch`

```
$ zpool status scratch
        NAME                                     STATE
        scratch                                  ONLINE
          nvme-Corsair_MP700_PRO_A7GGB349000E5P  ONLINE
          nvme-Corsair_MP700_PRO_A7GGB3490008HV  ONLINE

nvme0 | Corsair MP700 PRO | 32.0 GT/s PCIe x4
nvme1 | Corsair MP700 PRO | 32.0 GT/s PCIe x4

$ zfs get -H volblocksize,compression,primarycache,sync,logbias scratch/vast-docker
scratch/vast-docker  volblocksize  64K       -
scratch/vast-docker  compression   off       local
scratch/vast-docker  sync          standard  default
scratch/vast-docker  logbias       latency   default
```

Also a 2-wide Gen5 NVMe stripe. `vdb` = this zvol -> xfs -> `/var/lib/docker` in the guest.

```
$ (guest) grep -E " vd[ab] " /proc/diskstats   ->  converted
vda read_GB=4.75    written_GB=32.60
vdb read_GB=889.29  written_GB=1405.23

$ (guest) df -h /var/lib/docker
/dev/vdb  3.0T  1.2T  1.9T  39%  /var/lib/docker
```

1.4 TB written to `vdb` over the VM's life. `compression=off` on the zvol is correct (the guest writes already-decompressed layer data through xfs; double compression would just burn CPU). `volblocksize=64K` is reasonable for a container-image filesystem.

**Neither the source nor the destination array is close to limiting.** Both are 2-wide Gen5 NVMe stripes with ~10-20 GB/s of real sequential capability against a 1.35 GB/s demand. The owner's expectation of "far more, since the source is a fast NVMe array and the destination another Gen5 NVMe array" is entirely correct — the storage was never the problem.

---

## 6. What was actually pulled — and the concurrency arithmetic

This is where the read-only manifest inspection pays off.

### 6.1 The repositories and tags

```
$ ls .../repositories
deepseek-v4-flash-0731-vast
deepseek-v4-flash-r21-appliance
deepseek-v4-flash-r21-runtime

$ ls .../repositories/deepseek-v4-flash-r21-appliance/_manifests/tags
infernal-invocation-r21-baked
infernal-invocation-r21-baked-index
infernal-invocation-r21-warm-cache-cold1
infernal-invocation-r21-warm-cache-cold1-index
```

Both `-baked` and `-warm-cache-cold1` are OCI image indexes (`application/vnd.oci.image.index.v1+json`) with a single `linux/amd64` manifest each.

### 6.2 Layer composition

```
== infernal-invocation-r21-baked            layers 133  total 167.57 GB
== infernal-invocation-r21-warm-cache-cold1 layers 134  total 167.59 GB

mediaType histogram (baked):
  124  application/vnd.docker.image.rootfs.diff.tar.gzip
    9  application/vnd.oci.image.layer.v1.tar+gzip
config: application/vnd.oci.image.config.v1+json  327185 B

largest 10 layers, GB:
  [26.25, 26.25, 26.23, 26.20, 23.87, 23.74, 2.69, 1.84, 1.21, 0.71]
smallest 5 layers, bytes: [32, 32, 32, 32, 32]
```

**Every single layer is gzip.** No zstd, no uncompressed, no estargz.

### 6.3 The 53-blob / 156.32 GB figure reconciles exactly

```
Six largest layers:  26.25 + 26.25 + 26.23 + 26.20 + 23.87 + 23.74  =  152.54 GB
Stated pull:                                                            156.32 GB
Remainder:                                                                3.78 GB
Stated blob count: 53   ->   6 huge  +  47 small  =  53   [MATCH]
```

**91.4% of the transferred bytes live in just six layers.** The other 47 blobs total 3.78 GB — 2.4% of the transfer, and they complete almost instantly. (The manifest holds 133-134 layers; 80-81 were already present in the guest's content store, which is why only 53 were fetched.)

### 6.4 Concurrency: confirmed 3, and it maps cleanly onto the timing

```
$ (guest) cat /etc/docker/daemon.json
{"runtimes":{"nvidia":{"args":[],"path":"/var/lib/vastai_kaalia/latest/kaalia_docker_shim"}}}
                       ^ no max-concurrent-downloads override

$ (guest) dockerd --help | grep -A1 max-concurrent
      --max-concurrent-downloads int          Set the max concurrent
                                              downloads (default 3)
      --max-concurrent-uploads int            Set the max concurrent
                                              uploads (default 5)

$ (guest) docker info
 Server Version: 29.7.2
 Storage Driver: overlayfs        <- containerd snapshotter (driver-type io.containerd.snapshotter.v1)
 Cgroup Driver: systemd / v2
 CPUs: 64
 Total Memory: 251.6GiB
 containerd version: aad11006b869517fcd3009450b6f82da282e1a9b.m  (containerd v2.3.3)
```

**`max-concurrent-downloads = 3`, the default, not overridden. `max-concurrent-uploads = 5`.**

Now the timing. With six ~25 GB layers and three download slots, the pull is **two waves of three parallel giant streams**, with the 47 small blobs interleaved in the gaps. So essentially three streams were saturated for nearly the whole window:

```
Per-stream rate  = 1.3467 GB/s / 3  =  0.4489 GB/s  =  448.9 MB/s  =  3.591 Gbit/s

Cross-check from the layer structure:
  two waves x 26.25 GB per slot = 52.5 GB per slot
  52.5 GB / 116.06 s            = 452 MB/s per stream       [MATCHES 449 MB/s]
```

The arithmetic you asked for holds: **1.347 GB/s / 3 streams = 449 MB/s per stream**, and the layer-size structure independently predicts 452 MB/s. Three streams really were running for the duration.

### 6.5 Is 449 MB/s consistent with one gzip-over-TLS HTTP stream?

Partly — and this is the one place the evidence is genuinely ambiguous.

**Against TLS being the per-stream limit:** 449 MB/s costs ~0.28 core at the registry's measured efficiency, or ~11-22% of a core for AES-GCM alone (Section 4). Nowhere near a ceiling.

**For decompression being a per-stream limit:** I measured the actual gzip expansion ratio by reading each big layer's gzip trailer. The last 8 bytes of a gzip member are CRC32 + ISIZE (uncompressed size **mod 2^32**); for a 26 GB member the true size is `ISIZE + k x 2^32`, and only one `k` yields a plausible ratio:

```
csz_GB=26.25 hdr=1f8b0800 isize=2865391616 -> k=11 uncomp_GB=50.11 ratio=1.9088
csz_GB=26.25 hdr=1f8b0800 isize=2865391616 -> k=11 uncomp_GB=50.11 ratio=1.9090
csz_GB=26.23 hdr=1f8b0800 isize=2865391616 -> k=11 uncomp_GB=50.11 ratio=1.9102
csz_GB=26.20 hdr=1f8b0800 isize=2865387008 -> k=11 uncomp_GB=50.11 ratio=1.9126
csz_GB=23.87 hdr=1f8b0800 isize= 470472704 -> k=11 uncomp_GB=47.72 ratio=1.9992
csz_GB=23.74 hdr=1f8b0800 isize= 335726080 -> k=11 uncomp_GB=47.58 ratio=2.0040
```

All six land on the same `k=11` and cluster tightly at **1.91-2.00x**. (A wrong `k` would scatter the ratios; the consistency validates the choice. `hdr=1f8b0800` = standard gzip, deflate, no extra flags.)

So each stream must inflate:

```
448.9 MB/s wire  x  1.91  =  857 MB/s of decompressed output per stream
                 aggregate  =  2.57 GB/s across three streams
```

And the decompressor is available and preferred:

```
$ (guest) which unpigz pigz
/usr/bin/unpigz
/usr/bin/pigz
```

containerd's `archive/compression` package shells out to `unpigz` when it is on `PATH`. **Crucially, pigz does not parallelise inflate** — DEFLATE decompression is inherently serial; pigz only pipelines CRC and I/O onto helper threads. So each layer gets roughly **one inflate thread**.

**Single-threaded zlib inflate typically sustains 250-500 MB/s of output.** 857 MB/s per stream is well above that. Two readings are possible:

1. **Decompression ran asynchronously behind the fetch.** With the containerd image store (confirmed in use: `Storage Driver: overlayfs`, `driver-type io.containerd.snapshotter.v1`), `Pull` writes compressed blobs into the content store while unpacking proceeds as a *concurrent* stage. If the 116.06 s figure is the fetch window, decompression is off the critical path and irrelevant to the number.
2. **Decompression was in-line and is a genuine co-limiter**, in which case 449 MB/s/stream is roughly what one inflate thread can feed.

That decompression happens *somewhere* is not in doubt — `vdb` shows 1,405 GB written and `docker system df` reports 754.7 GB of images.

**I could not resolve which reading is correct read-only.** Distinguishing them requires the concurrency test in Section 9.

---

## 7. Everything else, ruled out

**TCP windowing and loss:**

```
$ (guest) sysctl -n net.ipv4.tcp_rmem net.core.rmem_max net.ipv4.tcp_congestion_control
4096    131072  6291456
212992
cubic

$ (guest) nstat -az | grep -E 'TcpRetransSegs|TCPTimeouts'
TcpRetransSegs      111
TcpExtTCPTimeouts    42

$ (guest) /proc/net/dev enp1s0:  rx_dropped=36  (lifetime)
$ (host)  vnet0: rx_dropped=0  tx_dropped=0
```

Autotuning ceiling is 6 MiB. On a purely virtual path the RTT is on the order of 0.05 ms, so the bandwidth-delay product at 1.5 GB/s is roughly **75 KB** — the window is ~80x larger than needed. 111 retransmits and 36 dropped frames across 37 hours and 676 GB is statistical noise. **Not window-limited, not loss-limited.**

**NUMA:** `NUMA node(s): 1` — single node, so no cross-socket memory penalty on the vhost copy. Not a factor.

**Host contention:** load average was `5.22, 4.92, 3.54` during this investigation, on a 128-thread box also running `k3d-cnpg-recovery-*`, `buildx_buildkit_*`, `vast-monitor`, `vast-market-raw-postgres`, and `context7-key-rotator-mcp`. That is light. However, **I cannot verify what the host load was during Run 1**, so I cannot fully exclude transient interference. The vhost thread's affinity (`32-63,96-127`, disjoint from the vCPU pin set) means it at least never contended with the guest's own vCPUs.

---

## 8. Ranking and verdict

### 8.1 Evidence ranking

**1. virtio-net single queue / single vhost-net thread — PRIMARY. Overwhelming evidence.**
- No `<driver queues=...>` in the domain XML (Section 1.6)
- QEMU: single scalar `"fd"` and `"vhostfd"`, no `mq`, no `vectors` (2.1b)
- Exactly one `vhost-7829` kernel thread (2.1c)
- Guest `ethtool -l`: `Combined: 1` as a **pre-set maximum** (2.1d)
- Guest: only `virtio0-input.0`/`output.0`, each on one vCPU; 98%+ of NET_RX softirq on `cpu22` (2.1e)
- 64 vCPUs served by 1 queue (2.2)
- virtio-blk got multiqueue automatically; virtio-net did not (2.3)
- **Quantitative:** 446.18 CPU-s for 676.0 GB = 1.5151 GB/vhost-CPU-s; the pull ran at 88.9% of that lifetime average, or ~53-71% under a per-packet/per-byte cost model. Either way it is the most loaded single-threaded resource in the path *and the only one that cannot scale out.*

**2. Gzip decompression (pigz) — plausible per-stream co-limiter. Unresolved.**
- All layers gzip; measured expansion 1.91-2.00x (6.5)
- Requires ~857 MB/s inflate output per stream, vs 250-500 MB/s typical for one inflate thread
- `unpigz` present; pigz does not parallelise inflate
- Cannot determine read-only whether it was on the critical path

**3. Docker `max-concurrent-downloads = 3` — contributing multiplier, not the wall.**
- Confirmed default, not overridden (6.4)
- Sets exactly 3 streams x 449 MB/s. It bounds how much parallelism can be brought to bear, so it interacts with whatever the real ceiling is — but by itself, 3 streams should comfortably exceed 1.35 GB/s given the registry's 0.84-core cost and the storage headroom, *unless something shared caps the aggregate*.

**4. MTU 1500 — secondary contributor.**
- 1500 everywhere on the virtual path, but TSO/GSO/GRO all working and ~51 KB super-frames survive intact end to end (1.9)
- So the cost is paid inside vhost's copy loop and guest GRO, not in the host IP stack
- Nonetheless free to fix: `virbr0 maxmtu 65535`, `vnet0 maxmtu 65521`, and **no physical NIC constrains it**

**5. Registry process / TLS — ruled out.** 1.6078 GB/CPU-s, 0.84 core-equivalents for the whole pull, 60 threads, `cpu.max = max`, AES-NI + VAES + SHA-NI (Section 4).

**6. ZFS read — ruled out.** 2x Gen5 NVMe stripe, ~10-20 GB/s real capability vs 1.35 GB/s demand; ~5-13% utilised (Section 5).

**7. Physical 10 GbE in the path — categorically ruled out.** No physical NIC on `virbr0`; one i40e port dead with 0 lifetime bytes, the other at 2.5 Gb/s on a different subnet (Section 1).

**8. tc/QoS shaping — ruled out.** HTB root with zero classes, `dropped 0 overlimits 0` (1.7).

**9. `docker-proxy` relay — ruled out.** In-kernel DNAT matches; proxy holds listen-fd only (1.10).

**10. TCP window / loss — ruled out.** 6 MiB rmem vs ~75 KB BDP; 111 retransmits (Section 7).

### 8.2 The verdict

> **Primary limiter: the single-queue virtio-net interface on `vast-ubuntu` and the single `vhost-net` kernel thread (`vhost-7829`, TID 7842) that serves it.**

The supporting case, in one paragraph: the domain XML has no `<driver queues=...>`, so QEMU created the NIC with one queue pair (`"fd":"40","vhost":true,"vhostfd":"42"` — scalar, not plural), the host runs exactly one vhost worker thread for it, and the guest reports `Combined: 1` as an immovable pre-set maximum with 98%+ of its network softirq work landing on a single vCPU. That one host thread has moved 676.0 GB using 446.18 CPU-seconds — **1.5151 GB per CPU-second** — and the observed 1.3467 GB/s is 88.9% of that figure (53-71% under a more conservative per-packet cost model). Meanwhile every other component in the path has 3-10x headroom: the registry used 0.84 core-equivalents across 60 uncapped threads, the ZFS stripe was ~5-13% utilised, and the guest's receive CPU was ~25% busy. The vhost thread is the only single-threaded, non-scalable resource in the chain, and it is by a wide margin the most heavily loaded one.

### 8.3 The owner's fear, answered plainly

> **Is the traffic on a physical 10 GbE link? NO.**

Three independent proofs:

1. **Topology.** `192.168.122.1` is `virbr0`. `bridge link show` lists exactly one member: `vnet0`, the VM's tap. No physical interface is enslaved. `ip route get 192.168.122.248` -> `dev virbr0`.
2. **Counters.** `enp212s0f0np0` has `Link detected: no` and **`rx_bytes=0 tx_bytes=0` for the entire 37-hour uptime** — it has never carried a single byte. `enp212s0f1np1` is on `192.168.0.253/24`, a different subnet, and is not in the route.
3. **Arithmetic.** The only live physical port negotiated **2500 Mb/s = 0.3125 GB/s**. The measured pull was **1.3467 GB/s — 4.31x faster**. A transfer cannot exceed the capacity of a link it traverses. **The measurement is itself the proof that the traffic stayed inside the box.**

There is not even a 10 GbE link *up* on this machine. The similarity between 10.774 Gbit/s and 10 GbE line rate is coincidence — it is the throughput ceiling of one vhost-net thread, which happens to land in the same numeric neighbourhood. That coincidence is common enough to be a known trap: single-queue virtio-net routinely benchmarks in the 10-20 Gbit/s band, which is exactly why it gets mistaken for a 10 GbE wire.

### 8.4 What I could not determine read-only

Stated plainly, rather than guessed:

1. **The live blob-GET benchmark was not run.** The registry requires auth (`GET /v2/` -> 401), no non-TLS endpoint exists, and the only credential lives in `/root/.docker/config.json` inside the guest, which the `ubuntu` account cannot read. Per your instruction I did not escalate to obtain it. **Consequently I have no host-local vs guest-side throughput comparison**, which is the cleanest single way to isolate the virtio boundary.
2. **I could not run the variable-concurrency test**, which is the decisive discriminator between an *aggregate* limiter (shared vhost thread) and a *per-stream* limiter (decompression / per-connection effects). Both hypotheses predict 449 MB/s per stream at concurrency 3; they diverge only when concurrency changes.
3. **The vhost thread's per-packet vs per-byte cost split is not separable** from lifetime counters alone. "50-89% of one core during the pull" is a modelled range bracketed by the guest's independently measured 1.18 us/skb NAPI cost — not a direct measurement.
4. **Whether gzip decompression was on the fetch critical path** is unresolved (Section 6.5). If it was, it is a genuine co-limiter at ~857 MB/s of inflate output per stream.
5. **Host load during Run 1 is unknown.** I observed load 3.5-5.2 during this investigation on a 128-thread box, but cannot reconstruct conditions at measurement time.
6. **I did not confirm which of the two tags** (`-baked` vs `-warm-cache-cold1`) Run 1 pulled. Both share the identical six large layers, so the analysis is unaffected.

---

## 9. The one test that would settle it

All read-only, all HTTP GET of an existing blob to `/dev/null` — but it **requires the registry credential**, which I deliberately did not obtain.

Pick a big blob (e.g. the 26.25 GB layer) and run, **from the guest**:

```
# N = 1, then 3, then 6 -- same blob, N parallel GETs, measure AGGREGATE
for i in $(seq 1 N); do
  curl -sk -o /dev/null \
    -w "size=%{size_download} time=%{time_total} speed=%{speed_download}\n" \
    -u "$REGUSER:$REGPASS" \
    "https://192.168.122.1:5001/v2/deepseek-v4-flash-r21-appliance/blobs/sha256:<digest>" &
done; wait
```

**Interpretation:**

- **Aggregate stays flat at ~1.35 GB/s regardless of N** -> confirms a **shared aggregate ceiling** = the single vhost thread. **This is my prediction.**
- **Aggregate scales roughly linearly with N** -> the limit is **per-stream** (decompression is not in a raw `curl` path, so this would point at per-connection TLS/TCP behaviour) and raising `max-concurrent-downloads` alone would help.

Then repeat **from the host** against `https://127.0.0.1:5001/...` or `https://172.17.0.2:5000/...`, which **bypasses `virbr0`, `vnet0`, and vhost-net entirely**:

- **Host-local much faster than guest-side** -> the virtio boundary is confirmed as the limiter.
- **Host-local roughly the same** -> the limit is on the registry/TLS/storage side, and my ranking is wrong.

While any of these run, sample the vhost thread:

```
watch -n1 'awk "{print (\$14+\$15)/100}" /proc/7829/task/7842/stat'
```

If it climbs at ~100 ticks/s, the thread is pinned at one full core and the case is closed.

---

## 10. Recommendations, in expected-impact order

1. **Enable virtio-net multiqueue.** Add to the `<interface>` element of `vast-ubuntu`:
   ```xml
   <driver name='vhost' queues='8'/>
   ```
   (8-16 is sensible for 64 vCPUs; each queue costs one vhost thread and ~64 KB of host memory.) **Requires a full VM shutdown/start** — the PCI device must be re-created with more queues. Then verify in the guest with `ethtool -l enp1s0` (pre-set maximum should rise) and, if the guest does not auto-enable them, `ethtool -L enp1s0 combined 8`. **Expected gain: 3-6x.**

2. **Raise MTU to 9000** on `virbr0` and the guest's `enp1s0`. This is **free** here precisely because there is no physical NIC in the path — `virbr0 maxmtu 65535`, `vnet0 maxmtu 65521`, and nothing downstream constrains the frame size. Cuts per-segment work in the vhost copy loop and guest GRO by ~6x. Set it on the libvirt network definition so it survives restarts.

3. **Raise `max-concurrent-downloads`** in the guest's `/etc/docker/daemon.json` to 6-8. **Only do this after step 1** — with a single queue it will not help and may add contention.

4. **Consider zstd instead of gzip** for these layers. zstd decompresses 3-5x faster than DEFLATE and parallelises properly. With 91% of the bytes in six ~25 GB layers expanding ~1.91x, this removes any doubt about decompression being a co-limiter.

5. **Raise ZFS `zfs_arc_max`** above 32 GiB (503 GiB of RAM is available; 128-192 GiB would be reasonable). Will not affect the 1.35 GB/s ceiling, but makes repeat pulls of the same image dramatically faster.

6. **Unrelated but worth flagging:** `models` is a **2-wide stripe with no redundancy**. A single NVMe failure loses 2.89 TB of model data.

---

## Appendix: environment reference

| Item | Value |
|---|---|
| Host | `bloodarrow`, Linux 7.1.8-zen1-3-zen, uptime 133,589 s (37.1 h) |
| Host CPU | AMD Ryzen Threadripper PRO 9985WX, 64C/128T, 1 NUMA node, max 5476 MHz |
| Host crypto | aes, pclmulqdq, vaes, vpclmulqdq, sha_ni, avx2, avx512f/dq/bw/vl |
| Host RAM | 503.0 GiB |
| Guest | `vast-ubuntu`, 64 vCPU (pinned, SMT-paired), 256 GiB (`<locked/>`, memfd, shared), 4 GPU hostdevs |
| Guest Docker | 29.7.2, containerd v2.3.3, overlayfs snapshotter, cgroup v2/systemd |
| QEMU PID / vhost TID | 7829 / 7842 (`vhost-7829`), affinity 32-63,96-127 |
| Guest NIC | virtio_net `enp1s0`, PCI 0000:01:00.0, MTU 1500, **1 combined queue (max 1)** |
| Bridge | `virbr0` 192.168.122.1/24, MTU 1500, sole member `vnet0` |
| Registry | `registry:2`, container `12eb788604ea`, PID 1445779, 172.17.0.2:5000, published 192.168.122.1:5001, TLS + htpasswd, **no CPU limit** |
| Registry data | `/srv/ai-models/runtimes/oci-registry/data` on `models/ai-models` (lz4, recordsize 1M, atime off) |
| `models` pool | 2x Samsung 9100 PRO 4TB, PCIe Gen5 x4 (32 GT/s), **striped**, 7.25T / 39% used |
| `scratch` pool | 2x Corsair MP700 PRO, PCIe Gen5 x4, striped; `scratch/vast-docker` zvol 64K, compression off |
| ARC | c_max 32.0 GiB, size 32.0 GiB (at cap) |

### Key derived numbers

| Quantity | Value |
|---|---|
| Pull rate | 156.32 GB / 116.06 s = **1.3467 GB/s = 10.774 Gbit/s** |
| Per-stream rate (3 streams) | **448.9 MB/s = 3.591 Gbit/s** |
| Fastest live physical port | 2500 Mb/s = 0.3125 GB/s -> **pull was 4.31x faster** |
| vhost thread lifetime CPU | 446.18 CPU-s (utime 0, stime 44,618 ticks) |
| vhost thread lifetime bytes | 676.0 GB (667.22 tx + 8.79 rx), 155.89 M packets |
| **vhost efficiency** | **1.5151 GB per CPU-second** -> pull = **88.9%** of it |
| vhost load, modelled (a=1.0-2.0 us/skb) | **53-71% of one core** |
| Guest NAPI CPU (`cpu22`) | 121.70 CPU-s for 667.22 GB = **5.483 GB/CPU-s** -> **24.6% busy** |
| Registry lifetime CPU | 194.97 CPU-s for 313.47 GB = **1.6078 GB/CPU-s** |
| Registry cost, one pull | 97.23 CPU-s / 116.06 s = **0.838 core-equivalents** (60 threads) |
| Registry bytes / stated pull | 313.47 / 156.32 = **2.005** -> exactly two runs |
| Frame size, registry eth0 TX | **50,906 B/packet** (TSO super-frames) |
| Frame size, guest enp1s0 RX | 6,492 B/packet (all traffic); segments/skb 4.468 |
| Gzip expansion, six big layers | **1.9088, 1.9090, 1.9102, 1.9126, 1.9992, 2.0040** |
| Inflate output required | 857 MB/s per stream, 2.57 GB/s aggregate |
| Pull composition | 6 layers x ~25 GB (152.54 GB) + 47 small (3.78 GB) = **53 blobs, 156.32 GB** |
