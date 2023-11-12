import glob
import os
import shutil

"""
    .pyw conversion (no terminal - GUI only).
    Converts all client .py files to .pyw, and copies them to UI_Files directory.
"""
def main():
    dir_path = os.getcwd() + '\\client'
    py_file_paths = [file for file in glob.glob(dir_path + '\\*.py')]

    try:
        os.mkdir(os.path.join(dir_path, '../client/UI_Files'))
    except FileExistsError:
        pass

    for file in py_file_paths:
        pre, _ = os.path.splitext(file)
        directory, filename = os.path.split(pre)
        shutil.copyfile(file, directory + '\\UI_Files\\' + filename + '.pyw')


if __name__ == '__main__':
    main()
