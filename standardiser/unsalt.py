####################################################################################################
# 
# Copyright [2014] EMBL - European Bioinformatics Institute
# 
# Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in
# compliance with the License.  You may obtain a copy of
# the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software distributed under the
# License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.
# 
####################################################################################################

"""Remove salt/solvates"""

########################################################################

# Module imports...

from __future__ import print_function

import logging
logger = logging.getLogger(__name__)

import os
import csv
import re
import copy

from rdkit import Chem

########################################################################

# Module configuration...

use_inchi = False ### Chem.INCHI_AVAILABLE

salts_file = "salts.tsv"

non_organic_elements = "[!#1&!#6&!#7&!#8&!#9&!#15&!#16&!#17&!#35&!#53]"
# TODO: Check if this tmp change has any influence on results.
# boron!
non_organic_elements = non_organic_elements[:-1]+"&!#5]"

########################################################################

# Module initialization...

non_organic_elements = Chem.MolFromSmarts(non_organic_elements)

salts = {}

salts_fh = open(os.path.join(os.path.dirname(__file__), "data",  salts_file))

for record in csv.DictReader(salts_fh, delimiter="\t"):

    smiles, name = record["SMILES"], record["name"]

    if re.match(r"\s*(#|$)", smiles): continue  # NB assumes SMILES is in first column

    mol = Chem.MolFromSmiles(smiles)

    if not mol:

        logger.warning("Bad SMILES in salt/solvate file: {smiles} {name}".format(smiles=smiles, name=name))

        continue

    Chem.RemoveStereochemistry(mol)

    key = Chem.MolToInchi(mol) if use_inchi else Chem.MolToSmiles(mol)

    salts[key] = {'SMILES': smiles, 'name': name}

########################################################################

def is_nonorganic(mol):

    if mol.GetSubstructMatch(non_organic_elements):

        logger.debug("Fragment contains a non-organic element")

        return True

    return False

# is_nonorganic

######

def is_salt(mol):

    mol = copy.deepcopy(mol)

    Chem.RemoveStereochemistry(mol)

    key = Chem.MolToInchi(mol) if use_inchi else Chem.MolToSmiles(mol)

    if key in salts:

        logger.debug("Fragment matches salt/solvate '{name}'".format(name=salts[key]['name']))

        return True

    return False

# is_salt

########################################################################
# End
########################################################################
