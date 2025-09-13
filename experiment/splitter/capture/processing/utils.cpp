#include "utils.h"

std::pair<uint64_t, uint64_t> minmaxTs(const std::unordered_map<uint64_t, uint64_t>& timestamps){
    uint64_t min{UINT64_MAX};
    uint64_t max{0};

    for(const auto& [k, v] : timestamps){
        if(v<min)min=v;
        if(v>max)max=v;
    }

    return std::make_pair(min, max);
}

std::pair<uint64_t, uint64_t> minmaxId(const std::unordered_map<uint64_t, uint64_t>& timestamps){
    uint64_t min{UINT64_MAX};
    uint64_t max{0};

    for(const auto& [k, v] : timestamps){
        if(k<min)min=k;
        if(k>max)max=k;
    }

    return std::make_pair(min, max);
}

std::pair<uint64_t, uint64_t> minmaxIdFirstPktGen(const std::unordered_map<uint64_t, uint64_t>& timestamps){
    uint64_t min{UINT64_MAX};
    uint64_t max{0};

    for(const auto& [k, v] : timestamps){
        if(k & 0xFF00000000000000ULL)continue;
        if(k<min)min=k;
        if(k>max)max=k;
    }

    return std::make_pair(min, max);
}

void removeOffset(std::unordered_map<uint64_t, uint64_t>& timestamps){
    auto [minTs, maxTs] = minmaxTs(timestamps);
    for(auto& [k, v] : timestamps){
        v -= minTs;
    }
}
