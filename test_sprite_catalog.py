"""Critical placement rules: phase gates, approval and variant deduplication."""
import unittest
from copy import deepcopy
from sprite_catalog import placements


def entry(site, start=1180, end=1180, priority=10):
    return dict(id=site+str(priority), site_id=site, asset='image.png',
                approval=dict(provisional_map_use=True), technical_qa=dict(status='pass'),
                availability=dict(from_year=start, through_year=end), selection_priority=priority)


class PlacementRules(unittest.TestCase):
    def test_montfort_is_excluded_at_1180(self):
        montfort=entry('montfort',1226,1271)
        self.assertEqual(placements(dict(assets=[montfort]),1180),[])
        self.assertEqual(placements(dict(assets=[montfort]),1250),[montfort])
        self.assertEqual(placements(dict(assets=[montfort]),1272),[])

    def test_only_highest_priority_variant_places(self):
        sheet=entry('krak'); alternate=entry('krak',priority=20)
        self.assertEqual(placements(dict(assets=[sheet,alternate]),1180),[alternate])

    def test_missing_unapproved_and_failed_qa_never_place(self):
        valid=entry('belvoir')
        missing=deepcopy(valid);missing['asset']=None
        unapproved=deepcopy(valid);unapproved['approval']['provisional_map_use']=False
        failed=deepcopy(valid);failed['technical_qa']['status']='fail'
        self.assertEqual(placements(dict(assets=[missing,unapproved,failed]),1180),[])


if __name__=='__main__':
    unittest.main()
