'''
    This file is part of the 3CU Source code.
    
    3CU - organizational tool helping you to categorize files in folders,
          combine folder content, clean up folders.
    Copyright (C) 2016  Timofei Tonu <timofei.tonu@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
'''

                            ####################
                            # HELPER FUNCTIONS #
                            # FOR CLEANING UP  #
                            ####################

import shutil, os, sys, stat, filecmp, send2trash, winshell, time





#------------------------------------------------------------------------------#
#-------------------------GLOBAL VARIABLES AND CLASSES-------------------------#
#------------------------------------------------------------------------------#


# Program signature, used for folder creation.
PROGRAM_SIGNATURE = "(3CU) "

# Global variables.
TARGET_DIRECTORY_PATH = ""
DELETE_EMPTY = False
DELETE_DUPLICATE = False
DELETE_REDUNDANT = False
EXCEPTIONS = []

HIDDEN_DIRECTORIES = []
HIDDEN_FILES = []
VISIBLE_DIRECTORIES = []
VISIBLE_FILES = []
DELETED_FILES = []
RELOCATED_DIRECTORIES = []

DUPLICATE_FILES = 0
EMPTY_FILES = 0
EMPTY_FOLDERS = 0
REDUNDANT_SUBFOLDERS = 0
ACTIVITY_REPORT = ""


# Defining a class for objects to store into the global file list
# information about the organized files.
# in the global file list.
# Each file object will have three descriptive fields:
# - the original absolute path
# - the renamed absolute path (in case of renaming)
# - the new absolute path

class RelocatedDirectory(object):
    original_path = ""
    new_path = ""

    def __init__(self, o_path, n_path):
        self.original_path = o_path
        self.new_path = n_path

#------------------------------------------------------------------------------#
#-------------------------------GENERAL FUNCTIONS------------------------------#
#------------------------------------------------------------------------------#



def checkIfCleanable(target, exceptions, delete_empty, delete_duplicate,
                     delete_redundant):

    # store the data in the global variables
    global TARGET_DIRECTORY_PATH, EXCEPTIONS, DELETE_EMPTY, DELETE_DUPLICATE, \
           DELETE_REDUNDANT, HIDDEN_DIRECTORIES, HIDDEN_FILES
    
    TARGET_DIRECTORY_PATH = target
    EXCEPTIONS = exceptions
    DELETE_EMPTY = delete_empty
    DELETE_DUPLICATE = delete_duplicate
    DELETE_REDUNDANT = delete_redundant

    
    # store the hidden files and folders
    storeHiddenFilesAndFolders()

    # search for cleanable files
    # pass the error code, if some
    # beforehand, empty global hidden lists
    result = searchForCleanablePattern()
    if result != None:
        HIDDEN_DIRECTORIES, HIDDEN_FILES = [], []
        return result
    
    # store the original directory structure
    storeVisibleFilesAndDirectories()


#____________________________________________________________________






# Stores the hidden files and folders from the target directory
# into the global lists.
def storeHiddenFilesAndFolders():

    # walk the target directory path
    directory_tree = os.walk(TARGET_DIRECTORY_PATH)

    # iterate through its folders
    for folder, folder_subfolders, folder_files in directory_tree:

        # append the hidden ones
        if isHidden(folder):       
            HIDDEN_DIRECTORIES.append(folder)

        # iterate through the files
        for file in folder_files:

                # append the hidden ones
                if isHidden(folder + "\\" + file):
                    HIDDEN_FILES.append(folder + "\\" + file)



#____________________________________________________________________





