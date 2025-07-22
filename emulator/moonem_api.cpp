#include <chrono>
#include <iostream>
#include <map>
#include <mutex>
#include <string>
#include <thread>
#include <sys/socket.h>
#include <cstring>
#include <netinet/in.h>
#include <unistd.h>
#include "moonem_common.h"
#include <atomic>

static std::mutex mutex_;
static connection_data* array_buffer = nullptr;
static connection_data* array_use = nullptr;
static uint64_t array_size = 0;
static std::atomic<bool> array_used_flag;

static void data_receiver(int connection, int amount, connection_data* arr) {
    ssize_t buffer_size = amount * sizeof(connection_data);
    ssize_t received = 0;

    while (received < buffer_size) {
        ssize_t len = read(connection, arr + received, buffer_size - received);
        if (len <= 0) {
            break;
        }
        received += len;
    }

    if (received == buffer_size) {
        for (int i = 0; i < amount; i++) {
            uint64_t ts = rte_get_tsc_hz() * (arr[i].timestamp);
            arr[i].timestamp = rte_rdtsc() + ts;
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
        std::cout << "Listening on port " << port << std::endl;
        int connection = accept(sock, nullptr, nullptr);
        std::cout << "Accepted connection" << std::endl;
        int amount = 0;
        if(read(connection, &amount, sizeof(amount)) <= 0) {
            break;
        }

        array_buffer = (connection_data*) malloc(amount * sizeof(connection_data));
        array_use = (connection_data*) malloc(amount * sizeof(connection_data));

        char msg[32];
        int len = sprintf(msg, "SEND %d", amount);
        write(connection, msg, len);
            
        data_receiver(connection, amount, array_use);
        array_size = amount;
        array_used_flag.store(true);

        while(1) {
            while(!array_used_flag.load());
            char msg[32] = {0};
            int len = sprintf(msg, "SEND %d", amount);
            write(connection, msg, len);
            data_receiver(connection, amount, array_buffer);
            array_used_flag.store(false);
        }
        close(connection);
        free(array_buffer);
        free(array_use);
    }
}

uint64_t cons = 0;

extern "C" float get_connection_data(uint64_t timestamp) {
    std::lock_guard<std::mutex> lock(mutex_);
    if(array_size > 0) {
        if((timestamp > array_use[array_size - 1].timestamp)) {
            uint64_t last_end_ts = array_use[array_size - 1].timestamp;
            memcpy(array_use, array_buffer, array_size * sizeof(connection_data));
            array_used_flag.store(true);
        }
    }
    return 0.1;
}