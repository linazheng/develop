#!/usr/bin/python

class FileSystemFormatEnum(object):
    raw = 0
    ext3 = 1
    ntfs = 2
    ext4 = 3
    format_dict = {raw:"raw",
                   ext3:"ext3",
                   ntfs:"ntfs",
                   ext4:"ext4"}
