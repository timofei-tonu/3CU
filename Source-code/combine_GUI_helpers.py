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
                            #  FOR COMBINING   #
                            ####################

import shutil, os, re, sys, stat



#------------------------------------------------------------------------------#
#-------------------------GLOBAL VARIABLES AND CLASSES-------------------------#
#------------------------------------------------------------------------------#


# Program signature, used for some 3rd party destination.
PROGRAM_SIGNATURE = "(3CU) "

# Global variables.
PROCESSED_DIRECTORIES = []
DESTINATION_PATH = ""
COMBINING_METHOD = ""
TREE_MODE = False
EXCEPTIONS = []

HIDDEN_DIRECTORIES = []
HIDDEN_FILES = []
VISIBLE_DIRECTORIES = []
VISIBLE_FILES = []
DUPLICATE_DIRECTORIES = []



# Defining a class for objects to store into the global file list
# information about the moved files.
# Each file object will have three descriptive fields:
# - the original absolute path
# - the renamed absolute path (in case of renaming)
# - the new absolute path
class MovedFile(object):
    original_abs_path = ""
    new_abs_path = ""

    def __init__(self, o_path, n_path):
        self.original_abs_path = o_path
        self.new_abs_path = n_path
        

class RenamedFolder(object):
    original_path = ""
    new_path = ""

    def __init__(self, o_path, n_path):
        self.original_path = o_path
        self.new_path = n_path



#------------------------------------------------------------------------------#
#-------------------------------GENERAL FUNCTIONS------------------------------#
#------------------------------------------------------------------------------#



# Checks whether we can move files, based on the following conditions:
# - the destination file has to be visible;
# - at least one of the directories from which we have to move files has to have
#   at least one visible file on a visible path.
# Returns true, if affirmative. Otherwise, returns false.
# Does some preliminary organizatorical work.
def canMoveFiles(processed_dirs, destination_dir, method, mode, exceptions):
    
    # store the global vars
    global PROCESSED_DIRECTORIES, DESTINATION_PATH, COMBINING_METHOD, \
           TREE_MODE, EXCEPTIONS, HIDDEN_DIRECTORIES, HIDDEN_FILES

    DESTINATION_PATH = destination_dir
    PROCESSED_DIRECTORIES = processed_dirs
    EXCEPTIONS = exceptions
    COMBINING_METHOD = method
    TREE_MODE = mode

    
    # populate the global lists with target directories hidden files and folders
    storeHiddenFilesAndFolders()

    # search for movable files
    # if no movable files, return the error code
    # beforehand empty the global lists
    result = searchForMovingBase()
    if result != None:
        HIDDEN_DIRECTORIES, HIDDEN_FILES = [], []
        return result        

    # otherwise, store the original directory structure
    storeVisibleDirectories()



#____________________________________________________________________






# Stores the hidden files and folders from all the involved directories.
def storeHiddenFilesAndFolders():

    # make sure all the involved directories are checked
    all_dirs = []
    for d in PROCESSED_DIRECTORIES:
        all_dirs.append(d)
    if DESTINATION_PATH not in PROCESSED_DIRECTORIES:
        all_dirs.append(DESTINATION_PATH)
    
    # iterate through all the involved directories
    for d in all_dirs:

        # walk the target directory path
        directory_tree = os.walk(d)

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






