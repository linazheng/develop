#ifndef HOST_INFO_HPP
#define HOST_INFO_HPP

#include "util.hpp"
#include "compute_pool.hpp"
#include "status_info.hpp"


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

        typedef StorageTypeEnum DiskTypeEnum;

        class HostPort{
        public:
            HostPort():_server_port(0),_host_port(0),_public_port(0),_protocol(PortProtocolEnum::all_protocol)
            {
            }

            const uint32_t& getServerPort()const { return _server_port;}
            const uint32_t& getHostPort()const { return _host_port;}
            const string& getPublicIP()const { return _public_ip;}
            const uint32_t& getPublicPort()const { return _public_port;}
            const PortProtocolEnum& getProtocol()const { return _protocol;}

            void setServerPort(const uint32_t& value) {  _server_port = value;}
            void setHostPort(const uint32_t& value) {  _host_port = value;}
            void setPublicIP(const string& value) {  _public_ip = value;}
            void setPublicPort(const uint32_t& value) {  _public_port = value;}
            void setProtocol(const PortProtocolEnum& value) {  _protocol = value;}

        private:
            uint32_t _server_port;
            uint32_t _host_port;
            string _public_ip;
            uint32_t _public_port;
            PortProtocolEnum _protocol;
        };

        class HostRequirement{
        public:
            HostRequirement(const uint32_t& cpu_count,const uint32_t& memory,const uint32_t& disk_volume,const uint32_t& backup_disk_volume)
            :_cpu_count(cpu_count),_memory(memory),_disk_volume(disk_volume),_backup_disk_volume(backup_disk_volume)
            {
            }

            const uint32_t& getCpuCount()const { return _cpu_count;}
            const uint32_t& getMemory()const { return _memory;}
            const uint32_t& getDisk()const { return _disk_volume;}
            const uint32_t& getBackupDisk()const { return _backup_disk_volume;}

        private:
            HostRequirement(){}
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

            }

            void setName(const string& value){ _self.setName(value); }
            void setUUID(const UUID_TYPE& value){ _self.setUUID(value); }
            void setContainer(const string& value){ _container = value; }
            void setCpuCount(const uint32_t& value ){ _cpu_count = value;}
            void setMemory(const uint64_t& value ){ _memory = value;}
            void setAutoStart(bool value ){ _auto_start = value;}
            void setDataDisk(const uint64_t& value ){ _data_disk_count = value;}
            void setDisk(const ResourceCounter& value) {  _disk_volume = value; }
            void setUser(const string& value){ _user = value; }
            void setGroup(const string& value){ _group = value; }
            void setDisplay(const string& value){ _display = value; }
            void setAuthentications(const string& value){ _authentication = value; }
            void setNetwork(const string& value){ _network = value; }
            void setPublicIP(const string& value) {  _public_ip = value;}
            void setPublicPort(const uint32_t& value) {  _public_port = value;}
            void setServerIP(const string& value) {  _server_ip = value;}
            void setServerPort(const uint32_t& value) {  _server_port = value;}
            void setInboundBandwidth(const uint32_t& value) {  _inbound_bandwidth = value;}
            void setOutboundBandwidth(const uint32_t& value) {  _outbound_bandwidth = value;}
            void setMaxIops(const uint32_t& value) {  _max_iops = value;}
            void setCpuPriority(const uint32_t& value) {  _cpu_priority = value;}
            void setVpcIp(const string& value){ _vpc_ip = value; }
            void setPoolUUID(const UUID_TYPE& value){ _pool = value; }
            void setForwardUUID(const UUID_TYPE& value){ _forwarder = value; }
            void setNetworkUUID(const UUID_TYPE& value){ _network_source = value; }
            void setDiskUUID(const UUID_TYPE& value){ _disk_source = value; }
            void setNetworkType(const NetworkTypeEnum& value){_network_type = value;}
            void setDiskType(const DiskTypeEnum& value){_disk_type = value;}
            void setLocalBackup(const EnableLocalBackupEnum& value ) {_enable_local_backup = value;}
            void setUsbExt(const EnableUsbExtEnum& value ) {_enable_usb_ext = value;}
            void setThinProvisioning(const ThinProvisioningModeEnum& value ) {_thin_provisioning = value;}
            void setBackupImage(const BackingImageModeEnum& value ) {_backing_image = value;}
            void setVedioType(const VideoTypeEnum& value ) {_video_type = value;}




            const UUID_TYPE& getName()const { return  _self.getName(); }
            const UUID_TYPE& getUUID()const { return  _self.getUuid(); }
            const string& getContainer()const { return _container; }
            const uint32_t& getCpuCount() const { return _cpu_count;}
            const uint64_t& getMemory() const { return _memory;}
            bool getAutoStart() const { return _auto_start;}
            const uint64_t& getDataDisk() const { return _data_disk_count;}
            const ResourceCounter& getDisk()const { return _disk_volume; }
            const string& getUser()const { return _user; }
            const string& getGroup()const { return _group; }
            const string& getDisplay()const { return _display; }
            const string& getAuthentications()const { return _authentication; }
            const string& getNetwork()const { return _network; }
            const string& getPublicIP()const { return _public_ip;}
            const uint32_t& getPublicPort()const { return _public_port;}
            const string& getServerIP()const { return _server_ip;}
            const uint32_t& getServerPort()const { return _server_port;}
            const uint32_t& getInboundBandwidth()const { return _inbound_bandwidth;}
            const uint32_t& getOutboundBandwidth()const { return _outbound_bandwidth;}
            const uint32_t& getMaxIops()const { return _max_iops;}
            const uint32_t& getCpuPriority()const { return _cpu_priority;}
            const string& getVpcIP()const { return _vpc_ip;}
            const UUID_TYPE& getPoolUUID()const { return  _pool; }
            const UUID_TYPE& getForwardUUID()const { return  _forwarder; }
            const UUID_TYPE& getNetworkUUID()const { return  _network_source; }
            const UUID_TYPE& getDiskUUID()const { return  _disk_source; }
            const NetworkTypeEnum& getNetworkType()const {return _network_type;}
            const DiskTypeEnum& getDiskType()const {return _disk_type;}
            const EnableLocalBackupEnum& getLocalBackup()const {return _enable_local_backup;}
            const EnableUsbExtEnum& getUsbExt()const {return _enable_usb_ext;}
            const BackingImageModeEnum& getBackupImage()const {return _backing_image;}
            const VideoTypeEnum& getVedioType()const {return _video_type;}
            const ThinProvisioningModeEnum& getThinProvisioning()const  {return _thin_provisioning;}


        private:
            BaseSelfInfo _self;
            string _container;
            uint32_t _cpu_count;
            uint64_t _memory;
            bool _auto_start;
            uint64_t _data_disk_count;
            ResourceCounter _disk_volume;
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
            UUID_TYPE _pool;//compute pool id
            UUID_TYPE _forwarder;//forwarder uuid
            NetworkTypeEnum _network_type;
            UUID_TYPE _network_source;//address pool id
            DiskTypeEnum _disk_type;
            UUID_TYPE _disk_source;//storage pool id
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
