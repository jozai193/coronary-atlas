"""Create visibly synthetic demo profiles, not held-out evaluation patients."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ml.schema import *

df=read_data()
base={c:float(df[c].median()) if c in NUMERIC else str(df[c].mode()[0]) for c in FEATURES}
base['BMI'] = base['Weight'] / (base['Length'] / 100) ** 2
profiles=[
    ('a','Profile A · age 42',dict(Age=42,DM='0',HTN='0',BP=115,PR=70,FBS=88,LDL=85,TG=100,HDL=48,**{'Typical Chest Pain':'0','Atypical':'Y','St Depression':'0','Tinversion':'0','EF-TTE':60,'Region RWMA':'0','Sex':'Fmale','Current Smoker':'0'})),
    ('b','Profile B · age 72',dict(Age=72,DM='1',HTN='1',BP=155,PR=85,FBS=180,LDL=155,TG=230,HDL=32,**{'Typical Chest Pain':'1','Atypical':'N','St Depression':'1','Tinversion':'1','EF-TTE':35,'Region RWMA':'2','Sex':'Male','Current Smoker':'1'})),
]
samples=[]
for id,name,changes in profiles:
    features=base|changes
    features['BMI']=features['Weight'] / (features['Length'] / 100) ** 2
    # Unchosen investigation flags must not imply a documented negative test
    # or valve severity merely because a cohort mode happens to be frequent.
    unknown_fields=[c for c in ['Q Wave','St Elevation','LVH','Poor R Progression','BBB','VHD'] if c not in changes]
    for field in unknown_fields: features[field]=None
    provenance=dict(explicit_fields=[c for c in FEATURES if c in changes],
                    derived_fields=['BMI'],
                    default_fields=[c for c in FEATURES if c not in changes and c!='BMI' and c not in unknown_fields],
                    unknown_fields=unknown_fields,
                    default_method='Source-cohort numeric median or categorical mode; not a clinical case report.',
                    clinician_reviewed=False)
    samples.append(dict(id=id,name=name,synthetic=True,note='Synthetic demonstration profile assembled from cohort summary values and explicit overrides. Unspecified ECG flags and valve findings remain unknown. No ground truth; not validation evidence.',features=features,provenance=provenance))
write_json(ROOT/'data/processed/sample_patients.json',samples)
