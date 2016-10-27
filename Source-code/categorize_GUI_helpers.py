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
                            # FOR CATEGORIZING #
                            ####################

import shutil, os, re, sys, stat







#------------------------------------------------------------------------------#
#-------------------------GLOBAL VARIABLES AND CLASSES-------------------------#
#------------------------------------------------------------------------------#


# Program signature, used for folder creation.
PROGRAM_SIGNATURE = "(3CU) "

# Global variables.
TARGET_DIRECTORY_PATH = ""
ORGANIZING_METHOD = ""
DADDY_MODE = False
EXCEPTIONS = []

HIDDEN_DIRECTORIES = []
HIDDEN_FILES = []
VISIBLE_DIRECTORIES = []
VISIBLE_FILES = []
EXTENSION_LIST = []
MOVED_DIRECTORIES = []




# Defining a class to store into the global file list
# information about the organized files.
# in the global file list.
# Each file object will have three descriptive fields:
# - the original absolute path
# - the renamed absolute path (in case of renaming)
# - the new absolute path
class OrganizedFile(object):
    original_path = ""
    new_path = ""

    def __init__(self, o_path, n_path):
        self.original_path = o_path
        self.new_path = n_path

# Defining a class to store in the global list
# information about the moved directories during the "hold me daddy" mode:
# - original folder path;
# - new folder path;
# - current file extension.
# The reason for this class is presented lower.
class MovedDirectory(object):
    original_path = ""
    new_path = ""
    extension = ""

    def __init__(self, o_path, n_path, ext):
        self.original_path = o_path
        self.new_path = n_path
        self.extension = ext




#------------------------------------------------------------------------------#
#-------------------------------GENERAL FUNCTIONS------------------------------#
#------------------------------------------------------------------------------#



# Checks whether the target directory has at least a file that is visible,
# and whose ancestors up to the target directory are also visible.
# Returns the error code, if no organizable files.
# Does some preliminary organizational work.
def hasOrganizableFiles(target, method, mode, exceptions):
    
    # store the data in the global variables
    global TARGET_DIRECTORY_PATH, ORGANIZING_METHOD, DADDY_MODE, EXCEPTIONS, \
           HIDDEN_DIRECTORIES, HIDDEN_FILES

    ORGANIZING_METHOD = method
    DADDY_MODE = mode
    EXCEPTIONS = exceptions
    TARGET_DIRECTORY_PATH = target
    
    # before checking, store the hidden files and folders,
    # as they're excepted by the program
    storeHiddenFilesAndFolders()

    # search for organizable files
    # if no such files, return the error code
    # beforehand, empty the hidden lists
    result = searchForOrganizableFiles()
    if result != None:
        HIDDEN_DIRECTORIES, HIDDEN_FILES = [], []
        return result

    # if everything is alright,    
    # store the original directory structure
    storeVisibleDirectories()
    
    # get the extensions
    getFileExtensions()



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






# Searches for organizable files in the target directory.
# The file must not be hidden or excepted and it must not have
# hidden or excepted ancestors, up to and including the target directory.
# Returns "found" / "not found", based on the result of the search.
def searchForOrganizableFiles():

    # handle hidden or excepted or unexecutable target directory specifically
    if TARGET_DIRECTORY_PATH in HIDDEN_DIRECTORIES:
        return 1
    elif TARGET_DIRECTORY_PATH in EXCEPTIONS:
        return 2
    elif not os.access(TARGET_DIRECTORY_PATH, os.X_OK):
        return 4


    # walk the target directory path
    directory_tree = os.walk(TARGET_DIRECTORY_PATH)

    # flag variable
    flag_found = False

    # iterate through directory folders
    for folder, folder_subfolders, folder_files in directory_tree:

        # go to next directory, if current is hidden or excepted
        # or has a hidden or excepted ancestor
        if isForbiddenPath(folder):
            continue

        # we got here, so it's not a forbidden path
        # iterate through the files of this directory
        for file in folder_files:

                # go to next file, if current hidden or excepted
                if isForbiddenFile(folder, file):
                    continue

                # we got here, so the current file meets the conditions
                # flip the flag variable
                # break the loop
                flag_found = True
                break


        # check the flag variable before taking the next folder
        # terminate the folder loop if the variable has been flipped
        if flag_found == True:
            break

    # if no organizable files, return error code
    if flag_found == False:
        return 3

#____________________________________________________________________





# Stores the visible directories of the target directory.
# Appends to global list.
def storeVisibleDirectories():
    
    original_tree = os.walk(TARGET_DIRECTORY_PATH)
    
    for folder, folder_subfolders, folder_files in original_tree:
        
        if not isForbiddenPath(folder):
            VISIBLE_DIRECTORIES.append(folder)



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


#___________________________________________________________________




# Populates the global list with the extensions of visible files in visible paths.
def getFileExtensions():
    
    directory_tree = os.walk(TARGET_DIRECTORY_PATH)

    for folder, folder_subfolders, folder_files in directory_tree:

        # exclude hidden or excepted paths
        if isForbiddenPath(folder):
            continue
        
        for file in folder_files:
            
            # exclude hidden or excepted files
            if isForbiddenFile(folder, file):
                continue

            name, extension = os.path.splitext(file)
            EXTENSION_LIST.append(extension)



#____________________________________________________________________


    

# Organizes into categories all the files from the target directory.
def organizeFiles(delete_request):

    # organizes video files, if any
    if hasVideoFiles():
        organizeVideoFiles()

    # organizes audio files, if any
    if hasAudioFiles():
        organizeAudioFiles()

    # organizes image files, if any
    if hasImageFiles():
        organizeImageFiles()

    # organizes document files, if any
    if hasDocumentFiles():
        organizeDocumentFiles()

    # organizes application files, if any
    if hasApplicationFiles():
        organizeApplicationFiles()
        
    # organizes other types of files, if any
    if hasOtherFiles():
        organizeOtherFiles()

    # at the end, if the user asks to delete
    # the empty directories left behind, do it
    if delete_request:
        deleteEmptyDirectories()