# Searches for a cleanable pattern.
# Returns the error code, if nothing to clean.
def searchForCleanablePattern():

    global HIDDEN_DIRECTORIES, HIDDEN_FILES

    # handle hidden or excepted target directory specifically
    if TARGET_DIRECTORY_PATH in HIDDEN_DIRECTORIES:
        return 1
    elif TARGET_DIRECTORY_PATH in EXCEPTIONS:
        return 2

    # walk the target directory path
    directory_tree = os.walk(TARGET_DIRECTORY_PATH)

    # flag variable
    flag_found = False

    # temporary file storage
    files = []

    # iterate through directory folders
    for folder, folder_subfolders, folder_files in directory_tree:

        # go to next directory, if current is hidden or excepted
        # or has a hidden or excepted ancestor
        if isForbiddenPath(folder):
            continue

        # if user asked to delete empty files and folders
        # and we have an empty folder
        # bingo!
        if DELETE_EMPTY:
            if isEmptySubfolder(folder, folder_subfolders, folder_files):
                flag_found = True
                break  
            
        # if user asked to delete redundant folders
        # and we have an one
        # bingo!
        if DELETE_REDUNDANT:
            if isRedundantSubfolder(folder, folder_subfolders, folder_files):
                flag_found = True
                break  

        # we got here, so it's not a forbidden path
        # iterate through the files of this directory
        for file in folder_files:

                # go to next file, if current hidden or excepted
                if isForbiddenFile(folder, file):
                    continue

                # if user asked to delete empty files and folders
                # and we have an empty file
                # bingo!
                if DELETE_EMPTY:
                    if isEmptyFile(folder, file):
                        flag_found = True
                        break
                    
                # append the current file to the local list
                # necessary to check for duplicates later
                files.append(folder + "\\" + file)

                # if user asked to delete duplicate files
                # and we have one
                # bingo!
                if DELETE_DUPLICATE:
                    if isDuplicateFile(folder, file, files):
                        flag_found = True
                        break

        # check the flag variable before taking the next folder
        # terminate the folder loop if the variable has been flipped
        if flag_found == True:
            break

    # if no cleanable pattern, return code
    if flag_found == False:
        return 3


#____________________________________________________________________



# Determines whether the a subfolder is empty.
# Returns true if affirmative, false otherwise.
# THE TARGET DIR SHOULD BE EXCLUDED, AS ALL THE FOLDERS ARE JUDGED.
def isEmptySubfolder(folder, folder_subfolders, folder_files):

    # current folder has no files, no subfolders,
    # and isn't the target dir
    if folder_subfolders == [] and \
       folder_files == [] and \
       folder != TARGET_DIRECTORY_PATH:
        return True


# Determines whether a subfolder is a redundant link.
# Returns true if affirmative, false otherwise.
# THE FOLDER CAN BE THE TARGET DIR, AS ONLY THE SUBFOLDERS ARE JUDGED. 
def isRedundantSubfolder(folder, folder_subfolders, folder_files):

    # current folder has only one subfolder, no files, is writable,
    # and the subfolder isn't forbidden and is deletable,
    # it means the subfolder is a redundant link
    if len(folder_subfolders) == 1 and \
       folder_files == [] and \
       not isForbiddenPath(folder + "\\" + folder_subfolders[0]) and \
       os.access(folder + "\\" + folder_subfolders[0], os.W_OK) and \
       os.access(folder, os.X_OK):
        
        return True


# Determines whether the a file is empty.
# Returns true if affirmative, false otherwise.
def isEmptyFile(folder, file):

    # https://docs.python.org/3/library/os.html#os.stat
    if os.stat(folder + "\\" + file).st_size == 0:
        return True


# Determines whether the a file is a duplicate.
# Returns true if affirmative, false otherwise.
def isDuplicateFile(folder, file, file_list):

    # shallow comparison
    # https://docs.python.org/3/library/filecmp.html
    for f in file_list:
        if filecmp.cmp(f, folder + "\\" + file, shallow=True) and \
           folder + "\\" + file != f:
            return True


