# N_1002 node for semiemperical engine

class N_1002:
    # 
    def __init__(self, nodedata):
        """
        Initialize the semiempirical engine node.

        :nodedata nodesdata: Dictionary containing the parameters for optimization.
            e.g. {  'id': '3', 
                  'type': 'n_1002', 
                  'data': {'output': [0], 'options': ['xTB', '1000', '1',   '0']}
                                                        ^      ^      ^      ^
                                                 calculator  e_temp  spin  charge
                 } 
        """
        self.parameters = {
            "e_temperature": 3000,  # Example value, adjust as needed # Default is 3000
            "charge": 0,  # Example value, adjust as needed
            "spin": 1,  # Example value, adjust as needed
            "software": 'xTB' # 'xTB'(default) or 'DFTB+'
        }
        print(self.parameters,'aaa')


        self.parameters["e_temperature"] = float(nodedata['data']['options'][1])
        self.parameters["charge"] = int(nodedata['data']['options'][3])
        self.parameters["spin"] = float(nodedata['data']['options'][2])
        self.parameters["software"] = nodedata['data']['options'][0]  # No need to convert to float


        self.status = 'f' # Should always be finished

    def check(self, fileData):
        """
        Check to file uploaded. 
        """
        # ... existing code ...

        if(len(fileData)==0 ):
            return False


if __name__ == "__main__":
    pass