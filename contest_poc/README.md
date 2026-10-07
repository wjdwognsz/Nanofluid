# 2026 섬유연구자×소재데이터 아이디어 경진대회 — 공개 데이터 개념증명(PoC)

공개 GitHub 데이터만으로 실행한 소규모 검증 스크립트와 결과(JSON)입니다.
**데이터 파일은 이 저장소에 포함하지 않았습니다.** 라이선스가 저장소마다 다르기 때문입니다.
polyVERSE는 Georgia Tech 비상업 라이선스이고, 다른 저장소 다수는 라이선스 파일이 없습니다.
아래 명령으로 각자 내려받아 쓰세요.

## 1. 환경
```bash
pip install numpy pandas scipy scikit-learn rdkit openpyxl
```

## 2. 데이터 받기 (모두 GitHub)
```bash
mkdir -p data && cd data
git clone --depth 1 https://github.com/Ramprasad-Group/polyVERSE.git           # 기체·수증기 투과/확산/용해, CED, chi 등
git clone --depth 1 https://github.com/taltechloc/Cogni-E-Spin-FIRE.git        # Cogni-e-SpinDB 1.0 CSV (전기방사 809건)
git clone --depth 1 https://github.com/Sixty-four-floor/Exhaustion-PLA.git     # PLA 분산염료 흡진율 131건
git clone --depth 1 https://github.com/jsunn-y/PolymerGasMembraneML.git        # Yang et al. Sci. Adv. 2022 기체투과
git clone --depth 1 https://github.com/OfficialBhattacharya/KaggleNotebooks.git  # PoLyInfo 유래 Tg·기체 원자료 미러
git clone --depth 1 https://github.com/liugangcode/GREA.git                    # O2 투과
git clone --depth 1 https://github.com/IBM/materials.git                       # NETL/ACS-AMI 등 고분자 벤치마크
git clone --depth 1 https://github.com/jday96314/NeurIPS-polymer-prediction.git # LAMALAB Tg 미러
cd ..
```
`virtual_rr.py`는 파일 경로를 하드코딩해 두었습니다. 내려받은 위치에 맞게 경로를 고친 뒤 실행하세요.

## 3. 스크립트와 검증 내용

| 스크립트 | 검증하는 질문 | 결과 파일 |
|---|---|---|
| `poc_electrospin.py` | 단위·범위 조화. 무작위 CV와 논문 단위 CV 비교. 같은 조건의 논문 간 재현성. 계통수 사전정보 비교 | `results/electrospin_summary.json` |
| `poc_anchor.py` (+`poc_electrospin_features.py`) | 새 출처에서 기준점 k개로 보정했을 때의 회복 곡선과 논문 편차 비중 | `results/anchor_summary.json` |
| `poc_dye.py` | 염색(PLA 흡진율) 데이터의 감사, 출처 효과, 앵커 보정 | `results/dye_summary.json` |
| `virtual_rr.py` | 공개 DB 간 같은 고분자 값의 일치도(계보·재현성)와 단위 혼재 | `results/virtual_rr.json` |
| `poc_taxonomy_gas.py` (+`featurize.py`) | 소재 계통수 거리가 물성 유사도를 설명하는지, 계열 하나를 뺀 소수샷 계층 풀링 | `results/taxonomy_pair_summary.json` |
| `poc_transfer.py`, `poc_transfer_null.py` | 전이 가능성 점수와 실제 이득의 관계, 징검다리 체인, 순열 대조군 | `results/transfer_*.json` |
| `harmon_h2o.py` | 같은 고분자의 수증기 수송값이 시험 조건에 따라 얼마나 달라지는지 | (표준 출력) |
| `survivor.py` | 성공 데이터만 쓴 모델과 실패를 포함한 모델의 실패 탐지 AUC | (표준 출력) |

모든 수치는 랜덤포레스트 기반의 예비 결과입니다.
제출용으로 쓰려면 시드를 반복하고 신뢰구간을 다시 계산하세요.