# Searches for a moving base. Conditions differ, based on the combining method.
# If no moving ground found, informs the user and exits the program.
def searchForMovingBase():

    # The destination folder must always be available.
    if isHidden(DESTINATION_PATH):
        return 1
        
    elif DESTINATION_PATH in EXCEPTIONS:
        return 2

    elif not os.access(DESTINATION_PATH, os.X_OK):
        return 7

    # flag variable
    flag_found = False

    # iterate through the target directories
    for d in PROCESSED_DIRECTORIES:
    
        # walk the target directory path
        directory_tree = os.walk(d)

        # iterate through directory folders
        for folder, folder_subfolders, folder_files in directory_tree:

            # Movable scenario no. 1 for method "everything" (folder-wise):
            # 1. a folder is VISIBLE (naturally);
            # 2. that folder ISN'T inside the destination folder (again,
            #    naturally, as we don't move destination files or folders);
            # 3. that folder isn't the target directory itself (we don't
            #    combine empty directories)
            # Flip the flag and break the loop if conditions met.
            if COMBINING_METHOD == "everything" and \
               not isForbiddenPath(folder) and \
               d != DESTINATION_PATH and \
               folder != d:
                flag_found = True
                break

            # iterate through the files of this directory
            for file in folder_files:

                # Movable scenario no. 2 for method "everything" (file-wise):
                # 1. a file is VISIBLE;
                # 2. that file ISN'T inside the DESTINATION folder.
                # Flip the flag and break the loop if conditions met.
                if COMBINING_METHOD == "everything" and \
                   not isForbiddenFile(folder + "\\" + file) and \
                   d != DESTINATION_PATH:
                    flag_found = True
                    break

                # Movable scenarios for method "files only":
                # a) a file is VISIBLE and is inside on a NON-DESTINATION target
                #    directory (we move all such files from these directories).
                # b) a file is VISIBLE, the DESTINATION directory is among the 
                #    TARGET directories, the file is located INSIDE of it, but
                #    NOT DIRECTLY, only inside a destination SUBFOLDER (we only
                #    move destination files that aren't directly inside of it).
                # Flip the flag and break the loop if conditions met.
                if COMBINING_METHOD == "files only" and \
                   not isForbiddenFile(folder + "\\" + file) and \
                   (d != DESTINATION_PATH or \
                    d == DESTINATION_PATH and DESTINATION_PATH != folder):
                        flag_found = True
                        break

            # check the flag before the next folder
            if flag_found:
                break

        # check the flag before the next target directory
        if flag_found:
            break    
                        
                
    # if no movable files, inform and exit
    if flag_found == False:
        
        if COMBINING_METHOD == "files only":

            # method "files-only", and the destination folder is the only one
            # being processed
            if DESTINATION_PATH in PROCESSED_DIRECTORIES and \
               len(PROCESSED_DIRECTORIES) == 1:
                return 3
                
            # method "files-only", one processed directory, not the destination
            elif DESTINATION_PATH not in PROCESSED_DIRECTORIES and \
               len(PROCESSED_DIRECTORIES) == 1:
                return 4
            
            # method "files-only", multiple directories
            elif len(PROCESSED_DIRECTORIES) > 1:
                return 5

        elif COMBINING_METHOD == "everything":
            return 6

    


#____________________________________________________________________





# Stores the visible directories of the target directories.
# Appends to global list.
def storeVisibleDirectories():

    # make sure all the involved directories are checked
    all_dirs = []
    for d in PROCESSED_DIRECTORIES:
        all_dirs.append(d)
    if DESTINATION_PATH not in PROCESSED_DIRECTORIES:
        all_dirs.append(DESTINATION_PATH)
        
    # iterate through the concerned directories
    for d in all_dirs:
    
        original_tree = os.walk(d)
        
        for folder, folder_subfolders, folder_files in original_tree:
            
            if not isForbiddenPath(folder):
                VISIBLE_DIRECTORIES.append(folder)



#____________________________________________________________________




    
# Checks whether a file or a folder is hidden,
# based on the ACTUAL attributes of the file/folder.
# Used to populate the global lists.
# Three-platform solution (only the Windows part has been verified).
# Returns true is affirmative (or we have some unchecked for platform),
# and false otherwise.
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

    # return true for any other platform,
    # not having the ability to check
    else:
        return True

#____________________________________________________________________




# Checks whether the folder or one of its ancestors is hidden or excepted,
# based on IN-PROGRAM information (the populated global list),
# thus avoiding to organize forbidden folders.
# Returns true if affirmative.
def isForbiddenPath(absolute_path):

    # folder hidden
    if absolute_path in HIDDEN_DIRECTORIES:
        return True

    # folder on hidden path
    for d in HIDDEN_DIRECTORIES:
        if d in absolute_path:
            if os.path.dirname(d) != os.path.dirname(absolute_path):
                return True

    # folder excepted
    if absolute_path in EXCEPTIONS:
        return True

    # folder on excepted path
    for d in EXCEPTIONS:
        if d in absolute_path:
            if os.path.dirname(d) != os.path.dirname(absolute_path):
                return True
        

