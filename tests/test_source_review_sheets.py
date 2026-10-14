from html.parser import HTMLParser
import json
from ml.schema import ROOT,TARGETS,read_data
from scripts.build_source_review_sheets import generate
from scripts.create_review_profiles import create


class TableRows(HTMLParser):
    def __init__(self):
        super().__init__();self.rows=[];self.row=None;self.cell=None
    def handle_starttag(self,tag,attrs):
        if tag=='tr':self.row=[]
        if tag in ('th','td'):self.cell=''
    def handle_data(self,data):
        if self.cell is not None:self.cell+=data
    def handle_endtag(self,tag):
        if tag in ('th','td') and self.row is not None:self.row.append(self.cell);self.cell=None
        if tag=='tr' and self.row is not None:self.rows.append(self.row);self.row=None


def test_source_review_sheets_preserve_every_value_and_do_not_publish_predictions():
    generate(verify=True)
    source=read_data();schema=json.loads((ROOT/'data/processed/feature_schema.json').read_text(encoding='utf-8'))
    profiles=create()
    for index in (0,1):
        text=(ROOT/f'frontend/public/review/source-record-{index+1}.html').read_text(encoding='utf-8')
        parser=TableRows();parser.feed(text)
        values={row[0]:row[1] for row in parser.rows if len(row)>=2}
        row=source.iloc[profiles[index]['source']['record_index']]
        for field in schema:assert values[field['label']]==str(row[field['name']]),field['name']
        for target,name in TARGETS.items():assert values[target.upper()]==str(row[name])
        assert 'kg/m²' in text and '10³/µL' in text and 'Â' not in text
        assert 'Recorded target labels — not predictions' in text
        assert 'not new predictions or independent validation' in text
        assert 'CC BY 4.0' in text and '10.24432/C5461K' in text
        assert '<script' not in text and '<iframe' not in text
