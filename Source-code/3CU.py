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
                            #    GUI WINDOW    #
                            ####################



# GUI modules
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# file manipulation modules
import sys, os

# icon resource module
import images_qr

# helper modules
import categorize_GUI_helpers
import combine_GUI_helpers
import cleanup_GUI_helpers

# main window class
class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # app window title
        self.setWindowTitle("3CU")

        # app window icon
        # credit: http://cdnll.reallygoodstuff.com/images/xl/148322.jpg
        self.setWindowIcon(QIcon(":/icons/app-icon.png"))
        
        # app window min size
        self.setMinimumSize(600,300)

        # tab widget for the app
        CCCU_tabs = QTabWidget()

        # make it the main app widget
        self.setCentralWidget(CCCU_tabs)

        # make the tabs triangular
        CCCU_tabs.setTabShape(QTabWidget.Triangular)




#------- 1ST TAB -- CATEGORIZE TAB CONTENT ----------------------------
        catWidget = QWidget()
        CCCU_tabs.addTab(catWidget, "Categorize")
        catWidget.setStyleSheet("background-color: #99803D;")




        # DESCRIPTION
        # description is provided in form of tabs
        # 1st tab - categorize general description
        cat_general_description = '''        3CU Categorize takes a folder \
or drive and organizes its files into separate categories. It iterates through \
all the files of the target, checks what categories are present, \
right inside the target creates special \
folders for each of those categories, and then moves all the files to their \
corresponding category folder.
        The categories are: audio files, video \
files, documents, pictures, applications, and \
other files. Two of these categories have subcategories:
        - documents \
are divided into text documents, portable documents, spreadsheets, \
presentations, plain text documents, and other documents;
        - other files are divided into archives, virtual images, torrent files, coding \
files, and other (ahem!) "other" files.

        3CU Categorize uses two methods ("mirror" and "bulk") and one mode ("hold \
me daddy"). Their description follows.'''

        # 1st tab title
        catGenDescriptionTitleLabel = QLabel('I. 3CU Categorize')
        catGenDescriptionTitleLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        catGenDescriptionTitleLabel.setStyleSheet("font-weight: bold;"
                                                  "padding-top: 5px;")
        # 1st tab text
        catGenDescriptionTextLabel = QLabel(cat_general_description)
        catGenDescriptionTextLabel.setWordWrap(True)
        catGenDescriptionTextLabel.setStyleSheet("padding: 2px;")

        # 1st tab widget
        catGenDescriptionWidget = QWidget()
        catGenDescriptionLayout = QVBoxLayout()
        catGenDescriptionWidget.setLayout(catGenDescriptionLayout)
        catGenDescriptionLayout.addWidget(catGenDescriptionTitleLabel)
        catGenDescriptionLayout.addWidget(catGenDescriptionTextLabel)



        # the next description tabs follow the same structure
        cat_bulk_description = '''        The "bulk" method treats the \
newly created category folders as bulk deposits. It takes a file, checks \
its category, and moves it to the corresponding category folder. The file \
may be right inside the target folder or drive, or it may be stored somewhere \
deep inside the target tree - it doesn't matter! All the files of one \
category are moved one click away (target\\original\\
relative\\path\\to\\file becomes target\\special_category_folder\\file). 
        Duplicate-name issues are solved Windows-style (adding (2), (3), (4), \
etc.).
        You may opt to delete any empty directories that may have been left \
behind in the target folder or drive after moving all the files from them.
        This is useful for situations when you simply want to have all the files of a \
certain category in one place, one click away.'''

        catBulkDescriptionTitleLabel = QLabel('II. The "bulk" method')
        catBulkDescriptionTitleLabel.setStyleSheet("font-weight: bold;"
                                                   "padding-top: 5px;")
        catBulkDescriptionTitleLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        catBulkDescriptionTextLabel = QLabel(cat_bulk_description)
        catBulkDescriptionTextLabel.setWordWrap(True)
        catBulkDescriptionTextLabel.setStyleSheet("padding: 2px;")

        catBulkDescriptionWidget = QWidget()
        catBulkDescriptionLayout = QVBoxLayout()
        catBulkDescriptionLayout.addWidget(catBulkDescriptionTitleLabel)
        catBulkDescriptionLayout.addWidget(catBulkDescriptionTextLabel)
        catBulkDescriptionWidget.setLayout(catBulkDescriptionLayout)



        cat_mirror_description = '''        The "mirror" method creates \
category folders as well, they also contain only files of a specific \
type, however, each specialized category folder is a "mirror" \
of the target folder. This means that the original location of the file \
inside the target folder or drive is important, as the file's relative \
path is preserved (target\\original\\relative\\path\\to\\file becomes \
target\\special_category_folder\\original\\relative\\path\\to\\file).
        Again, you may opt to delete any empty directories that may have been left \
behind in the target folder or drive after moving all the files from them.
        This method is useful for situations when the file's original location \
inside the target tree is important in the process of file organization.'''

        catMirrorDescriptionTitleLabel = QLabel('III. The "mirror" method')
        catMirrorDescriptionTitleLabel.setStyleSheet("font-weight: bold;"
                                                     "padding-top: 5px;")
        catMirrorDescriptionTitleLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        catMirrorDescriptionTextLabel = QLabel(cat_mirror_description)
        catMirrorDescriptionTextLabel.setWordWrap(True)
        catMirrorDescriptionTextLabel.setStyleSheet("padding: 2px;")

        catMirrorDescriptionWidget = QWidget()
        catMirrorDescriptionLayout = QVBoxLayout()
        catMirrorDescriptionLayout.addWidget(catMirrorDescriptionTitleLabel)
        catMirrorDescriptionLayout.addWidget(catMirrorDescriptionTextLabel)
        catMirrorDescriptionWidget.setLayout(catMirrorDescriptionLayout)



        cat_daddy_description = '''        As an intermediate solution, 3CU Categorize \
offers you the possibility to move all the files of a certain category in \
one place (right inside the newly created category folders), but together \
with their immediate parent folder (target\\original\\relative\\path\\to\\file \
becomes target\\special_category_folder\\to\\file). This is the \
special "hold me daddy" mode, available when categorizing in "bulk". 
        Duplicate-name issues among parent folders are solved Windows-style, \
and you may opt to delete left behind empty directories.
        This proves useful for situations when the parent folder is \
important in the process of file organization (ex. you want to move all the \
pictures from an event, but you don't want them mixing with the thousands \
of other pictures you have in your target folder or drive, so you move \
them with their parent folder). '''

        catDaddyDescriptionTitleLabel = QLabel('IV. The "hold me daddy" mode')
        catDaddyDescriptionTitleLabel.setStyleSheet("font-weight: bold;"
                                                    "padding-top: 5px;")
        catDaddyDescriptionTitleLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        catDaddyDescriptionTextLabel = QLabel(cat_daddy_description)
        catDaddyDescriptionTextLabel.setWordWrap(True)
        catDaddyDescriptionTextLabel.setStyleSheet("padding: 2px;")

        catDaddyDescriptionWidget = QWidget()
        catDaddyDescriptionLayout = QVBoxLayout()
        catDaddyDescriptionLayout.addWidget(catDaddyDescriptionTitleLabel)
        catDaddyDescriptionLayout.addWidget(catDaddyDescriptionTextLabel)
        catDaddyDescriptionWidget.setLayout(catDaddyDescriptionLayout)

        

        cat_untouchables_description = '''        3CU Categorize will not affect \
any hidden files \
or folders on your computer. This type of files and folders are usually \
essential, either to the user or to the system itself, so the \
program won't take the risk of moving them around. 
        Aditionally, 3CU Categorize gives you the possibility to exclude \
from the categorizing process any files or folders existing inside the \
target folder or drive. Just add these files and/or folders in the \
"Exceptions" section and they won't be touched.

        Now, 3CU does generally check whether files and/or folders have \
the appropriate permissions to perform the operations involved, however \
most probably these aren't all accounted for. Even though the code uses \
try-except statements in abundance in order to deal with potential errors, \
things could go horribly wrong if, say, you start using 3CU on a system \
folder riddled with limited-access content. So, play it safe, use 3CU on \
normal user content, and it should do the trick.'''

        catUntouchablesDescriptionTitleLabel = QLabel('V. The Untouchables')
        catUntouchablesDescriptionTitleLabel.setStyleSheet("font-weight: bold;"
                                                    "padding-top: 5px;")
        catUntouchablesDescriptionTitleLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        catUntouchablesDescriptionTextLabel = QLabel(cat_untouchables_description)
        catUntouchablesDescriptionTextLabel.setWordWrap(True)
        catUntouchablesDescriptionTextLabel.setStyleSheet("padding: 2px;")

        catUntouchablesDescriptionWidget = QWidget()
        catUntouchablesDescriptionLayout = QVBoxLayout()
        catUntouchablesDescriptionLayout.addWidget(catUntouchablesDescriptionTitleLabel)
        catUntouchablesDescriptionLayout.addWidget(catUntouchablesDescriptionTextLabel)
        catUntouchablesDescriptionWidget.setLayout(catUntouchablesDescriptionLayout)



        cat_restore_description = '''        After processing, 3CU Categorize \
offers you the possibility to restore the target folder or drive to the \
state it was before categorization.
        However, if you want to be able to restore, DON'T CLOSE THE PROGRAM \
SESSION AFTER CATEGORIZING! Run the categorization, check the result, and, \
if you're not satisfied, roll back the changes.
        For this feature to work correctly, in the meantime, don't rename, \
delete or move around any of the affected files and folders.'''

        catRestoreDescriptionTitleLabel = QLabel('VI. Restoring')
        catRestoreDescriptionTitleLabel.setStyleSheet("font-weight: bold;"
                                                    "padding-top: 5px;")
        catRestoreDescriptionTitleLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        catRestoreDescriptionTextLabel = QLabel(cat_restore_description)
        catRestoreDescriptionTextLabel.setWordWrap(True)
        catRestoreDescriptionTextLabel.setStyleSheet("padding: 2px;")

        catRestoreDescriptionWidget = QWidget()
        catRestoreDescriptionLayout = QVBoxLayout()
        catRestoreDescriptionLayout.addWidget(catRestoreDescriptionTitleLabel)
        catRestoreDescriptionLayout.addWidget(catRestoreDescriptionTextLabel)
        catRestoreDescriptionWidget.setLayout(catRestoreDescriptionLayout)
        # END OF 1ST TAB DESCRIPTION


        # INPUT SECTION STARTS HERE
        # TARGET DIRECTORY line
        # the label
        catTargetDirLabel = QLabel("1. Choose the target directory:")
        catTargetDirLabel.setStyleSheet("font-weight: bold;")

        # the line edit
        # make it read-only (for a valid URI)
        self.catTargetDirLineEdit = QLineEdit()
        self.catTargetDirLineEdit.setReadOnly(True)
        self.catTargetDirLineEdit.setStyleSheet("background-color: white;"
                                                   "border-radius: 2px;"
                                                   "height: 20px;")

        # the button - connect it to the function that fills the line
        # icons credit: https://github.com/yusukekamiyamane/fugue-icons
        catBrowseTargetDirButton = QPushButton(
            QIcon(':/icons/folder-horizontal.png'),"Browse")      
        catBrowseTargetDirButton.setStyleSheet("background-color: grey;")
        catBrowseTargetDirButton.pressed.connect( self.catChooseTargetDir )


        # METHOD line
        # the label
        catMethodLabel = QLabel("2. Select the method:")
        catMethodLabel.setStyleSheet("font-weight: bold;")
        catMethodLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)


        # the methods
        # connects the method buttons to the "enable daddy mode" function
        self.catMirrorRadioButton = QRadioButton("Mirror")
        self.catMirrorRadioButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.catMirrorRadioButton.setStyleSheet("padding-left: 43px;")
        self.catMirrorRadioButton.clicked.connect ( self.catEnableDaddyMode )
        
        self.catBulkRadioButton = QRadioButton("Bulk")
        self.catBulkRadioButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.catBulkRadioButton.setStyleSheet("padding-left: 50px;")
        self.catBulkRadioButton.clicked.connect ( self.catEnableDaddyMode )

        # group the method radio button to separate them from
        # other potential radio buttons
        catMethodGroupBox = QGroupBox()
        catMethodRadioLayout = QHBoxLayout()
        catMethodRadioLayout.addWidget(self.catMirrorRadioButton)
        catMethodRadioLayout.addWidget(self.catBulkRadioButton)
        catMethodGroupBox.setLayout(catMethodRadioLayout)
        catMethodGroupBox.setStyleSheet("border: 0;")
        catMethodGroupBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        # the mode (disabled by default)
        self.catDaddyCheckBox = QCheckBox("Hold Me Daddy")
        self.catDaddyCheckBox.setStyleSheet("padding-left: 10px;")
        self.catDaddyCheckBox.setDisabled(True)


        # EXCEPTIONS line
        # the label
        catExceptLabel = QLabel("3. Add any exceptions:")
        catExceptLabel.setStyleSheet("font-weight: bold;")

        # the buttons
        # connected to the function that fills the edit line
        catExceptFileButton = QPushButton(QIcon(':/icons/prohibition.png'),
                                          "Add file")      
        catExceptFileButton.setStyleSheet("background-color: grey;"
                                          "margin-left: 20px;"
                                          "padding: 4 17;")
        catExceptFileButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        catExceptFileButton.pressed.connect( self.catExceptFile )
        
        
        catExceptDirButton = QPushButton(QIcon(':/icons/prohibition.png'),
                                         "Add folder")      
        catExceptDirButton.setStyleSheet("background-color: grey;"                                         
                                          "margin-left: 20px;"
                                          "padding: 4 10")
        catExceptDirButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        catExceptDirButton.pressed.connect( self.catExceptDirectory )

        # the plain text edit (lineedit allows only one line)
        self.catExceptPlainTextEdit = QPlainTextEdit()
        self.catExceptPlainTextEdit.setStyleSheet("background-color: white;"
                                             "border-radius: 2px;"
                                             "max-height: 75px;"
                                             "min-width: 200px;"
                                             "margin-left: 46px;")


        # DELETE EMPTY DIRS line
        # the label
        catDeleteEmptyDirsLabel = QLabel("4. Delete empty directories?")
        catDeleteEmptyDirsLabel.setStyleSheet("font-weight: bold;")
        catDeleteEmptyDirsLabel.setSizePolicy(QSizePolicy.Fixed,
                                              QSizePolicy.Fixed)


        # the option
        self.catDeleteCheckBox = QCheckBox("Yes")
        self.catDeleteCheckBox.setSizePolicy(QSizePolicy.Fixed,
                                             QSizePolicy.Fixed)
        self.catDeleteCheckBox.setStyleSheet("padding-left: 11px;")
        

        # THE ACTION BUTTONS line
        # categorize button
        catButton = QPushButton(QIcon(':/icons/arrow-out.png'), "CATEGORIZE")
        catButton.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        catButton.setStyleSheet("padding: 5 10; font-weight: bold;"
                                "margin-bottom: 10px;"
                                "background-color: #53A68C;")
        catButton.pressed.connect( self.catCategorize )

        # restore button
        catRestoreButton = QPushButton(QIcon(':/icons/arrow-in.png'), "Restore")
        catRestoreButton.setSizePolicy(QSizePolicy.Maximum,
                                       QSizePolicy.Maximum)
        catRestoreButton.setStyleSheet("padding: 3 6; font-weight: bold;"
                                       "font-size: 12px;" "margin-bottom: 10px;"
                                       "background-color: #713D99;")
        catRestoreButton.pressed.connect( self.catRestore )

        

        # CATEGEORIZE TAB LAYOUT
        catLayout = QVBoxLayout()

        # the description widget 
        catDescriptionWidget = QTabWidget()
        catDescriptionWidget.setTabPosition(QTabWidget.West)
        catDescriptionWidget.addTab(catGenDescriptionWidget, "v")
        catDescriptionWidget.addTab(catBulkDescriptionWidget, "v")
        catDescriptionWidget.addTab(catMirrorDescriptionWidget, "v")
        catDescriptionWidget.addTab(catDaddyDescriptionWidget, "v")
        catDescriptionWidget.addTab(catUntouchablesDescriptionWidget, "v")
        catDescriptionWidget.addTab(catRestoreDescriptionWidget, "v")
        catDescriptionWidget.setSizePolicy(QSizePolicy.Minimum,
                                           QSizePolicy.Minimum)

        # the target dir line widget
        catTargetDirLayout = QHBoxLayout()
        catTargetDirLayout.addWidget(catTargetDirLabel)
        catTargetDirLayout.addWidget(self.catTargetDirLineEdit)
        catTargetDirLayout.addWidget(catBrowseTargetDirButton)

        # the method line widget
        catMethodLayout = QHBoxLayout()
        catMethodLayout.addWidget(catMethodLabel)
        catMethodLayout.addWidget(catMethodGroupBox)
        catMethodLayout.addWidget(self.catDaddyCheckBox)

        # the exceptions widget
        catExceptLayout = QHBoxLayout()
        catExceptAIAreaLayout = QVBoxLayout()
        catExceptAIAreaLayout.addWidget(catExceptLabel)
        catExceptAIAreaLayout.addWidget(catExceptFileButton)
        catExceptAIAreaLayout.addWidget(catExceptDirButton)
        catExceptUserAreaLayout = QVBoxLayout()
        catExceptUserAreaLayout.addWidget(self.catExceptPlainTextEdit)        
        catExceptLayout.addLayout(catExceptAIAreaLayout)
        catExceptLayout.addLayout(catExceptUserAreaLayout)

        # the delete widget
        catDeleteEmptyDirsLayout = QHBoxLayout()
        catDeleteEmptyDirsLayout.addWidget(catDeleteEmptyDirsLabel)
        catDeleteEmptyDirsLayout.addWidget(self.catDeleteCheckBox)
        catDeleteEmptyDirsLayout.setAlignment(Qt.AlignLeft)

        # the main buttons widget
        # grids within a grid
        # use the grid (position and span) to center the main button
        # and right-align the restore button
        catButtonLayout = QGridLayout()
        catCategorizeButtonLayout = QGridLayout()
        catCategorizeButtonLayout.addWidget(catButton, 0, 1)
        catCategorizeButtonLayout.setAlignment(Qt.AlignCenter)
        catRestoreButtonLayout = QGridLayout()
        catRestoreButtonLayout.addWidget(catRestoreButton, 0, 2)
        # right-align the restore button down here
        catRestoreButtonLayout.setAlignment(Qt.AlignRight)
        # center-span the action button down here
        catButtonLayout.addLayout(catCategorizeButtonLayout, 0, 1, 0, 2)
        catButtonLayout.addLayout(catRestoreButtonLayout, 0, 2)

        # add all the widgets to the main categorize layout
        # use a spacer item in-between
        spacerItem = QSpacerItem(500, 10)

        catLayout.addWidget(catDescriptionWidget)
        catLayout.addItem(spacerItem)
        catLayout.addLayout(catTargetDirLayout)
        catLayout.addItem(spacerItem)
        catLayout.addLayout(catMethodLayout)
        catLayout.addItem(spacerItem)
        catLayout.addLayout(catExceptLayout)
        catLayout.addItem(spacerItem)
        catLayout.addLayout(catDeleteEmptyDirsLayout)
        catLayout.addItem(spacerItem)
        catLayout.addLayout(catButtonLayout)
        # set the layout
        catWidget.setLayout(catLayout)
        





        
