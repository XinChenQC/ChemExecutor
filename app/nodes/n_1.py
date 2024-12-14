# N_1 node for loading geometry file. 

class N_1:
    # 
    def __init__(self, nodedata):
        """
        Initialize the file loading nodes.
        :nodedata nodesdata: Dictionary containing the parameters for optimization.
            e.g. {  'id': '1', 
                  'type': 'n_1', 
                  'data': {{'input': [0], 'output': [0], 'options': [False]}
                                                     ^                 ^     
                                              Structure File          Add H  
        """
        self.fileData = "" # files loaded from front-end JSON
        print(nodedata)
        self.fileData = nodedata['data']['output']
        self.status = 'f' # Should always be finished
        
        self.parameters = {}
    # 
    def check(self, fileData):
        """
        Check to file uploaded. 
        """
        # ... existing code ...

        if(len(fileData)==0 ):
            return False
            
    '''
    def compute(self):
        """
        Perform the geometry optimization.

        :return: Optimized geometry.
        """
        # ... existing code ...
        pass
    '''

# 
if __name__ == "__main__":
    pass