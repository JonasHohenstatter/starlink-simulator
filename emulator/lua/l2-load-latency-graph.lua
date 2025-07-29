local mg     = require "moongen"
local memory = require "memory"
local device = require "device"
local ts     = require "timestamping"
local stats  = require "stats"
local hist   = require "histogram"

local ETH_DST	= "12:13:14:15:16:17"

local function getRstFile(...)
	local args = { ... }
	for i, v in ipairs(args) do
		result, count = string.gsub(v, "%-%-result%=", "")
		if (count == 1) then
			return i, result
		end
	end
	return nil, nil
end

function configure(parser)
	parser:description("Generates bidirectional CBR traffic with hardware rate control and measure latencies.")
	parser:argument("dev1", "Device to transmit/receive from."):convert(tonumber)
	parser:argument("dev2", "Device to transmit/receive from."):convert(tonumber)
	parser:option("-r --rate", "Transmit rate in Mbit/s."):default(10000):convert(tonumber)
	parser:option("-f --file", "Filename of the latency histogram."):default("histogram.csv")
	parser:option("-s --size", "Packet size."):default(60):convert(tonumber)
end

function master(args)
	local dev1 = device.config({port = args.dev1, rxQueues = 2, txQueues = 2})
	local dev2 = device.config({port = args.dev2, rxQueues = 2, txQueues = 2})
	device.waitForLinks()
	dev1:getTxQueue(0):setRate(args.rate, args.size)
	dev2:getTxQueue(0):setRate(args.rate, args.size)
	mg.startTask("loadSlave", dev1:getTxQueue(0), args.size)
	if dev1 ~= dev2 then
		mg.startTask("loadSlave", dev2:getTxQueue(0), args.size)
	end
	stats.startStatsTask{dev1, dev2}
	mg.startSharedTask("timerSlave", dev1:getTxQueue(1), dev2:getRxQueue(1), args.file, args.size)
	mg.waitForTasks()
end

function loadSlave(queue, size)
	local mem = memory.createMemPool(function(buf)
		buf:getEthernetPacket():fill{
			ethSrc = nil, -- default ethernet source
			ethDst = ETH_DST,
			ethType = 0x1234
		}
	end)
	local bufs = mem:bufArray()
	while mg.running() do
		bufs:alloc(size)
		queue:send(bufs)
	end
end


function timerSlave(txQueue, rxQueue, histfile, size)
	local timestamper = ts:newTimestamper(txQueue, rxQueue)
	local latencies = {}
	mg.sleepMillis(1000) -- ensure that the load task is running
	local start = os.clock()
	while mg.running() do
		local timestamp = os.clock() - start
		local latency, _ = timestamper:measureLatency(function(buf) buf:getEthernetPacket().eth.dst:setString(ETH_DST) end, 100)
		if latency ~= nil then
			table.insert(latencies, {timestamp, latency / 1000000}) -- convert to microseconds		
		end
	end
	local file = io.open(histfile, "w")
	for _, pair in ipairs(latencies) do
		local timestamp, latency = unpack(pair)
		file:write(string.format("%.6f,%.6f\n", timestamp, latency))
	end
	file:close()
end