#-------2ND TAB #COMBINE TAB CONTENT ----------------------------------
        comWidget = QWidget()
        CCCU_tabs.addTab(comWidget, "Combine")
        comWidget.setStyleSheet("background-color: #53A68C;")


        # DESCRIPTION
        # description is provided in form of tabs
        # 1st tab - combine general description
        com_general_description = '''        3CU Combine takes two or \
more folders or drives and combines their content. The destination for the \
combined content can be one of the processed folders or some third-party \
folder altogether.
        3CU Combine uses two methods ("files only" and "everything") and \
one mode ("tree"). Their description follows.'''

        # 1st tab title
        comGenDescriptionTitleLabel = QLabel('I. 3CU Combine')
        comGenDescriptionTitleLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        comGenDescriptionTitleLabel.setStyleSheet("font-weight: bold;"
                                                  "padding-top: 5px;")
        # 1st tab text
        comGenDescriptionTextLabel = QLabel(com_general_description)
        comGenDescriptionTextLabel.setWordWrap(True)
        comGenDescriptionTextLabel.setStyleSheet("padding: 2px;")

        # 1st tab widget
        comGenDescriptionWidget = QWidget()
        catGenDescriptionLayout = QVBoxLayout()
        comGenDescriptionWidget.setLayout(catGenDescriptionLayout)
        catGenDescriptionLayout.addWidget(comGenDescriptionTitleLabel)
        catGenDescriptionLayout.addWidget(comGenDescriptionTextLabel)


        # the next description tabs follow the same structure
        com_files_only_description = '''        The "files only" \
method works like a file extractor. It extracts all the files from \
the processed folders/drives and moves them inside the destination. \
Given its nature, you may even have only one processed directory (even \
the destination directory itself) and 3CU Combine will simply \
"flush" all its files to the "surface" of the destination \
directory (i.e. right inside of it).'''

        comFilesOnlyDescriptionTitleLabel = QLabel('II. The "files only" method')
        comFilesOnlyDescriptionTitleLabel.setStyleSheet("font-weight: bold;"
                                                   "padding-top: 5px;")
        comFilesOnlyDescriptionTitleLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        comFilesOnlyDescriptionTextLabel = QLabel(com_files_only_description)
        comFilesOnlyDescriptionTextLabel.setWordWrap(True)
        comFilesOnlyDescriptionTextLabel.setStyleSheet("padding: 2px;")

        comFilesOnlyDescriptionWidget = QWidget()
        comFilesOnlyDescriptionLayout = QVBoxLayout()
        comFilesOnlyDescriptionLayout.addWidget(comFilesOnlyDescriptionTitleLabel)
        comFilesOnlyDescriptionLayout.addWidget(comFilesOnlyDescriptionTextLabel)
        comFilesOnlyDescriptionWidget.setLayout(comFilesOnlyDescriptionLayout)

        
        com_everything_description = '''        The "everything" method \
works as if you'd open a folder, copy its files and folders, and paste \
them in some other - destination - folder. This is exactly what this \
method does - it combines the entire content of the processed folders or \
drives in the destination. Again, the destination can also be among the \
processed directories.
        Duplicate-name issues between folders are solved Windows-style \
(adding (2), (3), (4), etc.).'''

        comEverythingDescriptionTitleLabel = QLabel('III. The "everything" method')
        comEverythingDescriptionTitleLabel.setStyleSheet("font-weight: bold;"
                                                     "padding-top: 5px;")
        comEverythingDescriptionTitleLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        comEverythingDescriptionTextLabel = QLabel(com_everything_description)
        comEverythingDescriptionTextLabel.setWordWrap(True)
        comEverythingDescriptionTextLabel.setStyleSheet("padding: 2px;")

        comEverythingDescriptionWidget = QWidget()
        comEverythingDescriptionLayout = QVBoxLayout()
        comEverythingDescriptionLayout.addWidget(comEverythingDescriptionTitleLabel)
        comEverythingDescriptionLayout.addWidget(comEverythingDescriptionTextLabel)
        comEverythingDescriptionWidget.setLayout(comEverythingDescriptionLayout)

        
        com_tree_description = '''        The "tree" mode is a special \
combining mode of the "everything" method. It still combines the entire \
content of the processed directories, but it doesn't simply copy-paste it. \
First, it scans the folder structures of all the processed directories, \
then, based on that, it builds a tree-like folder structure inside the \
destination in such a way that the subfolders with similar names from \
different processed directories don't cause duplicate-name issues, but \
actually overlap.
        Basically, the original folder structure \
of each of the processed directories is preserved and can be followed \
inside the destination folder, and the latter will "grow twigs and leaves" \
in such a way as to accommodate even the farthest "branches" in a harmonious \
way, without any duplicate-name issues among the folders.'''

        comTreeDescriptionTitleLabel = QLabel('IV. The "tree" mode')
        comTreeDescriptionTitleLabel.setStyleSheet("font-weight: bold;"
                                                    "padding-top: 5px;")
        comTreeDescriptionTitleLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        comTreeDescriptionTextLabel = QLabel(com_tree_description)
        comTreeDescriptionTextLabel.setWordWrap(True)
        comTreeDescriptionTextLabel.setStyleSheet("padding: 2px;")

        comTreeDescriptionWidget = QWidget()
        comTreeDescriptionLayout = QVBoxLayout()
        comTreeDescriptionLayout.addWidget(comTreeDescriptionTitleLabel)
        comTreeDescriptionLayout.addWidget(comTreeDescriptionTextLabel)
        comTreeDescriptionWidget.setLayout(comTreeDescriptionLayout)

        
        com_untouchables_description = '''        3CU Combine will not affect \
any hidden files \
or folders on your computer. This type of files and folders are usually \
essential, either to the user or to the system itself, so the \
program won't take the risk of moving them around. 
        Aditionally, 3CU Combine gives you the possibility to exclude \
from the combining process any files or folders existing inside the \
target folder or drive. Just add these files and/or folders in the \
"Exceptions" section and they won't be touched.

        Now, 3CU does generally check whether files and/or folders have \
the appropriate permissions to perform the operations involved, however \
most probably these aren't all accounted for. Even though the code uses \
try-except statements in abundance in order to deal with potential errors, \
things could go horribly wrong if, say, you start using 3CU on a system \
folder riddled with limited-access content. So, play it safe, use 3CU on \
normal user content, and it should do the trick.'''

        comUntouchablesDescriptionTitleLabel = QLabel('V. The Untouchables')
        comUntouchablesDescriptionTitleLabel.setStyleSheet("font-weight: bold;"
                                                    "padding-top: 5px;")
        comUntouchablesDescriptionTitleLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        comUntouchablesDescriptionTextLabel = QLabel(com_untouchables_description)
        comUntouchablesDescriptionTextLabel.setWordWrap(True)
        comUntouchablesDescriptionTextLabel.setStyleSheet("padding: 2px;")

        comUntouchablesDescriptionWidget = QWidget()
        comUntouchablesDescriptionLayout = QVBoxLayout()
        comUntouchablesDescriptionLayout.addWidget(comUntouchablesDescriptionTitleLabel)
        comUntouchablesDescriptionLayout.addWidget(comUntouchablesDescriptionTextLabel)
        comUntouchablesDescriptionWidget.setLayout(comUntouchablesDescriptionLayout)


        com_restore_description = '''        After processing, 3CU Combine \
offers you the possibility to restore all your folders to the \
state they were before combining.
        However, if you want to be able to restore, DON'T CLOSE THE PROGRAM \
SESSION AFTER COMBINING! Run the process, check the result, and, \
if you're not satisfied, roll back the changes.
        For this feature to work correctly, in the meantime, don't rename, \
delete or move around any of the affected files and folders.'''

        comRestoreDescriptionTitleLabel = QLabel('VI. Restoring')
        comRestoreDescriptionTitleLabel.setStyleSheet("font-weight: bold;"
                                                    "padding-top: 5px;")
        comRestoreDescriptionTitleLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        comRestoreDescriptionTextLabel = QLabel(com_restore_description)
        comRestoreDescriptionTextLabel.setWordWrap(True)
        comRestoreDescriptionTextLabel.setStyleSheet("padding: 2px;")

        comRestoreDescriptionWidget = QWidget()
        comRestoreDescriptionLayout = QVBoxLayout()
        comRestoreDescriptionLayout.addWidget(comRestoreDescriptionTitleLabel)
        comRestoreDescriptionLayout.addWidget(comRestoreDescriptionTextLabel)
        comRestoreDescriptionWidget.setLayout(comRestoreDescriptionLayout)
        # END OF 2ND TAB DESCRIPTION


        # @ND TAB USER INPUT AREA
        # PROCESSED DIRECTORIES line
        # the label
        comProcessedDirsLabel = QLabel("1. Folders to combine:")
        comProcessedDirsLabel.setStyleSheet("font-weight: bold;")        

        # the button (connect to fill editline function)
        comProcessedDirsButton = QPushButton(QIcon(':/icons/folder-horizontal.png'),
                                         "Browse")      
        comProcessedDirsButton.setStyleSheet("background-color: grey;"                                         
                                          "margin-left: 25px;"
                                          "padding: 3 10")
        comProcessedDirsButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        comProcessedDirsButton.pressed.connect( self.comAddProcessedDir )

        # the plain text edit (lineedit allows only one line)
        # read only (for valid URIs)
        self.comProcessedDirsPlainTextEdit = QPlainTextEdit()
        self.comProcessedDirsPlainTextEdit.setStyleSheet("background-color: white;"
                                             "border-radius: 2px;"
                                             "max-height: 50px;"
                                             "min-width: 200px;"
                                             "margin-left: 46px;")
        self.comProcessedDirsPlainTextEdit.setReadOnly(True)


        # METHOD line
        # the label
        comMethodLabel = QLabel("2. Select the method:")
        comMethodLabel.setStyleSheet("font-weight: bold;")
        comMethodLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)


        # the methods
        # connects the method buttons to the "enable tree mode" function
        self.comFilesOnlyRadioButton = QRadioButton("Files only")
        self.comFilesOnlyRadioButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.comFilesOnlyRadioButton.setStyleSheet("padding-left: 40px;")
        self.comFilesOnlyRadioButton.clicked.connect ( self.comEnableTreeMode )
        
        self.comEverythingRadioButton = QRadioButton("Everything")
        self.comEverythingRadioButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.comEverythingRadioButton.setStyleSheet("padding-left: 50px;")
        self.comEverythingRadioButton.clicked.connect ( self.comEnableTreeMode )

        # group the method radio button
        comMethodGroupBox = QGroupBox()
        comMethodRadioLayout = QHBoxLayout()
        comMethodRadioLayout.addWidget(self.comFilesOnlyRadioButton)
        comMethodRadioLayout.addWidget(self.comEverythingRadioButton)
        comMethodGroupBox.setLayout(comMethodRadioLayout)
        comMethodGroupBox.setStyleSheet("border: 0;")
        comMethodGroupBox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        # the mode (disabled by default)
        self.comTreeCheckBox = QCheckBox("Tree")
        self.comTreeCheckBox.setStyleSheet("padding-left: 5px;")
        self.comTreeCheckBox.setDisabled(True)

        
        # DESTINATION DIRECTORY line
        # the label
        comDestinationDirLabel = QLabel("3. Choose the destination:")
        comDestinationDirLabel.setStyleSheet("font-weight: bold;")

        # the line edit (readonly)
        self.comDestinationDirLineEdit = QLineEdit()
        self.comDestinationDirLineEdit.setReadOnly(True)
        self.comDestinationDirLineEdit.setStyleSheet("background-color: white;"
                                                   "border-radius: 2px;"
                                                   "height: 20px;"
                                                     "margin-left: 24px;")
        # the button
        # icons credit: https://github.com/yusukekamiyamane/fugue-icons
        comBrowseDestinationDirButton = QPushButton(
            QIcon(':/icons/folder-horizontal.png'),"Browse")      
        comBrowseDestinationDirButton.setStyleSheet("background-color: grey;")
        comBrowseDestinationDirButton.pressed.connect( self.comChooseDestinationDir )


        # EXCEPTIONS line
        # the label
        comExceptLabel = QLabel("4. Add any exceptions:")
        comExceptLabel.setStyleSheet("font-weight: bold;")

        # the buttons (connected to fill edit line function)
        comExceptFileButton = QPushButton(QIcon(':/icons/prohibition.png'),
                                          "Files")      
        comExceptFileButton.setStyleSheet("background-color: grey;"
                                          "margin-left: 0px;"
                                          "padding: 5 15;")
        comExceptFileButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        comExceptFileButton.pressed.connect( self.comExceptFile )
        
        
        comExceptDirButton = QPushButton(QIcon(':/icons/prohibition.png'),
                                         "Folders")      
        comExceptDirButton.setStyleSheet("background-color: grey;"
                                          "padding: 5 5;")
        comExceptDirButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        comExceptDirButton.pressed.connect( self.comExceptDirectory )

        # the plain text edit (lineedit allows only one line)
        self.comExceptPlainTextEdit = QPlainTextEdit()
        self.comExceptPlainTextEdit.setStyleSheet("background-color: white;"
                                             "border-radius: 2px;"
                                             "max-height: 50px;"
                                             "min-width: 200px;"
                                                  "margin-left: 23px;")

        # DELETE EMPTY DIRS line
        # the label
        comDeleteEmptyDirsLabel = QLabel("5. Delete empty directories?")
        comDeleteEmptyDirsLabel.setStyleSheet("font-weight: bold;")
        comDeleteEmptyDirsLabel.setSizePolicy(QSizePolicy.Fixed,
                                              QSizePolicy.Fixed)


        # the option
        self.comDeleteCheckBox = QCheckBox("Yes")
        self.comDeleteCheckBox.setSizePolicy(QSizePolicy.Fixed,
                                             QSizePolicy.Fixed)
        self.comDeleteCheckBox.setStyleSheet("padding-left: 9px;")
        

        # THE ACTION BUTTONS line
        # combine button
        comButton = QPushButton(QIcon(':/icons/arrow-join.png'), "COMBINE")
        comButton.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        comButton.setStyleSheet("padding: 5 10; font-weight: bold;"
                                "margin-bottom: 10px;"
                                "background-color: #713D99;")
        comButton.pressed.connect( self.comCombine )

        

        # restore button
        comRestoreButton = QPushButton(QIcon(':/icons/arrow-split.png'), "Restore")
        comRestoreButton.setSizePolicy(QSizePolicy.Maximum,
                                       QSizePolicy.Maximum)
        comRestoreButton.setStyleSheet("padding: 3 6; font-weight: bold;"
                                       "font-size: 12px;" "margin-bottom: 10px;"
                                       "background-color: #99803D;")
        comRestoreButton.pressed.connect( self.comRestore )


        # COMBINE TAB LAYOUT 
        comLayout = QVBoxLayout()

        # the description widget
        comDescriptionWidget = QTabWidget()
        comDescriptionWidget.setTabPosition(QTabWidget.West)
        comDescriptionWidget.addTab(comGenDescriptionWidget, "v")
        comDescriptionWidget.addTab(comFilesOnlyDescriptionWidget, "v")
        comDescriptionWidget.addTab(comEverythingDescriptionWidget, "v")
        comDescriptionWidget.addTab(comTreeDescriptionWidget, "v")
        comDescriptionWidget.addTab(comUntouchablesDescriptionWidget, "v")
        comDescriptionWidget.addTab(comRestoreDescriptionWidget, "v")
        comDescriptionWidget.setSizePolicy(QSizePolicy.Minimum,
                                           QSizePolicy.Minimum)

        # the processed dirs widget
        comProcessedDirsLayout = QHBoxLayout()
        comProcessedDirsAIAreaLayout = QVBoxLayout()
        comProcessedDirsAIAreaLayout.addWidget(comProcessedDirsLabel)
        comProcessedDirsAIAreaLayout.addWidget(comProcessedDirsButton)
        comProcessedDirsUserAreaLayout = QVBoxLayout()
        comProcessedDirsUserAreaLayout.addWidget(self.comProcessedDirsPlainTextEdit)        
        comProcessedDirsLayout.addLayout(comProcessedDirsAIAreaLayout)
        comProcessedDirsLayout.addLayout(comProcessedDirsUserAreaLayout)

        # the method line widget
        comMethodLayout = QHBoxLayout()
        comMethodLayout.addWidget(comMethodLabel)
        comMethodLayout.addWidget(comMethodGroupBox)
        comMethodLayout.addWidget(self.comTreeCheckBox)

        # the destination dir line widget
        comDestinationDirLayout = QHBoxLayout()
        comDestinationDirLayout.addWidget(comDestinationDirLabel)
        comDestinationDirLayout.addWidget(self.comDestinationDirLineEdit)
        comDestinationDirLayout.addWidget(comBrowseDestinationDirButton)

        # the exceptions widget
        comExceptLayout = QHBoxLayout()
        comExceptAIAreaLayout = QVBoxLayout()
        comExceptAIAreaLayout.addWidget(comExceptLabel)
        comExceptButtonsLayout = QHBoxLayout()
        comExceptButtonsLayout.addWidget(comExceptFileButton)
        comExceptButtonsLayout.addWidget(comExceptDirButton)
        comExceptAIAreaLayout.addLayout(comExceptButtonsLayout)
        comExceptUserAreaLayout = QVBoxLayout()
        comExceptUserAreaLayout.addWidget(self.comExceptPlainTextEdit)        
        comExceptLayout.addLayout(comExceptAIAreaLayout)
        comExceptLayout.addLayout(comExceptUserAreaLayout)

        # the delete widget
        comDeleteEmptyDirsLayout = QHBoxLayout()
        comDeleteEmptyDirsLayout.addWidget(comDeleteEmptyDirsLabel)
        comDeleteEmptyDirsLayout.addWidget(self.comDeleteCheckBox)
        comDeleteEmptyDirsLayout.setAlignment(Qt.AlignLeft)

        # the main buttons widget
        # grids within a grid
        # use the grid (position and span) to center the action button
        # and right-align the restore button
        comButtonLayout = QGridLayout()
        comCombineButtonLayout = QGridLayout()
        comCombineButtonLayout.addWidget(comButton, 0, 1)
        comCombineButtonLayout.setAlignment(Qt.AlignCenter)
        comRestoreButtonLayout = QGridLayout()
        comRestoreButtonLayout.addWidget(comRestoreButton, 0, 2)
        # right-align the restore button here
        comRestoreButtonLayout.setAlignment(Qt.AlignRight)
        # center-span the action button here
        comButtonLayout.addLayout(comCombineButtonLayout, 0, 1, 0, 2)
        comButtonLayout.addLayout(comRestoreButtonLayout, 0, 2)

        # add all the widgets to the main categorize layout
        # use a spacer item in-between
        spacerItem1 = QSpacerItem(500, 5)

        comLayout.addWidget(comDescriptionWidget)
        comLayout.addItem(spacerItem1)
        comLayout.addLayout(comProcessedDirsLayout)
        comLayout.addItem(spacerItem1)
        comLayout.addLayout(comMethodLayout)
        comLayout.addItem(spacerItem1)
        comLayout.addLayout(comDestinationDirLayout)
        comLayout.addItem(spacerItem1)
        comLayout.addLayout(comExceptLayout)
        comLayout.addItem(spacerItem1)
        comLayout.addLayout(comDeleteEmptyDirsLayout)
        comLayout.addItem(spacerItem1)
        comLayout.addLayout(comButtonLayout)
        # set the layout
        comWidget.setLayout(comLayout)        
        
        
        
