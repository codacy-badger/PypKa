
#! /usr/bin/python

"""
A python API and CLI to perform pKa calculations on peptides,
proteins or lipid bilayers.
"""

import os

import config as config
from cli import checkParsedInput, readSettings, inputParametersFilter
from cleaning import inputPDBCheck, cleanPDB
from formats import convertTermini, pdb2gro
import log as log

from delphi4py import Delphi

from molecule import Molecule
from concurrency import startPoolProcesses, runDelPhiSims


__author__ = "Pedro Reis"
__version__ = "0.4"

__email__ = "pdreis@fc.ul.pt"
__status__ = "Development"


def getTitrableSites(pdb):
    config.f_in = pdb
    config.params['ffID'] = 'G54A7'
    config.script_dir = os.path.dirname(__file__)

    tit_mol = Molecule()

    tit_mol.makeSimpleSites()

    sites = tit_mol.getSitesOrdered()
    sites_keys = []
    for site in sites:
        sitename = site.getName()
        sitenumber = site.getResNumber()
        sitenumber = convertTermini(sitenumber)
        if sitename in ('NTR', 'CTR'):
            if sitename == 'NTR':
                sites_keys.append('{0}N'.format(sitenumber))
            else:
                sites_keys.append('{0}C'.format(sitenumber))
        else:
            sites_keys.append(str(sitenumber))

        print sitenumber, sitename

    return sites_keys


