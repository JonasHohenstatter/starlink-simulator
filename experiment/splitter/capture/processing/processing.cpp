#include <iostream>
#include <unistd.h>
#include <fstream>
#include <unordered_map>
#include <map>
#include <thread>
#include <functional>
#include <vector>
#include <algorithm>
#include <iterator>
#include <cmath>
#include <filesystem>

#include "importer.h"
#include "utils.h"

void latency_histogram(const std::string& path, const std::unordered_map<uint64_t, uint64_t>& pre, const std::unordered_map<uint64_t, uint64_t>& post){
    std::map<int64_t, uint64_t> hist;

    for(const auto& [k, v] : pre){
        auto postElement = post.find(k);
        if(postElement != post.end()){
            int64_t diff = postElement->second - v;
            ++hist[diff];
        }
    }

    std::ofstream file;
    file.open(path.c_str(), std::ios::out | std::ios::trunc);

    for(const auto& [k, v] : hist){
        file << std::fixed << k << "," << v << std::endl;
    }

    std::cout << "Finished writing " << path << "!" << std::endl;
}

void latency_worst(const std::string& path, const std::unordered_map<uint64_t, uint64_t>& pre, const std::unordered_map<uint64_t, uint64_t>& post, uint64_t count){
    std::vector<std::pair<int64_t, uint64_t>> latencies;

    for(const auto& [k, v] : pre){
        auto postElement = post.find(k);
        if(postElement != post.end()){
            int64_t latency = postElement->second - v;
            latencies.push_back({latency, v});
        }
    }

    std::sort(latencies.begin(), latencies.end(), std::greater());

    std::ofstream file;
    file.open(path.c_str(), std::ios::out | std::ios::trunc);

    uint64_t i = 0;
    for(const auto& [l, t] : latencies){
        if(i++ >= count) break;
        file << std::fixed << t << "," << l << std::endl;
    }

    std::cout << "Finished writing " << path << "!" << std::endl;
}

void latency_median(const std::string& path, const std::unordered_map<uint64_t, uint64_t>& pre, const std::unordered_map<uint64_t, uint64_t>& post){
    std::vector<int64_t> latencies;

    for(const auto& [k, v] : pre){
        auto postElement = post.find(k);
        if(postElement != post.end()){
            int64_t latency = postElement->second - v;
            latencies.push_back(latency);
        }
    }

    std::sort(latencies.begin(), latencies.end(), std::less());

    std::ofstream file;
    file.open(path.c_str(), std::ios::out | std::ios::trunc);

    int median_index = latencies.size() / 2;
    double median_value;
    if(latencies.size() % 2 != 0){
        median_value = latencies[median_index];
    }else{
        median_value = (latencies[median_index-1]+latencies[median_index])/2.0f;
    }
    file << std::fixed << median_value << std::endl;
    
    std::cout << "Finished writing " << path << "!" << std::endl;
}

void latency_percentiles(const std::string& path, const std::unordered_map<uint64_t, uint64_t>& pre, const std::unordered_map<uint64_t, uint64_t>& post, std::vector<double> percentiles){
    std::vector<int64_t> latencies;

    for(const auto& [k, v] : pre){
        auto postElement = post.find(k);
        if(postElement != post.end()){
            int64_t latency = postElement->second - v;
            latencies.push_back(latency);
        }
    }

    std::sort(latencies.begin(), latencies.end(), std::less());

    std::ofstream file;
    file.open(path.c_str(), std::ios::out | std::ios::trunc);

    for(double p: percentiles){
        int percentile_index = std::max(std::ceil(latencies.size() * p) - 1, 0.0);
        uint64_t percentile_value = latencies[percentile_index];
        file << std::fixed << p << "," << percentile_value << std::endl;
    }
    std::cout << "Finished writing " << path << "!" << std::endl;
}

