#pragma once

#include <iostream>
#include <unordered_map>
#include <unistd.h>

std::pair<uint64_t, uint64_t> minmaxTs(const std::unordered_map<uint64_t, uint64_t>& timestamps);
std::pair<uint64_t, uint64_t> minmaxId(const std::unordered_map<uint64_t, uint64_t>& timestamps);
std::pair<uint64_t, uint64_t> minmaxIdFirstPktGen(const std::unordered_map<uint64_t, uint64_t>& timestamps);
void removeOffset(std::unordered_map<uint64_t, uint64_t>& timestamps);