"""Build a bounded, attributed ECG reference library; never fits CAD models."""
import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/external_audit/physionet_v1/raw/ptbxl-verified'
OUT = ROOT / 'frontend/public/reference-ecg'
BASE = 'https://physionet.org/files/ptb-xl/1.0.3/'
MIRROR = 'https://physionet-open.s3.amazonaws.com/ptb-xl/1.0.3/'
LEADS = ['I', 'II', 'III', 'AVR', 'AVL', 'AVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def provider_hashes():
    entries = {}
    for line in (RAW / 'SHA256SUMS.txt').read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        entries[name.lstrip('./')] = digest
    return entries


def check_file(name, hashes):
    if sha(RAW / name) != hashes[name]:
        raise ValueError(f'Provider checksum mismatch: {name}')


def select_records(df):
    selected = []
    seen = set()
    for fold in [1, 9, 10]:
        chosen = []
        for _, row in df[df.strat_fold == fold].sort_values('ecg_id').iterrows():
            if row.patient_id not in seen:
                chosen.append(row)
                seen.add(row.patient_id)
            if len(chosen) == 4:
                break
        if len(chosen) != 4:
            raise ValueError('Insufficient distinct source patients in provider fold')
        selected.extend(chosen)
    return selected


def decode_wfdb16(header, signal):
    """Strict decoder for the exact fixed-format PTB-XL WFDB-16 release.

    Rejects other encodings, skew, calibration, length or checksum mismatches.
    Independent header first-sample and checksum checks protect the rendering.
    """
    lines = Path(header).read_text().splitlines()
    first = lines[0].split()
    if len(first) != 4 or first[1:] != ['12', '100', '1000'] or len(lines) != 13:
        raise ValueError('Unsupported WFDB record dimensions')
    raw = np.frombuffer(Path(signal).read_bytes(), dtype='<i2')
    if raw.size != 12000:
        raise ValueError('Unexpected signal byte length')
    samples = raw.reshape(1000, 12)
    values = np.empty(samples.shape, dtype=float)
    names = []
    for channel, line in enumerate(lines[1:]):
        parts = line.split()
        if len(parts) != 9 or parts[0] != Path(signal).name or parts[1] != '16' or parts[3] != '16' or parts[7] != '0':
            raise ValueError('Unsupported WFDB channel encoding')
        calibration = re.fullmatch(r'([0-9.]+)\((-?\d+)\)/mV', parts[2])
        if not calibration:
            raise ValueError('Unsupported calibration or unit')
        gain, baseline = float(calibration[1]), int(calibration[2])
        if gain <= 0 or int(parts[4]) != baseline:
            raise ValueError('Invalid ADC baseline/gain')
        if int(samples[0, channel]) != int(parts[5]) or int(samples[:, channel].astype(np.int64).sum()) % 65536 != int(parts[6]) % 65536:
            raise ValueError('WFDB channel initial value/checksum mismatch')
        names.append(parts[8])
        values[:, channel] = (samples[:, channel].astype(float) - baseline) / gain
    if names != LEADS or not np.isfinite(values).all():
        raise ValueError('Unexpected lead order or nonfinite signal')
    return values


def download(name, hashes):
    if not re.fullmatch(r'records100/\d{5}/\d{5}_lr\.(?:hea|dat)', name):
        raise ValueError('Unexpected source path')
    path = RAW / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or sha(path) != hashes[name]:
        pending = path.with_suffix(path.suffix + '.download')
        subprocess.run(['curl.exe', '-f', '-sS', '-L', '--connect-timeout', '10',
            '--max-time', '40', MIRROR + name, '-o', str(pending)], check=True, capture_output=True)
        if sha(pending) != hashes[name]:
            raise ValueError(f'Downloaded bytes do not match provider: {name}')
        pending.replace(path)
    check_file(name, hashes)


def plot(values, ecg_id, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MultipleLocator
    plt.rcParams['svg.hashsalt'] = 'coronary-atlas-ptbxl-v1'
    figure, axes = plt.subplots(3, 4, figsize=(12, 6.5), facecolor='#102c30')
    order = [['I', 'AVR', 'V1', 'V4'], ['II', 'AVL', 'V2', 'V5'], ['III', 'AVF', 'V3', 'V6']]
    bound = max(1.5, np.ceil(np.abs(values[:250]).max() * 2) / 2 + .25)
    for row in range(3):
        for column in range(4):
            axis = axes[row, column]
            lead = order[row][column]
            axis.set_facecolor('#102c30')
            axis.plot(np.arange(250) / 100, values[:250, LEADS.index(lead)], color='#8de4c6', linewidth=.8)
            axis.set(xlim=(0, 2.5), ylim=(-bound, bound), title=lead, xlabel='Seconds', ylabel='mV')
            axis.title.set_color('#e2eeea')
            axis.xaxis.label.set_color('#b5ccc8'); axis.yaxis.label.set_color('#b5ccc8')
            axis.tick_params(colors='#b5ccc8', labelsize=7)
            axis.xaxis.set_major_locator(MultipleLocator(.5)); axis.xaxis.set_minor_locator(MultipleLocator(.1))
            axis.yaxis.set_major_locator(MultipleLocator(1)); axis.yaxis.set_minor_locator(MultipleLocator(.2))
            axis.grid(which='major', color='#456765', linewidth=.5)
            axis.grid(which='minor', color='#254745', linewidth=.3)
            for spine in axis.spines.values(): spine.set_color('#456765')
    figure.suptitle(f'PTB-XL {ecg_id} | source 100 Hz | first 2.5 seconds per lead', color='#e2eeea', fontsize=13)
    figure.text(.5, .01, 'Calibrated source voltage; shared display range; schematic scale. Educational reference, not diagnostic interpretation.', ha='center', color='#b5ccc8', fontsize=8)
    figure.tight_layout(rect=[0, .035, 1, .94])
    figure.savefig(path, format='svg', metadata={'Date': None, 'Creator': 'Coronary Atlas PTB-XL reference renderer'})
    plt.close(figure)


def prepare():
    hashes = provider_hashes()
    for name in ['ptbxl_database.csv', 'scp_statements.csv', 'LICENSE.txt']:
        check_file(name, hashes)
    df = pd.read_csv(RAW / 'ptbxl_database.csv')
    statements = pd.read_csv(RAW / 'scp_statements.csv', index_col=0).fillna('')
    if df.patient_id.isna().any() or df.groupby('patient_id').strat_fold.nunique().max() != 1:
        raise ValueError('Provider patient/fold separation failed')
    selected = select_records(df)
    paths = [str(row.filename_lr) + suffix for row in selected for suffix in ['.hea', '.dat']]
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda name: download(name, hashes), paths))
    OUT.mkdir(parents=True, exist_ok=True)
    cases = []
    for row in selected:
        name = str(row.filename_lr)
        values = decode_wfdb16(RAW / (name + '.hea'), RAW / (name + '.dat'))
        codes = ast.literal_eval(row.scp_codes)
        if not isinstance(codes, dict) or any(k not in statements.index or not isinstance(v, (int, float)) or not 0 <= v <= 100 for k, v in codes.items()):
            raise ValueError('Unexpected source statement/likelihood')
        image_name = f'ptbxl-{int(row.ecg_id):05d}.svg'
        plot(values, int(row.ecg_id), OUT / image_name)
        cases.append(dict(ecg_id=int(row.ecg_id),provider_fold=int(row.strat_fold),
            age=float(row.age) if pd.notna(row.age) and row.age <= 89 else None,
            age_note='Age withheld or privacy protected' if pd.isna(row.age) or row.age > 89 else 'Reported age at ECG',
            sex_source_code=int(row.sex) if pd.notna(row.sex) else None,
            report=str(row.report),validated_by_human=bool(row.validated_by_human),
            statements=[dict(code=key,description=str(statements.loc[key, 'description']),source_likelihood=float(value)) for key, value in codes.items()],
            waveform=f'/reference-ecg/{image_name}',
            source_header=BASE+name+'.hea',source_signal=BASE+name+'.dat',
            header_sha256=hashes[name+'.hea'],signal_sha256=hashes[name+'.dat'],
            waveform_sha256=sha(OUT/image_name)))
    index = dict(source='https://physionet.org/content/ptb-xl/1.0.3/',version='1.0.3',license='CC BY 4.0',
        citation='Wagner et al. PTB-XL v1.0.3, PhysioNet (2022), doi:10.13026/kfzx-aw45; Scientific Data (2020), doi:10.1038/s41597-020-0495-6.',
        selection='First four distinct-patient ECGs by ID from each provider fold 1, 9 and 10. Reference display only, not a benchmark or validation cohort.',
        signal_display='Source 100 Hz WFDB-16; first 250 samples (2.5 seconds) per lead, calibrated to mV; shared vertical range within each figure. Schematic scaling, not diagnostic ECG paper.',
        cases=cases)
    (OUT/'index.json').write_text(json.dumps(index,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    (OUT/'LICENSE.txt').write_bytes((RAW/'LICENSE.txt').read_bytes())
    audit=dict(source=index['source'],acquisition_mirror=MIRROR,metadata_sha256=sha(RAW/'ptbxl_database.csv'),dictionary_sha256=sha(RAW/'scp_statements.csv'),
        provider_checksum_list_sha256=sha(RAW/'SHA256SUMS.txt'),metadata_rows=len(df),unique_patients=int(df.patient_id.nunique()),
        per_fold={str(int(f)):dict(records=len(part),patients=int(part.patient_id.nunique())) for f,part in df.groupby('strat_fold')},
        missing_counts={name:int(df[name].isna().sum()) for name in ['age','sex','height','weight','report']},
        columns=df.columns.tolist(),selected_ecg_ids=[c['ecg_id'] for c in cases],selected_distinct_patients=len({row.patient_id for row in selected}),
        provider_checksums_verified=3+len(paths),waveform_headers_and_channel_checksums_verified=12,
        display_index_sha256=sha(OUT/'index.json'),cad_model_fitted=False,independent_cad_validation=False,
        compatibility='Age/sex/body measurements are incomplete or require reviewed coding/timing. ECG statements are not the UCI ECG input contract. No echo/laboratory/alcohol/lifestyle inputs or angiographic CAD/LAD/LCX/RCA targets are established by this table. No row pairing with the original source cohort.')
    (ROOT/'data/external_audit/physionet_v1/ptbxl-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    print(json.dumps({k:audit[k] for k in ['metadata_rows','unique_patients','selected_ecg_ids','selected_distinct_patients','provider_checksums_verified']},indent=2))


def verify():
    index = json.loads((OUT/'index.json').read_text(encoding='utf-8'))
    hashes = provider_hashes()
    selected = select_records(pd.read_csv(RAW/'ptbxl_database.csv'))
    assert [c['ecg_id'] for c in index['cases']] == [int(row.ecg_id) for row in selected]
    assert len({row.patient_id for row in selected}) == 12
    for case,row in zip(index['cases'],selected,strict=True):
        for suffix in ['.hea','.dat']:check_file(str(row.filename_lr)+suffix,hashes)
        values=decode_wfdb16(RAW/(str(row.filename_lr)+'.hea'),RAW/(str(row.filename_lr)+'.dat'))
        assert values.shape==(1000,12)
        assert case['report']==row.report and case['provider_fold']==int(row.strat_fold)
        assert {item['code']:item['source_likelihood'] for item in case['statements']}==ast.literal_eval(row.scp_codes)
        assert sha(OUT/Path(case['waveform']).name)==case['waveform_sha256']
    print('Verified 12 selected source records, distinct patients, folds, source reports/codes, waveform calibration/checksums and display hashes.')


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','verify']);args=parser.parse_args()
    prepare() if args.mode=='prepare' else verify()