class Titration(object):
    """Main pypka class

    Serves as a wrapper to all other classes

    Attributes:
        _pKas: A dict with the calculated pKa values.
    """
    def __init__(self, parameters, sites='all', debug=None, datfile=None):
        """
        self._pKas = {}
        """
        self._pKas = {}

        if sites: # None if from CLI
            parameters['sites_A'] = sites
            if sites != 'all':
                config.sites = sites

        if datfile:
            config.f_dat = datfile
            parameters = readSettings(datfile)

        # Check Input Variables Validity
        inputParametersFilter(parameters)

        print 'Start Preprocessing'
        self.preprocessing()

        print config.tit_mole._NTR, config.tit_mole._CTR
        print config.tit_mole.getSites()
        exit()

        self.processDelPhiParams()

        print 'Start PB Calculations'
        self.DelPhiLaunch()

        print 'API exited successfully'

    def preprocessing(self):
        # Creating instance of TitratingMolecule
        config.tit_mole = Molecule()

        if config.f_in_extension == 'gro':
            groname = config.f_in
            if len(config.sites) > 0:
                chains_length, chains_res = inputPDBCheck(config.f_in, config.sites)
                config.tit_mole.loadSites(chains_length, chains_res)
            else:
                log.inputVariableError('sites',
                                       'defined.',
                                       'When using a .gro file format input is used, '
                                       'sites needs to be defined')

        if config.f_in_extension == 'pdb':
            # Reading .st files
            # If the titrable residues are defined
            if len(config.sites) > 0:
                chains_length, chains_res = inputPDBCheck(config.f_in, config.sites)
                config.tit_mole.loadSites(chains_length, chains_res)
            # If the titrable residues are not defined and
            # the input pdb file is incomplete
            elif config.params['clean_pdb']:
                chains_res, sites = config.tit_mole.makeSimpleSites()
                print 'after simpleSites->', config.sites, config.tit_mole.getSites().keys()
            # If the titrable residues are not defined and
            # the input pdb is not missing any atoms
            else:
                chains_res, sites = config.tit_mole.makeSimpleSites()
                config.tit_mole.deleteAllSites()
                config.tit_mole.makeSites(sites=sites)

            termini = {config.tit_mole._NTR: config.tit_mole._NTR_atoms,
                       config.tit_mole._CTR: config.tit_mole._CTR_atoms}
            # Creates a .pdb input for DelPhi, where residues are in their standard state
            if config.params['clean_pdb']:
                inputpqr = 'clean.pqr'
                outputpqr = 'cleaned_tau.pqr'
                sites = config.tit_mole.getSites()
                site_numb_n_ref = {}
                for site in sites:
                    site_numb_n_ref[site] = sites[site].getRefTautomerName()
                cleanPDB(config.f_in, config.pdb2pqr, chains_res,
                         termini, config.userff, config.usernames,
                         inputpqr, outputpqr, site_numb_n_ref)
            
                log.checkDelPhiErrors('LOG_addHtaut')
                print 'before makeSites->', config.sites, config.tit_mole.getSites().keys()
                config.tit_mole.deleteAllSites()
                config.tit_mole.makeSites(useTMPgro=True, sites=sites.keys())
            else:
                pdb2gro(config.f_in, 'TMP.gro', config.tit_mole.box, config.sites, termini)
            groname = 'TMP.gro'

        config.tit_mole.readGROFile(groname)

    def processDelPhiParams(self):
        # TODO: scale is only input in .pHmdp, not gsize
        #if pbc_dim == 2:
        #    params['scaleP'] = (float(params['gsizeP']) - 1) / (config.tit_mole.box[0] * 10)
        #    params['scaleM'] = int(4 / params['scaleP'] + 0.5) * params['scaleP']

        # Storing DelPhi parameters and Creates DelPhi data structures

        config.params['precision'] = 'single' # TODO: add to input parameter file
        delphimol = Delphi(config.f_crg, config.f_siz, 'delphi_in_stmod.pdb',
                           config.tit_mole.getNAtoms(),
                           config.params['gsizeM'],
                           config.params['scaleM'],
                           config.params['precision'],
                           epsin=config.params['epsin'],
                           epsout=config.params['epssol'],
                           conc=config.params['ionicstr'],
                           ibctyp=config.params['bndcon'],
                           res2=config.params['maxc'],
                           nlit=config.params['nlit'],
                           nonit=config.params['nonit'],
                           relfac=config.params['relfac'],
                           relpar=config.params['relpar'],
                           pbx=config.params['pbx'],
                           pby=config.params['pby'],
                           debug=config.debug, outputfile='LOG_readFiles')

        log.checkDelPhiErrors('LOG_readFiles', 'readFiles')

        # Loads delphi4py object as TitratingMolecule attributes
        config.tit_mole.loadDelPhiParams(delphimol)

        if config.debug:
            config.tit_mole.printAllSites()
            config.tit_mole.printAllTautomers()
            print delphimol

    def DelPhiLaunch(self):
        if len(config.tit_mole.getSites()) < 1:
            raise Exception('At least one site has to be correctly defined.')

        # Runs DelPhi simulations for all tautomers
        results = startPoolProcesses(runDelPhiSims,
                                     config.tit_mole.iterAllSitesTautomers(),
                                     config.params['ncpus'])

        # Calculates the pKint of all tautomers
        config.tit_mole.calcpKint(results)

        # Calculates sites interaction energies and write .dat file
        config.tit_mole.calcSiteInteractionsParallel(config.params['ncpus'])

        #  Monte Carlo sampling
        pKas, pmeans = config.tit_mole.runMC()

        sites = config.tit_mole.getSitesOrdered()

        c = -1
        for i in pKas:
            c += 1
            site = sites[c]._res_number
            pK = i[0]
            if pK != 100.0:
                self._pKas[site] = pK
            else:
                self._pKas[site] = '-'
        self._pmeans = pmeans

    def getAverageProt(self, site, pH):
        pKa = self[site]
        if type(pKa) == str:
            return 'pk Not In Range'
        average_prot = 10 ** (pKa - pH) / (1 + 10 ** (pKa - pH))
        return average_prot

    def getProtState(self, site, pH):
        state = 'undefined'
        average_prot = self.getAverageProt(site, pH)

        if type(average_prot) == str:
            return state, average_prot

        if average_prot > 0.9:
            state = 'protonated'
        elif average_prot < 0.1:
            state = 'deprotonated'

        return state, average_prot

    def getTitration(self, site, pH='all'):
        site = self.correct_site_numb(site)
        pmeans = []
        for pH in self._pmeans.keys():
            self._pmeans[pH][site]

    def __iter__(self):
        self._iterpKas = []
        for site in config.tit_mole.getSitesOrdered():
            self._iterpKas.append(site.getResNumber())
        self._iternumb = -1
        self._itermax = len(self._iterpKas)
        return self

    def next(self):
        self._iternumb += 1
        if self._iternumb < self._itermax:
            site = self._iterpKas[self._iternumb]
            if site > config.terminal_offset:
                if site - config.terminal_offset == config.tit_mole._NTR:
                    site = 'NTR'
                elif site - config.terminal_offset == config.tit_mole._CTR:
                    site = 'CTR'
                else:
                    raise Exception('Something is terribly wrong')
            return site
        else:
            raise StopIteration

    def correct_site_numb(self, numb):
        if numb == 'NTR':
            numb = config.tit_mole._NTR + config.terminal_offset
        elif numb == 'CTR':
            numb = config.tit_mole._CTR + config.terminal_offset
        if type(numb) == str:
            try:
                numb = int(numb)
            except:
                raise Exception('Unknown site')
        return numb

    def __getitem__(self, numb):
        numb = self.correct_site_numb(numb)
        return self._pKas[numb]

    def __str__(self):
        output = '  Site   Name      pK'
        sites = config.tit_mole.getSites()

        for site in self._pKas:
            sitename = sites[site].getName()
            pk = self._pKas[site]
            if pk != '-':
                pk = round(pk, 2)
            else:
                pk = 'Not In Range'
            site = convertTermini(site)
            output += '\n{0:>6}    {1:3}    {2:>}'.format(site,
                                                          sitename, pk)
        return output


def CLI():
    # Assignment of global variables
    parameters = checkParsedInput()
    Titration(parameters, sites=None)
    print 'CLI exited successfully'

if __name__ == "__main__":
    CLI()