#____________________________________________________________________


    
# YOU WANT THE FILES SEPARATED INTO CATEGORIES, BUT ON THEIR ORIGINAL PATH,
# AS IT IS IMPORTANT THEY STAY THIS WAY.
# Organizes files using the "mirror" method:
# - creates a category subfolder.
# - copies into it only the category files and the folders on their path,
#   thus preserving their path relative to the target directory
# - for example, path\to\target directory\some folder\file
#   becomes path\to\target directory\CATEGORY FOLDER\some folder\file
# Basically, each category folder becomes a mirror of the target directory.
def mirrorOrganizeFiles(category_folder, checking_function):

    # append the file list first thing
    mirrorAppendFileList(category_folder, checking_function)

    # create the folder for the calling (sub)category
    category_path = TARGET_DIRECTORY_PATH + category_folder
    if not os.path.exists(category_path):
        try:
            os.makedirs(category_path)
        except:
            pass
    
    # walk the directory tree of the target directory
    directory_tree = os.walk(TARGET_DIRECTORY_PATH)

    # iterate through it
    for folder, folder_subfolders, folder_files in directory_tree:

        # exclude hidden or excepted paths
        if isForbiddenPath(folder):
            continue
        
        for file in folder_files:

            # exclude hidden or excepted files
            if isForbiddenFile(folder, file):
                continue

            name, extension = os.path.splitext(file)

            # process the (sub)category files only
            # exclude the newly created category folder (avoid recursion)
            if TARGET_DIRECTORY_PATH + category_folder not in folder and \
               checking_function(extension) == True:

                # get the original relative path 
                rel_path = os.path.relpath(folder, TARGET_DIRECTORY_PATH)

                # build the new absolute path 
                abs_path = TARGET_DIRECTORY_PATH + category_folder + "\\" + \
                           rel_path

                # create the new absolute path
                if not os.path.exists(abs_path):
                    try:
                        os.makedirs(abs_path)
                    except:
                        pass

                # move the category file there
                try:
                    shutil.move(folder + "\\" + file, abs_path + "\\" + file)
                except:
                    pass



#____________________________________________________________________


    
# YOU DON'T CARE ABOUT THE ORIGINAL PATH,
# YOU WANT ALL THE FILES CATEGORIZED AND IN ONE PLACE.
# Organizes files using the "bulk" method. Pretty straightforward:
# - creates a category subfolder.
# - moves all the files of that specific category from the target directory
#   to the newly created category subfolder.
# - for example, path\to\target directory\some folder\file
#   becomes path\to\target directory\CATEGORY FOLDER\file
# - duplicate name issues between files are solved Windows-style (adding (2), (3), etc.)
# This method contains a special mode, HoldMeDaddy, described inside.
def bulkOrganizeFiles(category_folder, checking_function):
    
    # create the folder for the calling (sub)category
    category_path = TARGET_DIRECTORY_PATH + category_folder
    if not os.path.exists(category_path):
        try:
            os.makedirs(category_path)
        except:
            pass
    
    # walk the directory tree of the target directory
    directory_tree = os.walk(TARGET_DIRECTORY_PATH)

    # move all the category files from the target directory to the new subfolder
    for folder, folder_subfolders, folder_files in directory_tree:

        # exclude hidden or excepted paths
        if isForbiddenPath(folder):
            continue
        
        for file in folder_files:

            # exclude hidden or excepted files
            if isForbiddenFile(folder, file):
                continue
            
            name, extension = os.path.splitext(file)
            
            if checking_function(extension) == True and \
               TARGET_DIRECTORY_PATH + category_folder not in folder:

                # YOU DON'T CARE SO MUCH ABOUT THE ORIGINAL PATH,
                # YOU WANT ALL THE FILES IN ONE PLACE,
                # BUT INSIDE THEIR OLD PARENT FOLDER, JUST BECAUSE.
                # HoldMeDaddy is a special mode of the "bulk" method.
                # In this mode, files are moved in BULK to the category folder,
                # but WITH their immediate parent directory.
                # For example, target directory\grandpa_folder\pa_folder\file
                # becomes target directory\CATEGORY FOLDER\pa_folder\file
                # Duplicate name issues between folders are solved Windows-style (adding (2), (3), etc.)
                if DADDY_MODE == True:

                    # if the original parent folder is the target directory
                    # itself, just move the file inside the category folder.
                    # these files were already inside the target dir outside
                    # any subfolders, so no need to create one now.
                    if folder == TARGET_DIRECTORY_PATH:
                        
                        # beforehand append the file list
                        bulkAppendFileList(file, "", folder, category_path)

                        # move the file to the new location
                        try:
                            shutil.move(folder + "\\" + file, category_path + \
                                    "\\" + file)
                        except:
                            pass
                        
                        continue


                    # check if the parent dir has already been moved
                    # if affirmative, the function will perform the
                    # necessary actions, so we skip the file
                    if wasParentDirAlreadyMoved(folder, file, extension):
                        continue

                    # get the name of the original parent directory
                    parent_dir = os.path.basename(folder)

                    # build the new path to the file
                    new_folder_path = category_path + "\\" + parent_dir

                    # if such a path doesn't exist already
                    if not os.path.exists(new_folder_path):

                        # create it
                        try:
                            os.makedirs(new_folder_path)
                        except:
                            pass

                        # store it for other potential files from the same path
                        MOVED_DIRECTORIES.insert(0, MovedDirectory(folder, \
                                                                   new_folder_path, \
                                                                   extension))

                        # beforehand append the file list
                        bulkAppendFileList(file, "", folder, new_folder_path)

                        # move the file to the new location
                        try:
                            shutil.move(folder + "\\" + file, new_folder_path + \
                                    "\\" + file)
                        except:
                            pass

                    # if such a directory already exists     
                    else:

                        # solve duplicate name issue
                        new_folder_path = solveDuplicateName(new_folder_path, "")
                        
                        # create the new directory
                        try:
                            os.makedirs(new_folder_path)
                        except:
                            pass

                        # store it for other potential files from the same path
                        MOVED_DIRECTORIES.insert(0, MovedDirectory(folder, \
                                                                   new_folder_path, \
                                                                   extension))

                        # beforehand append the file list
                        bulkAppendFileList(file, "", folder, new_folder_path)

                        # move the file to the new location
                        try:
                            shutil.move(folder + "\\" + file, new_folder_path + \
                                    "\\" + file)
                        except:
                            pass

                # simple bulk 
                else:

                    # if no name clashes between files
                    if os.path.isfile(category_path + "\\" + file) == False:

                        # append the file list
                        bulkAppendFileList(file, "", folder, category_path)

                        # move the file
                        try:
                            shutil.move(folder + "\\" + file,
                                        category_path + "\\" + file)
                        except:
                            pass

                    # if we have duplicate name issues
                    else:

                        # solve them
                        new_name = solveDuplicateName(category_path, file)
                        
                        # append the file list
                        bulkAppendFileList(file, new_name, folder, category_path)

                        # move the file
                        try:
                            shutil.move(folder + "\\" + file, category_path + \
                                    "\\" + new_name)
                        except:
                            pass


#____________________________________________________________________


