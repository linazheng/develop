#include "query_computepool.h"

using namespace zhicloud;
using namespace control_server;
using namespace util;

QueryComputePoolTask::QueryComputePoolTask(NodeService *messsage_handler,ComputePoolManager& computepool_manager,StatusManager& status_manager)
    :BaseTask(TaskType::query_compute_pool, "QueryComputePoolTask", (uint32_t)RequestEnum::query_compute_pool, messsage_handler),
    _computepool_manager(computepool_manager),
    _status_manager(status_manager)
{
    _logger = getLogger("QueryComputePoolTask");

}


void QueryComputePoolTask::invokeSession(TaskSession &session)
{
    try{
        AppMessage &request = session.getInitialMessage();

        map<UUID_TYPE,ComputePool> pool_list;
        _computepool_manager.queryAllPool(pool_list);
         _logger->info(boost::format("[%08X] <query_compute_pool> success, %d compute pools available") %session.getSessionID() %pool_list.size());

        AppMessage::string_array_type name;
        AppMessage::string_array_type uuid;
        AppMessage::uint_array_array_type node;
        AppMessage::uint_array_array_type host;
        AppMessage::uint_array_type cpu_count;
        AppMessage::float_array_type cpu_usage;
        AppMessage::uint_array_array_type memory;
        AppMessage::float_array_type memory_usage;
        AppMessage::uint_array_array_type disk_volume;
        AppMessage::float_array_type disk_usage;
        AppMessage::uint_array_type status;

        AppMessage::uint_array_type tmp;
        
        /*vector<string> name;
        vector<UUID_TYPE> uuid;
        vector<vector<uint64_t>> node;
        vector<vector<uint64_t>> host;
        vector<uint64_t> cpu_count;
        vector<float> cpu_usage;
        vector<vector<uint64_t>> memory;
        vector<float> memory_usage;
        vector<vector<uint64_t>> disk_volume;
        vector<float> disk_usage;
        vector<uint64_t> status;

         vector<uint64_t> tmp;*/

        for(const auto & compute_pool :pool_list)
        {
            ComputePoolStatus pool;
            if(!_status_manager.getComputePoolStatus(compute_pool.first,pool))
            {
                pool.setName(compute_pool.second.getName());
                pool.setUUID(compute_pool.second.getUUID());
                pool.setStatus(UnitStatusEnum(compute_pool.second.getStatus()));
                //TODO: pool.setStatus(UnitStatusEnum::status_stop);
        }


            name.emplace_back(pool.getName());
            uuid.emplace_back(pool.getUUID());
            cpu_count.emplace_back(pool.getCpuCounter().getCpuCount());
            cpu_usage.emplace_back(pool.getCpuCounter().getCpuUsage());
            memory_usage.emplace_back(pool.getMemoryUsage());
            disk_usage.emplace_back(pool.getDiskUsage());
            status.emplace_back(uint64_t(pool.getStatus()));

            pool.getHost().transfertoArray(tmp);
            host.emplace_back(tmp);
            pool.getMemory().transfertoArray(tmp);
            memory.emplace_back(tmp);
            pool.getHost().transfertoArray(tmp);
            disk_volume.emplace_back(tmp);

        }

        //response
        AppMessage response(AppMessage::message_type::RESPONSE, RequestEnum::query_compute_pool);
        response.session = session.getRequestSession();
        response.success = true;

        response.setStringArray(ParamEnum::name, name);
        response.setStringArray(ParamEnum::uuid, uuid);
        response.setUIntArrayArray(ParamEnum::node, node);
        response.setUIntArrayArray(ParamEnum::host, host);
        response.setUIntArray(ParamEnum::cpu_count, cpu_count);
        response.setFloatArray(ParamEnum::cpu_usage, cpu_usage);
        response.setUIntArrayArray(ParamEnum::memory, memory);
        response.setFloatArray(ParamEnum::memory_usage, memory_usage);
        response.setUIntArrayArray(ParamEnum::disk_volume, disk_volume);
        response.setFloatArray(ParamEnum::disk_usage, disk_usage);

        response.setUIntArray(ParamEnum::status, status);

        sendMessage(response, session.getRequestModule());
        session.finish();

    }catch(exception& ex)
    {
        _logger->error(boost::format("[%08X]exception when invoke query computepool, message:%s")
                            %session.getSessionID() %ex.what());
        taskFail(session);
        return;
    }

}
