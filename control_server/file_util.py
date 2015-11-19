# encoding: utf8



import os




def deleteDir(dirpath):
    sub_file_list = os.listdir(dirpath)
    for sub_file in sub_file_list:
        sub_path = os.path.join(dirpath, sub_file)
        if os.path.isfile(sub_path):
            os.remove(sub_path)
        else:
            deleteDir(sub_path)
            os.rmdir(sub_path)
    os.rmdir(dirpath)