# Checks whether the parent folder has already been moved
# when "HoldMeDaddy" mode activated. If affirmative, uses
# the already available information to perform the necessary
# actions, then returns true.
# WHY: duplicate-name issues appear during the "bulk" method - between
# files when we move simply in "bulk", and between folders when we
# activate the "daddy" mode. The first scenario is simple, we check whether
# such a name already exists, rename the file and move it, in the meantime
# appending creating an object to store the original and new paths and
# appending the global list.
# Duplicate-name issues between folders are trickier. We may have multiple
# files of the same extension in that folder. Say we take the first file -
# we see that a parent folder of that name exists already, we rename the
# parent folder and move them. Say we take the second file - we see that a
# parent folder of that name exists already, we rename, we check again,
# the RENAMED PARENT FOLDER ALSO EXISTS so we go further until we hit home.
# So with two files of the same extension situated inside the same original
# parent folder we may end up with multiple renamed parent folders of just
# one file. The files would still moved, but that's not how we intended it.
# So when moving files in "daddy" mode, we create objects to store information
# about the file extension, original parent folder, and new parent folder.
# And beforehand we check, has this parent folder been moved for files of
# this extension - if not, we pursue the normal path, if yes though, we don't
# rename the parent folder anymore, we simply use the stored new path to
# move the files of the same extension and from the same original path
# to the new path. Phew!
def wasParentDirAlreadyMoved(folder, file, extension):

    # iterates through the already moved parent dirs
    for md in MOVED_DIRECTORIES:

        # if folder already moved for files of this extension
        if md.original_path == folder and md.extension == extension:

            # use the logged new path to append the file list
            bulkAppendFileList(file, "", folder, md.new_path)

            # and move the file there
            try:
                shutil.move(folder + "\\" + file, md.new_path + \
                    "\\" + file)
            except:
                pass

            return True

    
#____________________________________________________________________


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


    

# Appends objects with each allowed file's information to the file list:
# - old absolute path;
# - no renamed path ("");
# - new absolute path.
# Used for "mirror" method.
def mirrorAppendFileList(category_folder, checking_function):

    # walks the tree    
    original_tree = os.walk(TARGET_DIRECTORY_PATH)

    # iterates through it
    for folder, folder_subfolders, folder_files in original_tree:

        # exclude hidden or excepted paths
        if isForbiddenPath(folder):
            continue
        
        for file in folder_files:

            # exclude hidden or excepted files
            if isForbiddenFile(folder, file):
                continue            

            # gets the file extension
            # gets the file path relative to the target directory
            name, extension = os.path.splitext(file)
            relative_path = os.path.relpath(folder + "\\" + file, TARGET_DIRECTORY_PATH)

            # appends only information concerning files of a specific category
            if checking_function(extension) == True:
                
                o_path = folder + "\\" + file
                n_path = TARGET_DIRECTORY_PATH + category_folder + "\\" + relative_path
                
                VISIBLE_FILES.append(OrganizedFile(o_path, n_path))



#____________________________________________________________________


    

# Appends objects with each file's information to the file list.
# - old absolute path;
# - old renamed absolute path, if applicable, else ""
# - new absolute path.
# Used for "bulk" method.
def bulkAppendFileList(original_name, new_name, old_path, new_path):

    # if no renaming occurrs
    if new_name == "":
        
        o_path = old_path + "\\" + original_name
        n_path = new_path + "\\" + original_name

        VISIBLE_FILES.append(OrganizedFile(o_path, n_path))

    # for renamed files
    else:

        o_path = old_path + "\\" + original_name
        n_path = new_path + "\\" + new_name

        VISIBLE_FILES.append(OrganizedFile(o_path, n_path))




#____________________________________________________________________


    

# Recursively removes all the empty directories
# from the target directory tree.
def deleteEmptyDirectories():
    
    directory_tree = os.walk(TARGET_DIRECTORY_PATH, topdown = False)

    for folder, subfolders, files in directory_tree:

        # exclude hidden or excepted paths
        if isForbiddenPath(folder):
            continue
        
        if files == [] and subfolders == []:
            try:
                os.rmdir(folder)
                deleteEmptyDirectories()
            except:
                pass




#____________________________________________________________________


    

# Restores the content as it was before the program ran.
def restoreContent():

    global VISIBLE_FILES, VISIBLE_DIRECTORIES, HIDDEN_DIRECTORIES, \
           HIDDEN_FILES, EXTENSION_LIST, MOVED_DIRECTORIES

    # Restores the directories.
    for d in VISIBLE_DIRECTORIES:
        if not os.path.exists(d) and d != TARGET_DIRECTORY_PATH:
            try:
                os.makedirs(d)
            except:
                pass

    # Restores the files.
    for file in VISIBLE_FILES:
        try:
            shutil.move(file.new_path, file.original_path)
        except:
            pass

    # Deletes empty directories (including the ones generated by the program).
    deleteEmptyDirectories()

    # Re-add original empty directories that may have been deleted.
    for d in VISIBLE_DIRECTORIES:
        if not os.path.exists(d) and d != TARGET_DIRECTORY_PATH:
            try:
                os.makedirs(d)
            except:
                pass

    # empty global lists after restoring
    HIDDEN_DIRECTORIES = []
    HIDDEN_FILES = []
    VISIBLE_DIRECTORIES = []
    VISIBLE_FILES = []
    EXTENSION_LIST = []
    MOVED_DIRECTORIES = []











#------------------------------------------------------------------------------#
#----------------------------------VIDEO---------------------------------------#
#------------------------------------------------------------------------------#



# Determines the presence of video file extensions in an extension list.
# Returns true if present, false otherwise.
def hasVideoFiles():
    
    for extension in EXTENSION_LIST:
        if extension.lower() in VIDEO_FORMATS:
            return True

    return False


#____________________________________________________________________




# Checks whether the file is a video file based on its extension.
# Returns true is affirmative, false otherwise
def isVideoFile(extension):

    if extension in VIDEO_FORMATS:
        return True
    else:
        return False


#____________________________________________________________________



# Organizes video files.
def organizeVideoFiles():

    # the folder representation for this (sub)category
    category_folder = "\\" + PROGRAM_SIGNATURE + "Video Files"

    # the function to use when checking for files of this category
    checking_function = isVideoFile

    # call the corresponding organizing function based on the method
    if ORGANIZING_METHOD == "mirror":

        mirrorOrganizeFiles(category_folder, checking_function)

    elif ORGANIZING_METHOD == "bulk":

        bulkOrganizeFiles(category_folder, checking_function)









#------------------------------------------------------------------------------#
#----------------------------------AUDIO---------------------------------------#
#------------------------------------------------------------------------------#




# Determines the presence of audio file extensions in an extension list.
# Returns true if present, false otherwise.
def hasAudioFiles():
    
    for extension in EXTENSION_LIST:
        if extension.lower() in AUDIO_FORMATS:
            return True

    return False


#____________________________________________________________________




# Determines whethere the file is an audio file.
# Returns true if affirmative, false otherwise.
def isAudioFile(extension):

    if extension in AUDIO_FORMATS:
        return True
    else:
        return False


#____________________________________________________________________




# Organizes audio files.
def organizeAudioFiles():

    # the folder representation for this (sub)category
    category_folder = "\\" + PROGRAM_SIGNATURE + "Audio Files"

    # the function to use when checking for files of this category
    checking_function = isAudioFile

    # call the corresponding organizing function based on the method
    if ORGANIZING_METHOD == "mirror":

        mirrorOrganizeFiles(category_folder, checking_function)

    elif ORGANIZING_METHOD == "bulk":

        bulkOrganizeFiles(category_folder, checking_function)








#------------------------------------------------------------------------------#
#----------------------------------IMAGE---------------------------------------#
#------------------------------------------------------------------------------#




