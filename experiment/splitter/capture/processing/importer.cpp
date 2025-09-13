#include "importer.h"
#include <string>
#include <iostream>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <fstream>
#include <unordered_set>

void TimestampImporter::readData(const std::string& path, std::unordered_map<uint64_t, uint64_t>& map){
    // code for memory mapped files adapted from https://w3.cs.jmu.edu/kirkpams/OpenCSF/Books/csf/html/MMap.html
    int file = open(path.c_str(), O_RDONLY);

    struct stat file_stats;
    fstat(file, &file_stats);

    char* file_data = (char*)mmap(NULL, file_stats.st_size, PROT_READ, MAP_PRIVATE, file, 0);
    uint64_t packetCount{0};
   
    if(file_stats.st_size % sizeof(struct packetInfo) != 0){
        std::cerr << "Invalid input file!" << std::endl;
    }

    struct packetInfo* packets = (struct packetInfo*) file_data;
    packetCount = file_stats.st_size / sizeof(struct packetInfo);

    for(uint64_t i = 0; i < packetCount; i++){
        uint64_t id = packets[i].identifier;
        uint64_t timestamp = packets[i].timestamp;
        map.emplace(id, timestamp);
    }

    munmap(file_data, file_stats.st_size);
    close(file);
    std::cout.flush();

    std::cerr << "Imported " << packetCount << " packets!" << std::endl;
}