

class Indexer():
    def __init__(self):
        
        # Get the config file and resource folders
        self.resource_folder = "indexer-resources/"
        self.config_file = self.resource_folder + "indexer.config"

        # Dictionary to keep config settings in
        self.settings = {"html-folder": None, "index-file": None}
        
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
            return -2
        # Tell the user if anything else happened
        except:
            print("Unknown Error Occurred, Exiting...")
            return -1
        

        


#    def index(self):




if __name__ == '__main__':
    Indexer() 