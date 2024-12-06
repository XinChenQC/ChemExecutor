import json
import os
import subprocess
import re
import matplotlib.pyplot as plt

def process_output(task_id: str, data: dict) -> dict:
    calcTemp_path = f"./results/{task_id}/opt.xyz"
    with open(calcTemp_path) as f:
        coordinates = f.read()
    
    # Read SVG from energy_profile.svg file
    svg_path = f"./results/{task_id}/energy_profile.svg"
    with open(svg_path) as f:
        svg = f.read()
        
    n_101_nodes = [node for node in data['nodes'] if node['type'] == 'n_101']
    n_101_nodes[0]['data']['output'] = [coordinates, svg]
    
    return data


def load_data(file_path: str):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data



def runcalc(calc_dir: str):
    file_path = './uploaded_files/flow.json'
    result = load_data(file_path)
    xtb = "/home/ubuntu/software/xtb-dist/bin/xtb"

    if not os.path.exists(calc_dir):
        os.makedirs(calc_dir)

    for item in result['nodes']:
        if item['type'] == 'n_1':
            output_data = item['data']['output'][0].replace('\r\n', '\n')
            with open(calc_dir+'/aa.xyz', 'w') as f:
                f.write(output_data)
        if(item['type'] == 'n_1002'):
            etemp = item['data']['options'][1]
            print (etemp)
        if(item['type'] == 'n_101'):
            opt_cri = item['data']['options'][0]
            print( opt_cri)
      # Change directory to ./results
    # 记录初始目录
    original_dir = os.getcwd()



    try:
        # 切换到calc_dir
        os.chdir(calc_dir)
        
        # Execute Linux command and redirect output to out.log
        with open('out.log', 'w') as log_file:
            subprocess.run([xtb, 'aa.xyz', '--opt'], check=True, stdout=log_file)
        # Check if 'finished run' in out.log
        with open('out.log', 'r') as log_file:
            log_content = log_file.read()
            if 'finished run' in log_content:
                subprocess.run(["mv", "xtbopt.log", "opt.xyz"])
                
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
                print(calc_dir)
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
                
                status = "Finished"
            else:
                status = "error"
    finally:
        # 切换回初始目录
        os.chdir(original_dir)
    return status