OUT_FILE = os.getenv("OUT_FILE") or "results"
TEST_NAME = os.getenv("TEST_NAME") or "unknown"
PKG_COUNT = tonumber(os.getenv("PKG_COUNT") or "1500")

function file_exists(name)
   local f=io.open(name,"r")
   if f~=nil then io.close(f) return true else return false end
end

lines = {}
for line in io.lines('./pkglist.txt') do
    lines[#lines + 1] = line
end

request = function() 
    method = 'POST'
    path = '/api/v1/updates'
    wrk.headers['Content-Type'] = 'application/json'
    body = '{"package_list": ['

    for i=1,PKG_COUNT do
      body = body .. "\"" .. lines[math.random(1,#lines)] .. "\","
    end
    -- Add last without trailing comma
    body = body ..  "\"" .. lines[math.random(1,#lines)] .. "\"]}"
    -- print(body)
    return wrk.format(method, path, wrk.headers, body)
end



done = function(summary, latency, requests)
    -- open output file
    filename = 'out/' .. OUT_FILE .. '.csv'
    if file_exists(filename) then
        file = io.open(filename, "a+")
    else
        file = io.open(filename, "a+")
        file:write(string.format("name, pkg_count, minlat, maxlat, meanlat, stddev, 50, 90, 99, 99.999, duration, reqs, bytes\n"))
    end

    -- write below results to file
    --   minimum latency
    --   max latency
    --   mean of latency
    --   standard deviation of latency
    --   50percentile latency
    --   90percentile latency
    --   99percentile latency
    --   99.999percentile latency
    --   duration of the benchmark
    --   total requests during the benchmark
    --   total received bytes during the benchmark
    
    file:write(string.format("%s,%d, %f,%f,%f,%f,%f,%f,%f,%f,%d,%d,%d\n",
    TEST_NAME,
    PKG_COUNT,
    latency.min, latency.max, latency.mean, latency.stdev, latency:percentile(50),
    latency:percentile(90), latency:percentile(99), latency:percentile(99.999),
    summary["duration"], summary["requests"], summary["bytes"]))
    
    file:close()
  end