void latency_average_total(const std::string& path, const std::unordered_map<uint64_t, uint64_t>& pre, const std::unordered_map<uint64_t, uint64_t>& post){
    double average = 0;
    uint64_t count = 0;

    // averaging from https://stackoverflow.com/a/1934266
    for(const auto& [k, v] : pre){
        auto post_ts = post.find(k);
        if(post_ts != post.end()){
            int64_t diff = post_ts->second - v;
            count++;
            average += (diff-average) / count;
        }
    }

    {
        // output average latency
        std::ofstream file;
        file.open(path.c_str(), std::ios::out | std::ios::trunc);
        file << std::fixed << average << std::endl;
        std::cout << "Finished writing " << path << "!" << std::endl;
    }
}

void latency_average(const std::string& path, const std::unordered_map<uint64_t, uint64_t>& pre, const std::unordered_map<uint64_t, uint64_t>& post, uint64_t bucket_size){
    std::map<uint64_t, double> buckets;
    std::map<uint64_t, uint64_t> count;

    // averaging from https://stackoverflow.com/a/1934266
    for(const auto& [k, v] : pre){
        auto post_ts = post.find(k);
        if(post_ts != post.end()){
            int64_t diff = post_ts->second - v;
            uint64_t bucket = v / bucket_size;
            
            count[bucket]++;
            buckets[bucket] += (diff-buckets[bucket]) / count[bucket];
        }
    }

    {
        // output average latency
        std::ofstream file;
        file.open(path.c_str(), std::ios::out | std::ios::trunc);

        for(const auto& [k, v] : buckets){
            file << std::fixed << k*bucket_size << "," << v << std::endl;
        }
        std::cout << "Finished writing " << path << "!" << std::endl;
    }
}

void ipg_histogram(const std::string& path, const std::unordered_map<uint64_t, uint64_t>& timestamps){
    std::map<int64_t, uint64_t> hist;

    // calculate 
    for(const auto& [k, v] : timestamps){
        auto next_ts = timestamps.find(k+1);
        if(next_ts != timestamps.end()){
            int64_t diff = next_ts->second - v;            
            hist[diff]++;
        }
    }

    {
        // output ipg histogram latency
        std::ofstream file;
        file.open(path.c_str(), std::ios::out | std::ios::trunc);

        for(const auto& [k, v] : hist){
            file << std::fixed << k << "," << v << std::endl;
        }
        std::cout << "Finished writing " << path << "!" << std::endl;
    }
}

void loss_over_time(const std::string& path, const std::unordered_map<uint64_t, uint64_t>& pre, const std::unordered_map<uint64_t, uint64_t>& post, uint64_t bucket_size){
    std::map<uint64_t, std::pair<uint64_t,uint64_t>> loss_buckets;

    // count lost packets
    for(const auto& [k, v] : pre){
        auto post_ts = post.find(k);
        uint64_t bucket = v / bucket_size;

        if(post_ts == post.end()){
            loss_buckets[bucket].first++;
        }else{
            loss_buckets[bucket].second++;
        }
    }

    {
        // output loss values over time
        std::ofstream file;
        file.open(path.c_str(), std::ios::out | std::ios::trunc);

        for(const auto& [k, v] : loss_buckets){
            file << std::fixed << k*bucket_size << "," << v.first << "," << v.second << std::endl;
        }
        std::cout << "Finished writing " << path << "!" << std::endl;
    }
}

void removeStartAndEnd(std::unordered_map<uint64_t, uint64_t>& ts, uint64_t time){
    auto [minTS, maxTS] = minmaxTs(ts);
    std::erase_if(ts, [&minTS, &maxTS, &time](const auto& x){return x.second - minTS < time; });
    std::erase_if(ts, [&minTS, &maxTS, &time](const auto& x){return maxTS - x.second < time; });
}

void removeStart(std::unordered_map<uint64_t, uint64_t>& ts, uint64_t time){
    auto [minTS, maxTS] = minmaxTs(ts);
    std::erase_if(ts, [&minTS, &maxTS, &time](const auto& x){return x.second - minTS < time; });
}