# Determines the presence of image file extensions in an extension list.
# Returns true if present, false otherwise.
def hasImageFiles():
    
    for extension in EXTENSION_LIST:
        if extension.lower() in IMAGE_FORMATS:
            return True

    return False


#____________________________________________________________________




# Determines whethere the file is an image file.
# Returns true if affirmative, false otherwise.
def isImageFile(extension):
    
    if extension in IMAGE_FORMATS:
        return True
    else:
        return False


#____________________________________________________________________




# Organizes image files.
def organizeImageFiles():

    # the folder representation for this (sub)category
    category_folder = "\\" + PROGRAM_SIGNATURE + "Image Files"

    # the function to use when checking for files of this category
    checking_function = isImageFile

    # call the corresponding organizing function based on the method
    if ORGANIZING_METHOD == "mirror":

        mirrorOrganizeFiles(category_folder, checking_function)

    elif ORGANIZING_METHOD == "bulk":

        bulkOrganizeFiles(category_folder, checking_function)





#------------------------------------------------------------------------------#
#----------------------------------APPLICATION---------------------------------#
#------------------------------------------------------------------------------#



# Determines the presence of executable file extensions in an extension list.
# Returns true if present, false otherwise.
def hasApplicationFiles():
    
    for extension in EXTENSION_LIST:
        if extension.lower() in APPLICATION_FORMATS:
            return True

    return False


#____________________________________________________________________




# Determines whethere the file is an application file.
# Returns true if affirmative, false otherwise.
def isApplicationFile(extension):
    
    if extension in APPLICATION_FORMATS:
        return True
    else:
        return False


#____________________________________________________________________




# Organizes application files.
def organizeApplicationFiles():

    # the folder representation for this (sub)category
    category_folder = "\\" + PROGRAM_SIGNATURE + "Application Files"

    # the function to use when checking for files of this category
    checking_function = isApplicationFile

    # call the corresponding organizing function based on the method
    if ORGANIZING_METHOD == "mirror":

        mirrorOrganizeFiles(category_folder, checking_function)

    elif ORGANIZING_METHOD == "bulk":

        bulkOrganizeFiles(category_folder, checking_function)











#------------------------------------------------------------------------------#
#--------------------------------DOCUMENTS - GENERAL---------------------------#
#------------------------------------------------------------------------------#



# Determines the presence of document extensions in a list.
# Returns true if present, false otherwise.
def hasDocumentFiles():

    for extension in EXTENSION_LIST:
        if extension.lower() in DOCUMENT_FORMATS:
            return True

    return False


#____________________________________________________________________



# Determines whethere the file is a document file.
# Returns true if affirmative, false otherwise.
def isDocumentFile(extension):

    if extension in DOCUMENT_FORMATS:
        return True
    else:
        return False


#____________________________________________________________________



# Organizes into subcategories all the document files from the target directory.
def organizeDocumentFiles():

    # create the folder for the calling (sub)category
    category_path = TARGET_DIRECTORY_PATH + "\\" + PROGRAM_SIGNATURE + "Document Files"
    if not os.path.exists(category_path):
        try:
            os.makedirs(category_path)
        except:
            pass

    # organizes pdf documents, if any
    if hasPdfDocumentFiles() == True:
        organizePdfDocumentFiles()

    # organizes word documents, if any
    if hasWordDocumentFiles() == True:
        organizeWordDocumentFiles()

    # organizes excel documents, if any
    if hasExcelDocumentFiles() == True:
        organizeExcelDocumentFiles()

    # organizes ebook documents, if any
    if hasEbookDocumentFiles() == True:
        organizeEbookDocumentFiles()

    # organizes powerpoint documents, if any
    if hasPowerpointDocumentFiles() == True:
        organizePowerpointDocumentFiles()

    # organizes plain text documents, if any
    if hasPlainTextDocumentFiles() == True:
        organizePlainTextDocumentFiles()

    # organizes other types of documents, if any
    if hasOtherDocumentFiles() == True:
        organizeOtherDocumentFiles()








#------------------------------------------------------------------------------#
#----------------------------------PDF-----------------------------------------#
#------------------------------------------------------------------------------#



# Pdf-version of the function.
def hasPdfDocumentFiles():

    for extension in EXTENSION_LIST:
        if extension.lower() in PDF_FORMATS:
            return True

    return False 


#____________________________________________________________________



# PDF-version of the function.
def isPdfDocumentFile(extension):

    if extension in PDF_FORMATS:
        return True
    else:
        return False


#____________________________________________________________________



# Organizes pdf document files.
def organizePdfDocumentFiles():

    # the folder representation for this (sub)category
    category_folder = "\\" + PROGRAM_SIGNATURE + "Document Files\\Pdf Documents"

    # the function to use when checking for files of this category
    checking_function = isPdfDocumentFile

    # call the corresponding organizing function based on the method
    if ORGANIZING_METHOD == "mirror":

        mirrorOrganizeFiles(category_folder, checking_function)

    elif ORGANIZING_METHOD == "bulk":

        bulkOrganizeFiles(category_folder, checking_function)









#------------------------------------------------------------------------------#
#----------------------------------WORD----------------------------------------#
#------------------------------------------------------------------------------#



# Word-version of the function.
def hasWordDocumentFiles():

    for extension in EXTENSION_LIST:
        if extension.lower() in WORD_FORMATS:
            return True

    return False 


#____________________________________________________________________




# Word-version of the function.
def isWordDocumentFile(extension):

    if extension in WORD_FORMATS:
        return True
    else:
        return False


#____________________________________________________________________



    
# Organizes word document files.
def organizeWordDocumentFiles():

    # the folder representation for this (sub)category
    category_folder = "\\" + PROGRAM_SIGNATURE + "Document Files\\Word Documents"

    # the function to use when checking for files of this category
    checking_function = isWordDocumentFile

    # call the corresponding organizing function based on the method
    if ORGANIZING_METHOD == "mirror":

        mirrorOrganizeFiles(category_folder, checking_function)

    elif ORGANIZING_METHOD == "bulk":

        bulkOrganizeFiles(category_folder, checking_function)









#------------------------------------------------------------------------------#
#----------------------------------SPREADSHEETS--------------------------------#
#------------------------------------------------------------------------------#




# Excel-version of the function.
def hasExcelDocumentFiles():

    for extension in EXTENSION_LIST:
        if extension.lower() in SPREADSHEET_FORMATS:
            return True

    return False 


#____________________________________________________________________




# Excel-version of the function.
def isExcelDocumentFile(extension):
    
    if extension in SPREADSHEET_FORMATS:
        return True
    else:
        return False


#____________________________________________________________________




# Organizes excel document files.
def organizeExcelDocumentFiles():

    # the folder representation for this (sub)category
    category_folder = "\\" + PROGRAM_SIGNATURE + "Document Files\\Excel Documents"

    # the function to use when checking for files of this category
    checking_function = isExcelDocumentFile

    # call the corresponding organizing function based on the method
    if ORGANIZING_METHOD == "mirror":

        mirrorOrganizeFiles(category_folder, checking_function)

    elif ORGANIZING_METHOD == "bulk":

        bulkOrganizeFiles(category_folder, checking_function)









