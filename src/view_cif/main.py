#.venv/bin/python3.12 python3
import subprocess
import os
from gemmi.cif import read as read_cif
from gemmi import expand_if_pdb_code, is_pdb_code
import typer


TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)

def view_cif(cont:str):
    output = os.path.join(TEMP_DIR, os.path.basename(cont) + '.cif')
    
    if os.path.exists(cont):
        doc = read_cif(cont).as_string()
    
    elif is_pdb_code(cont):
        doc = read_cif(expand_if_pdb_code(cont)).as_string()
    
    elif cont.lower() in ('prdcc', 'clc', 'cc', 'prd', 'ccd'):
        ligand_dir = os.getenv('LIGAND_DIR')
        if cont == 'prd':
            doc = read_cif(os.path.join(ligand_dir, 'prd-all.cif.gz')).as_string()
        elif cont == 'prdcc':
            doc = read_cif(os.path.join(ligand_dir, 'prdcc-all.cif.gz')).as_string()
        elif cont == 'clc':
            doc = read_cif(os.path.join(ligand_dir, 'clc-all.cif.gz')).as_string()
        else:
            doc = read_cif(os.path.join(ligand_dir, 'components.cif.gz')).as_string()
    
    with open(output, 'w') as f:
        f.write(doc)
    
    subprocess.run(['code', '--new-window', '--wait', output])
    os.remove(output)

def main():
    typer.run(view_cif)
