local mg                  = require "moongen"
local memory              = require "memory"
local device              = require "device"
local ts                  = require "timestamping"
local hist                = require "histogram"
local ffi                 = require "ffi"

function configure(parser)
	parser:description("Measure the tx latency of a Intel E810 NIC.")
	
	-- Port settings
	parser:argument("dev", "Device to measure."):convert(tonumber)
end

function master(args)
	-- initialize ports
	local dev = device.config({port = args.dev})
	device.waitForLinks()

    dev:enableRxTimestampsAllPackets()
    mg.startSharedTask("measure", dev:getTxQueue(0), dev)
	mg.waitForTasks()
end

function measure(txQueue, dev)
	local mem = memory.createMemPool(function(buf)
		buf:getEthernetPacket():fill{
            ethSrc = "12:13:14:15:16:17",
			ethDst = "14:15:16:17:18:18",
			ethType = 0x1234
		}
	end)
    local hist = hist:new()
	local bufs = mem:bufArray(1)
	while mg.running() do
		bufs:alloc(64)
        bufs[1]:enableTimestamps()
        local push_ts = dev:readTime()
		txQueue:send(bufs)
        mg.sleepMillis(1)
        local send_ts = tonumber(dev:getTxTimestamp(txQueue, 0))
        hist:update(send_ts-push_ts)
	end
    hist:print()
    hist:save("histogram.csv")
end