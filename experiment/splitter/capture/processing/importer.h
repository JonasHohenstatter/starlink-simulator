#pragma once
#include <unistd.h>
#include <unordered_map>
#include <unordered_set>
#include <string>

class TimestampImporter{
public:
    static void readData(const std::string& path, std::unordered_map<uint64_t, uint64_t>& map);
private:
    struct packetInfo{
        uint64_t identifier;
        uint64_t timestamp;
    } __attribute__((__packed__));
};