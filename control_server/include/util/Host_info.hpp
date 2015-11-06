#ifndef HOST_INFO_HPP
#define HOST_INFO_HPP

#include "Util.hpp"
#include "Compute_pool.hpp"



namespace zhicloud
{
    namespace control_server{

        enum class PortProtocolEnum:uint32_t
        {
            all_protocol = 0,
            tcp_protocol = 1,
            udp_protocol = 2,
        };

        enum class NetworkTypeEnum:uint32_t
        {
            privates = 0,
            mono = 1,
            share = 2,
        };

        enum class DiskTypeEnum:uint32_t
        {
            local = 0,
            cloud = 1,
        };

        enum class EnableLocalBackupEnum:uint32_t
        {
            disabled = 0,
            enabled = 1,
        };

        enum class EnableUsbExtEnum:uint32_t
        {
            disabled = 0,
            enabled = 1,
        };

        enum class BackupHostModeEnum:uint32_t
        {
            fully = 0,
            partial = 1,
        };

        enum class VideoTypeEnum:uint32_t
        {
            mjpeg = 0,
            h264 = 1,
        };

        class HostPort{
        public:
            HostPort():_server_port(0),_host_port(0),_public_port(0),_protocol(PortProtocolEnum::all_protocol)
            {
            }
        private:
            uint32_t _server_port;
            uint32_t _host_port;
            string _public_ip;
            uint32_t _public_port;
            PortProtocolEnum _protocol;
        };

        class HostRequirement{
        public:
            HostRequirement():_cpu_count(0),_memory(0),_disk_volume(0),_backup_disk_volume(0)
            {
            }
        private:
            uint32_t _cpu_count;
            uint32_t _memory;
            uint32_t _disk_volume;
            uint32_t _backup_disk_volume;
        };

        class HostInfo{
        public:
            HostInfo():_cpu_count(0),_memory(0),_auto_start(false),_data_disk_count(0),_inbound_bandwidth(0),_outbound_bandwidth(0),
                _max_iops(0),_cpu_priority(0),_server_port(0),_public_port(0),_network_type(NetworkTypeEnum::privates),
                _disk_type(DiskTypeEnum::local),_enable_local_backup(EnableLocalBackupEnum::disabled),
                _enable_usb_ext(EnableUsbExtEnum::disabled),_thin_provisioning(ThinProvisioningModeEnum::disabled),
                _backing_image(BackingImageModeEnum::disabled),_video_type(VideoTypeEnum::mjpeg)
            {
                _disk_volume.resize(2,0);
            }
        private:
            BaseSelfInfo _self;
            string _container;
            uint32_t _cpu_count;
            uint32_t _memory;
            bool _auto_start;
            uint32_t _data_disk_count;
            vector<uint32_t> _disk_volume;
            vector<HostPort> _port;
            string _user;
            string _group;
            string _display;
            string _authentication;
            string _network;
            uint32_t _inbound_bandwidth;
            uint32_t _outbound_bandwidth;
            uint32_t _max_iops;
            uint32_t _cpu_priority;
            string _server_ip;
            string _public_ip;
            uint32_t _server_port;//display port in server
            uint32_t _public_port;//display port in public
            vector<uint32_t> _output_port_range;
            string _pool;//ompute pool id
            UUID_TYPE _forwarder;//forwarder uuid
            NetworkTypeEnum _network_type;
            string _network_source;//address pool id
            DiskTypeEnum _disk_type;
            string _disk_source;//storage pool id
            string _vpc_ip;
            EnableLocalBackupEnum _enable_local_backup;
            EnableUsbExtEnum _enable_usb_ext;
            ThinProvisioningModeEnum _thin_provisioning;
            BackingImageModeEnum _backing_image;
            VideoTypeEnum _video_type;

        };
    }
}

#endif // HOST_INFO_HPP
