/* IMPORTANT! This is an example. Real file is auto-generated from template. */

#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/udp.h>
#include "bpf_helpers.h"
#include "bpf_endian.h"

SEC("xdp_main")
int  xdp_filter(struct xdp_md *ctx)
{
    char *data_end = (char *)(long)ctx->data_end;
    char *eth = (char *)(long)ctx->data;

    struct ethhdr *eth_hdr = (struct ethhdr *) eth;
    struct iphdr *ip_hdr = (void *)eth_hdr + sizeof(struct ethhdr);
    if ((char *)ip_hdr + sizeof(struct iphdr) > data_end) {
        return XDP_PASS; // No room for IP header. Probably not IP, pass.
    }
    if (ip_hdr->protocol != 17) {
        return XDP_PASS; // Not UDP, pass.
    }
    char *ip_options = (void *)ip_hdr + 0x16;
    struct udphdr *udp_hdr = (void *)ip_hdr + (ip_hdr->ihl * 4);
    char *udp_data = (void *)udp_hdr + sizeof(udp_hdr);
    if (udp_data + 4 > data_end) {
        return XDP_PASS; // Packet doesn't contain "GET " - not our application (e.g., DNS?)
    }
    if (udp_data[0] != 'G' || udp_data[1] != 'E' || udp_data[2] != 'T' || udp_data[3] != ' ') {
        return XDP_PASS; // Only "GET" commands are protected, others just pass.
    }
    if (udp_data + 18 > data_end) {
        return XDP_DROP; // No flag ID in GET - strange (broken?) packet.
    }
    if (udp_data[4] == 'x' && udp_data[5] == 'x' && udp_data[6] == 'x' && udp_data[7] == 'x' && udp_data[8] == '-'
        && udp_data[9] == 'y' && udp_data[10] == 'y' && udp_data[11] == 'y' && udp_data[12] == 'y' && udp_data[13] == '-'
        && udp_data[14] == 'z' && udp_data[15] == 'z' && udp_data[16] == 'z' && udp_data[17] == 'z') {
        if (ip_hdr->ihl > 5 && ip_options + 4 <= data_end && *(unsigned int *)ip_options == bpf_htonl(0x11223344)) {
            return XDP_PASS;
        }
        return XDP_DROP;
    }
    return XDP_PASS;
}

char _license[] SEC("license") = "GPL";
