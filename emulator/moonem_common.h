#include <rte_mbuf.h>

struct moonem_config {
	uint64_t delay;
	uint64_t rate;
	uint64_t capacity;
	uint64_t loss_seed;
	float loss;
};

struct connection_data {
	uint64_t timestamp;
	uint64_t delay;
	uint64_t capacity;
	float loss;
};

#define BURST_SIZE 64
#define CONNECTION_DATA_AMOUNT 10
#define MIN(a,b) ((a) < (b) ? (a) : (b))
#define MAX(a,b) ((a) > (b) ? (a) : (b))

extern "C" connection_data get_connection_data(uint64_t timestamp);

//https://lemire.me/blog/2019/03/19/the-fastest-conventional-random-number-generator-that-can-pass-big-crush/
static uint64_t wyhash64(uint64_t* state) {
	*state += 0x60bee2bee120fc15;
  	__uint128_t tmp;
  	tmp = (__uint128_t) *state * 0xa3b195354a39b70d;
  	uint64_t m1 = (tmp >> 64) ^ tmp;
  	tmp = (__uint128_t)m1 * 0x1b03738712fad5c9;
  	uint64_t m2 = (tmp >> 64) ^ tmp;
  	return m2;
}

inline int applyLoss(uint16_t rx, struct rte_mbuf** bufs, struct rte_mbuf** bufs_send, uint64_t loss, uint64_t* loss_state){
	int accept_index = 0;
	for (int i = 0; i < rx; i++) {
		if(wyhash64(loss_state) < loss){
			rte_pktmbuf_free(bufs[i]);
		}else{
			bufs_send[accept_index++] = bufs[i];
		}
	}
	return accept_index;
}
