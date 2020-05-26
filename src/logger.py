self.logging_file = f"{os.pardir}/logs/usage_history.log"
        if os.path.isfile(self.logging_file):
            print("Usage File: ",  self.logging_file)
        else:
            self.logging_file = f"{os.curdir}/logs/usage_history.log"
            print("Usage File: ",  self.logging_file)
        logging.basicConfig(filename=self.logging_file, format='%(asctime)s %(message)s', filemode='w')
        #Creating an object
        self.logger=logging.getLogger()
        #Setting the threshold of logger to DEBUG
        self.logger.setLevel(logging.DEBUG)
        #Test messages
        self.logger.debug("Debug: Initialized")
        self.logger.info("Info: Initialized")
        self.logger.warning("Warning: Initialized")
        self.logger.error("Error: Initialized")
        self.logger.critical("Critical: Initialized")