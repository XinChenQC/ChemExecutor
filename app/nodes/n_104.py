import os
import json
import os
import subprocess
import re
import matplotlib.pyplot as plt

# N_101 node for geometry optimization

# 
class N_104:
    # 初始化方法
    def __init__(self, nodedata: dict):
        """
        ESM fold
        :nodedata nodesdata: Dictionary containing the parameters for optimization.
                e.g. {  'id': '104', 
                      'type': 'n_104', 
                      'data': {'input': [], 'output': [0], 'options': [seq]}
                                                ^                      ^     
                                          structurefile            Sequence
                     }
        """
        self.sequence = None
        self.engine_type = None # 'SE' or 'QM'

        self.status = 'w' #w: waiting, r:running f:finished u:cannot run. e:error

        self.sequence = nodedata['data']['options'][0].replace('\n', '').strip()
        self.outStruc = None

        self.tmpdir = nodedata['id']+"_esmfold"

        self.nodedata_return = nodedata['data']
        print(nodedata['data'])
        

    def getSource(self, prenodes: list, links: list):
        """
        Initialize the geometry optimization node.
        :prenodes prenodes: List of previous nodes that directed to this node. 
        :links    links:  List of edges name linked to this node.
        """
        
        self.status = 'w'



    # Compute engine
    def compute(self):
        """
        Run ESMfold

        :return: Optimized geometry.
        """
        self.status = "r"
        os.makedirs(self.tmpdir)
        print(self.tmpdir)
        os.chdir(self.tmpdir)
        
        try:
            # Execute Linux command and redirect output to out.log
            import requests
            
            
            invoke_url = "https://health.api.nvidia.com/v1/biology/nvidia/esmfold"

            headers = {
                "Authorization": "Bearer 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",
                "Accept": "application/json",
            }
            
            print(self.sequence)
            payload = {
            "sequence":  self.sequence
            }


            # re-use connections
            session = requests.Session()

            response = session.post(invoke_url, headers=headers, json=payload)
            response.raise_for_status()
            response_body = response.json()
            print(response_body)
            Struct = response_body['pdbs'][0]
            self.nodedata_return['output'] = [[Struct,'pdb']]
            self.outStruc = [[Struct,'pdb']]
            with open('out.pdb', "w") as f:
                f.write(Struct)
            self.status = "f"
        finally:
            pass
                
# Test
if __name__ == "__main__":

    pass