#------------------------------------------------------------------------------#
#----------------------------------EBOOK---------------------------------------#
#------------------------------------------------------------------------------#




# Ebook-version of the function.
def hasEbookDocumentFiles():

    for extension in EXTENSION_LIST:
        if extension.lower() in EBOOK_FORMATS:
            return True

    return False 


#____________________________________________________________________




# Ebook-version of the function.
def isEbookDocumentFile(extension):

    if extension in EBOOK_FORMATS:
        return True
    else:
        return False


#____________________________________________________________________




# Organizes ebook document files.
def organizeEbookDocumentFiles():

    # the folder representation for this (sub)category
    category_folder = "\\" + PROGRAM_SIGNATURE + "Document Files\\Ebook Documents"

    # the function to use when checking for files of this category
    checking_function = isEbookDocumentFile

    # call the corresponding organizing function based on the method
    if ORGANIZING_METHOD == "mirror":

        mirrorOrganizeFiles(category_folder, checking_function)

    elif ORGANIZING_METHOD == "bulk":

        bulkOrganizeFiles(category_folder, checking_function)









#------------------------------------------------------------------------------#
#----------------------------------TXT-----------------------------------------#
#------------------------------------------------------------------------------#



# Text-version of the function.
def hasPlainTextDocumentFiles():

    for extension in EXTENSION_LIST:
        if extension.lower() in TEXT_FORMATS:
            return True

    return False 


#____________________________________________________________________




# Text-version of the function.
def isPlainTextDocumentFile(extension):

    if extension in TEXT_FORMATS:
        return True
    else:
        return False


#____________________________________________________________________



# Organizes text document files.
def organizePlainTextDocumentFiles():

    # the folder representation for this (sub)category
    category_folder = "\\" + PROGRAM_SIGNATURE + "Document Files\\Plain Text Documents"

    # the function to use when checking for files of this category
    checking_function = isPlainTextDocumentFile

    # call the corresponding organizing function based on the method
    if ORGANIZING_METHOD == "mirror":

        mirrorOrganizeFiles(category_folder, checking_function)

    elif ORGANIZING_METHOD == "bulk":

        bulkOrganizeFiles(category_folder, checking_function)









#------------------------------------------------------------------------------#
#----------------------------------POWERPOINT----------------------------------#
#------------------------------------------------------------------------------#



# Powerpoint-version of the function.
def hasPowerpointDocumentFiles():

    for extension in EXTENSION_LIST:
        if extension.lower() in POWERPOINT_FORMATS:
            return True

    return False


#____________________________________________________________________




# Powerpoint-version of the function.
def isPowerpointDocumentFile(extension):

    if extension in POWERPOINT_FORMATS:
        return True
    else:
        return False


#____________________________________________________________________




# Organizes powerpoint document files.
def organizePowerpointDocumentFiles():

    # the folder representation for this (sub)category
    category_folder = "\\" + PROGRAM_SIGNATURE + "Document Files\\Powerpoint Documents"

    # the function to use when checking for files of this category
    checking_function = isPowerpointDocumentFile

    # call the corresponding organizing function based on the method
    if ORGANIZING_METHOD == "mirror":

        mirrorOrganizeFiles(category_folder, checking_function)

    elif ORGANIZING_METHOD == "bulk":

        bulkOrganizeFiles(category_folder, checking_function)









#------------------------------------------------------------------------------#
#----------------------------------OTHER DOCUMENTS-----------------------------#
#------------------------------------------------------------------------------#



# Checks whether we have documents that don't fall
# under any of the previous subcategories.
# Returns true if affirmative, false otherwise.
def hasOtherDocumentFiles():

    for extension in EXTENSION_LIST:
        if isDocumentFile(extension) == True and \
           isPdfDocumentFile(extension) == False and \
           isWordDocumentFile(extension) == False and \
           isExcelDocumentFile(extension) == False and \
           isPlainTextDocumentFile(extension) == False and \
           isPowerpointDocumentFile(extension) == False and \
           isEbookDocumentFile(extension) == False:

            return True

    return False 


#____________________________________________________________________



# Checks whether the document falls
# under either of the previous subcategories.
# Returns true if it doesn't (i.e. it's an OTHER document file),
# false otherwise.
def isOtherDocumentFile(extension):

    if isDocumentFile(extension) == True and \
       isPdfDocumentFile(extension) == False and \
       isWordDocumentFile(extension) == False and \
       isExcelDocumentFile(extension) == False and \
       isPlainTextDocumentFile(extension) == False and \
       isPowerpointDocumentFile(extension) == False and \
       isEbookDocumentFile(extension) == False:

        return True

    return False


#____________________________________________________________________




# Organizes other document files.
def organizeOtherDocumentFiles():

    # the folder representation for this (sub)category
    category_folder = "\\" + PROGRAM_SIGNATURE + "Document Files\\Other Documents"

    # the function to use when checking for files of this category
    checking_function = isOtherDocumentFile

    # call the corresponding organizing function based on the method
    if ORGANIZING_METHOD == "mirror":

        mirrorOrganizeFiles(category_folder, checking_function)

    elif ORGANIZING_METHOD == "bulk":

        bulkOrganizeFiles(category_folder, checking_function)








#------------------------------------------------------------------------------#
#----------------------------------OTHER FILES---------------------------------#
#------------------------------------------------------------------------------#




# Checks whether we have files that don't fall
# under any of the previous categories.
# Returns true if affirmative, false otherwise.
def hasOtherFiles():

    for extension in EXTENSION_LIST:
        if isVideoFile(extension) == False and \
           isAudioFile(extension) == False and \
           isImageFile(extension) == False and \
           isApplicationFile(extension) == False and \
           isDocumentFile(extension) == False:

            return True

    return False 


#____________________________________________________________________




# Checks whether the file falls
# under either of the previous categories.
# Returns true if it doesn't (i.e. it's an OTHER file),
# false otherwise.
def isOtherFile(extension):

    if isVideoFile(extension) == False and \
       isAudioFile(extension) == False and \
       isImageFile(extension) == False and \
       isApplicationFile(extension) == False and \
       isDocumentFile(extension) == False:

        return True

    return False


#____________________________________________________________________




# Organizes into subcategories the other types of files from the target directory.
def organizeOtherFiles():

    # create the folder for the calling (sub)category
    category_path = TARGET_DIRECTORY_PATH + "\\" + PROGRAM_SIGNATURE + "Other Files"
    if not os.path.exists(category_path):
        try:
            os.makedirs(category_path)
        except:
            pass

    # organizes coding files, if any
    if hasCodingFiles() == True:
        organizeCodingFiles()

    # organizes archive files, if any    
    if hasArchiveFiles() == True:
        organizeArchiveFiles()
        
    # organizes virtual image files, if any
    if hasVirtualImageFiles() == True:
        organizeVirtualImageFiles()

    # organizes torrent files, if any
    if hasTorrentFiles() == True:
        organizeTorrentFiles()

    # organizes remaining files, if any        
    if hasRemainingFiles() == True:
        organizeRemainingFiles()









