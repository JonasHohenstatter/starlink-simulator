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

static std::mutex mutex_;
static connection_data* arr;

extern "C" void receive_connection_data_loop(int port) {
    std::lock_guard<std::mutex> lock(mutex_);
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in address;
    std::cout << arr << "\n";
    address.sin_family = AF_INET;
    address.sin_port = htons(port);
    address.sin_addr.s_addr = INADDR_ANY;

    bind(sock, (struct sockaddr*)&address, sizeof(address));
    listen(sock, 1);

    char buffer[1024] = {0};
    while(1) {
        int connection = accept(sock, nullptr, nullptr);
        while(1) {
            memset(buffer, 0, sizeof(buffer));
            ssize_t len = read(connection, buffer, 1024);
            if(len == 0) {
                break;
            }
            std::cout << buffer;
        }
        close(connection);
    }
}

extern "C" float get_connection_data(uint64_t timestamp) {
    std::lock_guard<std::mutex> lock(mutex_);
    std::cout << timestamp << "\n";
    return 0.1;
}