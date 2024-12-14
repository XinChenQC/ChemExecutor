import os
import json
import os
import subprocess
import re
import matplotlib.pyplot as plt

# N_101 node for geometry optimization

# 
class N_101:
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
        '''
        # For SE
        self.parameters["e_temperature"] # Temperature
        self.parameters["charge"]        # Charge
        self.parameters["spin"]          # Spin
        self.parameters["software"]      # Software
        '''
        self.engine_type = None # 'SE' or 'QM'
        self.status = 'u' #w: waiting, r:running f:finished u:cannot run. e:error
        self.structure = None
        self.tmpdir = nodedata['id']+"_opt"
        self.xtb = "/home/ubuntu/software/xtb-dist/bin/xtb"
        self.dftbp = "dftbp"
        self.convcri = nodedata['data']['options'][0]
        self.nodedata_return = nodedata['data']

    def getSource(self, prenodes: list, links: list):
        """
        Initialize the geometry optimization node.
        :prenodes prenodes: List of previous nodes that directed to this node. 
        :links    links:  List of edges name linked to this node.
        """

        for node in prenodes:
            # semiempirical
            if(node[1]['type'] == 'n_1002'): 
                self.engine_type = 'SE'
                self.engine_parameter = node[1]['instance'].parameters

            # QM
            if(node[1]['type'] == 'n_1001'): 
                self.engine_type = 'QM'
                self.engine_parameter = node[1]['instance'].parameters

            # Read structure
            if(node[1]['type'] == 'n_1'): 
                self.structure = node[1]['instance'].fileData

            if self.structure and self.engine_parameter and self.engine_type:
                self.status = 'w'
    



    # Compute engine
    def compute(self):
        """
        Perform the geometry optimization.

        :return: Optimized geometry.
        """
        # ... existing code ...
        if (self.engine_type == 'SE'):
            temp     = str(self.engine_parameter["e_temperature"]) # Temperature
            chrg     = str(self.engine_parameter["charge"])        # Charge
            spin     = str(int(self.engine_parameter["spin"])-1)          # Spin
            software = str(self.engine_parameter["software"])     # Software
            
            if(self.convcri =='Tight'):
                conv = 'tight'
            if(self.convcri =='Normal'):
                conv = 'normal'
            if(self.convcri =='Loose'):
                conv = 'loose'

            os.makedirs(self.tmpdir)
            os.chdir(self.tmpdir)

            output_data = self.structure[0].replace('\r\n', '\n')
            with open('input.xyz', 'w') as f:
                f.write(output_data)

            if(software== 'xTB'):
                command = f"{self.xtb} --opt {conv} --charge {chrg} --uhf {spin} --etemp {temp} aa.xyz"

            print(command)
            print(f"Current directory: {os.getcwd()}")


            try:
                # Execute Linux command and redirect output to out.log
                with open('out.log', 'w') as log_file:
                    subprocess.run([self.xtb, 'input.xyz', '--opt',conv,'--charge',chrg,'--uhf',spin,'--etemp',temp], check=True, stdout=log_file)
                # Check if 'finished run' in out.log
                with open('out.log', 'r') as log_file:
                    log_content = log_file.read()
                    if 'finished run' in log_content:
                        subprocess.run(["mv", "xtbopt.log", "opt.xyz"])
                        print('here')
                        # Add energy extraction and plotting code
                        energies = []
                        steps = []


                        with open('opt.xyz', 'r') as f:
                            for line in f:
                                if ' energy:' in line:
                                    # Extract energy value using regex
                                    match = re.search(r'energy:\s*([-\d.]+)', line)
                                    if match:
                                        energies.append(float(match.group(1)))
                                        steps.append(len(steps) + 1)

                        # Create the plot
                        plt.figure(figsize=(10, 6))
                        plt.plot(steps, energies, 'b-', marker='o')
                        plt.xlabel('Optimization Step', fontsize=16)
                        plt.ylabel('Energy (Hartree)', fontsize=16)
                        plt.title('Optimization Energy Profile', fontsize=22)
                        plt.grid(True)
                        plt.xticks(fontsize=15)
                        plt.yticks(fontsize=15)
                        plt.gca().yaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))

                        plt.savefig('energy_profile.svg', format='svg')
                        plt.close()

                        self.status = "f"
                        
                        self.tmpdir = os.getcwd()
                        svg_path = f"{self.tmpdir}/energy_profile.svg"
                        with open(svg_path) as f:
                            svg = f.read()
                            
                        traj_path = f"{self.tmpdir}/opt.xyz"
                        with open(traj_path) as f:
                            traj = f.read()

                        conv_path = f"{self.tmpdir}/xtbopt.xyz"
                        with open(conv_path) as f:
                            fcoord = f.read()
                        
                        self.nodedata_return['output'] = [fcoord ,traj, svg]
                        #print(self.nodedata_return['data']['output'])
                    else:
                        print('ss')
                        self.status = "e"
            finally:
                pass

        

# Test
if __name__ == "__main__":

    pass