#___________________________________________________________________





# Checks whether the a file is hidden or excepted,
# based on IN-PROGRAM information (the populated global list),
# thus avoiding to organize forbidden files.
# Returns true if affirmative.
def isForbiddenFile(file_abs_path):

    if file_abs_path in HIDDEN_FILES:
        return True

    for d in HIDDEN_DIRECTORIES:
        if d in file_abs_path:
            if os.path.dirname(d) != os.path.dirname(file_abs_path):
                return True

    if file_abs_path in EXCEPTIONS:
        return True

    for d in EXCEPTIONS:
        if d in file_abs_path:
            if os.path.dirname(d) != os.path.dirname(file_abs_path):
                return True
        
#___________________________________________________________________

    

# Organizes into categories all the files from the target directory. 
def moveFiles(delete_request):

    if delete_request and DESTINATION_PATH in PROCESSED_DIRECTORIES:
        deleteEmptyDirectories(DESTINATION_PATH)

    if COMBINING_METHOD == "files only":
        combineFilesOnly()

    if COMBINING_METHOD == "everything":
        if TREE_MODE:
            combineEverythingTree()
        else:
            combineEverything()

    # at the end, if the user asks to delete
    # the empty directories left behind in the processed dirs, do it
    if delete_request:
        for d in PROCESSED_DIRECTORIES:
            deleteEmptyDirectories(d)
    


#____________________________________________________________________


# Moves all the files from the processed directories inside the destination.
# Duplicate name issues are solved Windows-style (adding (2), (3), etc.).
def combineFilesOnly():

    # iterate through the target dirs
    for d in PROCESSED_DIRECTORIES:
        
        # walk the tree
        directory_tree = os.walk(d)

        # iterate through its folders
        for folder, folder_subfolders, folder_files in directory_tree:

            # exclude hidden or excepted paths
            if isForbiddenPath(folder):
                continue

            # don't move files directly inside the destination
            if folder == DESTINATION_PATH:
                continue

            # iterate through its files
            for file in folder_files:

                # exclude hidden or excepted files
                if isForbiddenFile(folder + "\\" + file):
                    continue

                    
                # WE HAVE A MOVABLE FILE
                # store the file metadata
                # (solve any duplicate name issues)                
                if not os.path.isfile(DESTINATION_PATH + "\\" + file):
                    new_name = file
                else:
                    new_name = solveDuplicateName(DESTINATION_PATH, file)

                # append the file metadata
                o_abs_path = folder + "\\" + file
                n_abs_path = DESTINATION_PATH + "\\" + new_name
                VISIBLE_FILES.append(MovedFile(o_abs_path, n_abs_path))

                # move the file
                try:
                    shutil.move(o_abs_path, n_abs_path)
                except:
                    pass


def combineEverythingTree():

    # iterate through the target dirs
    for d in PROCESSED_DIRECTORIES:

        # ignore the destination path (we don't move anything there)
        if d == DESTINATION_PATH:
            continue

        # ignore hidden target dirs
        if isForbiddenPath(d):
                continue
            
        # walk the tree
        directory_tree = os.walk(d)

        # iterate through its folders
        for folder, folder_subfolders, folder_files in directory_tree:

            # exclude hidden or excepted paths
            if isForbiddenPath(folder):
                continue

            # for each folder subfolder
            # create a destination replica, if not there yet
            for subfolder in folder_subfolders:

                old_abs_path = folder + "\\" + subfolder
                rel_path = os.path.relpath(old_abs_path, d)
                new_abs_path = DESTINATION_PATH + "\\" + rel_path
                
                if not os.path.exists(new_abs_path):
                    try:
                        os.makedirs(new_abs_path)
                    except:
                        pass
            
            # move each folder file on the corresponding destination path
            # solve any duplicate name issues Windows-style
            for file in folder_files:

                # exclude hidden or excepted files
                if isForbiddenFile(folder + "\\" + file):
                    continue

                # create file metadata
                rel_path = os.path.relpath(folder, d)
                new_path = DESTINATION_PATH + "\\" + rel_path 
                
                if os.path.isfile(new_path + "\\" + file):
                    new_name = solveDuplicateName(new_path, file)
                else:
                    new_name = file
                    
                o_abs_path = folder + "\\" + file
                n_abs_path = new_path + "\\" + new_name

                # save the metadata
                VISIBLE_FILES.append(MovedFile(o_abs_path, n_abs_path))

                # move the file
                try:
                    shutil.move(o_abs_path, n_abs_path)
                except:
                    pass


                
                