#-------3RD TAB CLEANUP CONTENT -----------------------------------------
        cuWidget = QWidget()
        CCCU_tabs.addTab(cuWidget, "Clean Up")
        cuWidget.setStyleSheet("background-color: #713D99;")


        # DESCRIPTION
        # description is provided in form of tabs
        # 1st tab - categorize general description
        cu_general_description = '''        3CU Clean Up is a folder/drive \
sanitizing tool with a three-way action:
            - it removes all the empty files and folders from the target;
            - it removes all the duplicate files from the target;
            - it removes all the redundant folders from the target.

        You can choose what action to perform. All three are described in the \
following panels.'''

        # 1st tab title
        cuGenDescriptionTitleLabel = QLabel('I. 3CU Clean Up')
        cuGenDescriptionTitleLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        cuGenDescriptionTitleLabel.setStyleSheet("font-weight: bold;"
                                                  "padding-top: 5px;")
        # 1st tab text
        cuGenDescriptionTextLabel = QLabel(cu_general_description)
        cuGenDescriptionTextLabel.setWordWrap(True)
        cuGenDescriptionTextLabel.setStyleSheet("padding: 2px;")

        # 1st tab widget
        cuGenDescriptionWidget = QWidget()
        cuGenDescriptionLayout = QVBoxLayout()
        cuGenDescriptionWidget.setLayout(cuGenDescriptionLayout)
        cuGenDescriptionLayout.addWidget(cuGenDescriptionTitleLabel)
        cuGenDescriptionLayout.addWidget(cuGenDescriptionTextLabel)


        # the next description tabs follow the same structure
        cu_empty_description = '''        Simply enough, 3CU Clean Up will \
check the target directory for empty files and folders and will delete them.'''

        cuEmptyDescriptionTitleLabel = QLabel('II. Removing empty files and folders')
        cuEmptyDescriptionTitleLabel.setStyleSheet("font-weight: bold;"
                                                   "padding-top: 5px;")
        cuEmptyDescriptionTitleLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        cuEmptyDescriptionTextLabel = QLabel(cu_empty_description)
        cuEmptyDescriptionTextLabel.setWordWrap(True)
        cuEmptyDescriptionTextLabel.setStyleSheet("padding: 2px;")

        cuEmptyDescriptionWidget = QWidget()
        cuEmptyDescriptionLayout = QVBoxLayout()
        cuEmptyDescriptionLayout.addWidget(cuEmptyDescriptionTitleLabel)
        cuEmptyDescriptionLayout.addWidget(cuEmptyDescriptionTextLabel)
        cuEmptyDescriptionWidget.setLayout(cuEmptyDescriptionLayout)


        cu_duplicate_description = '''        3CU Clean Up will check for \
duplicate files in the target folder or drive and delete all of them.
        Duplicate refers to the actual digital content of the file, \
not its name (ex. two documents with the exact same text are duplicates, no \
matter the name; or a picture - storing it a second time under a different \
name gives a duplicate, so 3CU Clean Up will remove one of them). '''

        cuDuplicateDescriptionTitleLabel = QLabel('III. Removing duplicate files')
        cuDuplicateDescriptionTitleLabel.setStyleSheet("font-weight: bold;"
                                                     "padding-top: 5px;")
        cuDuplicateDescriptionTitleLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        cuDuplicateDescriptionTextLabel = QLabel(cu_duplicate_description)
        cuDuplicateDescriptionTextLabel.setWordWrap(True)
        cuDuplicateDescriptionTextLabel.setStyleSheet("padding: 2px;")

        cuDuplicateDescriptionWidget = QWidget()
        cuDuplicateDescriptionLayout = QVBoxLayout()
        cuDuplicateDescriptionLayout.addWidget(cuDuplicateDescriptionTitleLabel)
        cuDuplicateDescriptionLayout.addWidget(cuDuplicateDescriptionTextLabel)
        cuDuplicateDescriptionWidget.setLayout(cuDuplicateDescriptionLayout)


        cu_redundant_description = '''        Finally, 3CU Clean Up can \
remove redundant folders.
        What is a redundant folder in this case? Well, suppose we have \
the target directory "folder1". We open it and inside we find only the \
directory "folder2". We open "folder2" and inside we find "file1", \
"file2", and "file3". Well, in this case, "folder2" is a redundant folder; \
basically, a waste of a click. The files "file1", "file2", and "file3" \
could have easily been located directly inside "folder1", without the need \
for "folder2" at all. So 3CU Clean Up takes the content ("file1", "file2", \
and "file3") of the redundant folder ("folder2"), moves it up one step in \
the folder hierarchy (so they are now located in "folder1"), and then \
deletes the redundant folder ("folder2").
        Of course, if there's a chain of these redundant folders, 3CU \
Clean Up eliminates all the redundant links, bringing up the content as \
close as possible to the target directory.'''

        cuRedundantDescriptionTitleLabel = QLabel('IV. Removing redundant folders')
        cuRedundantDescriptionTitleLabel.setStyleSheet("font-weight: bold;"
                                                    "padding-top: 5px;")
        cuRedundantDescriptionTitleLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        cuRedundantDescriptionTextLabel = QLabel(cu_redundant_description)
        cuRedundantDescriptionTextLabel.setWordWrap(True)
        cuRedundantDescriptionTextLabel.setStyleSheet("padding: 2px;")

        cuRedundantDescriptionWidget = QWidget()
        cuRedundantDescriptionLayout = QVBoxLayout()
        cuRedundantDescriptionLayout.addWidget(cuRedundantDescriptionTitleLabel)
        cuRedundantDescriptionLayout.addWidget(cuRedundantDescriptionTextLabel)
        cuRedundantDescriptionWidget.setLayout(cuRedundantDescriptionLayout)
        

        cu_untouchables_description = '''        3CU Clean Up will not affect \
any hidden files \
or folders on your computer. This type of files and folders are usually \
essential, either to the user or to the system itself, so the \
program won't take the risk of moving them around. 
        Aditionally, 3CU Clean Up gives you the possibility to exclude \
from the cleaning process any files or folders existing inside the \
target folder or drive. Just add these files and/or folders in the \
"Exceptions" section and they won't be touched.

        Now, 3CU does generally check whether files and/or folders have \
the appropriate permissions to perform the operations involved, however \
most probably these aren't all accounted for. Even though the code uses \
try-except statements in abundance in order to deal with potential errors, \
things could go horribly wrong if, say, you start using 3CU on a system \
folder riddled with limited-access content. So, play it safe, use 3CU on \
normal user content, and it should do the trick.'''

        cuUntouchablesDescriptionTitleLabel = QLabel('V. The Untouchables')
        cuUntouchablesDescriptionTitleLabel.setStyleSheet("font-weight: bold;"
                                                    "padding-top: 5px;")
        cuUntouchablesDescriptionTitleLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        cuUntouchablesDescriptionTextLabel = QLabel(cu_untouchables_description)
        cuUntouchablesDescriptionTextLabel.setWordWrap(True)
        cuUntouchablesDescriptionTextLabel.setStyleSheet("padding: 2px;")

        cuUntouchablesDescriptionWidget = QWidget()
        cuUntouchablesDescriptionLayout = QVBoxLayout()
        cuUntouchablesDescriptionLayout.addWidget(cuUntouchablesDescriptionTitleLabel)
        cuUntouchablesDescriptionLayout.addWidget(cuUntouchablesDescriptionTextLabel)
        cuUntouchablesDescriptionWidget.setLayout(cuUntouchablesDescriptionLayout)


        cu_restore_description = '''        After processing, 3CU Clean Up \
offers you the possibility to restore the target folder or drive to the \
state it was before cleaning.
        However, if you want to be able to restore, DON'T CLOSE THE PROGRAM \
SESSION AFTER CATEGORIZING and DON'T EMPTY THE RECYCLE BIN! Run the cleanup, \
check the result, and, if you're not satisfied, roll back the changes.
        For this feature to work correctly, in the meantime, don't rename, \
delete or move around any of the affected files and folders.'''

        cuRestoreDescriptionTitleLabel = QLabel('VI. Restoring')
        cuRestoreDescriptionTitleLabel.setStyleSheet("font-weight: bold;"
                                                    "padding-top: 5px;")
        cuRestoreDescriptionTitleLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        cuRestoreDescriptionTextLabel = QLabel(cu_restore_description)
        cuRestoreDescriptionTextLabel.setWordWrap(True)
        cuRestoreDescriptionTextLabel.setStyleSheet("padding: 2px;")

        cuRestoreDescriptionWidget = QWidget()
        cuRestoreDescriptionLayout = QVBoxLayout()
        cuRestoreDescriptionLayout.addWidget(cuRestoreDescriptionTitleLabel)
        cuRestoreDescriptionLayout.addWidget(cuRestoreDescriptionTextLabel)
        cuRestoreDescriptionWidget.setLayout(cuRestoreDescriptionLayout)
        # END OF 3RD TAB DESCRIPTION


        # 3RD TAB USER INPUT AREA
        # TARGET DIRECTORY line
        # the label
        cuTargetDirLabel = QLabel("1. Choose the target directory:")
        cuTargetDirLabel.setStyleSheet("font-weight: bold;")

        # the line edit
        self.cuTargetDirLineEdit = QLineEdit()
        self.cuTargetDirLineEdit.setReadOnly(True)
        self.cuTargetDirLineEdit.setStyleSheet("background-color: white;"
                                                   "border-radius: 2px;"
                                                   "height: 20px;"
                                               "margin-left: 10px;")
        # the button
        # icons credit: https://github.com/yusukekamiyamane/fugue-icons
        cuBrowseTargetDirButton = QPushButton(
            QIcon(':/icons/folder-horizontal.png'),"Browse")      
        cuBrowseTargetDirButton.setStyleSheet("background-color: grey;")
        cuBrowseTargetDirButton.pressed.connect( self.cuChooseTargetDir )


        # DELETE EMPTY FILES AND DIRS line
        # the label
        cuDeleteEmptyLabel = QLabel("2. Delete empty files & folders?")
        cuDeleteEmptyLabel.setStyleSheet("font-weight: bold;")
        cuDeleteEmptyLabel.setSizePolicy(QSizePolicy.Fixed,
                                              QSizePolicy.Fixed)

        # the option
        self.cuDeleteEmptyCheckBox = QCheckBox("Yes")
        self.cuDeleteEmptyCheckBox.setSizePolicy(QSizePolicy.Fixed,
                                             QSizePolicy.Fixed)
        self.cuDeleteEmptyCheckBox.setStyleSheet("padding-left: 7px;")
        

        # DELETE DUPLICATE FILES line
        # the label
        cuDeleteDuplicateLabel = QLabel("3. Delete duplicate files?")
        cuDeleteDuplicateLabel.setStyleSheet("font-weight: bold;")
        cuDeleteDuplicateLabel.setSizePolicy(QSizePolicy.Fixed,
                                              QSizePolicy.Fixed)

        # the option
        self.cuDeleteDuplicateCheckBox = QCheckBox("Yes")
        self.cuDeleteDuplicateCheckBox.setSizePolicy(QSizePolicy.Fixed,
                                             QSizePolicy.Fixed)
        self.cuDeleteDuplicateCheckBox.setStyleSheet("padding-left: 46px;")

        
        # DELETE REDUNDANT DIRS line
        # the label
        cuDeleteRedundantLabel = QLabel("4. Delete redundant folders?")
        cuDeleteRedundantLabel.setStyleSheet("font-weight: bold;")
        cuDeleteRedundantLabel.setSizePolicy(QSizePolicy.Fixed,
                                              QSizePolicy.Fixed)

        # the option
        self.cuDeleteRedundantCheckBox = QCheckBox("Yes")
        self.cuDeleteRedundantCheckBox.setSizePolicy(QSizePolicy.Fixed,
                                             QSizePolicy.Fixed)
        self.cuDeleteRedundantCheckBox.setStyleSheet("padding-left: 23px;")


        # EXCEPTIONS line
        # the label
        cuExceptLabel = QLabel("5. Add any exceptions:")
        cuExceptLabel.setStyleSheet("font-weight: bold;")

        # the buttons
        cuExceptFileButton = QPushButton(QIcon(':/icons/prohibition.png'),
                                          "Add file")      
        cuExceptFileButton.setStyleSheet("background-color: grey;"
                                          "margin-left: 30px;"
                                          "padding: 4 17;")
        cuExceptFileButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        cuExceptFileButton.pressed.connect( self.cuExceptFile )
        
        
        cuExceptDirButton = QPushButton(QIcon(':/icons/prohibition.png'),
                                         "Add folder")      
        cuExceptDirButton.setStyleSheet("background-color: grey;"                                         
                                          "margin-left: 30px;"
                                          "padding: 4 10")
        cuExceptDirButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        cuExceptDirButton.pressed.connect( self.cuExceptDirectory )

        # the plain text edit (lineedit allows only one line)
        self.cuExceptPlainTextEdit = QPlainTextEdit()
        self.cuExceptPlainTextEdit.setStyleSheet("background-color: white;"
                                             "border-radius: 2px;"
                                             "max-height: 75px;"
                                             "min-width: 200px;"
                                             "margin-left: 54px;")


        # THE ACTION BUTTONS line
        # clean up button
        cuButton = QPushButton(QIcon(':/icons/broom.png'), "CLEAN UP")
        cuButton.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        cuButton.setStyleSheet("padding: 5 10; font-weight: bold;"
                                "margin-bottom: 10px;"
                                "background-color: #99803D;")
        cuButton.pressed.connect( self.cuCleanUp )
        

        # restore button
        cuRestoreButton = QPushButton(QIcon(':/icons/arrow-retweet.png'), "Restore")
        cuRestoreButton.setSizePolicy(QSizePolicy.Maximum,
                                       QSizePolicy.Maximum)
        cuRestoreButton.setStyleSheet("padding: 3 6; font-weight: bold;"
                                       "font-size: 12px;" "margin-bottom: 10px;"
                                       "background-color: #53A68C;")
        cuRestoreButton.pressed.connect( self.cuRestore )
        

        # 3RD TAB LAYOUT
        cuLayout = QVBoxLayout()

        # the description widget
        cuDescriptionWidget = QTabWidget()
        cuDescriptionWidget.setTabPosition(QTabWidget.West)
        cuDescriptionWidget.addTab(cuGenDescriptionWidget, "v")
        cuDescriptionWidget.addTab(cuEmptyDescriptionWidget, "v")
        cuDescriptionWidget.addTab(cuDuplicateDescriptionWidget, "v")
        cuDescriptionWidget.addTab(cuRedundantDescriptionWidget, "v")
        cuDescriptionWidget.addTab(cuUntouchablesDescriptionWidget, "v")
        cuDescriptionWidget.addTab(cuRestoreDescriptionWidget, "v")
        cuDescriptionWidget.setSizePolicy(QSizePolicy.Minimum,
                                           QSizePolicy.Minimum)

        # the target dir line widget
        cuTargetDirLayout = QHBoxLayout()
        cuTargetDirLayout.addWidget(cuTargetDirLabel)
        cuTargetDirLayout.addWidget(self.cuTargetDirLineEdit)
        cuTargetDirLayout.addWidget(cuBrowseTargetDirButton)

        # delete empty files and folders widget
        cuDeleteEmptyLayout = QHBoxLayout()
        cuDeleteEmptyLayout.addWidget(cuDeleteEmptyLabel)
        cuDeleteEmptyLayout.addWidget(self.cuDeleteEmptyCheckBox)
        cuDeleteEmptyLayout.setAlignment(Qt.AlignLeft)

        # delete duplicate files widget
        cuDeleteDuplicateLayout = QHBoxLayout()
        cuDeleteDuplicateLayout.addWidget(cuDeleteDuplicateLabel)
        cuDeleteDuplicateLayout.addWidget(self.cuDeleteDuplicateCheckBox)
        cuDeleteDuplicateLayout.setAlignment(Qt.AlignLeft)

        # delete redundant folders widget
        cuDeleteRedundantLayout = QHBoxLayout()
        cuDeleteRedundantLayout.addWidget(cuDeleteRedundantLabel)
        cuDeleteRedundantLayout.addWidget(self.cuDeleteRedundantCheckBox)
        cuDeleteRedundantLayout.setAlignment(Qt.AlignLeft)

        # the exceptions widget
        cuExceptLayout = QHBoxLayout()
        cuExceptAIAreaLayout = QVBoxLayout()
        cuExceptAIAreaLayout.addWidget(cuExceptLabel)
        cuExceptAIAreaLayout.addWidget(cuExceptFileButton)
        cuExceptAIAreaLayout.addWidget(cuExceptDirButton)
        cuExceptUserAreaLayout = QVBoxLayout()
        cuExceptUserAreaLayout.addWidget(self.cuExceptPlainTextEdit)        
        cuExceptLayout.addLayout(cuExceptAIAreaLayout)
        cuExceptLayout.addLayout(cuExceptUserAreaLayout)

        # the main buttons widget
        # grids within a grid
        # use the grid (position and span) to center the action button
        # and right-align the restore button
        cuButtonLayout = QGridLayout()
        cuCleanUpButtonLayout = QGridLayout()
        cuCleanUpButtonLayout.addWidget(cuButton, 0, 1)
        cuCleanUpButtonLayout.setAlignment(Qt.AlignCenter)
        cuRestoreButtonLayout = QGridLayout()
        cuRestoreButtonLayout.addWidget(cuRestoreButton, 0, 2)
        # right-align the restore button here
        cuRestoreButtonLayout.setAlignment(Qt.AlignRight)
        # center-span the action button here
        cuButtonLayout.addLayout(cuCleanUpButtonLayout, 0, 1, 0, 2)
        cuButtonLayout.addLayout(cuRestoreButtonLayout, 0, 2)

        # add all the widgets to the main categorize layout
        # use a spacer item in-between
        spacerItem = QSpacerItem(500, 10)

        cuLayout.addWidget(cuDescriptionWidget)
        cuLayout.addItem(spacerItem)
        cuLayout.addLayout(cuTargetDirLayout)
        cuLayout.addItem(spacerItem)
        cuLayout.addLayout(cuDeleteEmptyLayout)
        cuLayout.addItem(spacerItem)
        cuLayout.addLayout(cuDeleteDuplicateLayout)
        cuLayout.addItem(spacerItem)
        cuLayout.addLayout(cuDeleteRedundantLayout)
        cuLayout.addItem(spacerItem)
        cuLayout.addLayout(cuExceptLayout)
        cuLayout.addItem(spacerItem)
        cuLayout.addLayout(cuButtonLayout)
        # set the layout
        cuWidget.setLayout(cuLayout)
        





