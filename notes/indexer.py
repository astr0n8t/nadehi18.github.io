# Used to find files
from os import listdir, replace

class Indexer():
    def __init__(self):

        # Get the config file and resource folders
        self.resource_folder = "indexer-resources/"
        self.config_file = self.resource_folder + "indexer.config"

        # Dictionary to keep config settings in
        self.settings = {
            "html-folder": None, 
            "index-file": None, 
            "html-head-file": None, 
            "html-header-file": None, 
            "html-footer-file": None, 
            "note-item-file": None,
            "note-category-file": None
                         }
        # Set which settings are essential to set
        self.essential_settings = [
            "html-folder", 
            "index-file",
            "note-item-file",
            "note-category-file"
                        ]

        # Set what the markers look for
        self.markers = {
            "html-head-file": ('<head>', '</head>'),
            "html-header-file": ('<body>', None),
            "html-footer-file": ('</body>', None)
        }   

        # A list of what operations are enabled in order (IMPORTANT)
        self.operations = [
            "html-head-file",
            "html-header-file",
            "html-footer-file"
        ]
        
        # Process config file before beginnning indexing
        if(self.process_config_file()):
            # Start indexing

            self.files_to_process = self.get_files_to_index()

            for file in self.files_to_process:
                try:
                    self.process_file(file)
                    self.add_file_to_notes(file)
                    print("Indexed \"{}\" Successfully".format(file))
                except:
                    print("One or more errors while processing \"{}\".  It will not be indexed.".format(file))



        else:
            # File was not processed correclty so exit
            print("One or more errors occurred. Exiting...")
            return


    def process_config_file(self):
        processed_correctly = True
        # Try to open the config file
        try:
            with open(self.config_file, "r") as config:
                for line in config:
                    if line.strip() != "":
                        # Get the first paramter which is the option
                        option = line.split(":")[0].strip()
                        # Get the second parameter which is the value
                        setting = line.split(":")[1].strip()
                        # Check if it is a valid setting
                        if option in self.settings:
                            # Set the setting if it is valid
                            self.settings[option] = setting
        # Tell the user if the config file is not found
        except FileNotFoundError:
            print("ERROR: Config file \"{}\" not found!".format(self.config_file))
            processed_correctly = False
        # Tell the user if anything else happened
        except:
            print("Unknown Error Occurred While Opening Configuration File, Exiting...")
            processed_correctly = False
        # If the config file was processed properly then check if the required settings
        # were set 
        if processed_correctly:
            # Check if essential config files are set, if not exit with an error
            for setting in self.essential_settings:
                if not self.settings[setting]:
                    print("Option \'{}\' not specified in config file! Exiting...".format(setting))
                    processed_correctly = False
        
        # Check which operations are enabled in the config
        for op in self.operations:
            if op not in self.settings or self.settings[op] == None:
                self.operations.remove(op)

        # Return whether the config was properly parsed or not
        return processed_correctly

    # Assuming when this function is ran that the config options are configured  
    def get_files_to_index(self):
        # List to store all files in the indexing folder
        existing_files = []

        # Find all html files in the directory
        # Stored as full paths i.e. 'notefiles/test.html'
        path = self.settings["html-folder"]
        for file in listdir(path):
            full_path = str(path+"/"+file)
            if '.html' in file:
                existing_files.append(full_path)

        for x in range(len(existing_files)):
            file = existing_files[0]
            # Store the line
            line = None
            # Open each file and grab the third line
            with open(file, 'r') as current_file:
                line = current_file.readline().strip()
                
            # Check if the file has been indexed or if it is blank
            if line == "" or "<!--*INDEXED*-->" in line:
                existing_files.remove(file)
        # Return the list of paths which need to be indexed
        return existing_files
    
    def add_file_to_notes(self, filename):      

        # Define variables
        # The note name is pulled from the filename but you have to pull out the
        # directory and remove the file extension
        note_name = filename.split('/')[1].split('.html')[0]
        note_category = None
        note_line = None
        category_line = None


        # Assign category based on filename
        if "-" in note_name:
            # Pull the category from the filename based on the - char
            split_name = note_name.split("-")
            note_category = split_name[0]
            note_name = split_name[1]
            # Open and copy over the category template
            with open(str(self.resource_folder + self.settings["note-category-file"])) as cat_file:
                category_line = cat_file.readline()
            # Replace the marker with the correct variable
            category_line = category_line.replace("<!--*CATEGORYNAME*-->", note_category) + '\n'
        
        # Open and copy over the note item template
        with open(str(self.resource_folder +self.settings["note-item-file"])) as note_file:
            note_line = note_file.readline()
         # Replace the markers with the correct variable 
        note_line = note_line.replace("<!--*NOTENAME*-->", note_name).replace("<!--*NOTEURL*-->", filename) + '\n'

        # Open the files to read and write to
        old_index_file = open(self.settings["index-file"], "r")
        tmp_index_filename = str(self.settings["index-file"] + '.tmp')
        index_file = open(tmp_index_filename, "w")

        # Iterate through the index file until the beginning of the area is found
        start_of_edit_found = False
        while not start_of_edit_found:
            line = old_index_file.readline()
            if "<!--*STARTEDIT*-->" in line:
                start_of_edit_found = True
            # Copy over the text from the old file into the new file
            index_file.write(line)

        # Check if we are assigning this note to a category
        if note_category:
            # Search for the category
            category_found = False
            while not category_found:
                line = old_index_file.readline()
                # The category does not exist so add it
                if "<!--*ENDEDIT*-->" in line:
                    index_file.write(category_line)
                    index_file.write(note_line)
                    index_file.write(line)
                    category_found = True
                # 
                elif "note-list-category" in line and note_category in line.split("</i>")[1]:
                    index_file.write(line)
                    index_file.write(note_line)
                    category_found = True
                else:
                    index_file.write(line)
        else:
            index_file.write(note_line)
        
        for line in old_index_file:
            index_file.write(line)
        
        index_file.close()
        old_index_file.close()

        replace(tmp_index_filename, self.settings["index-file"])

    def process_file(self, filename):

        # Open file and temp file to write to
        old_file = open(filename, 'r')
        temp_filename = str(filename+'.tmp')
        temp_file = open(temp_filename, 'w')
        
        operations_to_do = self.operations.copy()
        markers_to_find = self.markers.copy()
        
        temp_file.write("<!--*INDEXED*-->\n")

        # Iterate through and parse the file
        # Doing one operation at a time
        num_line = 0
        for line in old_file:
            
            current_line = line.strip()
            if len(markers_to_find) > 0 and markers_to_find[operations_to_do[0]][0] in current_line:
                # Set the current operation to the next to do
                op = operations_to_do[0]
                # Set the beginnning marker
                marker_s = markers_to_find[operations_to_do[0]][0]
                # Set the end marker
                marker_e = markers_to_find[operations_to_do[0]][1]
                # Open the template for the operation
                template = open(str(self.resource_folder + self.settings[op]), 'r')

                # Split the line off of the marker
                split_line = current_line.split(marker_s)
                # If there is text before the delimiter, copy it to the new file before the template
                # Then make it so there is only one line in the split_line list
                if len(split_line) > 1:
                    temp_file.write(split_line[0])
                    split_line.remove(split_line[0])
                # Copy the template in 
                for temp_line in template:
                    temp_file.write(temp_line)
                
                # Write what came after the delimiter
                if split_line:
                    temp_file.write(split_line[0])
                
                # Close the template file 
                template.close()

                # Check if the end marker is set for this operation
                if marker_e:
                    # Prime the loop
                    end_marker_found = False
                    while not end_marker_found:
                        # Read the file until the end marker is found
                        old_line = old_file.readline()
                        if marker_e in old_line:
                            end_marker_found = True

                # Remove the marker and operation since we have completed them
                del markers_to_find[op]
                operations_to_do.remove(op)
            else:
                # Otherwise copy the old file over
                temp_file.write(line)
            
        # Close the files
        old_file.close()
        temp_file.close()

        # Overwrite the old file with the newly updated one
        replace(temp_filename, filename)





if __name__ == '__main__':
    Indexer() 