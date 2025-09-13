local mg     = require "moongen"
local memory = require "memory"
local device = require "device"
local ts     = require "timestamping"
local stats  = require "stats"
local hist   = require "histogram"
local bit    = require "bit"
local dpdkc  = require "dpdkc"
local ffi    = require "ffi"

function configure(parser)
	parser:description("Generate ethernet packets with an indentifier.")
	parser:argument("txDev", "Devices to transmit from."):convert(tonumber)
	parser:argument("rxDev", "Devices to receive from."):convert(tonumber)
	parser:option("-r --rate", "Transmit rate in Mbit/s. (0 to disable rate limiting)"):default(0):convert(tonumber)
    parser:option("-s --size", "Packet size in byte."):default(64):convert(tonumber)
    parser:option("-t --threads", "Number of Threads."):default(1):convert(tonumber)
	parser:option("-f --flows", "Number of Flows."):default(1):convert(tonumber)
	parser:option("-w --wait", "Time to wait before sending packets (in s)."):default(0):convert(tonumber)
end

function master(args)
    dpdkc.rte_vect_set_max_simd_bitwidth(512)

	local txDev = device.config({port = args.txDev, rxQueues = 1, txQueues = args.threads, disableOffloads = true})
	local rxDev = device.config({port = args.rxDev, rxQueues = 1, txQueues = 1, disableOffloads = true})	
	device.waitForLinks()

	-- remove size of automatically added crc
	args.size = args.size - 4

	if args.rate ~= 0 then
		txDev:setRate(args.rate, args.size)
	end

	mg.sleepMillis(args.wait*1000)

    stats.startStatsTask{txDev, rxDev}

	for i=1,args.threads do
		mg.startTask("gen", txDev:getTxQueue(i-1), i-1, args)
	end
    
	mg.waitForTasks()
end

function gen(queue, index, args)
	local mem = memory.createMemPool(function(buf)
		buf:getUdpPacket():fill{
			ethSrc = "12:13:14:15:16:17",
			ethDst = "12:13:14:15:16:18",
			ip4Dst = "10.0.0.2",
			udpSrc = 1234,
			udpDst = 1235
		}
	end)

    local counter = ffi.new("uint64_t", index)
	counter = bit.lshift64(counter, 56)
	
	local baseIP = parseIPAddress("10.0.0.0")
	local flowCounter = 1

	local bufs = mem:bufArray(128)
	while mg.running() do
		bufs:alloc(args.size)
        for i, buf in ipairs(bufs) do
			local pkt = buf:getUdpPacket()
			
			pkt.ip4.dst:set(baseIP + flowCounter)
			flowCounter = incAndWrap(flowCounter, args.flows)

			pkt.payload.uint64[0] = counter
            counter = counter + 1
		end
		queue:send(bufs)
	end
end