# Stores the visible directories of the target directory.
# Appends to global list.
def storeVisibleFilesAndDirectories():
    
    original_tree = os.walk(TARGET_DIRECTORY_PATH)
    
    for folder, folder_subfolders, folder_files in original_tree:
        
        if not isForbiddenPath(folder):
            VISIBLE_DIRECTORIES.append(folder)


        for file in folder_files:
            
            if isForbiddenFile(folder, file) or \
               isDuplicateFile(folder, file, VISIBLE_FILES) or \
               isEmptyFile(folder, file):
                continue
            else:
                VISIBLE_FILES.append(folder + "\\" + file)



#____________________________________________________________________




    
# Checks whether a file or a folder is hidden,
# based on the ACTUAL attributes of the file/folder.
# Used to populate the global lists.
# Three-platform solution (only the Windows part has been verified).
# Returns true if affirmative, otherwise false.
# For other platforms, always return false (not hidden).
# http://stackoverflow.com/questions/8220108/how-do-i-check-the-operating-system-in-python/
# http://stackoverflow.com/questions/284115/cross-platform-hidden-file-detection
# http://stackoverflow.com/questions/30629775/setting-hidden-status-in-mac-with-python
def isHidden(absolute_path):

    # Windows
    if sys.platform == "win32":
        return bool(os.stat(absolute_path).st_file_attributes & \
                    stat.FILE_ATTRIBUTE_HIDDEN)
    # Mac
    elif sys.platform == "darwin":
        return bool(os.stat(absolute_path).st_flags & stat.UF_HIDDEN)

    # Linux
    elif sys.platform.startswith('linux'):
        basename = os.path.basename(os.path.normpath(absolute_path))
        if basename.startswith('.'):
            return True
        else:
            return False

    # return false for any other platform,
    # not having the ability to check
    return False

#____________________________________________________________________




# Checks whether the folder or one of its ancestors is hidden or excepted,
# based on IN-PROGRAM information (the populated global list),
# thus avoiding to organize forbidden folders.
# Returns true if affirmative, false otherwise.
def isForbiddenPath(folder_abs_path):

    # folder hidden
    if folder_abs_path in HIDDEN_DIRECTORIES:
        return True

    # folder on hidden path
    # avoid erroneous overlap with hidden dirs situated in the same dir
    # whose name may be partially the same
    for d in HIDDEN_DIRECTORIES:
        if d in folder_abs_path:
            if os.path.dirname(d) != os.path.dirname(folder_abs_path):
                return True

    # folder excepted
    if folder_abs_path in EXCEPTIONS:
        return True

    # folder on excepted path
    # avoid erroneous overlap with excepted dirs situated in the same dir
    # whose name may be partially the same
    for d in EXCEPTIONS:
        if d in folder_abs_path:
            if os.path.dirname(d) != os.path.dirname(folder_abs_path):
                return True
        
    return False


#___________________________________________________________________





# Checks whether the a file is hidden or excepted,
# based on IN-PROGRAM information (the populated global list),
# thus avoiding to organize forbidden files.
# Returns true if affirmative, false otherwise.
def isForbiddenFile(folder, file):

    file_abs_path = folder + "\\" + file
    
    if file_abs_path in HIDDEN_FILES:
        return True

    for d in HIDDEN_DIRECTORIES:
        if d in file_abs_path:
            if os.path.dirname(d) != folder:
                return True

    if file_abs_path in EXCEPTIONS:
        return True

    for d in EXCEPTIONS:
        if d in file_abs_path:
            if os.path.dirname(d) != folder:
                return True
    
    return False


#____________________________________________________________________


    

# Performs the asked-for cleanup actions.
# Prepares the activity report.
def cleanUp():

    if DELETE_EMPTY:            
        deleteEmptyFolders()
        deleteEmptyFiles()

    if DELETE_DUPLICATE:
        deleteDuplicateFiles()

    if DELETE_REDUNDANT:
        deleteRedundantFolders()

    prepareActivityReport()
        


#____________________________________________________________________