#----------FUNCTION SECTION--------------------------------------------

    # 1ST TAB - CATEGORIZE FUNCTIONS
    
    # upon pressing the browse target dir button
    # fills the lineedit with the chosen folder's URI
    def catChooseTargetDir(self):

        # special folders-only flag    
        foldername = QFileDialog.getExistingDirectory(self, "Choose Directory",
                                                      "", QFileDialog.ShowDirsOnly)

        self.catTargetDirLineEdit.setText(foldername)


    # enables the daddy mode upon checking the bulk method
    # disables it upon checking the mirror method
    def catEnableDaddyMode(self):
        if self.catBulkRadioButton.isChecked():
            self.catDaddyCheckBox.setEnabled(True)
        else:
            self.catDaddyCheckBox.setDisabled(True)


    # upon pressing the browse exception file button
    # appends the text edit with the chosen file's URI
    def catExceptFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Choose File", "")

        self.catExceptPlainTextEdit.appendPlainText(filename)


    # upon pressing the browse exception folder button
    # appends the text edit with the chosen folder's URI
    def catExceptDirectory(self):
        foldername = QFileDialog.getExistingDirectory(self, "Choose Directory",
                                                      "", QFileDialog.ShowDirsOnly)

        self.catExceptPlainTextEdit.appendPlainText(foldername)


    # the main action function
    def catCategorize(self):


        # warn and return if no target provided
        if self.catTargetDirLineEdit.text() == "":

            QMessageBox.warning(self, "Categorize Error",
                                "You must choose a target directory.")
            return


        # make sure the target still exists when starting
        if not os.path.isdir(self.catTargetDirLineEdit.text()):
            QMessageBox.warning(self, "Categorize Error",
                                "You must choose a valid target directory.")
            return

            
        # warn and return if no method selected
        if not self.catBulkRadioButton.isChecked() and \
           not self.catMirrorRadioButton.isChecked():

            QMessageBox.warning(self, "Categorize Error",
                                "You must choose a categorizing method.")
            return


        # warn to close any files/folders before processing
        QMessageBox.warning(self, "3CU Categorize",
            "Make sure to close any files and folders "
            "from the target directory or drive.")


        # store the target path
        # the GUI dialog window returns the folder URI
        # we operate with paths, so we convert
        categorize_target = os.path.abspath(self.catTargetDirLineEdit.text())


        # store the method and the mode
        if self.catBulkRadioButton.isChecked():
            categorize_method = "bulk"

            if self.catDaddyCheckBox.isChecked():
                categorize_daddy_mode = True
            else:
                categorize_daddy_mode = False
        elif self.catMirrorRadioButton.isChecked():
            categorize_method = "mirror"
            categorize_daddy_mode = False


        # store the exceptions as abspaths
        # split on newline if multiple
        # remove duplicates
        categorize_exceptions = []
        for e in set(self.catExceptPlainTextEdit.toPlainText().split("\n")):
            categorize_exceptions.append(os.path.abspath(e))


        # call the helper function to check whether we have files to organize
        # pass it the stored values
        # store the return
        # if some error, the helper function will return an error code
        result = categorize_GUI_helpers.hasOrganizableFiles(categorize_target,
                                               categorize_method,
                                               categorize_daddy_mode,
                                               categorize_exceptions)

        # warn and return upon hidden target
        if result == 1:
            QMessageBox.warning(self, "Categorize Error",
                                "Can't organize any files. "
                                "The target directory is hidden.")
            return

        
        # warn and return upon excepted target
        elif result == 2:
            QMessageBox.warning(self, "Categorize Error",
                                "Can't organize any files. "
                                "The target directory is excepted.")
            return


        # warn and return upon inexistent/all-hidden/all-excepted files
        elif result == 3:
            QMessageBox.warning(self, "Categorize Error",
                                "Can't organize any files in this directory. "
                                "Perhaps you don't have any. "
                                "If you do, they're all hidden or excepted.")
            return
            
        # target not executable
        elif result == 4:
            QMessageBox.warning(self, "Categorize Error",
                                "Can't organize any files in this directory. "
                                "No executable permissions.")
            return


        # reaching this point means we can categorize files
        # store the delete empty dirs option    
        if self.catDeleteCheckBox.isChecked():
            delete_request = True
        else:
            delete_request = False


        # call the organizing function by passing it the stored value
        categorize_GUI_helpers.organizeFiles(delete_request)

        
        # inform about organizing success
        # inform about restoring possibility
        QMessageBox.information(self, "3CU Categorize",
          "Done! Please take a look!\n\n"
          '''We want you to be able to restore your target folder or drive \
to its initial state, so please don't close the program and don't rename, \
delete or move around any of the affected files and folders.''')

        

    # called upon clicking the restore function
    def catRestore(self):            

        # if nothing in the special helpers list, it means
        # we didn't categorize anything to be able to restore,
        # or we have just performed a restoration,
        # so inform and return
        if categorize_GUI_helpers.VISIBLE_FILES == []:
            QMessageBox.information(self, "3CU Categorize",
                                    "Nothing to restore.")
            return

        # else
        else:

            # warn to close affected files/folders before restoring
            QMessageBox.warning(self, "3CU Categorize",
            "Make sure that all the files and folders "
            "from the target directory or drive are closed.")

            # restore
            categorize_GUI_helpers.restoreContent()

            # inform
            QMessageBox.information(self, "3CU Categorize",
                                    "Restoration complete!")


