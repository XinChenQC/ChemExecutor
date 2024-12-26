import os
import json
import os
import subprocess
import re
import matplotlib.pyplot as plt

# N_101 node for geometry optimization

# 
class N_103:
    # 初始化方法
    def __init__(self, nodedata: dict):
        """
        Initialize the geometry optimization node.
        :nodedata nodesdata: Dictionary containing the parameters for optimization.
                e.g. {  'id': '2', 
                      'type': 'n_101', 
                      'data': {'input': [0, 0], 'output': [0], 'options': ['Tight',      'LBFGS',     False]}
                                         ^  ^              ^                 ^              ^            ^
                                    ngine  structurefile  Result:combo    Converge criteria   Algorithm    PBC
                     }
        """
        self.engine_parameter = None
        self.engine_type = None # 'SE' or 'QM'

        self.status = 'u' #w: waiting, r:running f:finished u:cannot run. e:error
        self.structures = [0,0]
        self.numStruc1 = nodedata['data']['options'][0]
        self.numStruc2 = nodedata['data']['options'][1]
        self.blocksize = nodedata['data']['options'][2]
        self.outStruc = None

        self.tmpdir = nodedata['id']+"_complexsearch"
        self.xtb = "/home/xchen/software/xtb-6.6.1/bin/xtb"
        self.packmol = "/home/xchen/software/packmol/packmol"

        self.nodedata_return = nodedata['data']
        print(nodedata['data'])
        

    def getSource(self, prenodes: list, links: list):
        """
        Initialize the geometry optimization node.
        :prenodes prenodes: List of previous nodes that directed to this node. 
        :links    links:  List of edges name linked to this node.
        """
        
        self.status = 'w'
        for node, link in zip(prenodes, links):
            num = int(link[-1])-1
            self.structures[num] = node[1]['data']['output'][0][0]
        #print(self.structures)



    # Compute engine
    def compute(self):
        """
        Perform the geometry optimization.

        :return: Optimized geometry.
        """
        self.status = "r"
        os.makedirs(self.tmpdir)
        print(self.tmpdir)
        os.chdir(self.tmpdir)

        i = 1
        for struct in self.structures:
            output_data = struct.replace('\r\n', '\n')
            with open(f'{str(i)}.xyz', 'w') as f:
                f.write(output_data)
            i = i+1
        packmol_content =  f"""tolerance 2.0
filetype xyz
output mixture.xyz

structure 1.xyz
  number {self.numStruc1}
  inside box 0. 0. 0. {self.blocksize}
end structure

structure 2.xyz
  number {self.numStruc2}
  inside box 0. 0. 0. {self.blocksize}
end structure
"""
        with open('inputfile', "w") as f:
            f.write(packmol_content)
        
        try:
            # Execute Linux command and redirect output to out.log
            result = subprocess.run(f"{self.packmol} < inputfile > out.log", check=True, capture_output=True, text=True, shell=True)
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            
            self.tmpdir = os.getcwd()

            mixStruct_path = f"{self.tmpdir}/mixture.xyz"
            with open(mixStruct_path) as f:
                mixStruct = f.read()
            self.nodedata_return['output'] = [[mixStruct,'xyz']]
            self.outStruc = [[mixStruct,'xyz']]
            self.status = "f"
        finally:
            pass
                
# Test
if __name__ == "__main__":

    pass