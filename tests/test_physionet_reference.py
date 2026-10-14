from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from scripts.physionet_reference import decode_wfdb16, LEADS, select_records


def record(tmp_path):
    values=(np.arange(12000).reshape(1000,12)%200-100).astype('<i2')
    signal=tmp_path/'test.dat';signal.write_bytes(values.tobytes())
    lines=['test 12 100 1000']
    for channel,lead in enumerate(LEADS):
        checksum=int(values[:,channel].astype(np.int64).sum())%65536
        lines.append(f'test.dat 16 1000.0(0)/mV 16 0 {values[0,channel]} {checksum} 0 {lead}')
    header=tmp_path/'test.hea';header.write_text('\n'.join(lines))
    return header,signal,values


def test_decodes_calibrated_original_values(tmp_path):
    header,signal,values=record(tmp_path)
    np.testing.assert_array_equal(decode_wfdb16(header,signal),values.astype(float)/1000)


@pytest.mark.parametrize('fault',['bytes','checksum','format','unit','gain','lead'])
def test_rejects_corrupted_or_unsupported_records(tmp_path,fault):
    header,signal,_=record(tmp_path)
    text=header.read_text()
    if fault=='bytes':signal.write_bytes(signal.read_bytes()[:-2])
    elif fault=='checksum':
        raw=bytearray(signal.read_bytes());raw[100]^=1;signal.write_bytes(raw)
    elif fault=='format':text=text.replace('test.dat 16 ','test.dat 212 ',1)
    elif fault=='unit':text=text.replace('/mV','/uV',1)
    elif fault=='gain':text=text.replace('1000.0(0)','0.0(0)',1)
    elif fault=='lead':text=text.rsplit('V6',1)[0]+'V5'
    header.write_text(text)
    with pytest.raises(ValueError):decode_wfdb16(header,signal)


def test_selection_is_by_id_and_distinct_patient_within_provider_folds():
    df=pd.DataFrame([{'ecg_id':fold*100+i,'strat_fold':fold,'patient_id':fold*100+i//2} for fold in [1,9,10] for i in range(10)])
    selected=select_records(df.sample(frac=1,random_state=3))
    assert [int(row.ecg_id) for row in selected]==[fold*100+i for fold in [1,9,10] for i in [0,2,4,6]]
    assert len({row.patient_id for row in selected})==12