void packet_count(const std::string& path, std::unordered_map<uint64_t, uint64_t>& timestamps){
    // output packet count to file
    std::ofstream file;
    file.open(path.c_str(), std::ios::out | std::ios::trunc);
    file << std::fixed << timestamps.size() << std::endl;
    std::cout << "Finished writing " << path << "!" << std::endl;
}

int main(int argc, char** argv){
    std::vector<std::string> arguments(argv, argv+argc);
    std::string inputPre{arguments.at(1)};
    std::string inputPost{arguments.at(2)};
    std::string output{arguments.at(3)};
    std::string removeFirst{arguments.at(4)};

    // parse number of seconds to remove from the start of the data
    int removeFirstSeconds = std::stoi(removeFirst);

    // load timestamps into hashmaps
    std::unordered_map<uint64_t, uint64_t> preTimestamps;
    std::unordered_map<uint64_t, uint64_t> postTimestamps;

    std::thread preThread([&preTimestamps, inputPre, output, removeFirstSeconds](){
        for(int i{1};;i++){
            std::string filePath = inputPre + "-" + std::to_string(i) + ".cap";
            if(!std::filesystem::exists(filePath)) break;
            TimestampImporter::readData(filePath, preTimestamps);
        }
        packet_count(output+"/count_pre.csv", preTimestamps);
        removeStartAndEnd(preTimestamps, 1000000000ul);
        if(removeFirstSeconds != 0) removeStart(preTimestamps, 1000000000ul * removeFirstSeconds);
    });

    std::thread postThread([&postTimestamps, inputPost, output, removeFirstSeconds](){
        for(int i{1};;i++){
            std::string filePath = inputPost + "-" + std::to_string(i) + ".cap";
            if(!std::filesystem::exists(filePath)) break;
            TimestampImporter::readData(filePath, postTimestamps);
        }
        packet_count(output+"/count_post.csv", postTimestamps);
        removeStartAndEnd(postTimestamps, 1000000000ul);
        if(removeFirstSeconds != 0) removeStart(postTimestamps, 1000000000ul * removeFirstSeconds);
    });

    preThread.join();
    postThread.join();

    // register all processing functions
    std::map<std::string, std::vector<std::function<void()>>> functions;

    functions["latency_histogram"].push_back([&](){latency_histogram(output+"/latency_histogram.csv", preTimestamps, postTimestamps); });

    functions["latency_worst"].push_back([&](){latency_worst(output+"/latency_worst.csv", preTimestamps, postTimestamps, 500000); });

    functions["latency_percentiles"].push_back([&](){latency_percentiles(output+"/latency_percentiles.csv", preTimestamps, postTimestamps, {0.0, 0.25, 0.50, 0.75, 1.0}); });
    
    functions["latency_average_total"].push_back([&](){latency_average_total(output+"/latency_average_total.csv", preTimestamps, postTimestamps); });

    functions["latency_median"].push_back([&](){latency_median(output+"/latency_median.csv", preTimestamps, postTimestamps); });

    functions["latency_average"].push_back([&](){latency_average(output+"/latency_average.csv", preTimestamps, postTimestamps, 5000000); });

    functions["ipg_histogram"].push_back([&](){ipg_histogram(output+"/ipg_histogram_pre.csv", preTimestamps); });
    functions["ipg_histogram"].push_back([&](){ipg_histogram(output+"/ipg_histogram_post.csv", postTimestamps); });

    functions["loss_over_time"].push_back([&](){loss_over_time(output+"/loss_over_time.csv", preTimestamps, postTimestamps, 1000000); });

    // start all processing threads
    std::vector<std::thread> processingThreads;
    for(size_t i{4}; i < arguments.size(); i++){
        auto functionList = functions.find(arguments[i]);
        if(functionList == functions.end())continue;

        for(auto func : functionList->second){
            processingThreads.push_back(std::thread(func));
        }
    }

    // wait for processing threads to finish
    for(auto& t : processingThreads){
        t.join();
    }

    std::cout << "Created output files!" << std::endl;

    // dont run destructors and let Linux clean up the memory -> faster
    exit(0);
}