#------------------------------------------------------------------------------#
#----------------------------------CODING---------------------------------------#
#------------------------------------------------------------------------------#



# Determines the presence of coding (script and source code) files.
# Returns true if present, false otherwise.
def hasCodingFiles():
    
    for extension in EXTENSION_LIST:
        if extension.lower() in CODING_FORMATS:
            return True

    return False


#____________________________________________________________________




# Checks whether the file is a coding file (script or source code).
# Returns true if affirmative, false otherwise.
def isCodingFile(extension):

    if extension in CODING_FORMATS:
        return True
    else:
        return False


#____________________________________________________________________




# Organizes coding files.
def organizeCodingFiles():

    # the folder representation for this (sub)category
    category_folder = "\\" + PROGRAM_SIGNATURE + "Other Files\\Coding Files"

    # the function to use when checking for files of this category
    checking_function = isCodingFile

    # call the corresponding organizing function based on the method
    if ORGANIZING_METHOD == "mirror":

        mirrorOrganizeFiles(category_folder, checking_function)

    elif ORGANIZING_METHOD == "bulk":

        bulkOrganizeFiles(category_folder, checking_function)








#------------------------------------------------------------------------------#
#----------------------------------ARCHIVE-------------------------------------#
#------------------------------------------------------------------------------#



# Determines the presence of archive files.
# Returns true if present, false otherwise.
def hasArchiveFiles():

    for extension in EXTENSION_LIST:
        if extension.lower() in ARCHIVE_FORMATS:
            return True

    return False


#____________________________________________________________________




# Checks whether the file is an archive file.
# Returns true if affirmative, false otherwise.
def isArchiveFile(extension):

    if extension in ARCHIVE_FORMATS:
        return True
    else:
        return False


#____________________________________________________________________




# Organizes archive files.
def organizeArchiveFiles():

    # the folder representation for this (sub)category
    category_folder = "\\" + PROGRAM_SIGNATURE + "Other Files\\Archive Files"

    # the function to use when checking for files of this category
    checking_function = isArchiveFile

    # call the corresponding organizing function based on the method
    if ORGANIZING_METHOD == "mirror":

        mirrorOrganizeFiles(category_folder, checking_function)

    elif ORGANIZING_METHOD == "bulk":

        bulkOrganizeFiles(category_folder, checking_function)









#------------------------------------------------------------------------------#
#----------------------------VIRTUAL IMAGE-------------------------------------#
#------------------------------------------------------------------------------#



# Determines the presence of virtual image files.
# Returns true if present, false otherwise.
def hasVirtualImageFiles():
    
    for extension in EXTENSION_LIST:
        if extension.lower() in VIRTUAL_IMAGE_FORMATS:
            return True

    return False


#____________________________________________________________________




# Checks whether the file is a virtual image file.
# Returns true if affirmative, false otherwise.
def isVirtualImageFile(extension):
    
    if extension in VIRTUAL_IMAGE_FORMATS:
        return True
    else:
        return False


#____________________________________________________________________




# Organizes virtual image files.
def organizeVirtualImageFiles(TARGET_DIRECTORY_PATH, ORGANIZING_METHOD):

    # the folder representation for this (sub)category
    category_folder = "\\" + PROGRAM_SIGNATURE + "Other Files\\Virtual Image Files"

    # the function to use when checking for files of this category
    checking_function = isVirtualImageFile

    # call the corresponding organizing function based on the method
    if ORGANIZING_METHOD == "mirror":

        mirrorOrganizeFiles(category_folder, checking_function)

    elif ORGANIZING_METHOD == "bulk":

        bulkOrganizeFiles(category_folder, checking_function)






#------------------------------------------------------------------------------#
#----------------------------------TORRENT---------------------------------------#
#------------------------------------------------------------------------------#



# Determines the presence of torrent file extensions in an extension list.
# Returns true if present, false otherwise.
def hasTorrentFiles():
    
    for extension in EXTENSION_LIST:
        if extension.lower() in TORRENT_FORMATS:
            return True

    return False


#____________________________________________________________________




# Determines whethere the file is a torrent file.
# Returns true if affirmative, false otherwise.
def isTorrentFile(extension):
    
    if extension in TORRENT_FORMATS:
        return True
    else:
        return False


#____________________________________________________________________





# Organizes torrent files.
def organizeTorrentFiles():

    # the folder representation for this (sub)category
    category_folder = "\\" + PROGRAM_SIGNATURE + "Other Files\\Torrent Files"

    # the function to use when checking for files of this category
    checking_function = isTorrentFile

    # call the corresponding organizing function based on the method
    if ORGANIZING_METHOD == "mirror":

        mirrorOrganizeFiles(category_folder, checking_function)

    elif ORGANIZING_METHOD == "bulk":

        bulkOrganizeFiles(category_folder, checking_function)







#------------------------------------------------------------------------------#
#-----------------------OTHER OTHER (ahem!) FILES------------------------------#
#------------------------------------------------------------------------------#




# Checks whether we have files that don't fall
# under any of the previous categories and subcategories.
# Returns true if affirmative, false otherwise.
def hasRemainingFiles():

    for extension in EXTENSION_LIST:
        if isOtherFile(extension) == True and \
           isArchiveFile(extension) == False and \
           isCodingFile(extension) == False and \
           isTorrentFile(extension) == False and \
           isVirtualImageFile(extension) == False:
            
            return True

    return False 


#____________________________________________________________________




# Checks whether the file falls
# under either of the previous categories and subcategories.
# Returns true if it doesn't (i.e. it's an other OTHER file),
# false otherwise.
def isRemainingFile(extension):

    if isOtherFile(extension) == True and \
       isArchiveFile(extension) == False and \
       isCodingFile(extension) == False and \
       isTorrentFile(extension) == False and \
       isVirtualImageFile(extension) == False:
        
        return True

    return False


#____________________________________________________________________




# Organizes remaining files.
def organizeRemainingFiles():

    # the folder representation for this (sub)category
    category_folder = "\\" + PROGRAM_SIGNATURE + "Other Files\\Remaining Files"

    # the function to use when checking for files of this category
    checking_function = isRemainingFile

    # call the corresponding organizing function based on the method
    if ORGANIZING_METHOD == "mirror":

        mirrorOrganizeFiles(category_folder, checking_function)

    elif ORGANIZING_METHOD == "bulk":

        bulkOrganizeFiles(category_folder, checking_function)









#------------------------------------------------------------------------------#
#-------------------------------FILE FORMATS-----------------------------------#
#------------------------------------------------------------------------------#




