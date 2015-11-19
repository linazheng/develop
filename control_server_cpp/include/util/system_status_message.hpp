#ifndef SYSTEM_STATUS_MESSAGE_HPP_INCLUDED
#define SYSTEM_STATUS_MESSAGE_HPP_INCLUDED

#include <util/define.hpp>
#include <transport/app_message.h>
#include "status_info.hpp"

namespace zhicloud
{
    namespace control_server{

        class SystemStatusMessage
        {
        public:
            SystemStatusMessage():_physical_node(0),_total_physical_node(0),_virtual_node(0),_total_virtual_node(0),
                    _network(0),_total_network(0),_total_cpu_usage(0.0),_memory_usage(0.0),_disk_usage(0.0)
            {

            }
            void toMessage(transport::AppMessage& request)
            {
                transport::AppMessage::uint_array_type number;

                number.emplace_back(_physical_node);
                number.emplace_back(_total_physical_node);
                request.setUIntArray(util::ParamEnum::physical_node, number);

                number.clear();
                number.emplace_back(_virtual_node);
                number.emplace_back(_total_virtual_node);
                request.setUIntArray(util::ParamEnum::virtual_node, number);

                number.clear();
                number.emplace_back(_network);
                number.emplace_back(_total_network);
                request.setUIntArray(util::ParamEnum::network, number);

                request.setFloat(util::ParamEnum::total_cpu_usage, _total_cpu_usage);
                request.setFloat(util::ParamEnum::memory_usage, _memory_usage);
                request.setFloat(util::ParamEnum::disk_usage, _disk_usage);

                request.setUInt(util::ParamEnum::read_request, _counter.getReadCount());
                request.setUInt(util::ParamEnum::read_bytes, _counter.getReadBytes());
                request.setUInt(util::ParamEnum::write_request, _counter.getWriteCount());
                request.setUInt(util::ParamEnum::write_bytes, _counter.getWriteBytes());
                request.setUInt(util::ParamEnum::io_error, _counter.getIOError());

                request.setUInt(util::ParamEnum::received_bytes, _received.getByte());
                request.setUInt(util::ParamEnum::recevied_packets, _received.getPacket());
                request.setUInt(util::ParamEnum::recevied_errors, _received.getError());
                request.setUInt(util::ParamEnum::received_drop, _received.getDrop());

                request.setUInt(util::ParamEnum::sent_bytes, _send.getByte());
                request.setUInt(util::ParamEnum::sent_packets, _send.getPacket());
                request.setUInt(util::ParamEnum::sent_errors, _send.getError());
                request.setUInt(util::ParamEnum::sent_drop, _send.getDrop());


                request.setString(util::ParamEnum::timestamp, _timestamp);
            }

            void fromMessage(transport::AppMessage& request)
            {
                transport::AppMessage::uint_array_type number;
                number =  request.getUIntArray(util::ParamEnum::physical_node);
                if(number.size() >= 2)
                {
                    _physical_node = number[0];
                    _total_physical_node=number[1];
                }


                number.clear();
                number =  request.getUIntArray(util::ParamEnum::virtual_node);
                if(number.size() >= 2)
                {
                    _virtual_node = number[0];
                    _total_virtual_node=number[1];
                }

                number.clear();
                number =  request.getUIntArray(util::ParamEnum::network);
                if(number.size() >= 2)
                {
                    _network = number[0];
                    _total_network=number[1];
                }
                _total_cpu_usage=  request.getFloat(util::ParamEnum::total_cpu_usage);
                _memory_usage=  request.getFloat(util::ParamEnum::memory_usage);
                _disk_usage=  request.getFloat(util::ParamEnum::disk_usage);

                _counter.setReadBytes(request.getUInt(util::ParamEnum::read_bytes));
                _counter.setReadCount(request.getUInt(util::ParamEnum::read_request));
                _counter.setWriteBytes(request.getUInt(util::ParamEnum::write_bytes));
                _counter.setWriteCount(request.getUInt(util::ParamEnum::write_request));
                _counter.setWriteCount(request.getUInt(util::ParamEnum::io_error));

                _received.setByte(request.getUInt(util::ParamEnum::received_bytes));
                _received.setPacket(request.getUInt(util::ParamEnum::recevied_packets));
                _received.setError(request.getUInt(util::ParamEnum::recevied_errors));
                _received.setDrop(request.getUInt(util::ParamEnum::received_drop));

                _send.setByte(request.getUInt(util::ParamEnum::sent_bytes));
                _send.setPacket(request.getUInt(util::ParamEnum::sent_packets));
                _send.setError(request.getUInt(util::ParamEnum::sent_errors));
                _send.setDrop(request.getUInt(util::ParamEnum::sent_drop));

                _timestamp=  request.getString(util::ParamEnum::timestamp);


            }

            bool isVaild()
            {
                return   (_timestamp.size() > 0 ? true:false);
            }

        private:
            uint32_t _physical_node;
            uint64_t _total_physical_node;
            uint32_t _virtual_node;
            uint64_t _total_virtual_node;
            uint32_t _network;
            uint32_t _total_network;
            float _total_cpu_usage;
            float _memory_usage;
            float _disk_usage;
            DiskCounter _counter;
            TrafficCounter _received;
            TrafficCounter _send;
            string _timestamp;

        };
    }
}

#endif // SYSTEM_STATUS_MESSAGE_HPP_INCLUDED