def combineEverything():

    # iterate through the target dirs
    for d in PROCESSED_DIRECTORIES:

        # ignore the destination path (we don't move anything there)
        if d == DESTINATION_PATH:
            continue

        # ignore hidden target dirs
        if isForbiddenPath(d):
                continue        

        # walk the tree
        directory_tree = os.walk(d)

        # iterate through its folders
        for folder, folder_subfolders, folder_files in directory_tree:

            # deal with content located directly in the processed directories,
            # potentially affected by duplicate-name issues that may occurr
            # when combining "everything"
            if folder == d:

                # iterate thorugh direct subfolders
                for subfolder in folder_subfolders:

                    old_abs_path = d + "\\" + subfolder

                    # ignore hidden/excepted paths
                    if isForbiddenPath(old_abs_path):
                        continue

                    # build the new absolute path
                    new_abs_path = DESTINATION_PATH + "\\" + subfolder

                    # if this path already exists, solve the duplicate-name
                    # issues, then append the global list
                    if os.path.exists(new_abs_path):
                        new_abs_path = solveDuplicateName(new_abs_path, "")
                        DUPLICATE_DIRECTORIES.append(RenamedFolder(old_abs_path, \
                                                                   new_abs_path))
                                                                   
                    # create the new subfoldes
                    try:
                        os.makedirs(new_abs_path)
                    except:
                        pass

                # iterate through the direct files
                for file in folder_files:

                    # ignore hidden/excepted
                    if isForbiddenFile(folder + "\\" + file):
                        continue

                    # set the new name, based on its availability
                    if os.path.isfile(DESTINATION_PATH + "\\" + file):
                        new_name = solveDuplicateName(DESTINATION_PATH, file)
                    else:
                        new_name = file

                    # append the file metadata
                    o_abs_path = d + "\\" + file
                    n_abs_path = DESTINATION_PATH + "\\" + new_name
                    VISIBLE_FILES.append(MovedFile(o_abs_path, n_abs_path))

                    # move the file
                    try:
                        shutil.move(o_abs_path, n_abs_path)
                    except:
                        pass

            # some kind of subfolder
            # these don't have duplicate names,
            # but they may be on some renamed path
            else:

                # iterate through deep subfolders
                for subfolder in folder_subfolders:

                    # hidden/excepted
                    if isForbiddenPath(folder + "\\" + subfolder):
                        continue

                    # deals with subfolders on a renamed path
                    # then continues to the next subfolder
                    if isOnRenamedPath(folder, subfolder):
                        continue

                    # if on a new path, create the new path
                    old_abs_path = folder + "\\" + subfolder
                    rel_path = os.path.relpath(old_abs_path, d)                                            
                    new_abs_path = DESTINATION_PATH + "\\" + rel_path

                    try:
                        os.makedirs(new_abs_path)
                    except:
                        pass

                # iterate through deep files
                for file in folder_files:

                    # hidden/excepted
                    if isForbiddenFile(folder + "\\" + file):
                        continue

                    # deals with files on a renamed path
                    # then continues to the next file
                    if isOnRenamedPath(folder, file):
                        continue

                    # if on a new path, build it, append the file list, move it
                    old_abs_path = folder + "\\" + file
                    rel_path = os.path.relpath(old_abs_path, d)
                    new_abs_path = DESTINATION_PATH + "\\" + rel_path

                    VISIBLE_FILES.append(MovedFile(old_abs_path, new_abs_path))

                    try:
                        shutil.move(old_abs_path, new_abs_path)
                    except:
                        pass

                
