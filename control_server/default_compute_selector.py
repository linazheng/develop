#!/usr/bin/python

from host_info import EnableLocalBackupEnum
import logging

class DefaultComputeSelector(object):

    logger = logging.getLogger("default_compute_selector")
    cpu_factor = 10
    memory_factor = 1
    disk_factor = 1
    max_cpu_usage = 0.3
    minimal_os_memory = 4 * 1024 * 1024 * 1024  # 4GiB
    minimal_memory = 2 * 1024 * 1024 * 1024  # 2GiB
    minimal_os_disk = 40 * 1024 * 1024 * 1024  # 40 GiB
    minimal_disk = 20 * 1024 * 1024 * 1024  # 20 GiB

    """
    requirement:      host requirement
    status_list: list of compute node and hosts status. Format: [(server_status, hosts_status_list), ...]
    @return:None or target server id if available
    """
    @staticmethod
    def selectComputeNode(requirement, status_list):
        max_rate = 0.0
        target_server_id = ""

        for server_status, hosts_status in status_list:
            server_id = server_status.uuid

            '''
            filter by cpu
            '''
            # nc cpu usage must be small than max cpu usage
            if server_status.cpu_usage >= 1:
                DefaultComputeSelector.logger.warn("<default_compute_selector> server '%s' filtered by cpu usage, greater than 100%%" % server_id)
                continue

            # nc cpu count must be more than new host cpu count
            if server_status.cpu_count < requirement.cpu_count:
                DefaultComputeSelector.logger.warn("<default_compute_selector> server '%s' filtered by cpu count, need '%s' but total '%s'" %
                                                   (server_id, requirement.cpu_count, server_status.cpu_count))
                continue

            total_allocated_cpu_count = 0
            total_allocated_memory = 0
            total_allocated_disk = 0
            for host in hosts_status:
                total_allocated_cpu_count += host.cpu_count
                total_allocated_memory += host.memory
                for disk_volumn in host.disk_volume:
                    total_allocated_disk += disk_volumn
                    if host.enable_local_backup == EnableLocalBackupEnum.enabled:
                        total_allocated_disk += disk_volumn

            # calculate cpu score
            # 1. if unallocated cpu count is more than new host cpu count, cpu_score = cpu_factor * (total - allocated - required) / total
            # 2. elif total/cpu_factor - allocated > new host cpu count, cpu_score = (total/cpu_factor - allocated - required) / (total / cpu_factor)
            # 3. ignore this nc
            if (server_status.cpu_count - total_allocated_cpu_count) > requirement.cpu_count:
                cpu_score = DefaultComputeSelector.cpu_factor * float(server_status.cpu_count - total_allocated_cpu_count - requirement.cpu_count) / server_status.cpu_count
            elif (server_status.cpu_count / DefaultComputeSelector.max_cpu_usage - total_allocated_cpu_count) > requirement.cpu_count:
                cpu_score = float(server_status.cpu_count / DefaultComputeSelector.max_cpu_usage - total_allocated_cpu_count - requirement.cpu_count) / (server_status.cpu_count / DefaultComputeSelector.max_cpu_usage)
            else:
                DefaultComputeSelector.logger.warn("<default_compute_selector> server '%s' filtered by allocating cpu, need '%d' but total '%d', allocated '%d', max_cpu_usage '%f'" %
                                                   (server_id, requirement.cpu_count, server_status.cpu_count, total_allocated_cpu_count, DefaultComputeSelector.max_cpu_usage))
                continue

            '''
            filter by memory
            '''
            # nc available memory must be more than the sum of new host memory and minimal memory
            available_memory = server_status.memory[0]
            if available_memory < (requirement.memory + DefaultComputeSelector.minimal_memory):
                DefaultComputeSelector.logger.warn("<default_compute_selector> server '%s' filtered by memory, need %.1f GiB but remain %.1f GiB" %
                                                   (server_id, float(requirement.memory + DefaultComputeSelector.minimal_memory) / 1073741824, float(available_memory) / 1073741824))
                continue

            # nc unallocated memory must be more than the sum of new host memory and minimal os memory
            total_physical_memory = server_status.memory[1]
            if (total_physical_memory - total_allocated_memory) <= (DefaultComputeSelector.minimal_os_memory + requirement.memory):
                DefaultComputeSelector.logger.warn("<default_compute_selector> server '%s' filtered by allocating memory, need %.1f GiB but remain %.1f GiB" %
                                                   (server_id, float(DefaultComputeSelector.minimal_os_memory + requirement.memory) / 1073741824, float(total_physical_memory - total_allocated_memory) / 1073741824))
                continue

            '''
            filter by disk volume
            '''
            # nc available disk volume must be more than the sum of new host disk volume and minimal disk
            available_disk = server_status.disk_volume[0]
            if available_disk < (requirement.disk_volume + requirement.backup_disk_volume + DefaultComputeSelector.minimal_disk):
                DefaultComputeSelector.logger.warn("<default_compute_selector> server '%s' filtered by disk, need %.1f GiB but remain %.1f GiB" %
                                                   (server_id, float(requirement.disk_volume + requirement.backup_disk_volume + DefaultComputeSelector.minimal_disk) / 1073741824, float(available_disk) / 1073741824))
                continue

            # nc unallocated disk volume must be more than the sum of new host disk volume and minimal os disk
            total_disk = server_status.disk_volume[1]
            if (total_disk - total_allocated_disk) < (requirement.disk_volume + requirement.backup_disk_volume + DefaultComputeSelector.minimal_os_disk):
                DefaultComputeSelector.logger.warn("<default_compute_selector> server '%s' filtered by allocated disk, need %.1f GiB but remain %.1f GiB" %
                                                   (server_id, float(requirement.disk_volume + requirement.backup_disk_volume + DefaultComputeSelector.minimal_os_disk) / 1073741824, float(total_disk - total_allocated_disk) / 1073741824))
                continue

            '''
            calculate score
            '''
            memory_score = DefaultComputeSelector.memory_factor * float(server_status.memory[1] - total_allocated_memory - requirement.memory) / server_status.memory[1]
            disk_score = DefaultComputeSelector.disk_factor * float(server_status.disk_volume[1] - total_allocated_disk - requirement.disk_volume - requirement.backup_disk_volume) / server_status.disk_volume[1]
            total_score = cpu_score + memory_score + disk_score

            if total_score > max_rate:
                max_rate = total_score
                target_server_id = server_status.uuid

        if 0.0 == max_rate:
            return None
        else:
            return target_server_id