# Recursively removes all the empty directories
# from the target directory tree.
def deleteEmptyFiles():

    global EMPTY_FILES
    
    directory_tree = os.walk(TARGET_DIRECTORY_PATH)

    for folder, subfolders, files in directory_tree:

        # exclude hidden or excepted paths
        if isForbiddenPath(folder):
            continue

        for file in files:

            # skip forbidden files
            if isForbiddenFile(folder, file):
                continue

            # if file hidden
            # append the global list
            # delete the file
            # update the global counter
            if isEmptyFile(folder, file):

                try:                        
                    DELETED_FILES.append(folder + "\\" + file)
                    send2trash.send2trash(folder + "\\" + file)
                    EMPTY_FILES += 1
                except:
                    pass
                



# Removes the duplicate files.
def deleteDuplicateFiles():

    global DUPLICATE_FILES
    
    directory_tree = os.walk(TARGET_DIRECTORY_PATH)

    for folder, subfolders, files in directory_tree:

        # exclude hidden or excepted paths
        if isForbiddenPath(folder):
            continue

        for file in files:

            # exclude forbidden files
            if isForbiddenFile(folder, file):
                continue

            # if file duplicate
            # append the global list
            # delete the file
            # update the global counter
            if isDuplicateFile(folder, file, VISIBLE_FILES):

                try:                                            
                    DELETED_FILES.append(folder + "\\" + file)
                    send2trash.send2trash(folder + "\\" + file)
                    DUPLICATE_FILES += 1
                except:
                    pass


#____________________________________________________________________



# Recursively removes all the redundant links.
# from the target directory tree.
def deleteRedundantFolders():

    global REDUNDANT_SUBFOLDERS

    # walk the target dir tree from the bottom up
    # WHY? we move the contents gradually closer
    # and it helps with the recursion 
    directory_tree = os.walk(TARGET_DIRECTORY_PATH, topdown = False)

    for folder, folder_subfolders, folder_files in directory_tree:

        # exclude hidden or excepted paths
        if isForbiddenPath(folder):
            continue

        # if current folder has a redundant link
        if isRedundantSubfolder(folder, folder_subfolders, folder_files):

            # update the global list
            RELOCATED_DIRECTORIES.insert(0, RelocatedDirectory(folder + "\\" + \
                                                            folder_subfolders[0], \
                                                            folder))
            # move the content of the redundant subfolder
            # inside the current folder
            old_dir = folder + "\\" + folder_subfolders[0]
            for f in os.listdir(old_dir):
                try:
                    shutil.move(old_dir + "\\" + f, folder + "\\" + f)
                except:
                    pass

            # remove the redundant subfolder, update the global counter
            try:
                os.rmdir(old_dir)
            except:
                pass
            REDUNDANT_SUBFOLDERS += 1

            # recursively call the function, as the tree structure updated
            deleteRedundantFolders()

            # we reached this, so the tree is clean from all the other
            # redundant links solved by the recursion
            # so we can't walk the original path of the tree anymore
            break

    

    

    
#____________________________________________________________________


    

# Recursively removes all the empty directories
# from the target directory tree.
def deleteEmptyFolders():

    global EMPTY_FOLDERS

    # walk the tree from the bottom up
    directory_tree = os.walk(TARGET_DIRECTORY_PATH, topdown = False)

    for folder, subfolders, files in directory_tree:

        # exclude hidden or excepted paths
        if isForbiddenPath(folder):
            continue
        
        if isEmptySubfolder(folder, subfolders, files):
            try:
                os.rmdir(folder)
                EMPTY_FOLDERS += 1
                deleteEmptyFolders()
            except:
                pass



#____________________________________________________________________


