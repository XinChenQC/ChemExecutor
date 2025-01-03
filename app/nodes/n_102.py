import os
import json
import os
import subprocess
import re
import matplotlib.pyplot as plt

# N_101 node for docking

# 
class N_102:
    # 初始化方法
    def __init__(self, nodedata: dict):
        """
        Initialize the geometry optimization node.
        :nodedata nodesdata: Dictionary containing the parameters for optimization.
                e.g. {  'id': '2', 
                      'type': 'n_101', 
                      'data': {'input': [0, 0], 'output': [0], 'options': ['location', 'sofware']}
                                         ^  ^              ^                 ^              ^        
                                    Targe ligand  Result:combo            dock location  software  
                     }
        """

        self.status = 'u' #w: waiting, r:running f:finished u:cannot run. e:error
        self.structures = [0,0] # 0 is Target, 1 is ligand
        self.postition = nodedata['data']['options'][0]
        self.software = nodedata['data']['options'][1]
        self.results = None

        self.tmpdir = nodedata['id']+"_docking"
        self.obabel = "obabel"

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
            print(link,'ss')
            if "Protein" in link:
                self.structures[0] = node[1]['data']['output'][0]
            else:
                self.structures[1] = node[1]['data']['output'][0]
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
        
        try:
            print(self.software)
            print(self.postition)
            if ("Vina" in self.software):
                # 打开日志文件
                log_file = open("vina_log.txt", "w")
                # 保存原始的 stdout 和 stderr
                original_stdout = os.dup(1)
                original_stderr = os.dup(2)
                os.dup2(log_file.fileno(), 1)
                os.dup2(log_file.fileno(), 2)
                from vina import Vina
                # Target
                ext_target = self.structures[0][1]
                output_data = self.structures[0][0].replace('\r\n', '\n')
                with open(f'target.{ext_target}', 'w') as f:
                    f.write(output_data)
                # Ligant
                ext_ligant = self.structures[1][1]
                output_data = self.structures[1][0].replace('\r\n', '\n')
                with open(f'ligant.{ext_ligant}', 'w') as f:
                    f.write(output_data)

                result = subprocess.run(f"{self.obabel} target.{ext_target} -O target.pdbqt  -xr  --partialcharge mmff94", check=True, capture_output=True, text=True, shell=True)
                print(f"stdout: {result.stdout}")
                print(f"stderr: {result.stderr}")

                result = subprocess.run(f"{self.obabel} ligant.{ext_ligant} -O ligant.pdbqt --partialcharge mmff94", check=True, capture_output=True, text=True, shell=True)
                print(f"stdout: {result.stdout}")
                print(f"stderr: {result.stderr}")

                v = Vina(sf_name='vina')
                v.set_receptor('target.pdbqt')
                v.set_ligand_from_file('ligant.pdbqt')

                v.compute_vina_maps(center=[0.190, 0.903, 0.917], box_size=[20, 20, 20])

                # Score the current pose
                energy = v.score()
                #print('Score before minimization: %.3f (kcal/mol)' % energy[0])

                # Minimized locally the current pose
                energy_minimized = v.optimize()
                #print('Score after minimization : %.3f (kcal/mol)' % energy_minimized[0])
                v.write_pose('ligand_minimized.pdbqt', overwrite=True)

                # Dock the ligand
                v.dock(exhaustiveness=32, n_poses=20)
                v.write_poses('ligand_vina_out.pdbqt', n_poses=5, overwrite=True)
                #obabel ligand_vina_out.pdbqt -O ligant_result.pdb

                result = subprocess.run(f"{self.obabel} ligand_vina_out.pdbqt -O ligant_result.pdb", check=True, capture_output=True, text=True, shell=True)
             

                print(f"stdout: {result.stdout}")
                print(f"stderr: {result.stderr}")
                
                traj_path = f"ligant_result.pdb"
                with open(traj_path) as f:
                    docking_results = f.read()   

                self.nodedata_return['output'] = [[docking_results,'pdb']]
                os.dup2(original_stdout, 1)
                os.dup2(original_stderr, 2)
                log_file.close()               

            self.status = "f"
        finally:
            pass
                
# Test
if __name__ == "__main__":

    pass