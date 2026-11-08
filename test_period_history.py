"""Period scope and record coverage are essential historical-map constraints."""
import unittest
from period_history import build,within


class PeriodHistory(unittest.TestCase):
    def test_full_source_coverage_and_scope(self):
        m=build()
        self.assertEqual((m['title'],m['from_year'],m['through_year']),('Crusader Period',1095,1291))
        self.assertEqual(len(m['sites']),147)
        self.assertEqual(len({s['id'] for s in m['sites']}),147)
        for s in m['sites']:
            self.assertTrue(s['occupation'])
            self.assertTrue(s['siege_label'])
            for e in s['sieges']:
                self.assertLessEqual(1095,e['from_year'])
                self.assertLessEqual(e['from_year'],e['through_year'])
                self.assertLessEqual(e['through_year'],1291)

    def test_date_clipping_does_not_invent_an_end_date(self):
        self.assertEqual(within('Lusignan 1192 - 1489'),'Lusignan 1192–1291 (continues)')
        self.assertEqual(within('Hospitaller 1309 - 1522'),'')
        self.assertEqual(within('1189 - 91'),'1189–1191')

    def test_separate_damietta_sieges_and_later_sieges_excluded(self):
        sites={s['modern_name']:s for s in build()['sites']}
        self.assertEqual([(e['from_year'],e['through_year']) for e in sites['Damietta']['sieges']],[(1169,1169),(1218,1219),(1249,1249)])
        self.assertFalse(sites['Famagusta']['sieges'])
        self.assertFalse(sites['Rhodes']['sieges'])
        self.assertEqual(sites['Montfort']['siege_label'],'1266; June 1271')


if __name__=='__main__':unittest.main()