# Prepares the activity report.
def prepareActivityReport():

    global ACTIVITY_REPORT

    ACTIVITY_REPORT += "Done! Removed:\n\n"
        
    if DELETE_DUPLICATE:
        duplicate_report = "Duplicate Files                     - " + \
                           str(DUPLICATE_FILES) + "\n"
    else:
        duplicate_report = ""

    if DELETE_EMPTY:
        empty_report = "Empty Files                          - " + \
                       str(EMPTY_FILES) + "\n" + \
                       "Empty Directories               - " + \
                       str(EMPTY_FOLDERS) + "\n"
    else:
        empty_report = ""

    if DELETE_REDUNDANT:
        redundant_report = "Redundant Directories       - " + \
                           str(REDUNDANT_SUBFOLDERS) + "\n"
    else:
        redundant_report = ""


    ACTIVITY_REPORT += duplicate_report + empty_report + redundant_report
    ACTIVITY_REPORT += "\nPlease have a look!\n"
    ACTIVITY_REPORT += "If you would like to restore your folder to the " + \
          "way it was, make sure not to rename, delete or move around any " + \
          "of the affected files or subfolders."
    

#____________________________________________________________________


    

# Restores the content as it was before the program ran.
def restoreContent():

    global HIDDEN_DIRECTORIES, HIDDEN_FILES, VISIBLE_DIRECTORIES, \
           VISIBLE_FILES, DELETED_FILES, RELOCATED_DIRECTORIES, \
           DUPLICATE_FILES, EMPTY_FILES, EMPTY_FOLDERS, REDUNDANT_SUBFOLDERS, \
           ACTIVITY_REPORT
    
    # restore redundant links
    if DELETE_REDUNDANT:

        # loop through the relocated dirs from the start
        for d in RELOCATED_DIRECTORIES:
            
            # restore the original path
            if not os.path.exists(d.original_path):
                try:
                    os.makedirs(d.original_path)
                except:
                    pass

            # loop through the content currently situated
            # outside the original path
            for f in os.listdir(d.new_path):

                # exclude the just restore original path
                if f == os.path.basename(d.original_path):
                    continue

                # move the content
                try:
                    shutil.move(d.new_path + "\\" + f, d.original_path + "\\" + f)
                except:
                    pass
                                    
    # restore deleted files (empty and/or duplicate)
    if DELETE_EMPTY or DELETE_DUPLICATE:

        # access the recycle bin
        recycle_bin = winshell.recycle_bin()

        # outside loop through the deleted files
        for df in DELETED_FILES:

            print(df)

            # outside loop through the recycle bin files
            for f in recycle_bin:

                # get the extension of the deleted file
                name, extension = os.path.splitext(f.real_filename())

                # build the original name of the deleted file
                # (for some reason, winshell removes the file
                # extension when deleting)
                # if the original name is a deleted file
                # restore it (including its extension)
                if f.original_filename() + extension == df:
                    try:

                        # it is possible that the extension-less file may clash
                        # with an existing folder
                        # so we temporarily rename the folder to restore the file,
                        # then restore the folder's name
                        if os.path.exists(f.original_filename()):
                            
                            temp_name = os.path.dirname(f.original_filename()) + \
                                        "\\" + os.path.basename(f.real_filename())
                            
                            os.rename(f.original_filename(), temp_name)
                            f.undelete()
                            os.rename(f.original_filename(), df)
                            os.rename(temp_name, f.original_filename())

                        # if no similar-name folder, just undelete and restore
                        # the file's name
                        else:
                            f.undelete()
                            os.rename(f.original_filename(), df)
                        break
                    except:
                        pass
        
    # Restores the directories.
    if DELETE_EMPTY:            
        for d in VISIBLE_DIRECTORIES:
            if not os.path.exists(d) and d != TARGET_DIRECTORY_PATH:
                try:
                    os.makedirs(d)
                except:
                    pass

    # empty the global lists
    HIDDEN_DIRECTORIES = []
    HIDDEN_FILES = []
    VISIBLE_DIRECTORIES = []
    VISIBLE_FILES = []
    DELETED_FILES = []
    RELOCATED_DIRECTORIES = []

    # zero-out the global vars
    DUPLICATE_FILES = 0
    EMPTY_FILES = 0
    EMPTY_FOLDERS = 0
    REDUNDANT_SUBFOLDERS = 0
    ACTIVITY_REPORT = ""