# deals with files and folders situated on a renamed path
def isOnRenamedPath(path, name):

    if os.path.isdir(path + "\\" + name):

        old_abs_path = path + "\\" + name
        
        for d in DUPLICATE_DIRECTORIES:
            if d.original_path in old_abs_path:
                rel_path = os.path.relpath(old_abs_path, d.original_path)
                new_abs_path = d.new_path + "\\" + rel_path

                DUPLICATE_DIRECTORIES.append(RenamedFolder(old_abs_path, \
                                                           new_abs_path))
                try:
                    os.makedirs(new_abs_path)
                except:
                    pass
                
                return True

    elif os.path.isfile(path + "\\" + name):

        old_abs_path = path + "\\" + name
        
        for d in DUPLICATE_DIRECTORIES:
            if d.original_path in old_abs_path:
                rel_path = os.path.relpath(old_abs_path, d.original_path)
                new_abs_path = d.new_path + "\\" + rel_path

                VISIBLE_FILES.append(MovedFile(old_abs_path, new_abs_path))

                try:
                    shutil.move(old_abs_path, new_abs_path)
                except:
                    pass
                
                return True
    

# Solves duplicate name clashes, Windows-style (adding (2), (3), etc.)
def solveDuplicateName(folder_path, file):

    # if we have a directory issue, extract its name from the path
    # cut the path, prepare it for the new folder name
    if file == "":
        name = os.path.basename(folder_path)
        folder_path = folder_path[:-len(name)]

    # if a file issue, we separate the name from the extension
    else:
        name, extension = os.path.splitext(file)
        
    # create a regex to capture potential (2), (3), etc. already in the name
    duplicate_regex = re.compile(r'\(\d+\)$')

    # search the name for this pattern
    match_object = duplicate_regex.search(name)

    # if no such pattern, add (2) to the name
    if match_object == None:
        new_name = name + " (2)"

    # if pattern found, increment the found number by 1
    else:
        # cut the name
        name = name[:-len(match_object.group())]

        # create the regex to capture the numbers
        digits_regex = re.compile(r'\d+')

        # capture them
        current_number = digits_regex.search(match_object.group())

        # increment them
        new_number = int(current_number.group()) + 1

        # build a new name
        new_name = name + "(" + str(new_number) + ")"

    # if the new name is still a duplicate
    # recursively call this function, until it sticks
    if file == "":
        # if directory, rebuild the path before checking
        folder_path += new_name
        if os.path.exists(folder_path) == True:
            folder_path = solveDuplicateName(folder_path, "")
        return folder_path
    else:
        # if file, add the exension before checking
        new_name += extension
        if os.path.isfile(folder_path + "\\" + new_name) == True:
            new_name = solveDuplicateName(folder_path, new_name)
        return new_name    

        
  


#____________________________________________________________________
    

    

# Recursively removes all the empty directories
# from the target directory tree.
def deleteEmptyDirectories(d):

    directory_tree = os.walk(d, topdown = False)

    for folder, subfolders, files in directory_tree:

        # exclude hidden or excepted paths
        if isForbiddenPath(folder):
            continue
        
        if files == [] and subfolders == []:
            try:
                os.rmdir(folder)
            except:
                pass
            
            deleteEmptyDirectories(d)



#____________________________________________________________________


    

# Restores the content as it was before the program ran.
def restoreContent():

    global VISIBLE_FILES, VISIBLE_DIRECTORIES, HIDDEN_DIRECTORIES, \
           HIDDEN_FILES, DUPLICATE_DIRECTORIES

    # Restores the directories.
    for d in VISIBLE_DIRECTORIES:
        if not os.path.exists(d):
            try:
                os.makedirs(d)
            except:
                pass

    # Restores the files
    for file in VISIBLE_FILES:
        try:
            shutil.move(file.new_abs_path, file.original_abs_path)
        except:
            pass

    # Deletes empty directories left in the destination folder
    deleteEmptyDirectories(DESTINATION_PATH)

    # Re-add original empty directories that may have been deleted.
    for d in VISIBLE_DIRECTORIES:
        if not os.path.exists(d):
            try:
                os.makedirs(d)
            except:
                pass

    # empty global lists after restoring
    HIDDEN_DIRECTORIES = []
    HIDDEN_FILES = []
    VISIBLE_DIRECTORIES = []
    VISIBLE_FILES = []
    DUPLICATE_DIRECTORIES = []



