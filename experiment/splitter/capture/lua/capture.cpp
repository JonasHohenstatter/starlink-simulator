// Modified version of Moongen "moonsniff.cpp" for use with timestamping tests

#include <cstdint>
#include <stdbool.h>
#include <ctime>
#include <string>
#include <iostream>
#include <mutex>
#include <fstream>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <unistd.h>

#include <rte_ethdev.h>
#include <rte_mbuf.h>
#include "lifecycle.hpp"
extern "C"{
	#include "timestamping.h"
}

namespace capture {
	/**
	 * Log packets.
	 */
	void ms_log_pkts(uint8_t port_id, uint16_t queue_id, struct rte_mbuf** rx_pkts, uint16_t nb_pkts, uint32_t packet_info_offset, const char* filename) {
		std::ofstream out (filename, std::ofstream::binary | std::ofstream::trunc);

		while (libmoon::is_running(0)) {
			uint16_t rx = rte_eth_rx_burst(port_id, queue_id, rx_pkts, nb_pkts);

			for (int i = 0; i < rx; i++) {
				uint64_t timestamp;
				
				//on ice NICs the timestamp is stored in the timestamp dynfield
				timestamp = get_timestamp_dynfield(rx_pkts[i]);

				if (packet_info_offset + 16 <= rx_pkts[i]->pkt_len) {
					uint64_t identifier = *(uint64_t*)((uint8_t*)rx_pkts[i]->buf_addr + rx_pkts[i]->data_off + packet_info_offset);

					out.write((char*)&identifier, sizeof(identifier));
					out.write((char*)&timestamp, sizeof(timestamp));
				} else {
					std::cerr << "Offset of sequence number greater than packet size\n";
				}

				rte_pktmbuf_free(rx_pkts[i]);
			}			
		}
	}

	typedef struct {
		uint32_t magic_number;  /* magic number */
		uint16_t version_major; /* major version number */
		uint16_t version_minor; /* minor version number */
		int32_t thiszone;       /* GMT to local correction */
		uint32_t sigfigs;       /* accuracy of timestamps */
		uint32_t snaplen;       /* max length of captured packets, in octets */
		uint32_t network;       /* data link type */
	} pcap_hdr_t;

	typedef struct {
		uint32_t ts_sec;   /* timestamp seconds */
		uint32_t ts_usec;  /* timestamp microseconds */
		uint32_t incl_len; /* number of octets of packet saved in file */
		uint32_t orig_len; /* actual length of packet */
	} pcaprec_hdr_t;

	size_t INITIAL_FILE_SIZE            = 512 * 1024 * 1024;
	uint32_t TCPDUMP_MAGIC              = 0xA1B2C3D4;
	uint32_t TCPDUMP_MAGIC_SWAPPED      = 0xD4C3B2A1;
	uint32_t TCPDUMP_MAGIC_NANO         = 0xA1B23C4D;
	uint32_t TCPDUMP_MAGIC_NANO_SWAPPED = 0x4D3CB2A1;

	void pcap_log_pkts(uint8_t port_id, uint16_t queue_id, struct rte_mbuf** rx_pkts, uint16_t nb_pkts, uint32_t packet_info_offset, const char* filename, uint32_t snap_len) {
		int fd = open(filename, O_RDWR | O_CREAT | O_TRUNC, 0666);
		if (!fd) {
			std::cerr << "open failed" << std::endl;
		}
		size_t size = INITIAL_FILE_SIZE;
		int ret = ftruncate(fd, size);
		if (ret) {
			std::cerr << "ftruncate failed: " << errno << std::endl;
		}
		uint8_t* addr = static_cast<uint8_t*>(mmap(0, size, PROT_WRITE, MAP_SHARED | MAP_NORESERVE, fd, 0));
		if (addr == MAP_FAILED) {
			std::cerr << "mmap failed: " << errno << std::endl;
		}

		size_t offset = 0;
		pcap_hdr_t hdr;
		pcaprec_hdr_t rechdr;

		hdr.magic_number = TCPDUMP_MAGIC_NANO;
		hdr.version_major = 2;
		hdr.version_minor = 4;
		hdr.thiszone = 0;
		hdr.sigfigs = 0;
		hdr.snaplen = snap_len;
		hdr.network = 1;

		memcpy(addr, &hdr, sizeof(pcap_hdr_t));
		offset += sizeof(pcap_hdr_t);

		while (libmoon::is_running(0)) {
			uint16_t rx = rte_eth_rx_burst(port_id, queue_id, rx_pkts, nb_pkts);

			for (int i = 0; i < rx; i++) {
				uint32_t incl_len = (rx_pkts[i]->pkt_len < snap_len) ? rx_pkts[i]->pkt_len : snap_len;
				if ((size_t)(offset + rx_pkts[i]->pkt_len + 8) >= size) {
					ftruncate(fd, 2*size);
					void* temp = mremap(addr, size, size*2, MREMAP_MAYMOVE);
					if (temp == (void*)-1) {
						perror("Error on mremap()");
					}
					addr = static_cast<uint8_t*>(temp);
					size *= 2;
				}
	
				uint32_t low;
				uint32_t high;
				
				//on ice NICs the timestamp is stored in the timestamp dynfield
				uint64_t timestamp64 = get_timestamp_dynfield(rx_pkts[i]);
				low = timestamp64 % 1000000000;
				high = timestamp64 / 1000000000;

				rechdr.ts_sec = high;
				rechdr.ts_usec = low;
				rechdr.incl_len = incl_len;
				rechdr.orig_len = rx_pkts[i]->pkt_len;
				memcpy(addr + offset, &rechdr, sizeof(rechdr));
				memcpy(addr + offset + sizeof(rechdr), (uint8_t*)rx_pkts[i]->buf_addr + rx_pkts[i]->data_off, incl_len);
				offset += incl_len + 16;

				rte_pktmbuf_free(rx_pkts[i]);
			}
		}

		munmap(addr, size);
		ftruncate(fd, offset);
		fsync(fd);
		close(fd);
	}

}

extern "C" {
	void capture_ms_log_pkts(uint8_t port_id, uint16_t queue_id, struct rte_mbuf** rx_pkts, uint16_t nb_pkts, uint32_t packet_info_offset, const char* filename) {
		capture::ms_log_pkts(port_id, queue_id, rx_pkts, nb_pkts, packet_info_offset, filename);
	}

	void capture_pcap_log_pkts(uint8_t port_id, uint16_t queue_id, struct rte_mbuf** rx_pkts, uint16_t nb_pkts, uint32_t packet_info_offset, const char* filename, uint32_t snap_len) {
		capture::pcap_log_pkts(port_id, queue_id, rx_pkts, nb_pkts, packet_info_offset, filename, snap_len);
	}

}