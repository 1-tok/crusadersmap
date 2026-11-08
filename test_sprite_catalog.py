"""Critical placement rules: phase gates, approval and variant deduplication."""
import unittest
from copy import deepcopy
from sprite_catalog import placements, build


def entry(site, start=1180, end=1180, priority=10):
    return dict(id=site+str(priority), site_id=site, asset='image.png',
                approval=dict(provisional_map_use=True), technical_qa=dict(status='pass'),
                availability=dict(from_year=start, through_year=end), selection_priority=priority)


class PlacementRules(unittest.TestCase):
    def test_bosphorus_companions_only_place_in_detail_view(self):
        c=build();sites={'galata-sykai','chrysopolis','chalcedon'}
        self.assertFalse(sites & {e['site_id'] for e in placements(c,1180)})
        detail=placements(c,1180,view='constantinople-detail')
        self.assertEqual(sites,{e['site_id'] for e in detail})
        self.assertTrue(all(e['display_width_units']==256 for e in detail))
        from build_constantinople_detail import layout
        self.assertEqual(len(layout(c)),4)

    def test_constantinople_uses_double_city_footprint(self):
        c=build()
        e=next(e for e in placements(c,1180) if e['site_id']=='constantinople')
        self.assertEqual(e['display_width_units'],2*512)
        self.assertEqual(e['visual_footprint']['display_width_atlas_px'],1024)
        self.assertEqual(e['technical_qa']['dimensions_px'][0],2048)
        self.assertEqual(e['map_region'],'aegean')
        self.assertAlmostEqual(e['longitude'],28+58/60+60/3600)
        self.assertAlmostEqual(e['latitude'],41+30/3600)

    def test_unreleased_city_batch_never_imports(self):
        from unittest.mock import patch
        import sprite_catalog
        original_read=sprite_catalog.read
        def held_batch(path):
            if path.parent.name=='greece-egypt-1180-batch04':
                return dict(release_status='audit-hold',assets=[dict(id='must-not-import')])
            return original_read(path)
        with patch.object(sprite_catalog,'read',side_effect=held_batch):
            c=sprite_catalog.build()
        self.assertNotIn('must-not-import',{e['id'] for e in c['assets']})
        self.assertEqual(len([e for e in c['assets'] if e.get('variant')=='generated-city']),25)

    def test_explicit_1180_ineligibility_overrides_date_window(self):
        for site in ('montfort', 'chateau-pelerin'):
            e=entry(site); e['period_1180_eligible']=False
            self.assertEqual(placements(dict(assets=[e]),1180),[])

    def test_recovered_catalog_contract(self):
        c=build()
        self.assertEqual(len(c['assets']),len({e['id'] for e in c['assets']}))
        for e in c['assets']:
            self.assertTrue(e['coordinate_evidence']['url'].startswith('https://'))
            self.assertEqual(e['coordinates'],[e['longitude'],e['latitude']])
            self.assertEqual(e['approval_for_placement'],bool(e['asset']) and e['period_1180_eligible'] and e['geographic_placement_ready'])
            if e['asset']:
                self.assertEqual(e['technical_qa']['alpha_extrema'][0],0)
                self.assertGreater(e['technical_qa']['alpha_extrema'][1],0)
                self.assertIn('visual_footprint',e)
        p=placements(c,1180)
        self.assertEqual(len(p),len({e['site_id'] for e in p}))
        self.assertNotIn('montfort',{e['site_id'] for e in p})
        self.assertNotIn('chateau-pelerin',{e['site_id'] for e in p})

    def test_montfort_is_excluded_at_1180(self):
        montfort=entry('montfort',1226,1271)
        self.assertEqual(placements(dict(assets=[montfort]),1180),[])
        self.assertEqual(placements(dict(assets=[montfort]),1250),[montfort])
        self.assertEqual(placements(dict(assets=[montfort]),1272),[])

    def test_recovered_archive_approval_and_provenance(self):
        c=build()
        archive=[e for e in c['assets'] if e['id'].startswith('archive-')]
        self.assertEqual(len(archive),40)
        self.assertEqual(sum(e['variant']=='archive-primary' for e in archive),16)
        self.assertFalse(any(e['asset'] is None for e in c['assets']))
        legacy=dict(assets=[e for e in c['assets'] if e.get('variant')!='generated-city'])
        self.assertEqual(len(placements(legacy,1180)),15)
        for site in ('montfort','chateau-pelerin'):
            e=next(e for e in archive if e['site_id']==site and e['variant']=='archive-primary')
            self.assertTrue(e['approval']['provisional_map_use'])
            self.assertFalse(e['approval_for_placement'])
            self.assertNotIn(site,{x['site_id'] for x in placements(c,1180)})
            self.assertIn(site,{x['site_id'] for x in placements(c,1250)})

    def test_only_highest_priority_variant_places(self):
        sheet=entry('krak'); alternate=entry('krak',priority=20)
        self.assertEqual(placements(dict(assets=[sheet,alternate]),1180),[alternate])

    def test_unlocated_art_is_approved_but_never_exported(self):
        c=build();e=next(e for e in c['assets'] if e['id']=='damietta-1180-v1')
        self.assertTrue(e['approval']['provisional_map_use'])
        self.assertFalse(e['approval_for_placement'])
        self.assertNotIn(e,placements(c,1180))

    def test_insets_match_existing_atlas_region_math(self):
        # Load the actual atlas Region class without rough.py's terrain I/O.
        import ast
        import numpy as np
        from pathlib import Path
        from pyproj import Transformer
        tree=ast.parse(Path('rough.py').read_text())
        node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Region')
        namespace=dict(np=np,Transformer=Transformer)
        exec(compile(ast.Module(body=[node],type_ignores=[]),'rough.py','exec'),namespace)
        Region=namespace['Region']
        import frame
        from sprite_geometry import sheet_anchor
        for name,point in [('aegean',[23.726,37.971]),('delta',[31.2578,30.0428])]:
            cfg=frame.INSETS[name];r=Region.from_lonlat(cfg['proj'],cfg['ext'],4800)
            x,y=r.ll_px(*point);bx,by=(190,190) if name=='aegean' else (190,13760-r.h)
            actual=sheet_anchor(dict(map_region=name,coordinates=point))
            self.assertAlmostEqual(actual[0],bx+x,places=7)
            self.assertAlmostEqual(actual[1],by+y,places=7)

    def test_missing_unapproved_and_failed_qa_never_place(self):
        valid=entry('belvoir')
        missing=deepcopy(valid);missing['asset']=None
        unapproved=deepcopy(valid);unapproved['approval']['provisional_map_use']=False
        failed=deepcopy(valid);failed['technical_qa']['status']='fail'
        self.assertEqual(placements(dict(assets=[missing,unapproved,failed]),1180),[])


if __name__=='__main__':
    unittest.main()