#----2ND TAB # COMBINE FUNCTIONS-----------------------------------------


    # upon pressing the browse button
    # fills the text edit with the chosen folder's URI
    def comAddProcessedDir(self):
        foldername = QFileDialog.getExistingDirectory(self, "Choose Directory",
                                                      "", QFileDialog.ShowDirsOnly)

        self.comProcessedDirsPlainTextEdit.appendPlainText(foldername)


    # enables the tree mode upon checking the "everything" method
    # disables it upon checking the "files only" method
    def comEnableTreeMode(self):
        if self.comEverythingRadioButton.isChecked():
            self.comTreeCheckBox.setEnabled(True)
        else:
            self.comTreeCheckBox.setDisabled(True)


    # upon pressing the browse destination dir button
    # fills the lineedit with the chosen folder's URI
    def comChooseDestinationDir(self):

        # special folders-only flag    
        foldername = QFileDialog.getExistingDirectory(self, "Choose Directory",
                                                      "", QFileDialog.ShowDirsOnly)

        self.comDestinationDirLineEdit.setText(foldername)


    # upon pressing the browse exception file button
    # appends the text edit with the chosen file's URI
    def comExceptFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Choose File", "")

        self.comExceptPlainTextEdit.appendPlainText(filename)


    # upon pressing the browse exception folder button
    # appends the text edit with the chosen folder's URI
    def comExceptDirectory(self):
        foldername = QFileDialog.getExistingDirectory(self, "Choose Directory",
                                                      "", QFileDialog.ShowDirsOnly)

        self.comExceptPlainTextEdit.appendPlainText(foldername)


    # the main action function
    def comCombine(self):

        # warn and return if no processed dirs provided
        if self.comProcessedDirsPlainTextEdit.toPlainText() == "":

            QMessageBox.warning(self, "Combine Error",
                                "You must provide directories to combine.")
            return


        # warn and return if no method selected
        if not self.comFilesOnlyRadioButton.isChecked() and \
           not self.comEverythingRadioButton.isChecked():

            QMessageBox.warning(self, "Combine Error",
                                "You must choose a combining method.")
            return


        # warn and return if no destination provided
        if self.comDestinationDirLineEdit.text() == "":

            QMessageBox.warning(self, "Combine Error",
                                "You must indicate a destination directory.")
            return
        
        
        # make sure the destination still exists when starting
        if not os.path.isdir(self.comDestinationDirLineEdit.text()):
            QMessageBox.warning(self, "Combine Error",
                                "You must choose a valid destination.")
            return


        # warn and return if method "everything" and only one dir to process
        if len(set(self.comProcessedDirsPlainTextEdit.toPlainText().split("\n"))) < 2 and \
           self.comEverythingRadioButton.isChecked():

            QMessageBox.warning(self, "Combine Error",
                                'For the "everything" method, you must '
                                'provide two or more directories to process.')
            return


        # warn to close any files/folders before processing
        QMessageBox.warning(self, "3CU Combine",
            "Make sure to close any files and folders "
            "that are about to be processed.")
        

        # we passed the surface tests, must go deeper
        # store the processed dirs' abspaths
        # remove duplicates
        combine_processed_dirs = []
        for pd in set(self.comProcessedDirsPlainTextEdit.toPlainText().split("\n")):
            combine_processed_dirs.append(os.path.abspath(pd))

        
        # store the method and the mode
        if self.comEverythingRadioButton.isChecked():
            combine_method = "everything"

            if self.comTreeCheckBox.isChecked():
                combine_tree_mode = True
            else:
                combine_tree_mode = False
        elif self.comFilesOnlyRadioButton.isChecked():
            combine_method = "files only"
            combine_tree_mode = False


        # store the destination abspath
        combine_destination = os.path.abspath(self.comDestinationDirLineEdit.text())


        # store the exceptions' abspaths
        # split on newline if multiple
        # remove duplicates
        combine_exceptions = []
        for e in set(self.comExceptPlainTextEdit.toPlainText().split("\n")):
            combine_exceptions.append(os.path.abspath(e))


        # call the helper function to check whether we have files to organize
        # pass it the stored values
        # if no movable files, the function returns special error codes
        # store the result
        result = combine_GUI_helpers.canMoveFiles(combine_processed_dirs,
                                                 combine_destination,
                                                 combine_method,
                                                 combine_tree_mode,
                                                 combine_exceptions)

        
        # warn and return upon hidden destination
        if result == 1:
            QMessageBox.warning(self, "Combine Error",
                                "Can't combine any files. "
                                "The destination directory is hidden.")
            return

        
        # warn and return upon excepted destination
        elif result == 2:
            QMessageBox.warning(self, "Combine Error",
                                "Can't combine any files. "
                                "The destination directory is excepted.")
            return


        # warn and return upon inexistent/all-hidden/all-excepted files
        # (the destination is the only processed dir in "files only")
        elif result == 3:
            QMessageBox.warning(self, "Combine Error",
                                "Can't extract any files. "
                                "You must have movable files "
                                "inside the destination's subfolders.")
            return


        # warn and return upon inexistent/all-hidden/all-excepted files
        # (one processed dir, not the destination, "files only")
        elif result == 4:
            QMessageBox.warning(self, "Combine Error",
                                "Can't move any files. "
                                "You must have movable files "
                                "inside the target directory.")
            return


        # warn and return upon inexistent/all-hidden/all-excepted files
        # multiple processed dirs, "files only"
        elif result == 5:
            QMessageBox.warning(self, "Combine Error",
                    "You must have movable files inside your destination's " \
                    "subfolders or inside at least one of the target " \
                    "directories.")
            return


        # warn and return upon inexistent/all-hidden/all-excepted files
        # method "everything"
        elif result == 6:
            QMessageBox.warning(self, "Combine Error",
                    "You must have movable files or folders inside at least one " \
                  "of your target directories that isn't the destination folder.")
            return

        # destination not executable
        elif result == 7:
            QMessageBox.warning(self, "Categorize Error",
                                "Can't use this destination. "
                                "No executable permissions.")
            return


        # reaching this point means we can combine
        # store the delete empty dirs option    
        if self.comDeleteCheckBox.isChecked():
            delete_request = True
        else:
            delete_request = False


        # call the combining function by passing it the stored value
        combine_GUI_helpers.moveFiles(delete_request)

        
        # inform about combining success
        # inform about restoring possibility
        QMessageBox.information(self, "3CU Combine",
          "Done! Please take a look!\n\n"
          '''We want you to be able to restore your folders and/or drives \
to their initial state, so please don't close the program and don't rename, \
delete or move around any of the affected files and folders.''')


    # called upon clicking the restore function
    def comRestore(self):            

        # if nothing in the special helpers lists, it means
        # we didn't move anything to be able to restore,
        # or we have just performed a restoration,
        # so inform and return
        if combine_GUI_helpers.VISIBLE_FILES == [] and \
           combine_GUI_helpers.VISIBLE_DIRECTORIES == []:
            QMessageBox.information(self, "3CU Combine",
                                    "Nothing to restore.")
            return

        # else
        else:

            # warn to close affected files/folders before restoring
            QMessageBox.warning(self, "3CU Combine",
            "Make sure that all the affected files and folders "
            "are closed.")

            # restore
            combine_GUI_helpers.restoreContent()

            # inform
            QMessageBox.information(self, "3CU Combine",
                                    "Restoration complete!")




           
