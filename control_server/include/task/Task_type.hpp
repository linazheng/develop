#ifndef TASK_TYPE_HPP
#define TASK_TYPE_HPP

namespace zhicloud
{
    namespace control_server{

        enum class TaskType:uint32_t
        {
            invalid = 1,
            load_service = 9,
            load_config = 10,
            query_server_room = 11,
            create_server_room = 12,
            modify_server_room = 13,
            delete_server_room = 14,

            query_server_rack = 15,
            create_server_rack = 16,
            modify_server_rack = 17,
            delete_server_rack = 18,

            query_server = 19,
            add_server = 20,
            modify_server = 21,
            remove_server = 22,

            query_service_type = 23,
            query_service_group = 24,
            query_service = 25,
            modify_service = 26,

            create_host = 27,
            delete_host = 28,
            modify_host = 29,
            start_host = 30,
            stop_host = 31,
            restart_host = 32,

            initial_node = 33,
            initial_storage = 34,

            query_iso_image = 35,
            upload_iso_image = 36,
            modify_iso_image = 37,
            delete_iso_image = 38,

            query_disk_image = 39,
            create_disk_image = 40,
            delete_disk_image = 41,
            modify_disk_image = 42,
            read_disk_image = 43,

            insert_media = 44,
            change_media = 45,
            eject_media = 46,
            query_whisper = 47,

            query_host = 48,
            query_application = 49,
            query_resource_pool = 50,
            query_struct = 51,

            resume_host = 52,
            attach_disk = 53,
            detach_disk = 54,

            start_observe = 55,

            query_operate_detail = 56,
            query_operate_summary = 57,
            query_service_detail = 58,
            query_service_summary = 59,

            //logical device
            query_device = 72,
            create_device = 73,
            delete_device = 74,
            modify_device = 75,

            query_address_pool = 110,
            create_address_pool = 111,
            delete_address_pool = 112,
            add_address_resource = 113,
            remove_address_resource = 114,
            query_address_resource = 115,

            query_port_pool = 116,
            create_port_pool = 117,
            delete_port_pool = 118,
            add_port_resource = 119,
            remove_port_resource = 120,
            query_port_resource = 121,

            query_compute_pool = 122,
            create_compute_pool = 123,
            delete_compute_pool = 124,
            add_compute_resource = 125,
            remove_compute_resource = 126,
            query_compute_resource = 127,

            query_storage_pool = 128,
            create_storage_pool = 129,
            delete_storage_pool = 130,
            add_storage_resource = 131,
            remove_storage_resource = 132,
            query_storage_resource = 133,

            //query_resource_pool = 134,
            halt_host = 135,
            query_host_info = 136,

            set_forwarder_status = 137,
            query_forwarder_summary = 138,
            query_forwarder = 139,
            get_forwarder = 140,

            create_load_balancer = 141,
            add_balancer_node = 141,
            remove_balancer_node = 142,
            modify_balancer_node = 143,
            enable_load_balancer = 144,
            disable_load_balancer = 145,
            delete_load_balancer = 146,
            query_balancer_summary = 147,
            query_load_balancer = 148,
            query_balancer_detail = 149,
            get_load_balancer = 150,

            bind_domain = 151,
            unbind_domain = 152,
            query_domain_summary = 153,
            query_domain_name = 154,
            get_bound_domain = 155,

            attach_address = 156,
            detach_address = 157,
            migrate_address_resource = 158,
            migrate_port_resource = 159,
            check_config = 160,
            modify_compute_pool = 161,
            modify_storage_pool = 162,
            add_forwarder = 163,
            remove_forwarder = 164,


            initial_storage_pool = 165,
            initial_storage_resource = 166,
            initial_device = 167,


            create_network = 168,
            modify_network = 169,
            delete_network = 170,

            query_network = 171,
            query_network_detail = 172,

            start_network = 173,
            stop_network = 174,

            query_network_host = 175,
            attach_host = 176,
            detach_host = 177,

            query_network_address = 178,
            network_attach_address = 179,
            network_detach_address = 180,

            query_network_port = 181,
            network_bind_port = 182,
            network_unbind_port = 183,

            flush_disk_image = 185,
            backup_host = 186,
            resume_backup = 187,
            query_host_backup = 188,

            initial_snapshot_pool = 190,
            query_snapshot_pool = 191,
            create_snapshot_pool = 192,
            modify_snapshot_pool = 193,
            delete_snapshot_pool = 194,

            initial_snapshot_node = 195,
            add_snapshot_node = 196,
            remove_snapshot_node = 197,
            query_snapshot_node = 198,

            query_snapshot = 200,
            create_snapshot = 201,
            delete_snapshot = 202,
            resume_snapshot = 203,

            add_rule = 205,
            remove_rule = 206,
            query_rule = 207,

            reset_host = 208,

            query_compute_pool_detail = 209,

            query_storage_device = 210,
            add_storage_device = 211,
            remove_storage_device = 212,
            enable_storage_device = 213,
            disable_storage_device = 214,

            storage_server_sync = 215,
            synch_service_status = 216,
        };
    }
}

#endif // TASK_TYPE_HPP