# list of video file formats
# https://en.wikipedia.org/wiki/Video_file_format
VIDEO_FORMATS = ['.3g2', '.3gp', '.amv', '.asf', '.avi', '.drc', \
                 '.f4a', '.f4p', '.f4v', '.fbb', '.flv', '.flv', \
                 '.gifv', '.m2v', '.m4p', '.m4v', '.m4v', '.mkv', \
                 '.mng', '.mov', '.mp2', '.mp4', '.mpe', '.mpeg', \
                 '.mpg', '.mpv', '.mxf', '.nsv', '.ogg', '.ogv', \
                 '.qt', '.rm', '.rmvb', '.roq', '.svi', '.vob', \
                 '.webm', '.wmv', '.yuv']


# list of audio file formats
# https://en.wikipedia.org/wiki/Audio_file_format
AUDIO_FORMATS = ['.aa', '.aac', '.aax', '.act', '.aiff', '.amr', \
                 '.ape', '.au', '.awb', '.dct', '.dss', '.dvf', \
                 '.flac', '.gsm', '.iklax', '.ivs', '.m4a', '.m4b', \
                 '.mmf', '.mp3', '.mpc', '.msv', '.oga', '.mogg', \
                 '.opus', '.ra', '.raw', '.sln', '.tta', '.vox', \
                 '.wav', '.wma', '.wv']


# list of image file formats
# http://www.altools.com/altools/alsee/features/view-23-image-formats.aspx
IMAGE_FORMATS = ['.ani', '.bmp', '.cal', '.fax', '.gif', '.img', \
                 '.jbg', '.jpe', '.jpeg', '.jpg', '.mac', '.pbm', \
                 '.pcd', '.pcx', '.pct', '.pgm', '.png', '.ppm', \
                 '.psd', '.ras', '.tga', '.tiff', '.tif', '.wmf']



# list of executable file formats
# http://www.thepreparednesspodcast.com/quick-list-on-executable-file-extensions-updated/
APPLICATION_FORMATS = ['.action', '.apk', '.app', '.bat', '.bin', '.cmd', \
                      '.com', '.command', '.cpl', '.exe', '.gadget', '.inf', \
                      '.ins', '.inx', '.ipa', '.isu', '.job', '.jse', '.ksh', \
                      '.lnk', '.msc', '.msi', '.msp', '.mst', '.osx', '.out', \
                      '.paf', '.pif', '.prg', '.ps1', '.reg', '.rgs', '.run', \
                      '.sct', '.shb', '.shs', '.u3p', '.vb', '.vbe', '.vbs', \
                      '.vbscript', '.workflow', '.ws', '.wsf']



# list of document file formats
# https://en.wikipedia.org/wiki/List_of_file_formats#Document
DOCUMENT_FORMATS = ['.602', '.abw', '.acl', '.afp', '.ami', '.ans', \
                    '.asc', '.aww', '.ccf', '.csv', '.cwk', '.dbk', \
                    '.doc', '.docm', '.docx', '.dot', '.dotx', '.egt', \
                    '.epub', '.ezw', '.fdx', '.ftm', '.ftx', '.gdoc', \
                    '.html', '.fb2', '.djvu', \
                    '.hwp', '.hwpml', '.log', '.lwp', '.mbp', '.md', \
                    '.mcw', '.mobi', '.nb', '.nbp', '.neis', '.odm', \
                    '.odt', '.ott', '.omm', '.pages', '.pap', '.pdax', \
                    '.pdf', '.pps', '.ppt', '.quox', '.rtf', '.rpt', \
                    '.sdw', '.se', \
                    '.stw', '.sxw', '.tex', '.info', '.troff', '.txt', \
                    '.uof', '.uoml', '.via', '.wpd', '.wps', '.wpt', \
                    '.wrd', '.wrf', '.wri', '.xhtml', '.xml', '.xps',\
                    '.123', '.ab2', '.ab3', '.aws', '.bcsv', '.clf', \
                    '.cell', '.csv', '.gsheet', '.numbers', '.gnumeric',\
                    '.ods', '.ots', '.qpw', '.sdc', '.slk', '.stc', \
                    '.sxc', '.tab', '.vc', '.wk1', '.wk3', '.wk4', '.wks',\
                    '.wq1', '.xlk', '.xlsb', '.xlsm', '.xlsx', '.xlr', \
                    '.xltm', '.xls', '.xlt','.xlw', \
                    '.aeh', '.apnx', '.ava', '.azn', '.azw', '.azw1', \
                    '.azw3', '.azw4', '.bdb2', '.bek', '.bfl', '.bkk', \
                    '.bpnueb', '.brn', '.cb7', '.cba', '.cbc', '.cbcx', \
                    '.cbds', '.cbmv', '.cbr', '.cbt', '.cbz', '.ceb', \
                    '.cebx', '.chmprj', '.cl2arc', '.cl2doc', '.comictpl', \
                    '.dbk', '.dnl', '.eba', '.ebaml', '.ebk', '.ebk2', '.ebo', \
                    '.ebx', '.edt', '.epub', '.fb2', '.fub', '.gpf', '.gpx', \
                    '.hsb', '.html0', '.htxt', '.htz4', '.iba', '.ibook', \
                    '.ibook', '.ibooks', '.imp', '.kf8', '.kml', '.lbxcol', \
                    '.lbxoeb', '.lit', '.lpr', '.lrf', '.lrs', '.lrt', '.lrx', \
                    '.mart', '.mbp1', '.meb', '.mga', '.mobi', '.mpub', '.nat', \
                    '.oeb', '.opf', '.orb', '.original_epub', '.original_mobi', \
                    '.pdb', '.pdg', '.phl', '.pkg', '.pml', '.pmlz', '.pobi', \
                    '.prc', '.prc', '.qmk', '.rb', '.sbrz', '.sgf', '.snb', \
                    '.stk', '.tbnueb', '.tcr', '.tk3', '.tpz', '.tr', '.tr2', \
                    '.tr3', '.txt7', '.txtc', '.txtr', '.txtz', '.ubk', '.umd', \
                    '.vbk', '.vellum', '.webz', '.wmga', '.wolf', '.xeb', '.xmdf',\
                    '.ybhtm', '.ybk', '.ybrar', '.ybrtf', '.ybtxt', '.zna', \
                    '.zno', '.emf', '.odp', '.pot', '.potm', '.potx', '.ppa', \
                    '.ppam', '.pps', '.ppsm', '.ppsx', '.pps', '.pptm', '.pptx']


# list of pdf document formats
PDF_FORMATS = ['.pdf', '.djvu']

# list of word document formats
WORD_FORMATS = ['.doc', '.docx', '.docm', '.dot', '.dotm', '.dotx', \
                '.odt', '.xml', '.xps', '.wps', '.rtf']


# list of spreadsheet formats
SPREADSHEET_FORMATS = ['.123', '.ab2', '.ab3', '.aws', '.bcsv', '.clf', \
                       '.cell', '.csv', '.gsheet', '.numbers', '.gnumeric',\
                       '.ods', '.ots', '.qpw', '.sdc', '.slk', '.stc', \
                       '.sxc', '.tab', '.vc', '.wk1', '.wk3', '.wk4', '.wks',\
                       '.wq1', '.xlk', '.xlsb', '.xlsm', '.xlsx', '.xlr', \
                       '.xltm', '.xls', '.xlt','.xlw']

