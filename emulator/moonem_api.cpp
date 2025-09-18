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

static int data_receiver(int connection, int amount, connection_data* arr) {
    ssize_t buffer_size = amount * sizeof(connection_data);
    ssize_t received = 0;

    while (received < buffer_size) {
        ssize_t len = read(connection, (char*)arr + received, buffer_size - received);
        if (len <= 0) {
            return 1;
        }
        received += len;
    }

    if (received == buffer_size) {
        for (int i = 0; i < amount; i++) {
            uint64_t ts = rte_get_tsc_hz() * (arr[i].timestamp);
            arr[i].timestamp = starting_ts + ts;
        }
    }
    return 0;
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
        int connection;
        int amount;
        connection = accept(sock, nullptr, nullptr);
        amount = 0;
        starting_ts = rte_rdtsc();

        if(read(connection, &amount, sizeof(amount)) <= 0) {
            continue;
        }

        array_buffer = new connection_data[amount]();
        array_use = new connection_data[amount]();

        char msg[32];
        int len = sprintf(msg, "SEND %d", amount);
        write(connection, msg, len);
                
        if(data_receiver(connection, amount, array_use)){
            continue;
        };

        write(connection, msg, len);

        if(data_receiver(connection, amount, array_buffer)) {
            break;
        };

        array_size = amount;

        array_used_flag.store(false);

        while(1) {
            while(array_buffer[0].timestamp > rte_rdtsc());
            memcpy(array_use, array_buffer, array_size * sizeof(connection_data));
            array_used_flag.store(true);
            write(connection, msg, len);
            if(data_receiver(connection, amount, array_buffer)) {
                break;
            };
            
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


static float linear_interpolation_float(float y0, float y1,
                                        float x0, float x1,
                                        float x) {
    if (x1 == x0) return y0;
    return y0 + (y1 - y0) * ((x - x0) / (x1 - x0));
}

extern "C" connection_data get_connection_data(uint64_t timestamp) {
    connection_data output = {};
    if(array_size > 0) {
        if(array_used_flag.load()) {
            current_index = 0;
            array_used_flag.store(false);
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
            
            output.delay = linear_interpolation(before.delay, after.delay, before.timestamp, after.timestamp, timestamp);
            output.loss = linear_interpolation_float(before.loss, after.loss, before.timestamp, after.timestamp, timestamp);
            output.capacity = before.capacity;
            return output;
        }
    }
    return output;
}