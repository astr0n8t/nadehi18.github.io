# Used to find files
from os import walk

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
                        "index-file"
                        ]
        
        # Process config file before beginnning indexing
        if(self.process_config_file()):
            # Start indexing

            self.files_to_process = self.get_files_to_index()




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
        
        return processed_correctly

    # Assuming when this function is ran that the config options are configured  
    def get_files_to_index(self):
        # List to store all files in the indexing folder
        existing_files = []

        # Find all html files in the directory and subdirectory
        # Stored as full paths i.e. 'notefiles/test.html'
        path = self.settings["html-folder"]
        for root, subdir, files in walk(path):
            for file in files:
                if '.html' in file:
                    existing_files.append(str(root+"/"+file))

        for file in existing_files:
            # Store the line
            line = None
            # Open each file and grab the third line
            with open(file, 'r') as current_file:
                for x in range(0,3):
                    line = current_file.readline().strip()
                
            # Check if the file has been indexed or if it is blank
            if line == "" or line == "<!--*INDEXED*-->":
                existing_files.remove(file)
        # Return the list of paths which need to be indexed
        return existing_files


        


#    def index(self):




if __name__ == '__main__':
    Indexer() 