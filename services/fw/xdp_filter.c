#include <stddef.h>
#include <string.h>
#include <stdbool.h>
#include <linux/bpf.h>
#include <linux/in.h>
#include <linux/if_ether.h>
#include <linux/if_packet.h>
#include <linux/ip.h>
#include <linux/udp.h>
#include "bpf_helpers.h"
#include "bpf_endian.h"

//bool contains_id(void *ip, char *id) {
//    return true;
//}
//
//bool contains_pass(void *ip, unsigned int pass) {
//    return *(int *)((char *)ip + 0x16) == pass;
//}

SEC("xdp_main")
int  xdp_filter(struct xdp_md *ctx)
{
    char *data_end = (char *)(long)ctx->data_end;
    char *eth = (char *)(long)ctx->data;
//    void *udpdata;
//    void *ip;


    struct iphdr *ip_hdr;
//    struct udphdr *udp_hdr;

    char *ip = eth + sizeof(struct ethhdr);
    if (ip > data_end) {
        return XDP_PASS; // Not ethernet packet.
    }
    struct ethhdr *eth_hdr = (struct ethhdr *) eth;


    if (eth_hdr->h_proto != bpf_htons(ETH_P_IP)) {
        return XDP_PASS; // Unknown protocol.
    }

    ip_hdr = (void *)eth_hdr + sizeof(struct ethhdr);
//    ip = (void *)ip_hdr;
    if (ip_hdr->protocol != IPPROTO_UDP) {
        return XDP_PASS; // Invalid protocol.
    }

//    if (contains_id((void *)ip_hdr, "cf5j-dxa9-6gpx") && !contains_pass((void *)ip_hdr, 0x11223344)) {
//        return XDP_DROP;
//    }
//    udp = (void *)ip + sizeof(struct iphdr); // FIXME: check ihl
//    if (udp->dest != bpf_htons(17777)) {
//        return XDP_PASS; // Invalid port.
//    }


//    udpdata = (void *)udp + sizeof(struct udphdr);
//    for (i=0; i < 18; i++) {
//        if (*(char *)(udpdata + i) != get[i]) {
//            return XDP_PASS;
//        }
//    }
    return XDP_PASS;
}

char _license[] SEC("license") = "GPL";
