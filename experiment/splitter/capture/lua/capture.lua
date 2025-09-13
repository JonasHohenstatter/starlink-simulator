--- Modified version of the Moongen Moonsniff Example script (removed unused options and functions and add multithreading and temperature measurements)

local mg     	= require "moongen"
local device 	= require "device"
local memory 	= require "memory"
local ts     	= require "timestamping"
local hist   	= require "histogram"
local timer  	= require "timer"
local log    	= require "log"
local stats  	= require "stats"
local barrier 	= require "barrier"
local pcap		= require "pcap"
local ms		= require "moonsniff-io"
local dpdkc		= require "dpdkc"

local ffi    	= require "ffi"
local capture = ffi.load("build/capture")

ffi.cdef[[
    void capture_ms_log_pkts(uint8_t port_id, uint16_t queue_id, struct rte_mbuf** rx_pkts, uint16_t nb_pkts, uint32_t packet_info_offset, const char* filename);
    void capture_pcap_log_pkts(uint8_t port_id, uint16_t queue_id, struct rte_mbuf** rx_pkts, uint16_t nb_pkts, uint32_t packet_info_offset, const char* filename, uint32_t snap_len);
]]

function configure(parser)
	parser:description("Capture packets using a E810 NIC.\nThe packets can be written to a pcap or to a binary file with timestamps and IDs.")
	parser:argument("dev", "devices to use."):args("+"):convert(tonumber)

	parser:flag("-p --pcap", "Store packets as pcap file.")

	parser:option("-f --filter", "Filter for the packets which should be captured (prepended x is required e.g. \"xFFFF\")"):default(""):convert(tostring)

	parser:option("-o --output", "Path to output files."):args(1):default(".")
	parser:option("--seq-offset", "Offset of the sequence number in bytes."):args("+"):convert(tonumber):default({42})
	parser:option("-s --snaplen", "Maximum capture length of recorded packets (default size 64 B). Only used when capturing pcaps."):args(1):convert(tonumber):default(64)
	parser:option("-t --threads", "Number of threads used for capturing (default 1)."):args(1):convert(tonumber):default(1)

	return parser:parse()
end

function configurePort(args, dev, index)
	local outputPrefix = ""
	if #args.dev ~= 1 then
		outputPrefix = tostring(index).."-"
	end

	stats.startStatsTask{rxDevices = {dev}, file = args.output .. "/" .. outputPrefix .. "capture-stats.csv", format = "csv"}
	dev:enableRxTimestampsAllPackets(dev)
	dev:clearTimestamps()

	-- if multiple offsets are specified, select the offset based on the port index
	local seq_offset = args.seq_offset[1]
	if #(args.seq_offset) ~= 1 then
		seq_offset = args.seq_offset[index]
	end

    local fileExtension
    if args.pcap then
        fileExtension = ".pcap"
    else
        fileExtension = ".cap"
    end


	if args.filter ~= "" and args.threads == 1 then
		-- capture only form queue 1 if filtering is enabled. The packets on queue 0 are dropped
		mg.startTask("timestamp", dev:getRxQueue(1), args, args.output.."/"..outputPrefix.."capture"..fileExtension, seq_offset)
	else 
		-- start the tasks to sample incoming packets
		if args.threads == 1 then
			mg.startTask("timestamp", dev:getRxQueue(0), args, args.output.."/"..outputPrefix.."capture-1"..fileExtension, seq_offset)
		else
			for i=1,args.threads do
				mg.startTask("timestamp", dev:getRxQueue(i-1), args, args.output.."/"..outputPrefix.."capture-"..tostring(i)..fileExtension, seq_offset)
			end
		end
	end
end

function master(args)
	-- if filter should be applied -> matched packets are captured from queue 1
	local threads = args.threads
	if args.filter ~= "" and threads == 1 then
		threads = 2
	end

	-- start all used ports
	local devices = {}
	for i, dev in ipairs(args.dev) do
		devices[i] = device.config{port = args.dev[i], txQueues = 1, rxQueues = threads, dropEnable = false, rssQueues = args.threads, rxDescs = 2048}
	end
	device.waitForLinks()

	-- configure all ports
	for i, dev in ipairs(devices) do
		configurePort(args, dev, i)
	end

    log:info("Started capturing packets")

	-- wait for all capturing processed to end
	mg.waitForTasks()
	log:info("Finished all capturing/writing operations")
end

function timestamp(queue, args, outputName, seq_offset)
	local bufs = memory.bufArray()
	local drainQueue = timer:new(0.5)
	while mg.running() and drainQueue:running() do
		local rx = queue:tryRecv(bufs, 1000)
		bufs:free(rx)
	end

	if args.pcap then
        capture.capture_pcap_log_pkts(queue.id, queue.qid, bufs.array, bufs.size, seq_offset, outputName, args.snaplen)
	else
        capture.capture_ms_log_pkts(queue.id, queue.qid, bufs.array, bufs.size, seq_offset, outputName)
	end
end