#---3RD TAB CLEAN UP FUNCTIONS-------------------------------------------    
    
    # upon pressing the browse target dir button
    # fills the lineedit with the chosen folder's URI
    def cuChooseTargetDir(self):

        # special folders-only flag    
        foldername = QFileDialog.getExistingDirectory(self, "Choose Directory",
                                                      "", QFileDialog.ShowDirsOnly)

        self.cuTargetDirLineEdit.setText(foldername)


    # upon pressing the browse exception file button
    # appends the text edit with the chosen file's URI
    def cuExceptFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Choose File", "")

        self.cuExceptPlainTextEdit.appendPlainText(filename)


    # upon pressing the browse exception folder button
    # appends the text edit with the chosen folder's URI
    def cuExceptDirectory(self):
        foldername = QFileDialog.getExistingDirectory(self, "Choose Directory",
                                                      "", QFileDialog.ShowDirsOnly)

        self.cuExceptPlainTextEdit.appendPlainText(foldername)


    # the main action function
    def cuCleanUp(self):

        # warn and return if no target provided
        if self.cuTargetDirLineEdit.text() == "":

            QMessageBox.warning(self, "Cleanup Error",
                                "You must choose a target directory.")
            return

        # make sure the target still exists when starting
        if not os.path.isdir(self.cuTargetDirLineEdit.text()):
            QMessageBox.warning(self, "Cleanup Error",
                                "You must choose a valid destination.")
            return

        
        # warn and return if no method selected
        if not self.cuDeleteEmptyCheckBox.isChecked() and \
           not self.cuDeleteDuplicateCheckBox.isChecked() and \
           not self.cuDeleteRedundantCheckBox.isChecked():

            QMessageBox.warning(self, "Cleanup Error",
                                "Choose at least one thing to do.")
            return


        # warn to close any files/folders before processing
        QMessageBox.warning(self, "3CU Cleanup",
            "Make sure to close any files and folders "
            "from the target directory or drive.")


        # store the target path
        # the GUI dialog window returns the folder URI
        # we operate with paths, so we convert
        cleanup_target = os.path.abspath(self.cuTargetDirLineEdit.text())


        # store the methods
        delete_empty = self.cuDeleteEmptyCheckBox.isChecked()
        delete_duplicate = self.cuDeleteDuplicateCheckBox.isChecked()
        delete_redundant = self.cuDeleteRedundantCheckBox.isChecked()

        
        # store the exceptions as abspaths
        # split on newline if multiple
        # remove duplicates
        cleanup_exceptions = []
        for e in set(self.cuExceptPlainTextEdit.toPlainText().split("\n")):
            cleanup_exceptions.append(os.path.abspath(e))


        # call the helper function to check whether we have files to organize
        # pass it the stored values
        # store the return (it will be a code if some error)
        result = cleanup_GUI_helpers.checkIfCleanable(cleanup_target,
                                                      cleanup_exceptions,
                                                      delete_empty,
                                                      delete_duplicate,
                                                      delete_redundant)

        
        # warn and return upon hidden target
        if result == 1:
            QMessageBox.warning(self, "Cleanup Error",
                                "Can't clean up anything. "
                                "The target directory is hidden.")
            return

        
        # warn and return upon excepted target
        elif result == 2:
            QMessageBox.warning(self, "Cleanup Error",
                                "Can't clean up anything. "
                                "The target directory is excepted.")
            return


        # warn and return upon inexistent/all-hidden/all-excepted
        # cleanable content
        elif result == 3:
            QMessageBox.warning(self, "Cleanup Error",
                                "Can't clean anything here. "
                                "Either there's nothing here, "
                                "or the cleanable content is inaccessible.")
            return


        # everything is fine here 
        # call the main function
        cleanup_GUI_helpers.cleanUp()
        
        # inform about organizing success
        # present the report
        # inform about restoring possibility
        QMessageBox.information(self, "3CU Cleanup",
          cleanup_GUI_helpers.ACTIVITY_REPORT)

        

    # called upon clicking the restore function
    def cuRestore(self):            

        # if nothing in the special helpers lists, it means
        # we didn't categorize anything to be able to restore,
        # or we have just performed a restoration,
        # so inform and return
        if cleanup_GUI_helpers.VISIBLE_FILES == [] and \
           cleanup_GUI_helpers.VISIBLE_DIRECTORIES == []:
            QMessageBox.information(self, "3CU Cleanup",
                                    "Nothing to restore.")
            return

        # else
        else:

            # warn to close affected files/folders before restoring
            QMessageBox.warning(self, "3CU Cleanup",
            "Make sure that all the files and folders "
            "from the target directory or drive are closed.")

            # restore
            cleanup_GUI_helpers.restoreContent()

            # inform
            QMessageBox.information(self, "3CU Cleanup",
                                    "Restoration complete!")


            
        

        
# create a qapp instance    
app = QApplication(sys.argv)

# create the main window instance
window = MainWindow()

# show it, as it's by default invisible
window.show()

# start the event loop
app.exec_()
