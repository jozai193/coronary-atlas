import json
from ml.schema import ROOT,FEATURES,NUMERIC,read_data


def test_sample_origins_cover_inputs_without_inventing_clinical_review():
    source=read_data()
    samples=json.loads((ROOT/'data/processed/sample_patients.json').read_text())
    assert len(samples)==2
    for sample in samples:
        p=sample['provenance']
        explicit,derived,default,unknown=map(set,(p['explicit_fields'],p['derived_fields'],p['default_fields'],p['unknown_fields']))
        assert not explicit&derived and not explicit&default and not derived&default
        assert not unknown&(explicit|derived|default)
        assert explicit|derived|default|unknown==set(FEATURES)
        assert p['clinician_reviewed'] is False and sample['synthetic'] is True
        assert unknown=={'Q Wave','St Elevation','LVH','Poor R Progression','BBB','VHD'}
        assert all(sample['features'][name] is None for name in unknown)
        assert len(FEATURES)-len(unknown)>=28
        for name in default:
            expected=float(source[name].median()) if name in NUMERIC else str(source[name].mode()[0])
            assert sample['features'][name]==expected
        f=sample['features']
        assert f['BMI']==f['Weight']/(f['Length']/100)**2