# list of pdf document formats
# http://www.file-extensions.org/filetype/extension/name/e-book-files
EBOOK_FORMATS = ['.aeh', '.apnx', '.ava', '.azn', '.azw', '.azw1', \
                 '.azw3', '.azw4', '.bdb2', '.bek', '.bfl', '.bkk', \
                 '.bpnueb', '.brn', '.cb7', '.cba', '.cbc', '.cbcx', \
                 '.cbds', '.cbmv', '.cbr', '.cbt', '.cbz', '.ceb', \
                 '.cebx', '.chmprj', '.cl2arc', '.cl2doc', '.comictpl', \
                 '.dbk', '.dnl', '.eba', '.ebaml', '.ebk', '.ebk2', '.ebo', \
                 '.ebx', '.edt', '.epub', '.fb2', '.fub', '.gpf', '.gpx', \
                 '.hsb', '.html0', '.htxt', '.htz4', '.iba', '.ibook', \
                 '.ibook', '.ibooks', '.imp', '.kf8', '.kml', '.lbxcol', \
                 '.lbxoeb', '.lit', '.lpr', '.lrf', '.lrs', '.lrt', '.lrx', \
                 '.mart', '.mbp1', '.meb', '.mga', '.mobi', '.mpub', '.nat', \
                 '.oeb', '.opf', '.orb', '.original_epub', '.original_mobi', \
                 '.pdb', '.pdg', '.phl', '.pkg', '.pml', '.pmlz', '.pobi', \
                 '.prc', '.prc', '.qmk', '.rb', '.sbrz', '.sgf', '.snb', \
                 '.stk', '.tbnueb', '.tcr', '.tk3', '.tpz', '.tr', '.tr2', \
                 '.tr3', '.txt7', '.txtc', '.txtr', '.txtz', '.ubk', '.umd', \
                 '.vbk', '.vellum', '.webz', '.wmga', '.wolf', '.xeb', '.xmdf',\
                 '.ybhtm', '.ybk', '.ybrar', '.ybrtf', '.ybtxt', '.zna', \
                 '.zno', '.mbp']


# list of plain text document formats
TEXT_FORMATS = ['.prn', '.txt', '.csv', '.dif', '.slk']


# list of presentation document formats
POWERPOINT_FORMATS = ['.emf', '.odp', '.pot', '.potm', '.potx', '.ppa', \
                      '.ppam', '.pps', '.ppsm', '.ppsx', '.pps', '.pptm', \
                      '.pptx']


# list of script and source code file formats
# https://en.wikipedia.org/wiki/List_of_file_formats#Script
# https://en.wikipedia.org/wiki/List_of_file_formats#Source_code_for_computer_programs
CODING_FORMATS = ['.ahk', '.applescript', '.as', '.au3', '.bat', '.bas', \
                  '.cljs', '.cmd', '.coffee', '.duino', '.egg', '.egt', \
                  '.erb', '.hta', '.ibi', '.ici', '.ijs', '.ipynb', '.itcl', \
                  '.js', '.jsfl', '.lua', '.m', '.mrc', '.ncf', '.nuc', \
                  '.nud', '.nut', '.php', '.php?', '.pl', '.pm', '.ps1', \
                  '.ps1xml', '.psc1', '.psd1', '.psm1', '.py', '.pyc', \
                  '.pyo', '.r', '.rb', '.rdp', '.scpt', '.scptd', '.sdl', \
                  '.sh', '.syjs', '.sypy', '.tcl', '.vbs', '.xpl', '.ebuild', \
                  '.ada', '.adb', '.2.ada', '.ads', '.1.ada', '.asm', '.s', \
                  '.bas', '.bb', '.bmx', '.c', '.clj', '.cls', '.cob', '.cbl', \
                  '.cpp', '.cc', '.cxx', '.cbp', '.cs', '.csproj', '.d', '.dba', \
                  '.dbpro123', '.e', '.efs', '.egt', '.el', '.for', '.ftn', '.f', \
                  '.f', '.f77', '.f90', '.frm', '.frx', '.fth', '.ged', '.gm6', \
                  '.gmd', '.gmk', '.gml', '.go', '.h', '.hpp', '.hxx', '.hs', \
                  '.i', '.inc', '.java', '.l', '.lgt', '.lisp', '.m', '.m4', \
                  '.ml', '.n', '.nb', '.p', '.pas', '.pp', '.php', '.php3', \
                  '.php4', '.php5', '.php6', '.phtml', '.piv', '.pl', '.pm', \
                  '.prg', '.pro', '.pol', '.py', '.r', '.red', '.reds', '.rb', \
                  '.resx', '.rc', '.rc2', '.rkt', '.rktl', '.scala', '.sci', \
                  '.sce', '.scm', '.sd7', '.skb', '.skc', '.skd', '.ski', '.skk', \
                  '.skm', '.sko', '.skp', '.skq', '.sks', '.skt', '.skz', '.sln', \
                  '.spin', '.stk', '.swg', '.tcl', '.vap', '.vb', '.vbg', '.vbp', \
                  '.vip', '.vbproj', '.vcproj', '.vdproj', '.xpl', '.cx', '.xsl', \
                  '.y']



# list of archive file formats
# https://en.wikipedia.org/wiki/List_of_file_formats#Archive_and_compressed
ARCHIVE_FORMATS = ['.cab', '.?q?', '.7z', '.ace', '.alz', '.apk', '.at3', \
                   '.bke', '.arc', '.arj', '.ass', '.sas', '.b', '.ba', \
                   '.big', '.bik', '.bin', '.bkf', '.bzip2', '.bld', '.c4', \
                   '.cals', '.clipflair', '.cpt', '.sea', '.daa', '.deb', \
                   '.dmg', '.ddz', '.dpe', '.egg', '.egt', '.ecab', '.ezip', \
                   '.ess', '.gho', '.gzip', '.ipg', '.jar', '.lbr', '.lqr', \
                   '.lha', '.lzip', '.lzo', '.lzma', '.lzx', '.mbrwizard', \
                   '.meta', '.mpq', '.nth', '.osz', '.pak', '.par', '.par2', \
                   '.paf', '.pyk', '.pk3', '.pk4', '.rar', '.rag', '.rags', \
                   '.rpm', '.sen', '.sit', '.skb', '.szs', '.tar', '.tgz', \
                   '.tb', '.tib', '.uha', '.uue', '.viv', '.vol', '.vsa', \
                   '.wax', '.z', '.zoo', '.zip']


# list of virtual image file formats
# https://en.wikipedia.org/wiki/List_of_file_formats#Physical_recordable_media_archiving
VIRTUAL_IMAGE_FORMATS = ['.iso', '.nrg', '.adf', '.adz', '.dms', '.dsk', \
                         '.d64', '.sdi', '.mds', '.mdx', '.dmg', '.cdi', \
                         '.cue', '.cif', '.c2d', '.daa', '.b6t']


# "list" of torrent formats
TORRENT_FORMATS = ['.torrent']
