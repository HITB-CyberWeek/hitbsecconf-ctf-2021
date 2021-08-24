#include <stddef.h>
#include <string.h>
#include <linux/bpf.h>
#include <linux/in.h>
#include <linux/if_ether.h>
#include <linux/if_packet.h>
#include <linux/ip.h>
#include <linux/udp.h>
#include "bpf_helpers.h"
#include "bpf_endian.h"

SEC("xdp_main")
int  xdp_filter(struct xdp_md *ctx)
{
    void *data_end = (void *)(long)ctx->data_end;
    void *data = (void *)(long)ctx->data;
//    void *udpdata;
//    char *get = "GET cf5j-dxa9-6gpx";

    struct ethhdr *eth;
    struct iphdr *ip;
//    struct udphdr *udp;
//    int i;

    if (data + sizeof(struct ethhdr) + sizeof(struct iphdr) + sizeof(struct udphdr) + 18 > data_end) {
        return XDP_PASS; // Too short packet.
    }

    bpf_printk("Got packet %d (0x%x) bytes\n", data_end - data, data_end - data);

    eth = data;
    if (eth->h_proto != bpf_htons(ETH_P_IP)) {
        return XDP_PASS; // Invalid protocol.
    }
    ip = (void *)eth + sizeof(struct ethhdr);
    if (ip->protocol != IPPROTO_UDP) {
        return XDP_PASS; // Invalid protocol.
    }
//    udp = (void *)ip + sizeof(struct iphdr); // FIXME: check ihl
//    if (udp->dest != bpf_htons(17777)) {
//        return XDP_PASS; // Invalid port.
//    }
    if (*(int *)((char *)ip + 0x16) != 0x44332211) {
        return XDP_DROP;
    }

//    udpdata = (void *)udp + sizeof(struct udphdr);
//    for (i=0; i < 18; i++) {
//        if (*(char *)(udpdata + i) != get[i]) {
//            return XDP_PASS;
//        }
//    }
    return XDP_PASS;
}

char _license[] SEC("license") = "GPL";
