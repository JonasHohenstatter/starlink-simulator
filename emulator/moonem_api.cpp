#include <chrono>
#include <iostream>
#include <map>
#include <string>
#include <thread>
#include <sys/socket.h>
#include <cstring>
#include <netinet/in.h>
#include <unistd.h>
#include "moonem_common.h"
#include <atomic>

static connection_data* array_buffer = nullptr;
static connection_data* array_use = nullptr;
static uint64_t array_size = 0;
static std::atomic<bool> array_used_flag;
static uint64_t starting_ts;

static void data_receiver(int connection, int amount, connection_data* arr) {
    ssize_t buffer_size = amount * sizeof(connection_data);
    ssize_t received = 0;

    while (received < buffer_size) {
        ssize_t len = read(connection, (char*)arr + received, buffer_size - received);
        if (len <= 0) {
            break;
        }
        received += len;
    }

    if (received == buffer_size) {
        for (int i = 0; i < amount; i++) {
            uint64_t ts = rte_get_tsc_hz() * (arr[i].timestamp);
            arr[i].timestamp = starting_ts + ts;
        }
    }
}

extern "C" void receive_connection_data_loop(int port) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
    setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_port = htons(port);
    address.sin_addr.s_addr = INADDR_ANY;

    int b = bind(sock, (struct sockaddr*)&address, sizeof(address));
    if(b < 0) {
        std::cerr << "Failed to bind socket: " << strerror(errno) << std::endl;
        return;
    }
    listen(sock, 1);
    
    while(1) {
        int connection = accept(sock, nullptr, nullptr);
        int amount = 0;
        starting_ts = rte_rdtsc();

        if(read(connection, &amount, sizeof(amount)) <= 0) {
            break;
        }

        std::cout << "received: " << amount << std::endl;

        array_buffer = (connection_data*) malloc(amount * sizeof(connection_data));
        array_use = (connection_data*) malloc(amount * sizeof(connection_data));

        array_buffer = new connection_data[amount]();
        array_use = new connection_data[amount]();
        std::cout << "received" << std::endl;

        char msg[32];
        int len = sprintf(msg, "SEND %d", amount);
        write(connection, msg, len);
            
        data_receiver(connection, amount, array_use);
        
        
        array_used_flag.store(true);

        while(1) {
            while(!array_used_flag.load());
            char msg[32] = {0};
            std::cout << "received" << std::endl;
            int len = sprintf(msg, "SEND %d", amount);
            write(connection, msg, len);
            data_receiver(connection, amount, array_buffer);
            array_size = amount;
            array_used_flag.store(false);
        }
        close(connection);
        free(array_buffer);
        free(array_use);
    }
}

static uint64_t current_index = 0;

static uint64_t linear_interpolation(uint64_t y0, uint64_t y1, uint64_t x0, uint64_t x1, uint64_t x) {
    if (x1 == x0) return y0;
    __int128 dx = (int64_t)(x - x0);
    __int128 dy = (int64_t)(y1 - y0);
    __int128 range = (int64_t)(x1 - x0);

    __int128 result = (__int128)y0 + dy * dx / range;
    return (uint64_t)result;
}

extern "C" uint64_t get_connection_data(uint64_t timestamp) {
    if(array_size > 0) {
        if(not array_used_flag.load()) {
            if(timestamp >= array_buffer[0].timestamp && array_buffer[0].timestamp > 0) {
                memcpy(array_use, array_buffer, array_size * sizeof(connection_data));
                array_used_flag.store(true);
                current_index = 0;
            }
        }
        if(timestamp >= array_use[0].timestamp && array_use[0].timestamp > 0) {
            connection_data before;
            connection_data after;
            while(current_index < (array_size - 1) && array_use[current_index + 1].timestamp <= timestamp) {
                current_index += 1;
            }
            if(timestamp > array_use[array_size - 1].timestamp) {
                before = array_use[array_size - 1];
                after = array_buffer[0];
            }
            else {
                before = array_use[current_index];
                after = array_use[current_index + 1];
            }
            if(not(before.timestamp <= timestamp && after.timestamp >= timestamp)) {
                std::cerr << "Timestamp out of bounds: " << timestamp << std::endl;
            }
            return linear_interpolation(before.delay, after.delay, before.timestamp, after.timestamp, timestamp);
        }
    }
    return 0;
}