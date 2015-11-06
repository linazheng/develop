#ifndef DEFAULT_COMPUTE_SELECTOR_HPP_INCLUDED
#define DEFAULT_COMPUTE_SELECTOR_HPP_INCLUDED

namespace zhicloud
{
    namespace control_server{
        class DefaultComputeSelector{
        public:
            DefaultComputeSelector():_cpu_factor(10),_memory_factor(1),_disk_factor(1),_max_cpu_usage(0.3),
                minimal_os_memory(4 * 1024 * 1024 * 1024),_minimal_memory(2 * 1024 * 1024 * 1024),
                minimal_os_disk(40 * 1024 * 1024 * 1024),_minimal_disk(20 * 1024 * 1024 * 1024)
            {
            }
        private:
            uint32_t _cpu_factor;
            uint32_t _memory_factor;
            uint32_t _disk_factor;
            float _max_cpu_usage;
            uint64_t _minimal_os_memory;//4GiB
            uint64_t _minimal_memory;//2GiB
            uint64_t _minimal_os_disk;//40GiB
            uint64_t _minimal_disk;//20GiB
        };
    }

}

#endif // DEFAULT_COMPUTE_SELECTOR_HPP_INCLUDED
