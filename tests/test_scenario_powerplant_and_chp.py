import os
import requests
from nose.tools import eq_
from deflex import config as cfg, basic_scenario, geometries


class TestScenarioPowerplantsAndCHP:
    @classmethod
    def setUpClass(cls):
        """Download pp-file from osf."""
        url = 'https://osf.io/qtc56/download'
        path = cfg.get('paths', 'powerplants')
        file = 'de21_pp.h5'
        filename = os.path.join(path, file)
    
        if not os.path.isfile(filename):
            req = requests.get(url)
            with open(filename, 'wb') as fout:
                fout.write(req.content)
        cls.regions = geometries.deflex_regions(rmap='de21')
        cls.pp = basic_scenario.scenario_powerplants(
            dict(), cls.regions, 2014, 'de21', 1)

    def scenario_pp_test(self):
        eq_(float(self.pp['volatile_source']['DE03', 'wind']), 3052.8)
        eq_(float(self.pp['transformer'].loc['capacity', ('DE03', 'lignite')]),
            1135.6)
    
    def test_scenario_transmission(self):
        lines = basic_scenario.scenario_transmission(
            self.pp, self.regions, 'de21')
        eq_(int(lines.loc['DE07-DE05', ('electrical', 'capacity')]), 1978)
        eq_(int(lines.loc['DE07-DE05', ('electrical', 'distance')]), 199)
        eq_(float(lines.loc['DE07-DE05', ('electrical', 'efficiency')]), 0.9)
        lines = basic_scenario.scenario_transmission(
            self.pp, self.regions, 'de21', copperplate=True)
        eq_(float(lines.loc['DE07-DE05', ('electrical', 'capacity')]),
            float('inf'))
        eq_(str(lines.loc['DE07-DE05', ('electrical', 'distance')]), 'nan')
        eq_(float(lines.loc['DE07-DE05', ('electrical', 'efficiency')]), 1.0)
       
    def test_scenario_commodity_sources(self):
        src = basic_scenario.scenario_commodity_sources(
            self.pp, 2014)['commodity_source']
        eq_(round(src.loc['costs', ('DE', 'hard coal')], 2), 8.93)
        eq_(round(src.loc['emission',  ('DE', 'natural gas')], 2), 201.24)
        
    def test_chp(self):
        eq_(int(self.pp['transformer'].loc['capacity', ('DE01', 'hard coal')]),
            1291)
        transf = basic_scenario.scenario_chp(
            self.pp, self.regions, 2014, 'de21')['transformer']
        eq_(int(transf.loc['capacity', ('DE01', 'hard coal')]), 485)
        eq_(int(transf.loc['capacity_elec_chp', ('DE01', 'hard coal')]), 806)
