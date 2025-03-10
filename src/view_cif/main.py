import subprocess
import os
from gemmi.cif import read as read_cif
from gemmi import expand_if_pdb_code, is_pdb_code
import typer
from typing_extensions import Annotated


TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)

def get_cif_path(cont: str, target_dir: str) -> str:
    path = os.path.join(target_dir, cont)
    if os.path.exists(path + '.cif'):
        return path + '.cif'
    elif os.path.exists(path + '.cif.gz'):
        return path + '.cif.gz'
    else:
        raise FileNotFoundError(f'File {cont}.cif not found in {target_dir}')



def view_cif(
        cont: Annotated[str, typer.Argument(help="The name of the CIF file to view")],
        target_dir: Annotated[str, typer.Argument(help="The directory to search for the CIF file")]=None,
        ccd_def: Annotated[bool, typer.Option('--ccd-definition', '-d', help="CCD File (definition file type)")]=False,
    ):
    
    output = os.path.join(TEMP_DIR, os.path.basename(cont) + '.cif')

    # cont is a file path
    if os.path.exists(cont):
        doc = read_cif(cont).as_string()

    elif target_dir:
        path = get_cif_path(cont, target_dir)
        doc = read_cif(path).as_string()
    
    # cont is a pdb code
    elif is_pdb_code(cont):
        doc = read_cif(expand_if_pdb_code(cont)).as_string()
    
    # cont is prdcc or prd or clc or ccd
    elif cont.lower() in ('prd', 'ccd'):
        if cont == 'prd':
            prd_dir = os.path.join(os.getenv('BIRD'), 'prd')
            if ccd_def:
                doc = read_cif(os.path.join(prd_dir, 'prd-all.cif.gz')).as_string()
            else:
                doc = read_cif(os.path.join(prd_dir, 'prdcc-all.cif.gz')).as_string()
        else:
            doc = read_cif(os.path.join(
                            os.getenv('MONOMERS'), 'components.cif.gz'
                        )).as_string()
            
    elif ccd_def:
        doc = read_cif(
                get_cif_path(cont.upper(), os.getenv('PRD_DIR'))
            ).as_string()
            
    else:
        doc = read_cif(
                get_cif_path(cont.upper(), os.getenv('CHEM_COMP'))
            ).as_string()
        
    with open(output, 'w') as f:
        f.write(doc)
    
    subprocess.run(['code', '--new-window', '--wait', output])
    os.remove(output)
