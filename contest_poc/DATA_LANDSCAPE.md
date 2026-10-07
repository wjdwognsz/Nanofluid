# 공개 데이터 지형 전체 목록 (2026-10-07 조사)

## 표 읽는 법

**링크 확인 등급**
- **접속 확인**: WebFetch, curl, git으로 실제 내용을 열거나 내려받은 경우.
- **미확인(검색 색인에만 존재)**: 검색 결과에 URL이 나왔지만 이 환경의 네트워크 정책 때문에 직접 열지 못한 경우.
- **미확인**: 위 둘 다 아닌 경우.

**수치와 활용도**
- 규모·라이선스 수치는 출처에서 확인된 것만 적었습니다. 모르면 unknown입니다.
- 활용도는 0~3점입니다. 참가자의 문제(바이오 고분자·섬유, 전기방사, 막)에 쓸 수 있는 정도를 뜻합니다.

**조사 한계**
- 조사 중 웹 검색 공용 한도(턴당 200회)가 소진되었습니다.
- 그래서 한국 공공 포털, 특허, 일부 저장소는 검증 범위가 제한적입니다.

## general materials DB (무기 결정 DFT 계산)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Materials Project (MP) + MPcules(분자) + MPContribs | https://materialsproject-build.s3.amazonaws.com/ (MP OpenData S3 버킷, 직접 확인). 웹 포털 next-gen.materialsproject.org는 WebFet… | 접속 확인 | DFT 계산값(무기 결정), MPcules 분자 DFT, MPContribs 커뮤니티 기여 데이터 | 2025-09-25 빌드 summary 문서 210,579건(S3 파일 21개를 직접 내려받아 행 수 집계). 이 중 원소가 C/H/O/N만인 항목 524건(0.25%, 대부분 H2O, HC2N3 같은 소분자 결정과 탄소 동소체), C와 H를 함께 포함한 항목 2,883건(1.4%),… | 생성 에너지, E_hull, 밴드갭(PBE), 체적·전단 탄성률, 유전·압전 텐서, 자성, 밀도, 결정 구조, 표면 에너지, XAS. 분자: 기하구조, 전자구조, 진동, 열역학 | CC BY 4.0(WebSearch 결과에 나온 Wikipedia와 이용약관 기준). API 키 필요. S3 OpenData는 무료 대량 다운로드 가능 | 0 K 완전결정을 가정한 PBE 계산이라 밴드갭이 과소평가됨. ICSD 기반 무기물 편향이 있음. 고분자, 비정질, 공정 이력, 섬유·막 물성은 스키마 자체에 없음 | 1 |

## general materials DB (계산 원자료 저장소 + 실험 EL

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| NOMAD Repository & Archive / NOMAD Oasis | https://nomad-lab.eu/services/repo-arch (WebSearch 결과에 등장, WebFetch는 차단됨). 코드 미러 https://github.com/nomad-coe/nomad 는 g… | 미확인(검색 색인에만 존재) | 60개 이상 코드의 계산 입출력 원자료와 공통 형식 아카이브(GROMACS/LAMMPS MD 파서 포함), Oasis를 통한 실험 데이터 스키마와 ELN | 업로드 엔트리 19,221,889건, 113.4 TB(2025-10-30 Mainz 발표자료, WebSearch 요약). 'more than 100 million calculations'(nomad-lab.eu 소개, WebSearch 요약). 고분자·섬유 엔트리 수는 unknown | 코드별 입력/출력, 총에너지, 구조, MD 궤적, 워크플로 메타데이터(Metainfo 스키마) | CC BY 4.0(nomad-lab.eu WebSearch 요약), 무료, DOI 발급, 10년 이상 보존 | 업로드자가 자율적으로 올리므로 계산 설정이 제각각임. 무기 DFT에 크게 치우쳐 있음. 실험 데이터는 개별 Oasis에 흩어져 있고 공개되는 양이 적음 | 1 |

## general materials DB (계산 + 커뮤니티 아카이브)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Materials Cloud (MC3D, MC2D, Archive) | https://archive.materialscloud.org (WebSearch 결과에 record/412, record/1146 등이 등장, 직접 접속은 차단됨) | 미확인(검색 색인에만 존재) | 무기 결정 DFT(MC3D/MC2D)와 연구자가 올리는 임의 데이터 레코드(Archive) | MC3D PBEsol-v2 기준 고유 구조 32,013개(약 34,000), MC2D 약 3,000개(2,710개 단층 최적화). Archive 레코드 1,000건 이상(NCCR MARVEL 뉴스). 고분자 관련 레코드 예: 'Polymer descriptor data set for … | 무기: 구조, 에너지, 전자·진동 물성. 고분자 Cp 레코드: 원자·분자 기술자 188개와 상온 비열 | 레코드별로 다름. 고분자 Cp 레코드는 CC BY 4.0(WebSearch 요약). 최소 10년 보존 | 무기 결정이 대부분임. 고분자 레코드는 소수이고 크기도 작으며 합성 고분자 중심 | 1 |

## general materials DB (무기 DFT)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| OQMD (Open Quantum Materials Database) | https://oqmd.org/ (WebSearch 결과에 등장, WebFetch 차단). 코드 https://github.com/wolverton-research-group/qmpy 는 직접 확인 | 미확인(검색 색인에만 존재) | DFT 열역학·구조 계산값(ICSD 화합물과 가상 원형 구조) | 1,407,395개 물질(oqmd.org 관련 WebSearch 요약). 다른 출처는 1,226,781개(버전 차이로 보임). JARVIS 재가공본은 oqmd_3d 800k로 표기(jarvis-tools 코드 문자열, 직접 확인) | 생성 에너지, 안정성(convex hull), 밴드갭, 자기모멘트, 격자 구조 | CC BY 4.0, 전체 DB 다운로드 가능(WebSearch 요약) | 무기 결정만 있음. PBE 오차와 가상 구조 편향이 있음 | 0 |
| AFLOW (aflow.org / AFLOWLIB) | https://aflow.org (WebSearch 결과에 aflow.org 강의 PDF들이 등장). 코드 https://github.com/aflow-org/aflow 는 직접 확인 | 미확인(검색 색인에만 존재) | 고처리량 DFT 계산값, 결정 원형(prototype) 라이브러리 | 약 350만 엔트리, 물성 7.25억 건 이상(aflow school 슬라이드, WebSearch). 다른 요약은 400만 화합물, 물성 8억 건. 시점이 달라 생긴 차이로 보임 | 생성 엔탈피, 밴드갭, 탄성(AEL), 열물성(AGL, Debye 근사), 대칭, 원형 | unknown(이번 조사에서 확인 못 함). REST-API와 AFLUX로 무료 조회 가능 | 무기 합금·화합물 중심. 열전도도는 Debye 근사값임 | 0 |
| Alexandria (Ruhr-Univ. Bochum, Schmidt/Marques) | https://alexandria.icams.rub.de/about.html (WebSearch 결과에 등장) | 미확인(검색 색인에만 존재) | 1D/2D/3D 주기 화합물 DFT(PBE, PBEsol, SCAN) | DFT 계산 500만 건 이상(WebSearch 요약). jarvis-tools 표기는 PBE 3D 5M, 2D 200k, 1D 100k, SCAN 3D 500k, PBEsol 3D 500k, 볼록껍질 위 116k(직접 확인) | 구조, 에너지, 안정성, 밴드갭 등 | CC BY 4.0(about 페이지 WebSearch 요약) | 가상 구조가 대부분이고 무기 전용 | 0 |

## general materials DB (DFT/FF/ML 통합)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| JARVIS (NIST) 및 jarvis-tools 데이터셋 모음(Polymer Genome 1k 포함) | https://jarvis.nist.gov/ (WebSearch 결과에 등장). 데이터셋 목록은 https://raw.githubusercontent.com/usnistgov/jarvis/master/jarvis/… | 미확인(검색 색인에만 존재) | DFT(3D/2D), 고전 FF, ML 학습셋, 다른 DB 재가공본(OQMD, MP, COD, QM9, Alexandria, Polymer Genome) | jarvis-tools(develop) 코드에 내려받을 수 있는 데이터셋이 66개 등록됨. 표기 크기는 dft_3d 76k, dft_2d 1.1k, polymer_genome 1k, cod 431k, qm9 130k, alex_pbe_3d_all 5M 등(직접 확인). 2026 리뷰는… | polymer_genome: 유기 고분자 결정의 DFT 밴드갭, 유전율, 원자화 에너지 등. 그 밖에는 무기 물성 전반 | NIST 오픈 라이선스이며 일부는 NIST-PD(퍼블릭 도메인)(WebSearch 요약) | Polymer Genome 1k는 합성 고분자의 이상적 결정을 DFT로 계산한 값임. 바이오 고분자, 비정질, 분자량, 공정 정보가 없음 | 1 |

## general materials DB (데이터 게시·검색 인프라)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Materials Data Facility (MDF) / Foundry-ML | https://github.com/MLMI2-CSSI/foundry (직접 확인). 연관 https://github.com/materials-data-facility/connect_client (직접 확인). 포털… | 접속 확인 | 시뮬레이션·실험 데이터셋 게시(Globus 기반), 외부 저장소 색인, ML용 데이터 패키징(Foundry) | 저장 데이터 40 TB, 외부 데이터셋 수백 개 색인, 메타데이터 레코드 수백만 건(labs.globus.org, WebSearch 요약). 고분자 데이터셋 수는 unknown | 데이터셋마다 다름 | 데이터셋별 라이선스, DOI 발급 | 큐레이션 수준이 데이터셋마다 다름. 무기·금속·계산 데이터에 치우침(추정) | 1 |

## general materials DB (무기 실험 데이터 큐레이션)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| MPDS (Materials Platform for Data Science, Pauling File) | https://developer.mpds.io/ (WebSearch 결과에 등장) | 미확인(검색 색인에만 존재) | 문헌에서 수작업으로 큐레이션한 무기 결정 구조, 물성, 상태도 | 결정 구조 409,771건, 물성 세트 1,075,676건, 상(phase) 189,682개(WebSearch 요약, 시점 미상). OPTIMADE providers.json에는 '약 50만 편 논문 기반'으로 기술됨(직접 확인) | 결정 구조, 물리 물성, 상태도 | 일부만 CC BY 4.0(이원 산화물 전체, 셀 파라미터의 온도·압력 의존 도표 등). 나머지는 구독 | 무기 전용. 실험 문헌 큐레이션 품질은 높은 편 | 0 |

## general materials DB (상호운용 API 표준)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| OPTIMADE (Open Databases Integration for Materials Design) API 연합 | https://raw.githubusercontent.com/Materials-Consortia/providers/master/src/links/v1/providers.json (직접 확인). 명세 저장소 http… | 접속 확인 | 결정 구조 질의용 표준 REST API와 제공자 목록 | providers.json 항목 30개. 예시·네임스페이스 5개(exmpl, optimade, optimake, httk, aiida)를 빼면 실제 DB 25개, 그중 base_url이 있는 것 22개(직접 집계). AFLOW, Alexandria, CCDC, COD, MP, MPDS… | structures 엔트리: 격자, 원자 위치, 화학식, 원소 등 | 데이터는 제공자별 라이선스 | 주기적 결정 구조 스키마라서 분자량 분포, 치환도, 블렌드, 가교, 결정화도, 연신 이력 같은 고분자 개념을 표현하지 못함 | 0 |

## general materials DB (ML 벤치마크 모음)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| matminer datasets / Matbench | https://raw.githubusercontent.com/hackingmaterials/matminer/master/matminer/datasets/dataset_metadata.json (직접 확인) | 접속 확인 | 다른 DB와 논문에서 정제한 ML용 표 데이터 | 데이터셋 39개(메타데이터 직접 파싱). 가장 큰 것은 matbench_mp_e_form 132,752건. 고분자 데이터셋은 0개. 실험 데이터셋은 expt_gap 6,354건, steel_strength 312건, citrine_thermal_conductivity 872건 등 무기… | 조성, 결정 구조, 밴드갭, 생성 에너지, 탄성률, 유전율, 금속유리 형성능, 강철 강도 등 | 원출처별 라이선스(데이터셋 메타데이터에 출처가 적혀 있음). 코드 라이선스는 이번에 확인하지 않음 | 무기 조성·구조 기반 벤치마크임. featurizer도 무기용이라 고분자에는 RDKit 등 별도 기술자가 필요함 | 0 |

## general materials DB (상용 플랫폼, 과거 공개 데이터)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Citrine Informatics (구 Citrination 공개 플랫폼, lolo 라이브러리) | https://www.re3data.org/repository/r3d100012077 (WebSearch 결과에 등장). 코드 https://github.com/CitrineInformatics/lolo 와 cit… | 미확인(검색 색인에만 존재) | 과거: 사용자 기여 데이터와 문헌 자동 추출 물성(PIF 형식). 현재: 기업용 상용 플랫폼 | 과거 '무료 데이터 레코드 1,700만 건 이상'(2016 발표 슬라이드, WebSearch 요약). 현재 공개 데이터의 규모와 접근성은 unknown. matminer에 재배포된 citrine_thermal_conductivity 872건은 직접 확인 | 과거 레코드는 물질별로 제각각인 물성 표 | unknown. 현재 공개 접근 여부도 확인하지 못함 | 자동 추출이라 품질이 고르지 않음. 공개 데이터의 지속성이 불확실하고, 저장소가 닫히면 데이터가 사라질 위험의 사례임 | 1 |

## general materials DB (실험 결정구조, 오픈)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| COD (Crystallography Open Database) | https://www.crystallography.net/cod (WebSearch 결과에 등장, WebFetch 차단). 도구 https://github.com/cod-developers/cod-tools 는 직… | 미확인(검색 색인에만 존재) | 유기·무기·금속유기 결정 구조(CIF) | 534,674건(마지막 기탁 2026-08-10, WebSearch 요약). 미러는 533,828건. JARVIS 재가공본은 431k(직접 확인). OMol25 논문에는 '50만 건 이상'으로 기술(본문 확인) | 단위격자, 원자 좌표, 공간군, 문헌 서지 | 퍼블릭 도메인(기여자가 공개 도메인으로 기탁, WebSearch 요약) | 생체고분자는 명시적으로 제외됨. 소분자 결정 위주이고 무질서·수소 누락 구조가 섞여 있음 | 1 |

## general materials DB (유기·금속유기 결정구조, 상용)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| CSD (Cambridge Structural Database, CCDC) | https://www.ccdc.cam.ac.uk/solutions/about-the-csd/ (WebSearch 결과에 등장) | 미확인(검색 색인에만 존재) | 실험 소분자 유기·금속유기 결정 구조 | 130만 건 이상(CSA Trust 2026-01 공지), CCDC 페이지 요약은 140만 건 이상(WebSearch) | 3D 결정 구조, 분자간 상호작용 기하, 실험 조건 메타데이터 | 구독(상용·학술). 개별 구조 무료 조회 서비스가 있다고 알려져 있으나 조건은 미확인 | 잔기 24개 이하의 펩타이드와 다당류만 수록하므로 셀룰로오스와 단백질 섬유 같은 고분자는 제외됨(WebSearch 요약). 제약 분자에 치우침 | 1 |

## general chemistry DB (소분자 중심, 비이산 구조 포함)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| PubChem (NCBI/NIH) | https://pubchem.ncbi.nlm.nih.gov/ (WebSearch 결과에 등장). 클라이언트 https://github.com/mcs07/PubChemPy 는 직접 확인 | 미확인(검색 색인에만 존재) | 화합물·물질 레코드, 식별자, 계산·실험 물성, 생물활성, 안전·독성(GHS), 특허·문헌 연결 | 데이터 출처 1,000개 이상, 화합물 1.19억, 물질 3.22억, 생물활성 2.95억(PubChem 2025 update, PubMed로 확인) | SMILES, InChI, CAS 등 동의어, 분자량, XLogP, TPSA, HBD/HBA, 일부 실험 물성(녹는점, 용해도 등, 출처별), GHS 유해성, 특허·문헌 공출현 정보. 2025년부터 고분자·UVCB·당사슬 같은 non-discrete 물질용 전용 페이지가 생김 | 대체로 공개 이용 가능(NCBI 정책). 일부 기탁자 데이터는 조건이 다를 수 있음(미확인) | 기탁자마다 품질이 다르고 동의어가 중복됨. 고분자는 반복단위나 분자량 분포로 표현하지 못해 물성 DB 역할을 못 함 | 2 |

## general chemistry DB (생물활성)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| ChEMBL (EMBL-EBI) | https://ebi.ac.uk/chembl/about (WebSearch 결과에 등장). 클라이언트 https://github.com/chembl/chembl_webresource_client 는 직접 확인 | 미확인(검색 색인에만 존재) | 약물 유사 소분자의 생물활성(결합, 기능, ADMET) | ChEMBL 35: 화합물 약 250만, 분석(assay) 170만(WebSearch 요약). ChEMBL 33: 활성값 20,334,684건(WebSearch 요약) | 구조, 표적, 활성값(IC50, Ki, MIC 등), 분석 조건, 문헌 | CC BY-SA 3.0(동일조건 변경허락, WebSearch 요약) | 신약개발 분자에 편향됨. 고분자와 섬유 소재는 범위 밖임 | 0 |

## general computational DB (분자 DFT, MLIP 학

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| OMol25 (Open Molecules 2025, Meta FAIR 외) | https://huggingface.co/facebook/OMol25 (arXiv 본문과 WebSearch 요약에 등장, HF 직접 접속은 차단됨). 코드 https://github.com/facebookresea… | 미확인(검색 색인에만 존재) | ωB97M-V/def2-TZVPD DFT 단일점 계산(에너지, 힘, 전하, 스핀 등) | 학습셋 140,641,161건, 고유 분자계 약 8,300만, 계당 원자 2–350개(평균 50), 원소 83종(논문 본문 확인) | 총에너지, 원자 힘, Mulliken/Löwdin/NBO 전하, HOMO-LUMO 갭 등. 실험 거시 물성은 없음 | 데이터 CC BY 4.0. 모델 가중치는 별도 라이선스(논문 본문) | 분자 단편 계산이라 고분자 응집상이나 공정 물성과 직결되지 않음. 영역은 생체분자(단백질, DNA, RNA), 금속착물, 전해질, 주족 분자로 구성 | 1 |

## general computational DB (고분자 DFT, OMol2

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| OPoly26 (Open Polymers 2026, LLNL + Meta + LBNL) | https://huggingface.co/facebook/OMol25 (OPoly26도 같은 위치에 공개, 논문 본문과 WebSearch 요약에 등장). 코드 github.com/facebookresearch/fa… | 미확인(검색 색인에만 존재) | 고분자 MD 스냅샷에서 잘라낸 360원자 미만 클러스터의 DFT 에너지와 힘 | DFT 계산 6.35M 이상(train 5,902,827 / val 201,865 / test 248,391), 단량체 2,444종, 총 원자 12억 개, MD 셀 94k. 구성: 고엔트로피 공중합체 33.0%, 교대 공중합체 27.5%, 반응성 11.1%, 지질 10.9%, 펩토이드… | 총에너지, 힘, 전하, 스핀 등(OMol25와 같은 설정). 실험 물성(Tg, 강도)은 없음 | CC BY 4.0(논문 본문) | 블록·가지·가교·그래프트 고분자와 Si 함유 고분자가 없음(논문 한계 절). 일부 단량체는 합성 가능성이 보장되지 않음. 펩토이드는 들어 있지만 다당류와 단백질 섬유는 명시되지 않음 | 1 |

## polymer computational DB (범용 계산 DB의 고분자판

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| PolyOmics (RadonPy 컨소시엄, MD 계산 고분자 DB) | https://huggingface.co/datasets/yhayashi1986/PolyOmics (WebSearch 요약과 논문 본문에 등장, HF 직접 접속은 차단됨). RadonPy 코드 https://git… | 미확인(검색 색인에만 존재) | RadonPy 자동 전원자 MD(GAFF2)로 계산한 고분자 물성과 ML로 예측한 χ 파라미터 | 고분자 10^5종 이상, 데이터 엔트리 7,301,307건 이상, MD 물성 43종. 등방 비정질 125,658종, 일반 고분자 약 73,000종(20개 계열), 셀룰로오스 유도체 약 50,000종(치환도 0–3, HF README 기준 50,661종), 용해도 파라미터 58,834종… | 밀도, Rg, 정압비열(Cp), 압축률, 체적탄성률, 선·체적 열팽창계수, 열전도도, 굴절률, 아베수, 유전율·유전손실, Tg, 용해도 파라미터, χ, 자기확산계수 등 | CC BY 4.0(HF 미러 Kendrick921/PolyOmics README, WebSearch 요약). 공식 저장소 라이선스 파일은 직접 열지 못함 | 처리량을 위해 계산 조건을 느슨하게 잡았다고 논문이 명시함. Cp는 실험보다 높게 나오고, 열팽창계수는 실험과 상관이 약함. 무정형 어택틱 사슬만 다루고 결정화도와 가공 이력이 없음. χ 대상은 아세톤, 톨루엔, DMF 같은 유기용매 15종과 가소제 4종이며 DES/IL은 포함되지 않음. 단백질(케라틴)도 없음 | 2 |

## general materials DB (ML 예측 무기 결정)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| GNoME (Google DeepMind) 데이터 | https://storage.googleapis.com/gdm_materials_discovery (GCS 버킷 목록, README, LICENSE를 직접 읽음). 코드 github.com/google-deepmi… | 접속 확인 | GNN과 DFT로 예측한 무기 결정 구조와 안정성 | 신규 결정 220만 개, 그중 안정 후보 약 38만 개(DeepMind 블로그, WebSearch 요약) | 결정 구조, 생성 에너지, 분해 에너지 | CC BY-NC 4.0(버킷 README와 LICENSE 직접 확인), 비상업 조건 | 이론 예측이라 합성 검증이 일부에 그침. 무기 전용 | 0 |

## general engineering materials DB (데이터시트 

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| MatWeb | https://matweb.com (WebSearch 결과에 등장) | 미확인(검색 색인에만 존재) | 공급사 데이터시트 기반의 금속, 플라스틱, 세라믹, 복합재, 섬유 물성 | 데이터시트 195,000건 이상(사이트 문구, WebSearch 요약). 섬유와 바이오 고분자 건수는 unknown | 인장강도, 탄성률, 신도, 밀도, 열변형온도, 흡수율 등 데이터시트 항목 | 기본 무료 열람, 회원과 프리미엄 기능은 유료. 대량 추출과 재배포 허용 여부는 미확인 | 상용 등급에 치우침. 시험 규격(ASTM/ISO)과 조건이 섞여 있어 바로 비교하기 어려움. 실험실 수준의 바이오 소재는 거의 없을 것으로 추정됨 | 1 |

## general engineering materials DB (표준화 데이

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| CAMPUS Plastics (ISO 10350/11403 표준화 플라스틱 DB) | https://www.altair.com/campus-plastics (WebSearch 결과에 등장). campusplastics.com은 미확인 | 미확인(검색 색인에만 존재) | 공급사가 국제표준 조건으로 측정한 플라스틱 물성 | unknown | ISO 10350 단일점 물성(인장, 충격, 열, 전기 등)과 ISO 11403 다점 물성(응력-변형 곡선, 온도 의존성 등) | 온라인과 데스크톱판 무료(WebSearch 요약). 재배포 조건은 미확인 | 범용·엔지니어링 플라스틱 상용 등급 중심이고 섬유와 바이오 고분자는 거의 없음 | 1 |

## general materials DB (상용 큐레이션)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| SpringerMaterials (Landolt-Börnstein, Polymer Thermodynamics 포함) | https://materials.springer.com (미확인. WebSearch에는 도서관 안내 페이지만 나옴) | 미확인 | 비판적으로 검토한 물성 집적(무기, 유기, 고분자) | 물질 25만 종 이상, 참고문헌 120만 건(WebSearch 요약). Polymer Thermodynamics는 고분자 150종, 데이터 포인트 30,000개(WebSearch 요약) | PVT, 열용량, 상평형 등 고분자 열역학 데이터 | 기관 구독 | 큐레이션 품질은 높지만 합성 범용 고분자 중심이고 접근이 유료임 | 1 |

## general engineering materials DB (상용 교육용

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Ansys Granta EduPack (섬유·고분자 교육용 DB) | https://www.ansys.com/academic/educators/education-resources/paper-fibers-in-the-granta-edupack (WebSearch 결과에 등장) | 미확인(검색 색인에만 존재) | 교육용 대표 물성 레코드(섬유, 고분자, 에코 데이터) | MS&E DB의 섬유 종류를 19종에서 31종으로 확대했고 섬유 단위(denier, tex, cN/tex)를 도입함(WebSearch 요약). 전체 레코드 수는 unknown | 섬유 인장 물성, 밀도, 가격, 환경 영향(에코 감사) 등 | 상용 학술 라이선스 | 대표값과 범위 위주라 실험 조건과 변동성 정보가 적음 | 1 |

## solvent DB (범용 NIST 표준참조데이터)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| NIST ILThermo (SRD 147, 이온성 액체 물성 DB) | https://catalog.data.gov/dataset/nist-ionic-liquids-database-ilthermo-srd-147-2ba92 (WebSearch 결과에 등장) | 미확인(검색 색인에만 존재) | 이온성 액체의 문헌 실험 물성과 측정 메타데이터 | v2.0 기준 이온성 액체 1,000종 이상, 실험 데이터 포인트 약 280,000개(WebSearch 요약) | 상전이, 밀도, 점도, 전기전도도, 표면장력, 굴절률, 음속, 증기압, 활동도계수, 열용량. 측정법, 시료 순도, 불확도 포함 | 웹 무료 공개(NIST SRD). 세부 이용 조건은 미확인 | 측정법, 순도, 불확도를 함께 기록해 조화의 모범이 됨. DES 데이터는 거의 없고 IL에 집중됨(추정) | 2 |

## general chemistry DB (소분자 열화학·스펙트럼)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| NIST Chemistry WebBook (SRD 69) | https://webbook.nist.gov/chemistry/ (WebSearch 결과에 등장) | 미확인(검색 색인에만 존재) | 소분자 열화학, 열물성, IR·MS·UV 스펙트럼 | unknown(화합물 수를 확인하지 못함) | 생성 엔탈피, 상전이, 증기압, IR 스펙트럼 등 | 무료 웹 열람(미국 정부 자료). 대량 다운로드 조건은 미확인 | 소분자 전용이고 고분자는 없음 | 1 |

## general chemistry DB (식별자 정규화)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| CAS Common Chemistry | https://commonchemistry.cas.org/ (WebSearch 결과에 등장) | 미확인(검색 색인에만 존재) | CAS 등록번호, 이름, 구조, 기본 물성 | 약 500,000종(2021 확장, WebSearch 요약) | CAS RN, 동의어, 구조(SMILES/InChI), 일부 실험 물성 | CC BY-NC 4.0(비상업) | 자주 쓰이거나 규제되는 물질 중심이고 고분자 표현은 제한적임 | 1 |

## fiber/electrospinning DB (교차 참조: 범용 DB가 

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Electrospinning-Data.org (+ Cogni-e-SpinDB 1.0, FEAD) | https://zenodo.org/records/16731638 (Cogni-e-SpinDB 1.0 데이터, WebSearch 결과에 등장). 플랫폼 https://electrospinning-data.org 는 … | 미확인(검색 색인에만 존재) | 문헌에서 추출한 전기방사 공정-구조-물성 레코드(실패·불안정 기록 스키마와 SEM 이미지 연결 포함) | 초기 릴리스 809건(논문 57편, 고분자 12종, 용매계 14종). 많이 나온 고분자는 PVDF, PVA, PVP, PAN. 'PVA/물, 단일 노즐, 평판 컬렉터, 섬유경 180–380 nm' 조건 질의 결과는 108건. 저자들의 선행 리뷰는 논문 312편을 검토해 137편(약 4… | 고분자·용매 조성, 농도, 점도, 표면장력, 전도도, pH, 전압, 유량, 노즐-컬렉터 거리, 방사 시간, 온도, 습도, 노즐·컬렉터 구성, 형태(Cogni-EMCV 통제어휘: 형상, 배향, 복합 구조, 표면, 결함, 직경, 직경 변동), 불안정성 라벨, SEM 이미지 | unknown(Zenodo 레코드 라이선스를 직접 확인하지 못함) | 규모가 작음. 온습도 결측이 가장 심함. 연구 간 변동이 30–50%임. 실패 기록 스키마는 아직 초기 단계라 성공 편향이 남아 있음. 논문에 적힌 코드 저장소(github.com/taltechloc/electrospinning-data.org)는 2026-10-07 git ls-remote에서 접근되지 않음 | 3 |

## polymer computational DB (교차 참조)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| HTP-MD (MIT·TRI 고분자 전해질 MD 원자료 플랫폼) | https://github.com/tri-amdd/htp_md (직접 확인) | 접속 확인 | 비정질 고분자 전해질 MD 궤적 원자료와 자동 분석값 | MD 궤적 6,286개, 5.7 TB(arXiv:2208.01692, WebSearch 요약) | SMILES, 이온전도도, 확산계수, 몰랄농도, 운반수, MSD, 구조(CIF) | unknown | 리튬 고분자 전해질 전용 | 0 |

**이 조사 블록에서 확인된 데이터 공백**

- 범용 소재 DB(MP, OQMD, AFLOW, JARVIS-DFT, Alexandria, GNoME, MPDS, MC3D, OPTIMADE 연합)는 무기 결정과 0 K DFT 중심이라 고분자·섬유 데이터가 사실상 없다. 직접 집계 결과 MP 2025-09-25 빌드 210,579건 중 C/H/O/N만으로 된 항목은 524건(0.25%)으로 소분자 결정과 탄소 동소체뿐이고 고분자는 0건이다. matminer 데이터셋 39개 중 고분자는 0개다.
- 바이오 기반 고분자(케라틴, PVA/PVAc, 셀룰로오스 유도체)의 실험 물성과 공정 데이터는 이번에 조사한 범용 DB 어디에도 없다. 대규모 계산값은 PolyOmics(셀룰로오스 유도체 약 5만 종, 일반 고분자 약 7.3만 종, GAFF2 MD)에만 있다. 케라틴 같은 단백질 섬유는 범용 DB와 계산 DB 모두에서 공백이다(OPoly26에는 펩토이드만 있다).
- 섬유 고유 물성(강도 cN/tex, 신도, 수분율, 흡습·속건, 위킹, 일방향 수분이동 지수)과 막 물성(투습도, 공극률, 접촉각 이력)은 범용 DB에 전혀 없다. 다만 Granta EduPack이 섬유 31종의 대표값만 상용으로 제공한다. 따라서 문헌 표·본문 추출이 필수다.
- 전기방사 공정의 구조화 공개 데이터는 Cogni-e-SpinDB/Electrospinning-Data.org의 809건(고분자 12종) 수준으로 작다. 온습도 결측이 많고, 실패와 음성 결과가 적어 출판 편향이 크다. 케라틴, 셀룰로오스 유도체, DES 용매계 포함 여부는 미확인이다.
- DES 물성: NIST ILThermo는 IL 중심(약 1,000종, 약 28만 포인트)이다. 이번 범용 DB 조사 범위에서 검증된 대규모 DES 전용 DB는 확인하지 못했으므로 용매 카테고리에서 별도 확인이 필요하다. PolyOmics의 χ 파라미터도 유기용매 15종과 가소제 4종뿐이고 DES/IL은 없다.
- 탄화(바이오 고분자 전구체 → 탄소)의 탄화 수율, 라만 ID/IG, 전도도, 기공 구조 데이터는 범용 DB에 없다. MP의 탄소 동소체(결정) 정보는 비정질·난흑연화 탄소와 거리가 멀다.
- 스키마 표현력이 부족하다. OPTIMADE, MP, OQMD 같은 결정 스키마는 분자량 분포, 치환도, 택티시티, 블렌드 비, 가교도, 결정화도, 연신·후처리 이력, 시험 규격과 조건을 표현하지 못한다. PubChem도 고분자는 non-discrete 레코드로만 다룬다.
- 확인하지 못한 항목: Citrination 공개 데이터의 현재 접근성, AFLOW 라이선스, NOMAD 내 고분자·MD 엔트리 수, MDF 내 고분자 데이터셋 수, NIST WebBook 화합물 수, CAMPUS 레코드 수, CSD 개별 구조 무료 조회 조건, Electrospinning-Data.org와 Cogni-e-SpinDB의 라이선스, PolyOmics 공식 저장소의 라이선스 파일(미러 README 기준으로는 CC BY 4.0). 대부분의 공식 사이트는 프록시 차단으로 직접 열지 못했고, WebSearch 요약의 수치는 시점이 오래됐을 수 있다.
- 라이선스 제약: GNoME과 CAS Common Chemistry는 CC BY-NC(비상업), ChEMBL은 CC BY-SA(동일조건 공유)다. CSD, SpringerMaterials, Granta는 구독형이고, MatWeb은 대량 추출 제한이 추정된다. 대회 이후 DYETEC과 함께 사업화하거나 재배포할 경우 이 소스들은 쓸 수 없을 수 있다.

## polymer DB

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| PoLyInfo (NIMS 고분자 데이터베이스) | https://polymer.nims.go.jp/ | 미확인(검색 색인에만 존재) | 문헌에서 수작업으로 수집한 실험 물성(구조, 시료 가공법, 측정 조건, 단량체·중합법 포함) | 2025-05-29 기준: 단일중합체(homopolymer) 19,227 / 공중합체 8,321 / 블렌드 2,788 / 복합재 3,209, 시료 174,968, 물성값 552,427, 문헌 21,793건 (PoLyInfo 소개 페이지 검색 스니펫). 2023-10 기준 494,820… | 물성 약 100종(열·전기·기계 등), 화학구조, IUPAC명, 시료 가공법, 측정 조건, 단량체, 중합법 | 무료지만 기관 이메일로 DICE 계정 등록 필요. MatNavi 이용약관상 대량 다운로드·스크래핑 금지(위반 시 계정 정지). 일괄 다운로드 불가(PolyOmics 논문 Table S1에서 'Bulk download: A'로 표기) | 전문가가 수작업으로 큐레이션해 품질은 높은 편. 다만 상용·연구가 많이 된 고분자에 데이터가 쏠려 있고, 같은 고분자라도 시료 이력·분자량·측정법에 따라 값이 크게 흩어짐. 측정 메타데이터(습도, 승온속도 등)가 빠진 경우가 많다는 지적이 있음(arXiv 2505.13494). 사용 제한 때문에 ML 학습용으로 재배포할 수 없음 | 2 |
| MaterialsMine / NanoMine (고분자 나노복합재 DB) | https://materialsmine.org/ | 미확인 | 고분자 나노복합재 실험 데이터(조성, 공정, 미세구조, 물성)를 스키마와 지식그래프로 정리 | 시료 2,500개 이상(검색 스니펫, 시점에 따라 500 / 1,700 / 2,500으로 다르게 보고됨). 기술자 약 350개(arXiv 2505.13494) | 매트릭스, 필러 종류·함량, 표면처리, 공정 조건, Tg, 탄성률, 유전특성 등 | 오픈소스 플랫폼(구체적 라이선스 미확인) | 전기 퍼콜레이션 등 일부 영역은 데이터가 드묾. 문헌 큐레이션 편향이 있음 | 2 |
| Polymer Genome / Khazana (Ramprasad 그룹) | https://www.polymergenome.org/ | 미확인(검색 색인에만 존재) | 예측 플랫폼(Tg, 밴드갭, 유전상수, 굴절률, 밀도, 용해도 파라미터 등) + Khazana 계산 데이터 저장소 | Khazana 고분자 데이터셋은 1,073종(Sci Data 2016, DFT). Khazana 전체는 논문 24편 유래 고분자·유기물 1,412종 + 무기물 2,657종(검색 스니펫). 플랫폼 학습 데이터 전체 규모는 공개되지 않음 | DFT 밴드갭, 유전상수, 원자화 에너지, 최적 구조. 플랫폼은 예측값만 제공 | 플랫폼은 무료 웹 예측. 2016 데이터셋은 Dryad(DOI 10.5061/dryad.5ht3n) 공개. 라이선스는 Dryad 기본 정책을 따를 것으로 보이나 직접 확인하지 못함 | DFT 계산값 중심이고 결정 모델을 가정함. 플랫폼 학습 데이터는 비공개 | 1 |
| CRIPT (Community Resource for Innovation in Polymer Technology) | https://criptapp.org/ | 미확인 | 그래프 기반 고분자 데이터 모델·생태계(합성, 공정, 특성 분석 이력 연결) | unknown (등록된 데이터 건수를 찾지 못함) | 재료, 공정(process), 시료, 측정(property·condition), BigSMILES 기반 구조 등 그래프 노드 | 웹 플랫폼(계정 필요 여부와 라이선스 미확인) | 데이터 모델은 정교하지만 실제로 공개된 데이터의 양이 적을 가능성이 있음(미확인) | 1 |
| CROW Polymer Properties Database (polymerdatabase.com) | https://polymerdatabase.com/ | 미확인 | 문헌 실험값 중심의 열물리 물성 정리 | 고분자 250종 이상. 약 95%가 실험값을 포함(arXiv 2309.01788 서술) | Tg, Hildebrand 용해도 파라미터, 몰 열용량, 굴절률, 몰 응집에너지 등 | 무료 웹 열람. 라이선스 미확인 | 상용 플라스틱 위주로 규모가 작음 | 1 |
| 고분자 전해질 이온전도도 DB (Bradford et al.) | https://doi.org/10.1021/acscentsci.2c01123 | 미확인 | 문헌에서 수집한 고체 고분자 전해질 이온전도도 | 이온전도도 측정 11,350건, 전해질 조성 1,700종 이상(검색 스니펫) | 고분자, 염, 염 농도, 고분자 분자량, 첨가제, 온도, 전도도 | ACS Cent. Sci. 2023 논문 SI(라이선스 미확인) | 제조 습도 등 결정성에 영향을 주는 조건이 누락된 경우가 많음(arXiv 2505.13494) | 0 |
| NIST Synthetic Polymer MALDI Recipes Database | https://maldi.nist.gov/ | 미확인(검색 색인에만 존재) | 문헌에서 모은 합성고분자 MALDI 질량분석 시료 준비 레시피 | 고분자/매트릭스 조합 1,250개 이상, 1988~2012년 문헌 | 고분자군(A~E), 매트릭스, 염, 용매, 문헌 DOI | 공개 웹. 라이선스 미확인(NIST가 검증하지 않은 레시피라는 면책 문구 있음) | 2012년 이후는 갱신되지 않음 | 0 |

## general materials DB

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| MatNavi (NIMS 재료 데이터베이스 포털) | https://mits.nims.go.jp/ | 미확인(검색 색인에만 존재) | NIMS 재료 DB 모음(PoLyInfo 포함) | unknown (이번 조사에서 포털 전체 규모 수치는 확인하지 못함) | DB별로 다름. 고분자 부분은 PoLyInfo를 참조 | 무료 회원가입. 소속 기관 이메일 도메인이 NIMS 관리 목록에 등록돼 있어야 함. 대량 다운로드·웹 스크래핑 금지 | PoLyInfo와 동일. 접근 장벽(기관 도메인 등록)이 있어 국내 대학 도메인이 등록돼 있는지 직접 확인해야 함 | 1 |
| MatWeb | https://matweb.com | 미확인(검색 색인에만 존재) | 재료 데이터시트(제조사·문헌) | 금속·플라스틱·세라믹·복합재 데이터시트 195,000개 이상(검색 스니펫) | 기계·열·전기 물성, 가공 정보 | 기본 무료, 고급 검색은 회원가입. 대량 추출·재배포 조건은 미확인 | 제조사 데이터시트라 시험 조건이 제각각이고 화학구조 정보가 없음 | 1 |

## polymer DB (computational)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| PolyOmics (RadonPy 컨소시엄, MD 기반 고분자 DB) | https://huggingface.co/datasets/yhayashi1986/PolyOmics | 미확인(검색 색인에만 존재) | 전원자(all-atom) 분자동역학(MD, GAFF2 힘장) 시뮬레이션으로 자동 계산한 물성 + 머신러닝으로 예측한 χ 파라미터(용매와 섞이는 정도) | 고분자 10^5종 이상, 데이터 항목 7,301,307건 이상. 등방성 비정질 고분자 125,658종 × 물성 43종, 범용 고분자 약 73,000종(20개 계열), 셀룰로오스 유도체 약 50,000종, 광학 후보 약 13,000종, PFAS 3,821종, 생분해 후보 폴리에스터·폴리… | 밀도, Cp/Cv, 압축률, 체적탄성률, 자기확산계수, 선/체적 팽창계수, Tg, 굴절률, 유전상수, 열전도도, 회전반경(Rg) 등 62종(이 중 43종에 데이터 있음). 용매 15종 + 가소제 4종에 대한 χ, 응집에너지 성분, 반복단위의 HOMO/LUMO, MD 조건, 이완 구조 … | Hugging Face 공개. 라이선스는 이번 조사에서 확인하지 못함(unknown). 논문 게재 후 radonpydb.org 웹 DB·API를 열 계획이라고 밝힘 | 모든 값이 시뮬레이션 값(MD는 Cp를 체계적으로 과대평가하고 Tg는 냉각 속도에 따라 달라지는 등 실험값과 차이가 남). 대부분 가상 고분자(SMiPoly·XenonPy 생성기로 만든 것)여서 합성 가능성 편향이 있음. 사슬당 약 1,000원자의 무정형(atactic) 모델이라 결정성·가공 이력은 반영되지 않음. 저자들은 개별 값을 조회하는 사전이 아니… | 3 |
| polyOne (가상 고분자 1억 종 + ML 예측 물성) | https://zenodo.org/records/7124188 | 미확인(검색 색인에만 존재) | 합성된 고분자 13,000여 종의 조각을 조합해 만든 가상 PSMILES와 polyBERT 계열 모델의 예측 물성 | 1억 종 × 예측 물성 29종 (Zenodo 기록 제목·검색 스니펫). PolyOmics Table S1은 Zenodo 7766806을 참조 | PSMILES, Tg·밴드갭·기체투과 등 ML 예측값 29종 (parquet) | 검색 스니펫상 '학술 목적 공개'. 정확한 라이선스는 미확인 | 모든 물성이 ML 예측값이라 '라벨'이 아님. 학습 분포 밖에서는 오차가 클 수 있음 | 1 |
| OPoly26 (Open Polymers 2026, Meta·LLNL·LBNL) | https://huggingface.co/facebook/OMol25 | 미확인 | 고분자 부분구조(360원자 미만)에 대한 DFT 단일점 계산(에너지·힘). 머신러닝 원자간 포텐셜(MLIP) 학습용 | DFT 계산 635만 건 이상, 원자 12억 개, 단량체 2,444종, MD 셀 94k(누적 239,000 ns). 분할은 학습 5,902,827 / 검증 201,865 / 시험 248,391 | 총에너지, 원자 힘, 전하, 스핀 등 (ωB97M-V/def2-TZVPD, OMol25와 같은 설정) | CC-BY-4.0 (논문에 명시). 코드는 github.com/facebookresearch/fairchem(git ls-remote로 존재 확인) | 블록·분지·가교·그래프트 구조와 Si 고분자는 없음. 합성 가능성을 보장하지 않음. 거시 물성 라벨이 없음 | 0 |

## GitHub dataset

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| polyVERSE (Ramprasad 그룹 정보학용 데이터 저장소) | https://github.com/Ramprasad-Group/polyVERSE | 접속 확인 | 실험·시뮬레이션·ML 예측 데이터 CSV 모음 + 가상 고분자 라이브러리 | 직접 행 수를 셈: 기체 투과·용해·확산 master 7,826행(wide 형식 1,050 고분자), χ 파라미터 1,586행, 용매 확산계수 3,043행, 용매 흡착(uptake) 2,276행, 용융점도 1,959행, 응집에너지밀도 294행, ROP 엔탈피 459행, AEM 전도도·… | 고분자/용매 SMILES, 온도, 활동도(activity), 용매 중량분율, 실험/시뮬레이션 구분자, 출처(DOI). 용융점도는 Mn·Mw·PDI·전단속도 포함 | GTRC General Public Use License(직접 확인): 복제·수정·배포는 허용하지만 상업적 판매는 별도 계약이 필요하고, 파생물도 같은 조건으로 무상 공개해야 함. Zenodo DOI 10.5281/zenodo.13352644 | 그룹 내부에서 모은 문헌 데이터라 출처 편향이 있음. 실험과 시뮬레이션이 섞인 파일에는 구분 열이 있음. Tg·인장물성 같은 핵심 실험 데이터셋은 'Other' 폴더에 없음 | 2 |
| RadonPy + PI1070 데이터셋 | https://github.com/RadonPy/RadonPy | 접속 확인 | MD 자동계산 물성(비정질 단일중합체) + 자동화 소프트웨어 | data/PI1070.csv: 1,077행 × 157열 (git으로 받아 직접 셈). 논문은 1,070종 단일중합체에 물성 15종이라고 보고 | monomer_ID, SMILES, 단량체 양자화학 값(HOMO/LUMO, 쌍극자, 분극률), 온도·압력·입체규칙성·중합도, 밀도/Rg/자기확산/Cp/Cv/압축률/체적탄성률/팽창계수/정적 유전상수/열전도도 등 각각의 평균·최소·최대·표준편차·개수 | BSD-3-Clause (저장소 LICENSE 직접 확인) | GAFF2 기반이라 실험 대비 계통 오차가 있음(특히 Cp). PoLyInfo에 실험값이 많은 범용 고분자 위주로 고른 세트 | 1 |
| SPACIER (RadonPy 연동 베이지안 최적화 고분자 설계 도구) | https://github.com/s-nanjo/Spacier | 접속 확인 | 소프트웨어(베이지안 최적화와 RadonPy 작업 자동 제출) + 예제 데이터(X.csv/y.csv 등) | 데이터셋이 아니라 도구임. 예제 데이터 규모는 확인하지 않음(unknown) | 획득함수 EI, PI, EHVI 등과 다목적 파레토 탐색 | BSD-3-Clause (README에 명시) | MD 계산 자원(HPC)을 전제로 함 | 1 |
| ADEPT + PolyGraphMT (다중충실도 고분자 데이터셋) | https://github.com/sobinalosious/PolyGraphMT | 접속 확인 | 실험값 + MD + DFT + 그룹기여법(GC) 추정값을 합친 다중충실도(multi-fidelity) 데이터와 학습 코드. ADEPT는 MD 자동화 파이프라인 | 약 62,000개 값, 물성 28종. 예: Cp 13,105(실험/MD/GC), Tg 7,360(실험/MD), Tm 3,671(실험), 밀도 3,644(MD), 열전도 2,327, 기체투과도(He/H2/CO2/N2/O2/CH4) 466~807(실험), DFT 전자물성 2,916, 탄성… | 열·기계·수송·기체투과·전자/광학·구조 물성 28종과 충실도 레벨 라벨 | 코드·처리된 데이터는 저장소에 공개. PolyGraphMT와 ADEPT의 LICENSE 파일은 확인하지 못함(raw 경로 404) → unknown | MD Cp는 체계적으로 과대평가됨(선형 보정으로 MAE 89% 감소). MD 밀도는 보정 후 R² 0.81. 충실도가 섞여 있어 가중치 설계가 필요함 | 1 |
| PI1M (가상 고분자 100만 종) | https://github.com/RUIMINMA1996/PI1M | 접속 확인 | PoLyInfo 고분자 약 12,000종으로 학습한 RNN 생성모델이 만든 가상 고분자 p-SMILES (라벨 없음) | 약 100만 종(README). PI1M_v2에는 SA 점수(합성 난이도) 추가 | p-SMILES, SA score | 저장소 LICENSE는 MIT이지만 README에는 'Data for academic purpose only'라고 적혀 있어 서로 충돌함 → 학술 목적으로만 쓰는 것이 안전함 | 실제로 합성된 적 없는 구조가 대부분. PoLyInfo의 화학공간 분포를 그대로 이어받음 | 1 |
| polyBERT / polyGNN (Ramprasad 그룹 모델 및 학습 데이터) | https://github.com/Ramprasad-Group/polyBERT | 접속 확인 | 고분자 화학 언어모델(지문 생성기). 학습 데이터는 polyOne(1억 종) + Polymer Genome 데이터 | 사전학습 1억 PSMILES. 다운스트림 라벨 데이터 규모는 공개 저장소에서 확인하지 못함 | polyBERT 지문(임베딩) | Academic Research Use License: 비상업 연구·교육 용도만 허용, 재배포 금지. 소스코드는 기관 이메일로 요청해야 받을 수 있음. polyGNN 저장소(Ramprasad-Group/polyGNN)는 git 접근 시 인증을 요구해… | PolyBench26에서 polyBERT는 그래프 모델보다 오차가 큼(예: 실험 Tg RMSE 37.9 vs 34.7 °C) | 1 |
| Open Macromolecular Genome (OMG) | https://github.com/TheJacksonLab/OpenMacromolecularGenome | 접속 확인 | 구매 가능한 단량체(eMolecules)에 중합 규칙 17개를 적용해 만든 합성 가능 가상 고분자 | 약 1,200만 종(PolyOmics 논문 Table S1). 데이터는 Zenodo 7556992(OMG_monomers_CRU.zip 369.4 MB, 검색 스니펫) | 단량체, 반복단위(CRU), 반응 유형. 물성 라벨 없음 | 코드는 GPL-3.0(LICENSE.md 직접 확인). Zenodo 데이터의 라이선스는 미확인 | 반응 규칙 기반이라 화학적으로는 그럴듯하지만 물성 라벨이 없음 | 1 |
| OMG_PhysicalProperties (OMG 1,200만 종의 단량체 수준 ML 물성) | https://github.com/TheJacksonLab/OMG_PhysicalProperties | 접속 확인 | 능동학습으로 얻은 DFT/TD-DFT 계산 결과 + OMG 1,200만 종에 대한 ML 예측(불확실성 포함). COSMO-SAC 기반 χ 추정 스크립트 | OMG 1,200만 종에 대한 예측(README). 계산 데이터 규모는 unknown. 전체는 Zenodo 13863778 | 단량체 수준의 화학·물리 물성, 예측 불확실성, χ(COSMO-SAC) | MIT (저장소 LICENSE 직접 확인) | 단량체 수준 계산을 고분자 성질의 대리값으로 쓰는 것이라 거시 물성과는 간극이 있음 | 1 |
| SMiPoly (규칙 기반 가상 고분자 생성기) | https://github.com/PEJpOhno/SMiPoly | 접속 확인 | 규칙 기반 중합 반응으로 만든 가상 고분자 라이브러리 생성 도구 + 단량체 샘플셋 | 샘플 단량체 1,083종(README). 생성 고분자는 약 16만~18만 종(PolyOmics 논문 Methods와 Table S1의 수치가 다름) | 단량체 분류(monc.py), 반복단위 생성(polg.py) | BSD-3-Clause (README) | 구조만 있고 물성 라벨은 없음 | 1 |
| PolyMetriX (정제된 Tg 데이터셋 + 특징화 라이브러리) | https://github.com/lamalab-org/PolyMetriX | 접속 확인 | 여러 출처의 실험 Tg를 합치고 신뢰도 등급을 매긴 데이터 + 주사슬/곁사슬 계층 특징화 도구 | 고유 Tg 7,367개(PolyBench26 저장소의 Tg.csv를 직접 셈. Fudan 리뷰 arXiv 2608.20979도 7,367로 기술) | PSMILES, Tg 범위, 데이터 개수, Tg 값, 신뢰도(reliability), 표준편차, 출처, 계층 특징 | MIT (LICENSE 직접 확인). Zenodo 15783761(v6, 2025-07-01) | 출처마다 값이 다를 때 신뢰도 등급으로 처리함. 측정법(DSC/DMA) 구분이 충분한지는 미확인 | 1 |
| PolyID (NREL) | https://github.com/NREL/polyid | 접속 확인 | GNN 학습·예측 프레임워크와 예제 데이터(입체규칙 고분자 입력, Mordred 기술자) | 저장소 데이터는 소규모(예제 CSV). 논문의 학습 데이터 규모는 unknown | 고분자 구조(m2p로 생성), 예측 물성(Tg, Tm, 밀도, 영률, 기체투과 등. 리뷰 arXiv 2608.20979의 Table 2) | BSD-3-Clause (LICENCE.md 직접 확인) | 바이오 기반·지속가능 고분자를 지향하지만 학습 데이터 출처는 확인하지 않음 | 1 |
| VIPEA + diblock 상(相) 데이터 (polymer-chemprop-data) | https://github.com/coleygroup/polymer-chemprop-data | 접속 확인 | 계산으로 얻은 공중합체 전자친화도(EA)·이온화 퍼텐셜(IP) + 블록공중합체 상 데이터 | 공중합체 42,966종 × EA/IP (PolyBench26 Table 1). diblock 데이터 규모는 unknown | 단량체 조합, 화학량론, 사슬 구조(교대·랜덤·블록), EA, IP | MIT (LICENSE 직접 확인) | 계산값이고 공액(광학) 고분자 단량체 공간에 한정됨 | 0 |
| TransPolymer 다운스트림 데이터셋 | https://github.com/ChangwenXu98/TransPolymer | 접속 확인 | 여러 문헌·DB에서 모은 회귀 데이터 10종(Egc, Egb, Eea, Ei, Xc, EPS, Nc, OPV, PE_I, PE_II) + 사전학습용 PI1M 증강 약 500만 개 | 파일이 Git LFS 포인터라 행 수를 직접 세지 못함(unknown). 사전학습 약 500만 개(README) | SMILES, 각 물성(밴드갭, 결정화 경향 Xc, 유전상수, 고분자 전해질 전도도 등) | LICENSE 파일을 찾지 못함(404) → unknown | 2차 가공된 데이터라 원 출처를 다시 확인해야 함 | 0 |

## polymer benchmark

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| NeurIPS 2025 Open Polymer Prediction (Kaggle, Open Polymer Challenge) | https://www.kaggle.com/competitions/neurips-open-polymer-prediction-2025 | 미확인(검색 색인에만 존재) | MD로 계산한 물성 5종 (경진대회 데이터) | 고유 고분자 11,475종 중 라벨이 있는 것 9,625종. 학습셋 7,973종. 학습셋 라벨 수는 Tg 511, FFV 7,030, 열전도도(TC) 737, Rg 614, 밀도 613. 비공개 리더보드 3,207종 (arXiv 2512.08896 Table 2·3) | SMILES, Tg, FFV(자유부피 분율), 열전도도, Rg, 밀도 | Kaggle 대회 규정을 따름. 대회 후 테스트셋이 별도 Kaggle 데이터셋(alexliu99/...-test-data)으로 공개됨. 구체적인 라이선스는 확인하지 못함(unknown). 생성 파이프라인 ADEPT는 GitHub 공개 | 두 연구 그룹이 서로 다른 힘장(GAFF2와 PCFF)과 프로토콜로 계산함. Tg 적합 방식(이중선형 vs 쌍곡선) 차이로 공개·비공개 리더보드 평균 Tg가 102.9→179.8 °C로 이동함. K↔°C 단위 오류, RDKit 버전 차이로 SMILES 약 20개가 무효가 된 사례, 과거 공개 데이터 유출도 보고됨. 라벨 불균형이 심함 | 1 |
| POINT2 (Polymer Informatics Training and Testing) | https://github.com/Jiaxin-Xu/POINT2 | 접속 확인 | 공개 데이터를 모아 학습/시험으로 나눈 벤치마크(실험값 + MD 값) + 불확실성·해석·합성가능성 프로토콜 | 학습/시험 = Tg 5,766/1,442, Tm 2,936/735, 열전도 1,264/316, FFV 6,436/1,610, 밀도 1,368/342, 투과도 O2 644/161, N2 635/159, CH4 544/137, H2 407/102, CO2 603/151 (arXiv 250… | SMILES, 각 물성값, 4:1 무작위 분할 | MIT (저장소 LICENSE). README에 '데이터·모델 공개는 정식 게재 후'라고 적혀 있어 현재 전체 데이터가 올라와 있는지는 불확실함 | 무작위 분할이라 분포 외(OOD) 평가가 아님. 기체투과는 MSA DB에서 왔고, TC·FFV는 MD 값 | 1 |
| PolyBench26 (Polymer Benchmark 2026) | https://github.com/rlearsch/PolymerBenchmark2026 | 접속 확인 | 실험 Tg + DFT(EA/IP, 굴절률) + MD(밀도, Cp, Cv, Rg)를 묶은 벤치마크. 단일중합체와 교대·랜덤·블록 공중합체 포함 | 약 250,000개 값, 물성 8종. 단일중합체 17,003개(반복단위 9,905종), 공중합체 232,959개(80,099종). 저장소의 PolyMetriX Tg.csv는 7,367행(직접 셈) | PSMILES/wPSMILES, Tg, EA, IP, 굴절률, 밀도, Cp, Cv, Rg. 과제는 분포 내 예측, 데이터 크기 스케일링, 반복단위 복잡도, 구조 미학습(held-out) 전이 | MIT (LLNL, 저장소 LICENSE 직접 확인). polyVERSE 유래 파일에는 GTRC 라이선스가 따로 붙음(THIRD_PARTY_LICENSES) | MD 값은 OPoly26 궤적에서 재계산한 것. Rg는 사슬 길이에 의존해 물리량으로 보기 어렵다고 저자가 명시. 실험 물성은 Tg 하나뿐임 | 1 |
| SimPoly / PolyArena (Microsoft) | https://arxiv.org/abs/2510.13696v1 | 미확인(검색 색인에만 존재) | MLFF(머신러닝 힘장) 학습용 DFT 구성 데이터(PolyData) + 실험 밀도·Tg 벤치마크 | 실험 벤치마크 고분자 130종. DFT 구성 680,000개(OPoly26 논문 인용) | 실험 밀도, Tg, DFT 에너지·힘 | OPoly26 논문(2025-12)에 따르면 SimPoly는 아직 공개되지 않음. 현재 상태는 미확인 | 안정한 단일중합체 130종으로 범위가 좁음 | 0 |

## patents/text

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Polymer Scholar (NLP/LLM 문헌 추출 물성 DB) | https://polymerscholar.org/ | 미확인 | 초록·전문에서 MaterialsBERT와 LLM(GPT-3.5, LlaMa 2)으로 자동 추출한 물성 레코드 | 2023년: 초록 약 13만 건에서 약 30만 레코드. 2024년: 논문 240만 편 중 고분자 관련 68.1만 편에서 물성 24종 100만 레코드 이상(Gupta 2024) | 고분자명, 물성명, 값, 단위, 일부 조건 | 웹 검색·시각화로만 이용 가능. 일괄 다운로드 불가(PolyOmics 논문 Table S1의 'Bulk download: A') | 자동 추출이라 중복이 많고, 같은 고분자인데 값·조건이 서로 다른 경우가 흔함(arXiv 2608.20979). 고분자 이름을 구조로 정규화하는 문제가 남아 있음 | 2 |
| OpenPoly / CEMP (LLM 추출 + 규칙 정제 실험 DB) | https://huggingface.co/datasets/cooperzvegintzov/OpenPoly | 미확인(검색 색인에만 존재) | LLM으로 문헌에서 추출한 뒤 규칙으로 정제한 실험 물성(50% 절사평균으로 중복값 통합) | 고신뢰 항목 약 2.1×10^4개(arXiv 2608.20979). 단일중합체 물성 26종, 물성별 30~443개(arXiv 2609.27036) | PSMILES, Tg, Tm, Td, 인장강도, 영률, 유전상수 등 | 검색 스니펫상 CC BY 4.0(HF 데이터셋 페이지). 이 HF 페이지가 원 저자의 공식 배포인지 미러인지는 확인하지 못함. 공식 플랫폼은 cleanenergymaterials.cn/polymer(미확인) | LLM 추출 오류 가능성이 있음. 물성별 데이터가 적음. 절사평균은 측정법 차이를 '평균으로 덮어버리는' 방식이라 조건 정보가 사라짐 | 1 |
| PolyIE (고분자 문헌 정보추출 주석 데이터셋) | https://github.com/jerry3027/PolyIE | 접속 확인 | 전문 논문 146편에 전문가가 단 개체명(화합물명, 물성명, 물성값, 조건)·n항 관계 주석 | 논문 146편(arXiv 2311.07715). 주석 레코드 수는 unknown | CN, PN, PV, Condition 개체와 <CN, PN, PV, Condition> 관계 | Apache-2.0 (LICENSE 직접 확인) | 고분자 태양전지와 리튬전지 분야에 한정됨. 바이오 고분자·섬유 분야는 없음 | 1 |

## biopolymer/solvent

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| PPPDB (Polymer Property Predictor and Database, χ·Tg·운점) | https://pppdb.uchicago.edu/ | 미확인(검색 색인에만 존재) | 문헌에서 추출한 Flory–Huggins χ(고분자–고분자, 고분자–용매), Tg, 임계 용해 운점(cloud point) | unknown (총 건수를 확인하지 못함). χ 추출에 Macromolecules 논문 376편이 쓰였다는 스니펫이 있음. 항목 번호는 최소 590번대까지 확인됨 | 고분자/용매 쌍, χ 값 또는 χ(T) 식, 온도 범위, 기준 부피, 측정법, 문헌 | 무료 웹 열람. 라이선스 미확인 | χ는 측정법과 이론 가정에 따라 값이 크게 달라지는 '현상론적' 파라미터임(arXiv 2505.13494). 합성 고분자 블렌드 위주 | 2 |
| 고분자 용해도 Crystal16 데이터셋 (Amrihesari et al. 2024) | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11684024/ | 미확인(검색 색인에만 존재) | 자체 측정 Crystal16 탁도(투과율) 데이터: 고분자×용매×농도×온도 | unknown (이번에 건수를 확인하지 못함) | 고분자, 용매, 농도, 온도, 투과율 → 용해 / 부분 용해 / 불용 3분류 | 오픈액세스 논문(J. Phys. Chem. B). 데이터 라이선스 미확인 | 단일 실험실·단일 장비라 내부 일관성은 높지만 화학공간 범위가 좁음 | 2 |
| 고분자 생분해성 HTE 데이터(폴리에스터·폴리카보네이트 642종) | https://pmc.ncbi.nlm.nih.gov/articles/PMC10266013 | 미확인(검색 색인에만 존재) | 고속 합성과 clear-zone 생분해 분석(Pseudomonas lemoignei)으로 얻은 실험 데이터 | 화학적으로 서로 다른 폴리에스터·폴리카보네이트 642종 | 반복단위 구조, 생분해 여부·정도, ML 분류 정확도 82% 이상 | PNAS 2023 오픈액세스 논문의 SI(데이터 라이선스 미확인) | 단일 균주·단일 분석법이라 실제 환경(토양·해양) 분해와는 다름 | 1 |

## membrane

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| MSA 고분자 기체분리막 데이터베이스 | https://research.csiro.au/virtualscreening/membrane-database-polymer-gas-separation-membranes | 미확인(검색 색인에만 존재) | 1950~2018년 문헌의 실험 기체투과도 | 고분자 약 1,500종. 정제 후 단일중합체 836종, 기체별 H2 509 / O2 805 / N2 794 / CO2 754 / CH4 681 (arXiv 2404.10903 스니펫) | 고분자, 기체별 투과도(Barrer) 등 | 공개 웹 DB(라이선스 미확인) | 빈칸(결측)이 많아 ML로 결측을 채우는 연구가 나올 정도. 막 제조·시험 조건이 제각각임 | 1 |

## fiber/textile

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| FibreCastML 전기방사 메타데이터셋 | https://arxiv.org/pdf/2601.04873 | 미확인(검색 색인에만 존재) | 문헌에서 수집한 전기방사 공정 변수와 섬유 직경 분포 | 연구 1,778건, 섬유 직경 관측 68,538개, 고분자 16종(CA, 젤라틴, PA6, PAN, PCL, PDLLA, PEEK, PET, PLA, PMMA, PS, PU, PVA, PVDF, PVP, γ-PGA). PVA만 6,610건 | DOI, 고분자, 용매 1~3과 비율, 농도, 니들 직경, 콜렉터 종류, 회전속도, 전압, 유량, 팁-콜렉터 거리, 온도, 습도 → 섬유 직경 분포 | 논문 '보충자료(Supplementary Material)'로 제공(심사 중 preprint). 라이선스 미확인. 웹앱 공개 | 점도·전도도·표면장력·분자량·습도는 보고율이 12% 미만이라 모델에서 제외됨. 젤라틴·γ-PGA 같은 수계·바이오 고분자는 R²<0.59로 예측이 어려움(pH, 이온강도, Bloom 값, 가수분해도가 누락된 탓이라고 저자가 분석). 출판 편향(성공 조건 위주) | 3 |
| Cogni-e-Spin DB 1.0 (전기방사 공개 데이터셋) | https://zenodo.org/records/16731638 | 미확인(검색 색인에만 존재) | 문헌에서 수작업 추출해 정리한 전기방사 공정·용액·환경 변수와 나노섬유 형태 | 실험 레코드 809건 | 공정·용액·환경 변수, 섬유 직경과 그 편차 | Zenodo 공개(DOI 10.5281/zenodo.16731638, v2). 라이선스 미확인. 논문은 Scientific Data(Data Descriptor) | 문헌 유래라 보고 편향이 있음. 고분자 구성은 미확인 | 3 |
| FEAD (Electrospun Fiber Experimental Attributes Dataset) | https://doi.org/10.5281/zenodo.10301664 | 미확인 | 문헌 메타데이터 + 저자 자체 실험으로 만든 PVDF 전기방사 데이터 | 레코드 745건, 연구 52편, PVDF 한 종(검색 스니펫) | 용액·공정 변수, 용매계, 섬유 직경, 비드(bead) 형성 여부 | Zenodo(라이선스 미확인) | 단일 고분자(PVDF)로 범위가 좁음 | 2 |

## polymer DB (commercial datasheet)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| CAMPUS 플라스틱 DB | https://altair.com/campus-plastics | 미확인(검색 색인에만 존재) | 제조사가 제공하는 상용 그레이드 물성(ISO 10350 단일점, ISO 11403 다점 곡선) | 한 출처는 원료 생산사 27곳의 그레이드 4,600개라고 함(시점 불명). 다른 출처는 생산사 45곳 이상 참여라고 함. 최신 총 그레이드 수는 unknown | 밀도, 인장·굴곡 물성, 열변형온도, 응력-변형 곡선, 내화학성, 노화 | 무료 열람(제조사 데이터). 재배포 조건은 미확인 | 시험 표준이 통일돼 그레이드 간 비교 가능성이 높음. 범용·엔지니어링 플라스틱 위주이고 바이오 기반 그레이드는 적음. 화학구조(SMILES)가 없음 | 1 |
| UL Prospector (구 IDES) | https://www.ulprospector.com/media/info/pdf/UL-IDES.pdf | 미확인(검색 색인에만 존재) | 플라스틱 데이터시트 + UL 인증 정보(Yellow Card) | 데이터시트 107,000개 이상, 제조사 1,000곳 이상(검색 스니펫, 시점 불명). Yellow Card 보유 플라스틱 60,000종 이상 | 그레이드별 물성, 난연 등급, 인증 | 상용(무료 등록 계층 존재 여부와 조건은 미확인) | 상용 그레이드 중심이고 구조 정보가 없음 | 1 |

## polymer DB (commercial handbook)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Polymer Handbook (Brandrup·Immergut·Grulke) / Wiley Database of Polymer Properties | https://www.wiley-vch.de/en/areas-interest/natural-sciences/polymer-handbook-978-0-471-47936-9 | 미확인(검색 색인에만 존재) | 선별된 실험 물성 핸드북과 그 온라인 DB판 | 고분자 2,500종 이상, 물성 약 350종(검색 스니펫) | 열·용액·기계·광학 물성, Mark-Houwink 상수, 반응성비, 용해도 파라미터 등 | 유료(도서 구매 또는 기관 구독). 재배포 불가 | 전문가가 선별한 고품질 값이지만 갱신이 느리고 고전적 고분자 위주 | 1 |
| Polymers: A Property Database (CRC, Ellis & Smith, 2판) | https://subjectguides.uwaterloo.ca/az/polymers-a-property-database | 미확인(검색 색인에만 존재) | 상용 고분자 물성 참고 DB(도서·온라인) | unknown | unknown(상용 고분자 물성) | 유료·기관 구독 | 미확인 | 0 |

**이 조사 블록에서 확인된 데이터 공백**

- 바이오 기반 고분자 전용 공개 실험 물성 DB는 사실상 없음: 케라틴, PVA/PVAc의 가수분해도별 물성, 셀룰로오스 유도체의 치환도(DS)별 실험 물성을 정형화해 공개한 대규모 DB를 찾지 못했음. 셀룰로오스 유도체는 PolyOmics의 MD 계산값(약 5만 종)뿐이고, PoLyInfo의 실험값은 대량 추출이 금지돼 있음. ICLR 2026 워크숍 논문 'Challenges and Vision For Standardization of Biopolymer Datasets for ML'도 바이오 고분자 데이터의 파편화를 지적함
- 공개 고분자 DB 대부분은 반복단위(SMILES) 중심이고 가공·이력 변수가 거의 없음: 분자량과 그 분포, 결정화도, 가교도, 가수분해도, 용매/DES/이온성 액체 처리 조건, 열처리 이력 같은 '공정→구조→물성' 변수를 갖춘 공개 고분자 DB는 polyVERSE 용융점도(Mn·Mw·PDI·전단속도)와 MaterialsMine 정도뿐임
- 전기방사 데이터는 있지만 섬유 직경 하나에 집중돼 있음: FibreCastML(68,538개 관측), Cogni-e-Spin(809건), FEAD(745건)는 모두 섬유 직경이나 형태가 목표값임. 점도·전도도·표면장력·분자량·습도는 보고율이 12% 미만이라 모델에서 빠졌음(FibreCastML 저자). 바이오·수계 고분자(젤라틴, γ-PGA)는 예측 R²가 0.59 미만임
- 섬유 매트·부직포·막의 '기능 물성' 공개 데이터는 찾지 못했음: 투습도(WVTR), 일방향 수분이동 지표(예: AATCC 195 계열 OWTC/AOTI), 기공률·기공크기 분포, 통기도를 모은 공개 DB는 이번 검색에서 발견하지 못함. 수증기 투과 ML 연구도 데이터가 36개, 40개 수준에 불과함
- 막 데이터는 기체분리에 쏠려 있음: MSA(약 1,500종), polyVERSE, POINT2, ADEPT의 투과도는 모두 He/H2/O2/N2/CH4/CO2 기체임. 수분·액체 수송(비대칭 젖음성 막) 데이터는 공개 DB 수준에서 부재함
- 탄화(탄소 수율·잔탄율, 탄소섬유 전구체 → 탄소 특성) 정형 공개 DB를 찾지 못했음: ReaxFF 시뮬레이션 연구와 바이오차 수율 ML(데이터 약 245건) 정도만 확인됨
- DES/이온성 액체와 고분자(셀룰로오스·케라틴)의 용해도 데이터는 고분자 DB 쪽에는 없음: PPPDB와 polyVERSE의 χ, PolyOmics의 ML-χ(유기용매 15종 + 가소제 4종)는 일반 유기용매에 한정됨. DES/IL 쪽은 이번 조사 범위 밖이라 별도 확인이 필요함
- 인장강도·신율 같은 기계적 물성의 개방형 실험 데이터가 부족함: 공개 대규모 데이터는 대부분 MD 탄성률(ADEPT 약 1,000건, PolyOmics)임. 실험 인장물성은 PoLyInfo(재배포 불가)와 Polymer Scholar(웹 열람만 가능)에 갇혀 있음
- 측정 메타데이터가 빠져 있음: Tg 측정법(DSC/DMA, 승온속도), 시험 습도, 시료 두께 같은 조건이 대부분 DB에서 누락되거나 비정형임. OPC에서는 Tg 적합 방식 차이만으로 리더보드 평균 Tg가 약 77 °C 이동함
- 라이선스가 불확실하거나 서로 충돌함: PI1M(MIT 파일과 'academic only' README가 충돌), PolyOmics(HF 라이선스 미확인), Kaggle OPC(대회 규정), polyVERSE(GTRC 카피레프트형), polyBERT(재배포 금지), PoLyInfo(대량 다운로드 금지). 대회 제출물에 데이터를 재배포하거나 상업적으로 활용할 때 제약이 됨
- 한국 고분자·섬유 특화 공개 물성 DB는 이번 검색에서 확인하지 못함(KRICT 화학정보 플랫폼은 통계·동향 중심으로 보임). 한국 공공 포털 조사는 별도 범위이므로 '없다'고 단정하지 않음
- 보완 방안: (1) FibreCastML·Cogni-e-Spin·FEAD를 교차로 조화(중복 DOI 제거, 단위·변수 정의 통일)하고, 결측된 용액 물성(점도·전도도)은 PolyOmics/PPPDB의 χ와 용해도 파라미터 같은 계산 기술자로 대리 보완한다. (2) 섬유·막 기능 물성은 Open Access 논문의 표를 LLM으로 추출하되 PolyIE 형식의 소규모 정답셋(30~50편)으로 정확도를 먼저 검증한다. (3) 고분자 구조 수준은 PolyOmics를 사전학습 소스로 쓰는 Sim2Real 전이를 하고, 참가자의 소량 자체 데이터(수십 건)를 미세조정·검증 앵커로 쓴다. (4) PoLyInfo는 수동 조회 소량만 앵커로 쓰고 재배포하지 않는다

## membrane

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| MSA Polymer Gas Separation Membrane Database (Thornton, Freeman, Robeson; CSIRO 개발, Membr… | https://membrane-australasia.org/polymer-gas-separation-membrane-database/ | 미확인(검색 색인에만 존재) | 문헌 수집 실험 기체 투과계수(Barrer), 웹 DB와 다운로드 | 약 1,500개 고분자, 1950–2018년 문헌 (Xu et al. 2024 SI와 WebSearch 스니펫 기준). 이 DB를 내보낸 것으로 보이는 Yuan et al. 파생본은 1,378행 (아래 항목에서 직접 확인) | 고분자명/분류(polyimide, PIM, cellulosic 등 약 30개 class), He·H2·O2·N2·CO2·CH4 투과계수, 문헌 DOI/저자. 온도·압력·막두께·aging·측정법 메타데이터는 불완전 | 공개 웹 DB. 이용약관/라이선스는 확인 못 함 (WebFetch EGRESS_BLOCKED). 공식 인용: 'Polymer Gas Separation Membrane Database (2012)' | 자발적 기여로 만든 DB라 '불완전하다'고 명시됨. 2018년 이후 데이터가 없음. 같은 고분자에 열처리·aging 조건이 다른 값이 여러 개 있음(중복). glassy/고성능 polyimide·PIM 쪽으로 치우쳐 있음. 측정 조건(25–35°C, 1–30 atm 등)이 표준화되어 있지 않음. 바이오계는 cellulosic 16행, PVA/EVOH 일부… | 1 |
| Topchiev Institute DB 'Gas Separation Properties of Glassy Polymers' (Yampolskii, TIPS RA… | https://istina.fnkcrr.ru/publications/article/57079416 | 미확인(검색 색인에만 존재) | 유리질 고분자의 기체 투과·확산·용해 파라미터 전자 핸드북 | unknown(검색 결과에 건수 없음) | 유리질 고분자의 P, D, S(세부 미확인) | unknown(접근 방식 미확인, 공개 다운로드 여부 불명) | 1990년대 후반부터 주기적으로 갱신했다고 함. 유리질 고분자만 대상이다 | 1 |
| Barnett et al. Sci. Adv. 2020 (eaaz4301) 기체분리 GPR 학습 데이터 | https://dare.uva.nl/id/43459d6d-92a8-4ad9-8db5-ca4dfeab4060 | 미확인(검색 색인에만 존재) | 실험 투과도와 polymer fingerprint | 약 700개 고분자 구성체, 기체별 약 400–700점(WebSearch 스니펫, Xu 2024 본문) | 6개 기체 투과도, 경로 기반 해시 fingerprint | unknown. Xu et al. 2024는 이 데이터의 일부에 '접근할 수 없다'고 언급함 | 공개 여부가 불명확하다 | 1 |
| OSN Database / OMD4SRNF (Ignacz, Szekely 외; J. Membr. Sci. 713 (2024) 123356 'Open and FA… | https://www.osndatabase.com | 미확인(검색 색인에만 존재) | 문헌과 상용 데이터시트에서 수집한 OSN 여과 실험(막 재료, 합성 조건, 운전 조건, 물성, 성능) | 2024년 4월 기준 고유 여과 5,006건, 문헌 294편, 용매 42종(JMS 2024 초록). KAUST 프로필에는 '7,000점 이상, 용매·혼합 20종'으로 표기(수치 간 불일치) | 막 재료·MWCO, 합성 파라미터, 용매, 용질(구조), 온도·압력·구성(CF/dead-end), 투과도(permeance), 배제율(rejection), 원문 링크 | 오픈 액세스(FAIR/O라고 표명). 구체적 라이선스(CC 등)는 미확인. OMD4SRNF에서 외부 사용자 업로드 가능 | 성공 사례 위주의 보고 편향이 있다. polyimide(DuraMem 등) 상용막에 편중되어 있다. 운전조건(정상상태 도달, 농도 분극)이 표준화되어 있지 않다 | 1 |
| Yang M., Ren Z.J. 외 – 투과증발 ML (ES&T 2024, 58, 10128 '최대 PV 데이터셋'; ES&T 2023, 57, 5934 아세트… | https://collaborate.princeton.edu/en/publications/machine-learning-for-polymer-design-to-enhance-pervaporation-base/ | 미확인(검색 색인에만 존재) | 문헌 수집 PV 실험(막 구조, 운전조건, 용질 물성, 분리계수, 총 플럭스) | 'the largest PV data set to date'라고 표명. 정확한 건수는 unknown | polymer fingerprint, 막 구조, 운전조건, 용질 물성, separation factor, total flux | unknown(SI나 리포지토리 공개 여부 미확인) | 데이터 누수(같은 논문·같은 막)와 seed 의존성을 저자들이 직접 지적하고 관리했다 | 1 |
| Open Membrane Database (OMD; Ritt et al., J. Membr. Sci. 641 (2022) 119927; Yale/Technion… | https://openmembranedatabase.org/ | 미확인(검색 색인에만 존재) | RO 막 성능·물성·합성조건(동료심사 논문, 특허, 상용 데이터시트) | RO 막 651개(논문 및 HKU 페이지 스니펫). NF/FO 확장 여부는 미확인 | 수투과도, NaCl 배제율, 물리화학 특성(접촉각, 제타전위, 거칠기 등), 합성 조건(단량체, 농도, 반응시간 등) | 검색 스니펫에 'CC BY'가 언급되지만, 논문의 라이선스인지 DB 데이터의 라이선스인지 불분명(직접 확인 실패, EGRESS_BLOCKED) | 폴리아마이드 TFC에 편중되어 있다. 시험 조건(압력, NaCl 농도)이 제각각이다. 성능 위주 보고 편향이 있다 | 1 |
| Polymer–MOF 혼합기질막(MMM) CO2 분리 시뮬레이션 빅데이터 (Adv. Sci. 2025, PMC12021122) | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12021122/ | 미확인(검색 색인에만 존재) | 고처리량 계산으로 얻은 MMM 성능(Maxwell 모델 등) | MMM 54,117개(고분자 9종 × MOF 6,013종)(WebSearch 스니펫) | 고분자, MOF, CO2 투과도·선택도 | unknown(데이터 공개 여부 미확인) | 전부 시뮬레이션이고 고분자는 9종뿐이다 | 0 |
| Matmerize/Ramprasad PEM 양성자전도도·함수율 큐레이션 데이터 (Tran et al. J. Phys. Chem. C 2023; arXiv 260… | https://arxiv.org/abs/2212.13198 | 미확인(검색 색인에만 존재) | 문헌 실험 σ(S/cm), 함수율 λ(wt%)와 T, RH, 액체/증기 조건 | 2023년: σ 2,137점, λ 1,879점(σ의 98.5%가 –SO3⁻). 2026년: σ 2,462점, λ 2,120점, 기체 투과 4,377점(alphaXiv로 본문 확인) | SMILES와 조성, T, RH, 침지 조건, σ, λ | 원데이터 미공개. 2026 논문 Data Availability는 '공개 출처에서 수집했고 파생물은 본문에 있음'이라고만 함 | 설폰산계에 극단적으로 편중되어 있다 | 0 |
| Phua, Fujigaya, Kato – AEM 음이온 전도도·알칼리 안정성 설명가능 ML (Sci. Technol. Adv. Mater. 2023) | https://doaj.org/article/55601b420af944aabccc8b122b698de4 | 미확인(검색 색인에만 존재) | 자체 구축(in-house) AEM 구조-물성 DB | 약 300개 고분자(WebSearch 스니펫) | 단일·공중합체 구조, 음이온 전도도, 알칼리 안정성 | unknown(STAM은 OA 저널이지만 DB 공개 여부 미확인) | 미확인 | 0 |

## GitHub dataset

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| polyVERSE – Gas_permeability_solubility_diffusivity (Phan et al., npj Comput. Mater. 2024… | https://github.com/Ramprasad-Group/polyVERSE/tree/main/Other/Gas_permeability_solubility_diffusivity | 접속 확인 | long-format CSV: 속성(p/d/s) × 출처(exp/sim) × 기체, SMILES, log값, 온도, activity | master_transport_2025_08_13.csv 7,826행, 고유 고분자 1,184(직접 집계). p_exp: O2 758, N2 743, CO2 695, CH4 620, H2 524, He 456, H2O 36. d_exp_H2O 90, s_exp_H2O 34, s_sim… | property(p_exp_CO2 등), smiles_string, p_csmiles, value(log10), unscaled_value, Activity, Temp, Solvent_SMILES(기체), source | GTRC 'General Public Use License Agreement'(직접 확인). 상업적 판매·영리 목적 재배포는 별도 계약 필요. 학술 사용은 가능 | 공정 이력과 측정법은 변수로 들어 있지 않고, 반복값을 분포 샘플로 취급한다. 시뮬레이션값은 체계적으로 과대평가된다(실험과의 r 약 0.78–0.83). H2O 데이터는 56개 고분자로 소량이다 | 2 |
| Polymer-Membranes-for-Pervaporation-Separation (Wang, Xu, Tang, Jiang, ACS AMI 2022, 14, … | https://github.com/maowang-code/Polymer-Membranes-for-Pervaporation-Separation | 접속 확인 | 문헌에서 수집한 투과증발 탈수 실험(고분자, 운전조건, 성능) | data.csv 681행, 고분자 16종, 물/유기 혼합 6종(직접 집계). PVA 182, sodium alginate 118, PDMS 110, chitosan 91, PEBA 59, PTMSP 35행 | ref(논문 제목), polymer, 물 접촉각, 두께, 지지체, MMM 필러, 혼합물(물/EtOH·IPA·BuOH·EG·MeOH·AA), 공급 물 함량, 온도, 투과측 압력, 총 플럭스(kg/m²h), 분리계수, PSI, 고분자·용매 용해도 파라미터 | LICENSE 없음(재배포 권리 불명확) | 분자량·공급압이 전부 결측이다. 혼합기질 정보는 거의 없다. 같은 논문의 조건 스캔이 다수 행을 차지해 누수 위험이 있다. 고분자 수준 기술자(접촉각, δ)가 거칠다 | 2 |
| LLM-driven Extraction and ML-based Analysis of ARG Removal by Membranes (jptvxqk) | https://github.com/jptvxqk/LLM-driven-Extraction-and-ML-based-Analysis-of-ARG-Removal-by-Membranes | 접속 확인 | LLM(OpenAI)으로 논문에서 추출한 막-항생제내성유전자 제거 데이터와 추출 코드(유사도 검색→분류→구조화 추출→퍼지 평가) | merged_done_data_with_experimental_data.csv 1,584행(직접 집계), 19개 추출 필드 | ARG, 막 이름·종류(NF/RO/UF 등), 기공크기, 제타전위, 접촉각, 거칠기, 플럭스, pH, 압력, 초기농도, LRV | LICENSE 없음 | LLM 추출 오류 가능성이 있다(저자가 그림·표 대비 퍼지 평가 스크립트를 제공). 도메인이 협소하다 | 2 |
| polyVERSE H2O 하위셋 – 고분자 수증기 투과·확산·용해(실험+시뮬) | https://github.com/Ramprasad-Group/polyVERSE/blob/main/Other/Gas_permeability_solubility_diffusivity/master_transport_2… | 접속 확인 | 고분자 SMILES별 H2O 투과·확산·용해(log10), activity, 온도 | 205행/56개 고분자(p_exp_H2O 36, d_exp_H2O 90, s_exp_H2O 34, s_sim_H2O 45)(직접 집계) | property, SMILES, value, unscaled_value, Activity(수분 활동도), Temp | GTRC General Public Use License | 고분자 본연의(조밀막) 물성이라 직물·다공막 WVTR(g/m²·day)와는 단위와 메커니즘이 다르다. 대부분 polyVERSE_2025 신규 수집분이라 출처 표기가 제한적이다 | 2 |
| PolymerGasMembraneML (Yang, Tao, He, McCutcheon, Li, Sci. Adv. 2022, eabn9545) | https://github.com/jsunn-y/PolymerGasMembraneML | 접속 확인 | SMILES와 실험 투과도 학습셋(Dataset A, 결측 대치 포함), 가상 고분자 스크리닝셋 B/C/D, 사전학습 모델 | Dataset A 778행 / 고유 SMILES 353 / 고유 PID 319, 1946–2018년 문헌(직접 집계). 기체별 실측 건수: He 311, H2 283, O2 618, N2 437, CO2 482, CH4 252. Dataset B 995,799행, C는 리포지토리에 첫… | Name, PID(P010001 형식으로 PoLyInfo ID처럼 보임), Smiles, Details(측정법), Condition(온도), Reference, Year, 6개 기체 투과도, log10 값, BLR/ExtraTrees 대치값 | MIT License(리포지토리 LICENSE, 직접 확인). 데이터에도 적용되는지는 README에 'refer to paper'로만 되어 있어 모호함 | 결측이 많아 대치값이 섞여 있으므로 실측과 대치값을 구분해서 써야 한다. 동일 고분자의 반복 측정은 측정법이 달라도 별도 행으로 들어 있다. 상한선 위 데이터가 희소하다(불균형). cellulose 유도체는 12행(cellulose, CTA, ethyl cellulose, CA 등) | 1 |
| polymer_permeability_imputation (Yuan et al., J. Membr. Sci. 2021, 기체 투과도 결측 대치) | https://github.com/qyuan7/polymer_permeability_imputation | 접속 확인 | MSA DB에서 파생된 표(고분자 class, 이름, 6개 기체 투과도, 출처 DOI)와 BLR/ERT 대치값 | Database_imputed_BLR_ERT.csv 1,378행, validation_dense/sparse 각 87행(직접 집계). class 상위: Polyimides 318, High free volume 103, Vinyl 95 … Cellulosic Polymers 16 | Polymer Type(MSA class), Polymer, He/H2/O2/N2/CO2/CH4, 저자, DOI, log10 및 대치값 | 리포지토리에 LICENSE 파일이 없음(기본적으로 저작권 유보). 원천 MSA DB 약관은 미확인 | MSA DB의 편향을 그대로 물려받는다. latin-1 인코딩 문제가 있다. SMILES가 없어서 구조 기반 ML을 하려면 별도로 매핑해야 한다. CMS·MMM·zeolite 같은 비고분자 행이 섞여 있다 | 1 |
| PolyGasPerm-GREA (Xu et al., Cell Rep. Phys. Sci. 2024, 설명 가능 GNN 기체분리막 설계) | https://github.com/Jiaxin-Xu/PolyGasPerm-GREA | 접속 확인 | 기체별 CSV(SMILES, log 투과도), MSA 정제본에 2018–2022년 문헌 약 90점 추가 | H2 509, CH4 681, CO2 754, N2 794, O2 805행, 고유 SMILES 약 825(직접 집계). 논문 기준 836개 단일중합체. 무라벨 스크리닝용 PoLyInfo 단일중합체 12,769개 | SMILES, 기체 투과도(동일 구조 다중값은 중앙값으로 축약) | LICENSE 파일 없음 | 공중합체·복합재·개질막은 제외했다. 중앙값 축약으로 조건 정보가 사라졌다. 상한선 위 데이터는 1.4–7%에 불과하다. polyimide 쪽으로 치우쳐 있다 | 1 |
| ML-Membrane-Permeability-Prediction (zentou88, 'Practical Prediction of Gas Separation Pe… | https://github.com/zentou88/ML-Membrane-Permeability-Prediction | 접속 확인 | 막 구조 변수, 운전조건, 기체 물성에 대한 Permeability 표 | Book1000.csv 3,617행 = 막 603개 × 기체 6종(직접 집계) | Aging, 평균 두께, 평균 기공크기, 총/미세기공 부피, 비표면적, 기체 kinetic diameter·임계온도·분극률, 온도, ΔP, feed/sweep 유량, 몰분율, Permeability | LICENSE 없음 | 재료 종류와 출처 문헌이 README에 문서화되어 있지 않고, 결측이 많다(KNN 대치) | 1 |
| osn-solvent-model (Ignacz, Algadhi, Szekely, J. Membr. Sci. 2023 – OSN 용매효과 XAI) 문헌 테스트셋 | https://github.com/ignaczgerg/osn-solvent-model | 접속 확인 | 문헌 OSN 배제율 테스트셋과 chemprop 모델 가중치 | data/literature.csv 120행(직접 확인). 학습용 자체 측정(용질 407종 × 용매 11종, polyimide 막)은 WebSearch 스니펫 기준이며 리포지토리에는 없음 | DOI, Year, Journal, Membrane, MWCO, solvent_name·SMILES, solute SMILES, rejection, Temperature, Process configuration | LICENSE 없음 | 소량이고 DuraMem 위주다 | 1 |
| polyVERSE – 고분자 내 용매 확산·수착 (Solvent_Diffusivity_Sorption; Nat. Commun. 2023 + npj 2025) | https://github.com/Ramprasad-Group/polyVERSE/tree/main/Other/Solvent_Diffusivity_Sorption_MTL_NCM | 접속 확인 | 고분자-용매 쌍별 확산계수(실험/시뮬레이션 selector)와 수착(uptake) | master_solvent_diffusivity_dataset.csv 3,043행(ncomm 2023 2,045 + npj 2025 999), master_uptake_sorption_dataset.csv 2,276행(직접 집계) | Polymer/Solvent canonical SMILES, Temperature, 용매 무게분율, 실험·시뮬 selector, log10 확산계수 / Activities, log10 uptake, 용매 밀도, MW | GTRC General Public Use License(영리 판매 금지) | 시뮬레이션 비중이 크고 상용 합성고분자 위주다 | 1 |
| polyVERSE – 음이온교환막(AEM) 전도도·함수율·팽윤 및 알칼리 열화 (Schertzer et al. J. Mater. Inform. 2025; J. … | https://github.com/Ramprasad-Group/polyVERSE/tree/main/Other/Conductivity_anionic_water_uptake_swelling | 접속 확인 | 공중합체(최대 3단량체 SMILES와 조성)별 AEM 물성. 별도로 알칼리 안정성 시계열 | AEM_anion_conductivity_WU_Swelling.csv 1,018행(OH⁻ 전도도 459, WU 346, 팽윤 213), aem_aging.csv 2,149행(직접 집계) | smiles1-3, c1-c3, Temp, RH, liquid/vapor 여부, prop, value. aging은 KOH 몰농도, 첨가제, 이론 IEC, 시험온도, 경과시간(h) | GTRC General Public Use License(영리 판매 금지) | 합성 방향족 AEM 위주이고 바이오계(키토산 등)는 없을 것으로 보인다(미확인). 측정조건(액체/증기)이 혼재하지만 변수로 기록되어 있다 | 1 |
| loose-nanofiltration (yuanjiZhang717) – 염료/염 분리 loose NF 앙상블 ML 데이터 | https://github.com/yuanjiZhang717/loose-nanofiltration | 접속 확인 | 문헌 수집 loose NF 막 구조·운전·성능(염료, 염) | data.xlsx all_data 시트 약 272행(헤더 2행 제외, 직접 확인) | 지지막, 필러, 블렌딩 여부, 제타전위, 기공반경, 접촉각, 거칠기, 공극률, 압력, 염·염료 농도, 유효면적, Congo Red/Direct Red 23 배제율, NaCl/Na2SO4/MgSO4/MgCl2 배제율, 수투과, DOI | LICENSE 없음 | 소량이고 결측이 많다(다중 헤더). 출처 문헌의 국가 편중 가능성이 있다(미확인) | 1 |
| ML-PEM-Dataset – PEM 수전해 셀 설계 1,203건 | https://github.com/amirayahea/ML-PEM-Dataset | 접속 확인 | 문헌 수집 PEM 전해조 설계·운전·성능 표 | PEM_Dataset.xlsx 1,203행(직접 확인) | 전극 종류·면적, 유로 면적, membrane_type, 촉매, 전해질, 셀 설계, 전압, 전류밀도 등 | LICENSE 없음 | 막 재료 수준이 아니라 소자 수준이다 | 0 |
| support-information-about-polyamide-nanofiltration-membranes (losema1) – 폴리아마이드 NF 이온 선택성… | https://github.com/losema1/support-information-about-polyamide-nanofiltration-membranes | 접속 확인 | 문헌 수집 NF 막 구조와 단일/혼합염 배제·선택도 | 총표 시트 약 152행(직접 확인) | 기공반경 rp, MWCO, 등전점, 제타전위(pH 7), NaCl·KCl·LiCl·CaCl2·MgCl2·Na2SO4·MgSO4 배제율, Cl⁻/SO4²⁻·Li⁺/Mg²⁺ 등 선택도, pH, 압력, 농도 | LICENSE 없음. README에 '사용 시 저자 문의' | 헤더가 중국어다. 소량이다 | 0 |
| Polyamide-nanofiltration (Atif255) – 미량오염물 제거율과 Na2SO4 배제 데이터 | https://github.com/Atif255/Polyamide-nanofiltration | 접속 확인 | 화합물 기술자와 막 특성에 따른 제거율 | 'Removal rate %.xlsx' 2,102행, Na2SO4.xlsx 1,243행(직접 확인) | pH, 화합물 MW·Kow·투영 크기, 막 MWCO·접촉각·제타전위, 압력, 시간, 초기농도, 제거율. Abraham 기술자(E,S,A,B,V). Na2SO4 셋은 반경, 제타, 압력, 농도 | LICENSE 없음 | 출처 문헌이 문서화되어 있지 않다 | 0 |
| QSAR-Model-for-Membrane-Nanofiltration (satyamagni) – 산업폐수 GC-MS 기반 NF 배제율 | https://github.com/satyamagni/QSAR-Model-for-Membrane-Nanofiltration | 접속 확인 | 실폐수 6개 배치 × NF/세라믹 막의 화합물별 배제율 | 화합물 41개 × 막 7종(README), 엑셀 시트 51/39/67행 | MW, pKa, Kow, 용해도, 막(200–8500 Da, NF90, NFX, NFS), % rejection | LICENSE 없음 | 극소량이고 단일 기업(Aevitas) 사례다 | 0 |
| Sulfonated MXene membrane desalination dataset (lukkathuyavan-cell) | https://github.com/lukkathuyavan-cell/Sulfonated-Mxene-Membrane-desalination-dataset | 접속 확인 | 엑셀(전해질 플럭스·배제, 플럭스 파울링 동역학) | Scenario-1 98행, Scenario-2 40행(직접 확인) | 미확인(시나리오 제목만 확인) | LICENSE 없음 | 극소량이고 문서화가 없다 | 0 |

## general materials DB

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Materials Cloud Archive record 2023.14 – CO2 분리용 고분자막 계산 탐색 데이터 | https://archive.materialscloud.org/record/2023.14 | 미확인(검색 색인에만 존재) | 학습 데이터(단일중합체 CO2 투과도, Tg, Td)와 계산 스크리닝 결과 | 학습 데이터 1,169개 단일중합체(WebSearch 스니펫) | CO2 permeability, Tg, Td | unknown(Materials Cloud는 보통 CC 라이선스지만 이 레코드는 미확인) | 스니펫 정보뿐이라 세부 출처 미확인 | 1 |

## polymer DB

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| PoLyInfo (NIMS) – 기체 투과 관련 물성 레코드 | https://polymer.nims.go.jp/en/ | 미확인 | 문헌 기반 고분자 물성 DB(기체 투과 레코드 포함) | 단일중합체 12,769개를 '기체 수송 데이터가 없는' 무라벨 집합으로 쓴 사례가 있음(Xu 2024). 기체·수증기 투과 레코드 건수는 unknown | 구조, 합성·가공, 물성(기체 투과계수 등). 수증기 투과 항목이 있는지는 미확인 | 회원 가입 후 웹 열람. 대량 다운로드와 재배포에 제한이 있다고 알려져 있으나 이번 조사에서 확인하지 못함 | 미확인 | 1 |
| Polymer Genome / PolymRize 기체 투과도 예측 모델 | https://www.polymergenome.org | 미확인 | 웹 예측 서비스(학습 데이터 원본은 다운로드 불가) | Zhu et al. 2020 원모델은 315개 고분자로 학습. 이후 1,052개로 확장(Phan 2024) | SMILES 입력, 6개 기체 투과도 예측 | 웹 사용만 가능(학습 데이터는 polyVERSE에 일부 공개) | Xu 2024에 따르면 신규 polyimide 예측이 실측보다 크게 낮았다 | 1 |

## GitHub

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| PyVaporation (Membrizard) – 투과증발 모델링 도구와 상용막 실험 데이터 | https://github.com/Membrizard/PyVaporation | 접속 확인 | VLE 데이터(이성분 8종)와 상용 PV막 확산곡선·이상 실험 CSV | 막 디렉토리 5개(Pervap 2510/4100/4101, Romakon PM-102, Chang et al. 1998)와 템플릿(직접 확인). 건수는 소량 | 성분, 온도, 공급조성별 투과도와 확산곡선 | Apache License 2.0(LICENSE.md 확인) | 소수 상용막이고 테스트용이다 | 1 |
| nf10k (ignaczgerg) – NF/OSN 배제율 예측 모델 | https://github.com/ignaczgerg/nf10k | 접속 확인 | chemprop 기반 예측 코드와 사전학습 모델(학습 데이터 원본은 리포지토리에 없음) | 막 7종(DM300, GMT-oNF-2, PBI, NF90, PMS600, SM122, NF270) × 용매 9종 × 구성 3종 예측. 학습 데이터 규모는 unknown(이름이 '10k'를 시사하지만 미확인) | solute SMILES, membrane, solvent, configuration → rejection | MIT(LICENCE 파일 확인, 'Copyright (c) 2024 TBD') | 데이터를 공개하지 않았다 | 0 |

## generic repository

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| US EPA – 'Effect of membrane performance variability with temperature and feed compositio… | https://catalog.data.gov/dataset/effect-of-membrane-performance-variability-with-temperature-and-feed-composition-on-pe… | 미확인(검색 색인에만 존재) | 논문 그림 값(xlsx, 'Calculated Values for Variable Permeability Graphs') | unknown(그림 데이터 수준, 소량). 대상: NaA 제올라이트와 PVA 막 2종의 에탄올/물 | 온도·공급조성에 따른 투과도 다변수식 계산값 | 미국 정부 공개 데이터(구체 라이선스 미확인), DOI 10.23719/1526074 | 문헌 데이터를 재계산한 값이다 | 1 |

## patents/text

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 특허 전문 XML(USPTO 공개공보)에 수록된 MMT/AATCC 195 결과표 – 예: US20230240400A1 'No Sweat Marks Fabric … | https://raw.githubusercontent.com/0pearlee/dtd_info/2202df2579e3b134da69b6eeb2f9e62868aa908b/000/US20230240400A1/US2023… | 접속 확인 | 특허 본문 표(비정형 XML 표). 정형 데이터셋이 아님 | unknown. 예시 1건에서 지수 10종(WTT, WTB, ART, ARB, MWRT, MWRB, SST, SSB, R(%), OMMC)과 편차·등급이 완전한 표로 들어 있음을 확인. GitHub 코드검색에서 'one way transport' OMMC 동시 언급은 이 미러 기준 3… | Top/Bottom wetting time, absorption rate, max wetted radius, spreading speed, one-way transport capability R(%), OMMC, 등급(1–5). 직물 조성·구조는 본문 서술에 있음 | 특허 공보는 일반적으로 공개 문서다(USPTO bulk data, Google Patents). 이 리포지토리 미러의 라이선스는 미확인 | 특허 편향(유리한 결과만 제시), 샘플 수가 적다, 시험조건 서술이 불균일하다, 표 파싱이 필요하다 | 2 |

## fiber/textile

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Electrospinning-Data.org / Cogni-e-SpinDB 1.0 (Mahdian, Ender, Pardy; arXiv 2603.27841; S… | https://electrospinning-data.org | 미확인 | 전기방사 공정-구조-물성 레코드(실패·불안정 포함), SEM 이미지, Excel 다운로드 | 초기 릴리스 809 레코드, 문헌 57편, 고분자 12종, 용매계 14종(PVDF, PVA, PVP, PAN이 다수). PVA/물 하위셋 조회 예시 108건 | 고분자·용매 조성, 점도·표면장력·전도도, 전압·유량·TCD, 온도·습도, 섬유경·분포, 형태 어휘(Cogni-EMCV), 기계물성. functional properties 테이블에 porosity, permeability, wettability 필드가 있으나 초기 데이터에서 채워진 … | 웹과 버전별 다운로드. 스키마와 어휘는 Zenodo(10.5281/zenodo.18847740, 10.5281/zenodo.16731638). 데이터 라이선스는 미확인 | 형태(섬유경) 중심이다. 환경변수 보고가 희소하다. 투습·일방향 수분이동 데이터는 사실상 없을 것으로 보인다 | 2 |

**이 조사 블록에서 확인된 데이터 공백**

- 일방향(Janus) 수분이동, OWTC/R(%), OMMC, MMT(AATCC 195) 공개 데이터셋은 이번 조사에서 하나도 찾지 못했다. GitHub 저장소 검색(moisture management fabric)은 0건이었다. WebSearch(Mendeley/figshare/Zenodo + AATCC 195/OMMC)에서도 데이터셋이 나오지 않았고, PubMed 검색도 0건이었다. 수치는 개별 논문의 그림·표와 특허 본문 표에만 흩어져 있다(특허 XML 1건에서 전체 MMT 지수표를 직접 확인함).
- 직물·막의 투습(WVTR/WVP, ASTM E96 upright/inverted cup, ASTM F2298, JIS L1099, ISO 11092 Ret 등)도 시험법 메타데이터를 갖춘 구조화 공개 DB를 찾지 못했다. GitHub 저장소 검색 'water vapor transmission rate'와 'fabric air permeability dataset'은 모두 0건이었다. 공개 ML 논문들(단일저지 100종 등)은 기업·기관 데이터라 비공개다.
- 고분자 수준의 수증기 투과 공개 데이터는 polyVERSE H2O 하위셋(56개 고분자, 205행)뿐이다. 조밀막 물성이라 직물·다공성 전기방사막 WVTR로 바로 변환할 수 없다(두께, 공극, 경계층 항이 없음).
- 방향성 수증기 투과(Janus) 연구(Empa/SUTD, arXiv 2301.00348: ISO 11092 sweating guarded hotplate와 이중챔버 방법, n=4)도 데이터 공개 진술이 없다. 시험법끼리 단위와 개념이 다르다(Ret vs WVP vs WVTR, MMT 지수). 그래서 문헌값을 '조화(b)'하는 일 자체가 연구 기여가 될 수 있는 영역이다.
- Robeson 상한선은 상한선 식과 파라미터만 공개되어 있다. 상한선을 정의한 원 데이터 포인트를 정리한 공개 CSV는 찾지 못했다. 실질적 대체재는 MSA DB와 그 파생본(Yuan 1,378행, Yang 778행, Xu 약 825 SMILES)이다.
- 바이오계 고분자는 막 데이터에서 극소수다. MSA 파생본은 cellulosic 16/1,378행, Yang Dataset A는 cellulose 유도체 12/778행이고 케라틴은 0이다. 키토산·알지네이트·PVA가 의미 있게 들어 있는 공개 막 데이터는 투과증발 Wang 2022 셋(681행 중 PVA 182, SA 118, CS 91)이 유일하다.
- 이온교환막: 대형 PEM σ/λ 큐레이션(2,462/2,120점, Ramprasad/Matmerize)은 미공개다. 공개된 것은 polyVERSE AEM 약 1천 행과 열화 약 2천 행뿐이다. 키토산 등 바이오계 이온교환막 데이터셋은 찾지 못했다.
- 투과증발 최대 데이터셋(Yang/Ren ES&T 2024)과 OSN Database 5,006건은 공개된다고 하지만, 라이선스와 다운로드 형식은 확인하지 못했다(사이트 EGRESS_BLOCKED). OMD도 'CC BY' 스니펫이 DB의 라이선스인지 논문의 라이선스인지 불분명하다.
- GitHub 소규모 막 데이터셋(NF, PV, GREA, Yuan 등) 대부분이 LICENSE 파일이 없다. 기본값은 저작권 유보이므로 경진대회 제출물에 재배포하거나 가공본을 공개하면 권리 문제가 생길 수 있다. 인용만 하고 원본 링크로 대체하는 쪽이 안전하다.
- 측정조건 메타데이터 부족이 공통 문제다. 기체 투과는 온도 25–35°C, 압력 1–30 atm이고 aging·열이력·두께가 누락되어 있다. PV는 분자량과 공급압이 전부 결측이다. NF는 압력과 농도가 이질적이다. 같은 논문 조건 스캔이 반복되어 데이터 누수 위험도 있다(Yang/Ren 2023이 지적).
- 이번 조사의 한계: 하위 에이전트들이 함께 쓰는 WebSearch 호출 한도(턴당 200회)를 조사 도중에 소진해서 PoLyInfo 수증기 투과 레코드 수, Topchiev DB 접근성, OMD/OSN 라이선스, 한국 공공데이터(KIPRIS 특허 MMT 표, data.go.kr, DYETEC 보유 데이터)는 확인하지 못했다. 사용자가 후속 메시지를 보내면 검색을 이어 갈 수 있다.

## fiber/textile

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Cogni-e-SpinDB 1.0 (TalTech) - GitHub/Zenodo | https://github.com/taltechloc/Cogni-e-SpinDB | 접속 확인 | 문헌에서 수작업 추출한 표 형식 CSV (공정→섬유 직경/형태) | 809 records, 57 DOI, 12 polymers, 20 fields (CSV 직접 집계: PVDF 351, PVA 141, PVP 95, PAN 62, PS 45, PCL 26, PMMA 20, γ-PGA 18, PDLLA 16, CA 15, PET 12, PLA 8) | polymer, solvent(s)/블렌드 조성(JSON), 농도+단위, needle type/gauge, collector type, rpm, kV, flow rate(mL/h), tip-collector distance, 온도, 습도, 섬유 형성 안정 여부, 평균 직경(nm), 직… | 공개. GitHub LICENSE 파일은 CC0 1.0인데 README 배지는 MIT로 표기되어 서로 다름. Zenodo 레코드 라이선스는 확인 못 함 | PVDF가 43%로 편중됨. 결측이 많음: needle gauge 310/809, 온도 214/809, rpm 555/809 (직접 집계). 성공 사례 위주로 보고됨. 바이오고분자는 CA 15건뿐이고 케라틴·젤라틴·키토산은 없음. 논문 기준선(5-fold CatBoost): PVDF R² 0.70, PVA R² 0.43 → 고분자당 표본이 적고 이질적임 | 3 |
| Cogni-e-SpinDB 예비 데이터셋 (TalTech Data Repository, Table1/Table2) | https://data.taltech.ee/records/pg8h6-rhw07 | 미확인(검색 색인에만 존재) | Excel 2개 표: 주석 달린 문헌 목록 + N/A 포함 전체 추출 레코드 | Table1: 문헌 318건 / Table2: 146개 출처에서 1,913 records (N/A 포함) - Sci Data 논문 Methods 기준 | 최종본과 같은 공정·용액·환경 변수(결측 포함) | 공개 저장소. 라이선스는 확인 못 함 | 불완전 레코드가 그대로 남아 있음. 출처마다 단위와 보고 관행이 다름 | 2 |
| Electrospinning-Data.org (FAIR 실시간 DB, Cogni-EMCV/Cogni-EVVR) | https://electrospinning-data.org | 미확인 | 관계형 DB(MySQL) 웹 플랫폼. 버전별 Excel 내보내기 + SEM 이미지 ZIP | 초기 809 records(Cogni-e-SpinDB에서 가져옴), 12 polymers, 14 solvent systems, 57편. 이후 커뮤니티 기여로 확장 예정 | 공정-구조-물성 스키마. 실패·불안정 기술자, 7축 형태 통제어휘(Shape/Topography/Size/Size variation/Composition/Texture/Defects), 물리 제약 검증 규칙(P-rules) | 웹 다운로드 가능하다고 기술됨. 라이선스는 확인 못 함 | 현재 내용은 Cogni-e-SpinDB와 같고, 전문가 검수가 병목임. 환경변수(T/RH) 보고율이 가장 낮다고 저자가 명시함 | 2 |
| FibreCastML 메타데이터셋 (Manchester Met.) | https://arxiv.org/abs/2601.04873 | 미확인(검색 색인에만 존재) | 문헌 메타데이터셋(개별 섬유 직경 관측치 = 분포 수준) + R Shiny 웹앱 | 68,538 개별 섬유 직경 관측, 1,778 studies, 16 polymers (CA, gelatin, nylon6, PAN, PCL, PDLLA, PEEK, PET, PLA, PMMA, PS, PU, PVA, PVDF, PVP, γ-PGA) | DOI, polymer, 용매 최대 3종+비율, 농도, needle, collector, rpm, kV, flow rate, 거리, T, RH → 직경 분포 | 웹앱(electrospinning.shinyapps.io)만 언급됨. 원시 데이터 다운로드 경로와 라이선스는 확인 못 함 | 고분자별로 따로 모델링함. gelatin·γ-PGA·sPEEK는 R²<0.59 (pH·이온강도·단백질 형태 같은 미기록 변수 때문). 같은 그룹의 SpinCastML은 '1,778 datasets'로 표기해 단위가 모호함 | 2 |
| SpinCastML (역설계 앱 + 용해도/혼화성 규칙표) | https://arxiv.org/abs/2602.09120 | 미확인(검색 색인에만 존재) | 문헌 데이터 + polymer-solvent 용해도표(OK/COND/NO, 최대 비율) + solvent-solvent 비혼화 목록. Windows exe에 데이터가 함께 들어 있음 | 68,480 섬유 직경, 1,778 datasets, 16 polymers | 용액·공정·환경 변수, 용매 비율(Dirichlet 생성), 화학 타당성 플래그 | 'open-source'라고 주장하나 저장소 URL과 라이선스는 확인 못 함(GitHub 검색 결과 0건) | 안정적으로 섬유가 형성된 레코드만 남김(실패 제외). 고분자 불균형을 log 가중 Sobol+D-optimal로 보정함 | 2 |
| FEAD 계열 PVDF 전기방사 데이터 + HSP 특징 (karthikbsk GitHub) | https://github.com/karthikbsk/Electrospinning-fiber-diameter-prediction | 접속 확인 | xlsx 표(문헌 31편 + 'FERN lab experiment data') | 997 rows, PVDF 단일 고분자 (직접 집계) | 용매/비율, 혼합 용매 δ, Ra(HSP 거리), RED, Flory-Huggins χ, 농도 wt%, kV, 거리, feed mL/h, 섬유 직경 nm | 저장소에 LICENSE 파일이 없어 재배포 권리 불명 | PVDF만 있음. 용매 칸 705행이 비어 있음(상위 행 상속 구조). FEAD(IIT Jodhpur)와 출처가 겹칠 가능성 | 2 |
| Spider Silkome Database (1000 spider silkomes) | https://mat-dacs.dxmt.mext.go.jp/en/?p=842 | 미확인(검색 색인에만 존재) | 웹 DB: 서열(전사체) + 실측 물성 | 전사체 1,098종, dragline silk 물성 446종 × 12개 물성 (Sci Adv 2022 초록) | 인장강도, 신율, 인성, 영률, 열·구조(XRD)·수화 물성, spidroin 서열/아미노산 모티프 | 논문에서 'open data'라고 명시. 정식 라이선스는 확인 못 함(spider-silkome.org) | dragline 한 종류이고 종 평균값임. 측정 프로토콜이 한 컨소시엄이라 일관성은 높음. 인공 방사 섬유가 아님 | 2 |
| 단일 식물섬유 인장 시험 실험실 간 비교(benchmark) 연구 (HAL) | https://hal.sorbonne-universite.fr/ENSMP_MAT/hal-04676142v1 | 미확인(검색 색인에만 존재) | 실험실 9곳 round-robin 결과 | 섬유 약 1,250개(대마·아마 3개 배치) | 인장강도(flax 383-1107 MPa, hemp 252-577 MPa 범위), 직경 측정법, 시험 조건 | 원시 데이터 공개 여부 unknown | 같은 섬유라도 실험실에 따라 값이 크게 갈림(그 자체가 연구 결과) | 2 |
| FasTEX ATR-FTIR 섬유 스펙트럼 (KCL/Northumbria; Mendeley rx3fjgz96x) | https://data.mendeley.com/datasets/rx3fjgz96x/3 | 미확인(검색 색인에만 존재) | ATR-FTIR 스펙트럼(원시/베이스라인 보정/평균/전처리 3종 행렬) + 코드 | 스펙트럼 160개, 검증 시료 137개, 섬유 세부유형 26종(천연·인조, 순섬유만) | 4000-550 cm⁻¹, 섬유 클래스/유형/세부유형, 출처 | 공개(라이선스 미확인) | 순섬유만이라 혼방이 없음. 세부유형당 표본이 적음 | 2 |
| 리그닌계 탄소섬유 문헌 비교표 (Polymers 2022, PMC9269417 Table 1/2) | https://pmc.ncbi.nlm.nih.gov/articles/PMC9269417/table/polymers-14-02591-t001 | 미확인(검색 색인에만 존재) | 리뷰 논문 표 | 수십 행 수준(정확한 수 미확인) | 리그닌 종류(SKL, HKL, 아세틸화 등), 방사법, 안정화/탄화 조건, 인장강도(0.15-1.06 GPa), 탄성률(약 40-52 GPa) | OA 논문 표 | 리뷰 요약값이라 조건 보고가 불완전함 | 2 |
| FEAD (Electrospun Fiber Experimental Attributes Dataset, IIT Jodhpur) | https://research.iitj.ac.in/publication/towards-an-interpretable-machine-learning-model-for-electrospun | 미확인(검색 색인에만 존재) | PVDF 문헌 메타DB + 자체 실험 | Cogni 논문 기준 745 records, 52 studies, 정제 후 약 340건 | 용액·공정 변수, χ, RED, 직경, bead 형성 여부 | unknown | PVDF만 있고 원래 구조가 ML용이 아님(Cogni 저자 지적) | 1 |
| AriadneD electrospinningdata / PVA-electrospinning (GitHub 소규모 표) | https://github.com/AriadneD/electrospinningdata | 접속 확인 | CSV 3개(논문 3편에서 추출) + 보간으로 증강한 CSV | data1 26행, data2 9행, data3 17행 (직접 확인). PVA-electrospinning 저장소에 augmented_data1~3 | voltage, concentration, rotational speed, distance, flow rate → diameter | LICENSE 파일 없음 | 아주 작음. 증강본은 보간으로 만든 합성값이라 실측으로 쓰면 안 됨 | 1 |
| Wichita State 전기방사 3,000점 데이터 (XGB+GA 역설계) | https://soar.wichita.edu/entities/publication/4a6007ff-a3eb-4e21-b8aa-2ccdf9e2d003 | 미확인(검색 색인에만 존재) | 문헌 추출 표(학위논문/논문) | 약 3,000 data points (스니펫 기준) | 고분자, 용매, 공정변수 → 직경. PS·PVC로 실험 검증 | 데이터 공개 여부 unknown | XGB R² 0.94, RMSE 275 nm. 무작위 분할이라 연구 간 누수 가능성 | 1 |
| DiameterJ 검증 데이터셋 (NIST/Data in Brief 2015) | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4556745/ | 미확인(검색 색인에만 존재) | 합성 이미지, 강선 SEM, 전기방사 고분자 SEM + 분할 결과 + 출력값 | 합성 이미지 130장, 강선 SEM 24장, 전기방사 SEM 다수(정확한 수 미확인) | 섬유 직경 분포, 분할 알고리즘별 결과, FibraQuant 비교 | unknown (NIST 관련 데이터) | 측정 알고리즘 검증용이라 공정 변수는 없음 | 1 |
| Data in Brief 개별 전기방사 데이터 기사 묶음 (P(3HB-co-4HB), PAN/halloysite, PVOH-epoxy, 폐PET, DegraPo… | https://doi.org/10.1016/j.dib.2019.104777 | 미확인 | 논문 부속 표·이미지(실험 단일 연구) | 기사당 수~수십 조건 (예: PHA 농도·전압·주입속도 조합, PAN/HNT 건·습윤 기계물성) | 공정변수, SEM 직경, 기계물성, 접촉각, FTIR 등 기사마다 다름 | Data in Brief 기사(CC BY 계열). 부속 데이터 라이선스는 기사별로 다름 | 단일 연구라 조건 폭이 좁음. 형식이 표준화되어 있지 않음 | 1 |
| 천연섬유 복합재 인장 통계 데이터 (Mendeley v25pzywt5c, Data in Brief 2017) | https://data.mendeley.com/datasets/v25pzywt5c/1 | 미확인(검색 색인에만 존재) | 원시 응력-변형률 곡선 + 계산 물성 + Weibull Python 코드 | 약 500 시편 (flax/jute/carbon × epoxy/vinyl ester, 직물 형태·배향 다양) | 탄성률, 강도, 파단 변형률, 섬유 배열, 수지 | unknown (Mendeley Data) | 섬유 단독이 아니라 복합재 수준이고, 연구실 한 곳의 데이터 | 1 |
| AL-Oqla 등 천연섬유 조성-물성 GP 모델 표 (arXiv 2404.07213) | https://arxiv.org/abs/2404.07213 | 미확인(검색 색인에만 존재) | 논문 표(문헌 범위값) | 섬유 10종(flax, hemp, jute, kenaf, ramie, sisal, banana, oil palm, cotton, coir) | 셀룰로오스/헤미셀룰로오스/리그닌/수분 함량, MFA → 영률, UTS, 신율(범위값) | arXiv 논문 본문 | n=10이고 값이 범위라 중간값으로 대체함. LOO에서 UTS 최고 R² 0.65 → 과적합 위험 | 1 |
| NIST 고성능 단섬유 Weibull 크기효과 데이터 (mds2-4239) | https://data.nist.gov/od/id/mds2-4239 | 미확인(검색 색인에만 존재) | MATLAB .mat (게이지 길이별 응력·직경·하중·면적) | 섬유 3종(LCP-1, Aramid-1, Amide-1), 다중 게이지 길이. 정확한 개수 미확인 | stress, diameter, force, area, gauge length. Weibull MLE + bootstrap 1만 회 | NIST 공개 데이터(정식 라이선스 문구 미확인) | 합성 고성능 섬유뿐임 | 1 |
| 작업복용 편성물 열·수분 관리 물성 (PMC12029065) | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12029065/ | 미확인(검색 색인에만 존재) | 논문 표(측정값) | 편성물 18종 | 열저항, 수증기 저항, 공기투과도(700-1200 mm/s), MMT OMMC(0.5-0.7) | OA 논문 표(재사용 조건은 논문 라이선스를 따름) | 아주 작음. 상용 원단이라 조성 정보가 제한적 | 1 |
| AI 기반 원단 물성·태(handfeel) 예측 체계적 리뷰 (PMC11509711) | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11509711/ | 미확인(검색 색인에만 존재) | 체계적 문헌고찰(데이터셋 목록 포함 가능) | unknown | KES-F/FAST 물성, 태 평가, ML 기법 | OA 리뷰 | 리뷰 대상 연구 대부분이 비공개 데이터를 씀(KES-F 공개 데이터셋은 검색으로 찾지 못함) | 1 |
| Deep4Chem 유기 발색단 광학물성 DB (Sci Data 2020) | https://figshare.com/articles/dataset/DB_for_chromophore/12045567 | 미확인(검색 색인에만 존재) | CSV(SMILES + 광학물성) | 20,236 발색단-용매 조합, 발색단 7,016종, 용매 365종 + 고체 매트릭스 17종, 논문 1,358편 | 흡수·발광 λmax, FWHM, 몰흡광계수, PLQY, 수명 | figshare 공개. 라이선스는 확인 못 함 | 광전자·바이오이미징 염료 중심이고, 섬유에 염착된 상태가 아니라 용액 상태 값임 | 1 |
| DyeDactic 천연 색소 데이터 (Colorifix GitHub) | https://github.com/Colorifix/DyeDactic | 접속 확인 | CSV(천연 색소 λmax) + TD-DFT/MPNN 학습 데이터 | data/pigments.csv 647줄(논문 기준 천연 색소 647종) | 이름, 화학 클래스, 생물종, SMILES, λmax, ε, 용매, 인용 | AGPL-3.0 (README 배지) | 문헌 수집이라 용매·측정 조건이 제각각 | 1 |
| BioColour Library (핀란드 BioColour 프로젝트) | https://library-biocolour.2.rahtiapp.fi | 미확인(검색 색인에만 존재) | 웹 DB(분류·화학·염색 섹션, 반사 스펙트럼) | 출처 399건, 용어 1,328개, 색 측정 664건(CIELAB 및/또는 반사스펙트럼) | 염료원 분류, 화합물, 염색 시료 CIELAB/반사율, 매염 정보 | 웹 공개. 라이선스는 확인 못 함 | 문헌 집적이라 측정 조건이 이질적이고 견뢰도는 체계적이지 않음 | 1 |
| 산업 염색 레시피→CIELAB 다중출력 모델 연구 (Autonomous Intelligent Systems 2024) | https://link.springer.com/article/10.1007/s43684-024-00076-8 | 미확인(검색 색인에만 존재) | 산업 염색 데이터 기반 ML 논문 | unknown | 염료·조제 투입량, 공정조건 → L*, a*, b* | 데이터 공개 여부 unknown(산업 데이터로 추정) | 기업 데이터라 재현할 수 없음 | 1 |
| NIST NIR-SORT (mds2-3325; Sci Data 2026) | https://data.nist.gov/od/id/mds2-3325 | 미확인(검색 색인에만 존재) | NIR 스펙트럼(benchtop + handheld) + 원단 현미경 이미지 + 메타데이터(csv/xlsx/py) | v1.0/2.0: 원단 113종(출처 확인 70 + 미염색 혼방 20 + 사용 후 11 + 사용 전 12) + 섬유 시편 61종, 시료당 약 7회 반복 | 833-2500 nm(benchtop), 1550-1950 nm(handheld 2종), 섬유 조성, 측정 불확도 | NIST 공개 데이터('These data are public'). 정식 라이선스 문구는 확인 못 함 | 저자들이 사용 후/사용 전(Source C/D) 시료는 라벨 불확실로 학습용 비권장. 종류 수가 제한적 | 1 |
| OpenTextile-NIR (VTT; Data in Brief 2026) | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12925456/ | 미확인(검색 색인에만 존재) | SWIR 초분광 영상 + RGB 사진 + 메타데이터 | 산업 후 폐의류 시료 71개, 스펙트럼 1,100만 개 이상(주석 600만 개 이상) | 섬유 조성 %(제조사 라벨), 색, 평균 스펙트럼 | unknown | 조성 라벨을 화학적으로 검증하지 않음(이상치 11건 표시). 핀란드 시료 한 곳 | 1 |
| Open Specy (Raman/FTIR 참조 라이브러리 + R 패키지) | https://github.com/wincowgerDEV/OpenSpecy-package | 접속 확인 | 분광 매칭 도구 + 온라인 참조 라이브러리(AWS 배포) | 라이브러리 크기는 확인 못 함 | Raman/FTIR 스펙트럼, 물질 메타데이터 | CC BY 4.0 (DESCRIPTION 파일) | 미세플라스틱 중심 | 1 |
| TMC Fibre Fragmentation Data Portal (The Microfibre Consortium) | https://www.europeanoutdoorgroup.com/articles/fibre-fragmentation-programme-tests-over-200-materials-for-global-database | 미확인(검색 색인에만 존재) | TMC 표준시험(ISO 105-C06 기반) 결과 + 원단 사양 | 2021년 기준 소재 250종 이상(편성물 약 170, 직물 약 80, 6-500 g/m²). 이후 보고서에서 원단 1,000종 이상 분석 | 탈락 질량, 섬유·원사·원단 구조 사양 | 서명사·회원만 제출·이용할 수 있고 공개 다운로드는 없음 | 회원사 원단에 편중됨. 표준 시험법은 하나지만 문헌값과는 비교할 수 없음 | 1 |
| 세탁 미세섬유 문헌 원자료/메타분석 (PLOS One 2021 37개 원단; 편성물 체계적 리뷰 32편; Textiles 2024 메타분석 52편; OMICS … | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10919082/ | 미확인(검색 색인에만 존재) | 논문 표·보충자료(S1 Table 등) | PLOS One 37개 텍스타일. 리뷰 32편, 메타분석 52편. 문헌 범위 9.6-1,240 mg/kg/세탁 | 섬유 종류, 원사 꼬임, 조직, 게이지, 세탁 조건, 탈락량 | OA 논문 보충자료(개별 상이) | 시험법이 서로 달라 단위(mg/kg, 개수, %w/w)가 혼재하고 직접 비교할 수 없음 | 1 |
| Higg MSI (Cascale/Worldly) | https://cascale.org/resources/press-news/press-releases/cascale-higg-msi-v3-11-new-cotton-data-home-materials-october-2… | 미확인(검색 색인에만 존재) | 소재별 cradle-to-gate 영향 점수(GWP, 물 부족, 부영양화, 화석자원, chemistry) | 소재 수는 확인 못 함. v3.11(2025-10)에서 면 데이터 신규, 홈 소재 확장 | 소재 생산 공정별 영향 지표 | Worldly 플랫폼 라이선스(회원·유료). 공개 다운로드 없음 | 2차 데이터는 Sphera(GaBi). 2022년 노르웨이 소비자청 '오해 소지' 지적 후 2023년 KPMG 검토 | 1 |
| Carbonfact Open Source LCA Database for Footwear & Apparel | https://github.com/carbonfact/lca-database-footwear-apparel | 접속 확인 | 공정별 impact-scores.csv + 방법론 PDF | impact-scores.csv 13개, 합계 313행(spinning 158, dyeing 37, non-woven 18, finishing 17, weaving 16, printing 15, use-phase 15, assembly 14, knitting 12 등; 직접 집계). … | 공정 descriptor(섬유·염료·기술·농색도), ACD/GHG/WTU 등 16개 지표, 데이터 품질 점수 | CC BY-SA 4.0. Zenodo DOI 10.5281/zenodo.21102755 | v1.1 초기판이고 Aii 벤치마크에 의존함. 섬유 원료 생산 데이터셋이 없고 전기방사·DES 공정도 없음 | 1 |
| Ecobalyse (프랑스 정부 환경표시 계산기) | https://github.com/MTES-MCT/ecobalyse | 접속 확인 | 오픈소스 계산기 + 소재/공정 JSON | public/data/textile/materials.json에 섬유 17종(대마, 양모, 면, 유기·재생면, 아마, 황마, 비스코스, PET, rPET, 나일론, 아크릴, PP, 엘라스탄 등) | 소재-공정 매핑, 국가, 운송. 영향값은 웹/API로 제공 | 코드 MIT. processes_impacts.json은 암호화되어 있음(ecoinvent 라이선스 제약으로 추정) | 원시 영향 데이터는 직접 열람할 수 없음 | 1 |
| 단일 탄소/유리섬유 자동 인장 대용량 데이터 (Mendeley ygyym4vy6b; Data in Brief 2021) | https://data.mendeley.com/datasets/ygyym4vy6b/1 | 미확인(검색 색인에만 존재) | 하중-변위 → 응력-변형률, 탄성률·강도 | 690 fibres(CF 4종 + GF 1종). T700S만 217개 | 강도, 탄성률, 게이지 길이(12 mm. 일부 4/20 mm로 compliance 보정) | unknown (Mendeley Data) | 상용 CF만 있고 전구체·공정 정보는 없음 | 1 |
| CF/폴리설폰 열가소 복합 로드 인장 DB (Sci Data 2026) | https://doi.org/10.1038/s41597-026-07333-w | 미확인 | 인장시험 원자료 | unknown(T700SC + PSU Ultrason S2010, 직경 1 mm 로드) | 인장 거동, 공정 조건 | unknown | 시스템 한 가지 | 1 |
| PAN 안정화 조건→CF 물성 소표본 ML 연구 (ECU/RMIT) | https://ro.ecu.edu.au/ecuworkspost2013/5550 | 미확인(검색 색인에만 존재) | 논문(SVR/ANN, 제한된 데이터) | unknown | 안정화 반응 파라미터 → CF 기계물성 | 데이터 공개 여부 unknown | 소표본이고 공정 데이터는 기업·연구소 비공개 | 1 |
| PEI 유래 N-도핑 전기방사 CNF 슈퍼커패시터 ANN 연구 | https://avesis.iuc.edu.tr/yayin/844a4893-7b83-4bb6-8fec-46e6b6b025c4/electrospun-polyethylenimine-pei-derived-nitrogen-… | 미확인(검색 색인에만 존재) | 논문 데이터(ANN) | unknown | SBET, N at%, ID/IG, Rs, 기공 부피, 평균 직경 → 비정전용량 | unknown | 단일 연구 | 1 |
| Paired HVI-AFIS 면섬유 데이터 (Data in Brief 2026) | https://doi.org/10.1016/j.dib.2026.113110 | 미확인 | 방적공장 원면 품질 표(HVI + AFIS 짝) | 행 수 unknown. 2024-06~2025-06, 원산지 8개국 | HVI 14열(Lot, Bale ID, SCI, 수분, MIC, maturity, UHML, UI, SF, strength, elongation, Rd, +b, color grade) + AFIS(길이분포, neps, 성숙도, 섬도) | unknown | 방글라데시 공장 한 곳이 구매한 원면에 한정됨 | 0 |
| USDA AMS Cotton Classing (주간 면 품질 데이터 파일) | https://www.ams.usda.gov/sites/default/files/media/CottonDBUnderstandingtheData.pdf | 미확인(검색 색인에만 존재) | 베일 단위 HVI 분급 통계 파일 | 주별 분급된 전 베일(미국 전체). 정확한 건수 미확인 | color grade, leaf, length, micronaire, strength, uniformity, Rd, +b, trash | 공개 통계 파일(개별 gin/bale 식별자는 제외) | 미국 면만, 상업 분급 목적 | 0 |
| Mendeley knitting-dataset (Daffodil Intl. Univ., Data in Brief 2025) | https://data.mendeley.com/datasets/vs2vjzkw5h | 미확인(검색 색인에만 존재) | 편직 공장 생산 보고서 표 | 12,569 rows × 38 columns (2023-06~08) | loop length, GSM, 조직, 혼용률, 부위, 원사 번수, 기계 직경/게이지, 원단 폭, 불량 여부 | unknown (Mendeley Data) | 공장 한 곳의 생산 QC 데이터이고 쾌적성·태 물성은 없음 | 0 |
| Textile weaving production/rejection dataset (Mendeley nxb4shgs9h, 6mwgj7tms3) | https://data.mendeley.com/datasets/nxb4shgs9h/1 | 미확인 | 직조 공장 일일 생산 보고서 | 121,148 rows × 18 parameters(9개월) | EPI, PPI, 경·위사 번수, 생산량, 불량률 등 | unknown | 공장 한 곳, 생산 지표 중심 | 0 |
| ASHRAE Global Thermal Comfort Database II | https://open.library.ubc.ca/collections/researchdata/items/1.0397701 | 미확인(검색 색인에만 존재) | 현장 열쾌적 조사 원자료 | 약 81,846 records | 실내 기후, 주관 온열감, 착의량(clo), 활동량, 인구통계 | 'open-source'라고 기술됨. 정식 라이선스는 확인 못 함 | 의복 앙상블 수준 clo(의자 보정 불명)이고 소재 정보는 없음 | 0 |
| CoMMonS 원단 표면 현미경 이미지 데이터셋 (Georgia Tech) | https://arxiv.org/pdf/2003.07725 | 미확인(검색 색인에만 존재) | 고해상도 현미경 이미지 + 표면 속성 라벨 | 6,912장, 원단 24종 | 촬영 조건, 표면 속성 등급 | unknown | 원단 수가 24종으로 적음 | 0 |
| TextileNet (UCL/RCA) | https://arxiv.org/abs/2301.06160 | 미확인 | 의류 이미지 + 섬유/원단 분류체계 라벨 | 760,949장 (fibre 442,035장/33 라벨, fabric 318,914장/27 라벨) | 섬유 종류, 원단 조직 라벨 | 오픈소스라고 기술됨. 라이선스 세부 미확인 | Google 이미지와 iMaterialist 재사용이라 라벨 노이즈가 있음(수동 점검 일치율 82%). 혼방 라벨 없음 | 0 |
| Max Weaver Dye Library (NC State) | https://pubs.rsc.org/en/content/articlehtml/2017/sc/c7sc00567a | 미확인(검색 색인에만 존재) | 염료 구조 DB(일부 공개) | 실물 바이알 약 98,000개, 디지털화 2,700종, 공개 150종 | 구조, 물성, 분석 스펙트럼 | 논문은 CC BY 3.0. 데이터 대부분은 비공개 | 공개분이 극히 일부 | 0 |
| TILDA Textile Texture Database (Freiburg) | https://lmb.informatik.uni-freiburg.de/resources/datasets/tilda.en.html | 미확인(검색 색인에만 존재) | TIF 이미지 | 3,200장, 1.2 GB | 원단 종류, 결함 종류(독일어 짧은 라벨) | 연구용 다운로드. 정식 라이선스 미확인 | 구형 저해상도이고 bbox가 없음 | 0 |
| TILDA-OBB (Mendeley 8y46pm2m6y) | https://data.mendeley.com/datasets/8y46pm2m6y/1 | 미확인(검색 색인에만 존재) | 이미지 + 회전 bbox 주석 | 1,562장, 원단군 4개, 결함 5종 | Cut, Foreign object, Hole, Stain, Thread defect | unknown | TILDA에서 파생 | 0 |
| AITEX Fabric Image Database (AFID) | https://datasetninja.com/afid | 미확인(검색 색인에만 존재) | 4096×256 그레이스케일 + 픽셀 마스크 | 245-247장(원단 7종, 결함 12종, 결함 이미지 105-106장) | 결함 클래스, 마스크 | unknown | 소규모이고 결함 클래스 불균형 | 0 |
| ZJU-Leaper | http://www.qaas.zju.edu.cn/zju-leaper/ | 미확인 | 원단 이미지 + 주석 | 98,777장, 원단 19종 | 결함 위치/마스크 | unknown | 중국 공장 원단 | 0 |
| Alibaba Tianchi 원단 결함 데이터 | https://tianchi.aliyun.com | 미확인 | 2446×1000 이미지 + YOLO/COCO 주석 | 결함 5,913장 + 정상 3,663장, 주석 9,523개, 20 클래스 | 결함 bbox | 대회 약관(재배포 제한 가능) | 대회용 데이터 | 0 |
| TSFabrics (Sci Data 2026) | https://isslab.csie.ncu.edu.tw/download/publications/TSFabrics A Time-Series Fabric Dataset for Real-Time Defect Detect… | 미확인(검색 색인에만 존재) | 환편기 시계열 그레이스케일 이미지 + 분할 마스크(figshare) | 93,196장(정상 89,900 / 이상 3,296), 생산 시나리오 22개 | 조명, 생산 속도, 원단 종류, 결함 마스크 | CC BY 4.0 (논문 Usage Notes) | 대만 공장 한 곳 | 0 |
| Carrilho et al. 2024 원단 이상탐지 데이터셋 (Applied Sciences 14:5298) | https://www.mdpi.com/2076-3417/14/12/5298 | 미확인(검색 색인에만 존재) | 공장 원단 이미지(증강 없음) | 학습 정상 32,000장. 테스트 정상 1,100장 + 결함 1,300장 | 정상/결함 | unknown | 포르투갈 공장 한 곳 | 0 |
| Industrial Textile Dataset (ITD, Thomine) | https://github.com/SimonThomine/IndustrialTextileDataset | 접속 확인 | MVTec 형식 컬러 이미지(Google Drive) | 원단/카메라 유형 10개, 총 5,662장 (README 표 합산) | good/anomaly | MIT (README) | 비지도 이상탐지용 | 0 |
| FabricDefect (msminhas93) | https://github.com/msminhas93/FabricDefect | 접속 확인 | 512×512 이미지 + 약한 마스크 | 24장 | 결함 bbox 마스크 | MIT | 아주 작음 | 0 |
| MVTec AD (carpet 등 텍스처 범주) | https://www.mvtec.com/company/research/datasets/mvtec-ad | 미확인(검색 색인에만 존재) | 고해상도 이미지 + 픽셀 주석 | 5,000장 이상, 15개 범주(carpet 포함) | 정상/결함 마스크 | CC BY-NC-SA 4.0 (상업 이용 불가) | 섬유 관련 범주는 carpet 하나뿐 | 0 |
| 기타 결함/원사 이미지 데이터 (Textil Santanderina DIB 2025, FabricSpotDefect, Mendeley 663j22s43c, 원사… | https://produccioncientifica.uca.es/documentos/67ea2f30f444465cb430c676 | 미확인(검색 색인에만 존재) | 원단·원사 이미지/영상 | FabricSpotDefect 원본 1,014장/주석 3,288개. 원사 hairiness 684장/주석 11,037개. 방적 영상 3개×20,200 프레임. 나머지 unknown | 결함·얼룩·잔털·넵 | 기사별 상이(unknown) | 단일 공장/연구실 | 0 |
| 해양 고분자 Raman 참조 라이브러리 (Sci Data 2022) | https://doi.org/10.1038/s41597-022-01883-5 | 미확인 | Raman 스펙트럼 csv + 메타데이터 | 인공 고분자(풍화 22 포함) + 생물 고분자 17. 스펙트럼 파일 87개 | Raman 스펙트럼, 고분자 종류 | unknown | 해양 시료 중심 | 0 |
| Nordic Textile Anatomy Database (DTU; Data in Brief 2025) | https://github.com/hmlogan/textileanatomy_dds | 접속 확인 | xlsx(의류별 섬유 혼용률·안감·방해요소) | 소매시장(DK) 4,495벌 + 사용 후 폐의류(SE) 1,248벌 (xlsx 시트 행 수로 확인) | 의류 유형(CN 코드), 섬유 혼용 %, 안감, 지퍼·단추 등 재활용 방해요소와 위치 | 원 저장소 DOI 10.11583/DTU.24581700. 라이선스는 확인 못 함 | 북유럽 시장 한정 | 0 |
| H&M·Uniqlo 의류 색상변형별 조성 데이터 (Data in Brief 2026) | https://doi.org/10.1016/j.dib.2026.113017 | 미확인 | JSONL(Zenodo) + 처리 스크립트(GitHub) | 47,522 variant records, component 등장 68,427건(UK/AU, 2026-03~04 수집) | 색상, 부위별 섬유 조성 %, 의류 범주 | 데이터 CC BY 4.0, 코드 MIT | 소매업체 웹 표기 기반이라 검증되지 않음 | 0 |
| 건조기 미세섬유 배출 참여형 연구 데이터 (Dryad prr4xgxzf) | https://datadryad.org/dataset/doi:10.5061/dryad.prr4xgxzf | 미확인(검색 색인에만 존재) | CSV/Excel(참여자 건조 기록 + 배기구 메시 분석) | 자원봉사 가정 3주 측정(가구 수는 확인 못 함). 1회 평균 138 mg | 건조 품목 조성, 메시 포집물 조성(셀룰로오스/PET 등), 질량 | Dryad(통상 CC0이나 미확인) | 가정 사용 조건이라 통제되지 않음 | 0 |
| 법과학 섬유 전이·잔류 데이터 (Data in Brief 2024/2025) | https://doi.org/10.1016/j.dib.2025.112228 | 미확인 | 회수 섬유 특징 표 | 전이 26,101개 섬유(2024), 잔류 175,948개 섬유(2025) | 섬유 유형, 색, 길이, 회수 위치, 활동 강도·시간 | unknown | 면 T셔츠·PET/면 후디 같은 특정 의류 시나리오 | 0 |
| PEFCR Apparel & Footwear v3.1 / EF 3.1 데이터셋 | https://www.carbonfact.com/hubfs/PEFCR%20Apparel%20%26%20Footwear.pdf | 미확인(검색 색인에만 존재) | 제품군 산정 규칙 + EF 2차 데이터셋 | 부문 데이터셋 641개(EF 3.1 목록 기반) | 16개 PEF 지표 | EF 데이터는 PEF 용도로 제한. WALDB(Quantis)와 ecoinvent는 상용 | 규제용 평균값 | 0 |
| ESPResso V2 (Avelero/UvA) - LLM 생성 합성 LCA 데이터 | https://github.com/Avelero/ESPResso-V2 | 접속 확인 | LLM 오케스트레이션으로 만든 합성 레코드 + 신경망 모델 | 검증 레코드 50,480개, 제품 범주 17개, 소재-공정 조합 1,200개 이상 | 소재 조성, 제조 순서, 운송 구간, 탄소·물 발자국 | PolyForm Noncommercial 1.0.0 | 실측이 아닌 합성 데이터(ecoinvent/Agribalyse 배경) | 0 |
| CMH-17 Composite Materials Handbook | https://wichita.edu/industry_and_defense/NIAR/cmh-17/about-cmh-17.php | 미확인(검색 색인에만 존재) | 인증 시험 데이터 핸드북 | 1,000건 이상(6권) | 복합재 기계물성 | SAE 판매(유료, 재배포 불가) | 항공 인증용 | 0 |

## Korean public

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| UNIST 재생 PET/PCT 극세사 염색 GPR 모델링 | https://scholarworks.unist.ac.kr/bitstream/201301/88650/2/Sustainable%20Dyeing%20Process%20Modeling%20for%20Recycled%20… | 미확인(검색 색인에만 존재) | 논문(국내 기관), 실험 데이터 기반 GPR | unknown | 염색 조건 → 색(K/S, CIELAB 추정) | unknown | 단일 연구 | 1 |
| 소재 연구데이터 플랫폼 (과기정통부, 2021-2027) | https://www.mt.co.kr/tech/2020/04/19/2020041911400188307 | 미확인(검색 색인에만 존재) | 국가 소재 연구데이터 플랫폼(뉴스 기사) | 7년간 약 640억 원. 연내 200만 건 수집 목표(2020 기사) | unknown(섬유·고분자 포함 여부 미확인) | unknown | 섬유 데이터 포함 여부와 공개 범위를 확인하지 못함 | 1 |
| 산업부 섬유소재 물성 DB (수송용 섬유소재 1단계, 중소기업 정보서비스) | https://www.imaeil.com/page/view/2016041819203209580 | 미확인(검색 색인에만 존재) | R&D 공정 물성 DB(기업 지원용) | unknown | 공정 물성, 연구결과물 | 중소기업 대상 서비스. 공개 다운로드는 아닌 것으로 보임 | 2016년 기사 기준이라 현재 상태 미확인 | 1 |
| 경북대 '생분해성 섬유 방사 공정 데이터 특성을 고려한 물성 예측 모델 개발' (국내 학회) | https://selab.knu.ac.kr/en/archive/conference/domestic/생분해성 섬유 방사 공정 데이터 특성을 고려한 물성 예측 모델 개발 | 미확인(검색 색인에만 존재) | 학회 발표(데이터 비공개로 추정) | unknown | 생분해성 섬유 방사 공정 → 물성 | 비공개(추정) | 확인 불가 | 1 |

**이 조사 블록에서 확인된 데이터 공백**

- 케라틴·양모 재생단백질 섬유의 공정(용해·방사·전기방사)과 물성을 잇는 공개 데이터가 없음(부족): Cogni-e-SpinDB에는 케라틴·젤라틴이 없고, FibreCastML은 gelatin을 포함하지만 원자료를 받을 수 있는지 확인하지 못했고 단백질계 R²<0.59임
- DES/이온성 액체 용매계의 방사·전기방사 공개 데이터가 없음(부족): 용매 기술자를 쓴 공개 표는 HSP·χ·RED를 넣은 PVDF 데이터(karthikbsk, 997행) 정도임
- 비대칭(일방향) 수분이동·Janus 막의 정량 데이터가 데이터셋 형태로 전혀 없음(부족): OWTC, AOTI, 투습 수치가 개별 논문 표에만 흩어져 있음
- 직물 쾌적성 데이터가 사실상 없음(부족): 태(KES-F/FAST), 투습(MVTR/Ret), 흡한속건(MMT, AATCC 195/201) 모두 공개 ML용 데이터셋을 찾지 못함. 체계적 리뷰도 비공개 데이터 위주임
- 염색 레시피(염료·조제·공정)와 CIELAB, 견뢰도 등급을 연결한 공개 데이터가 없음(부족): 공개 자원은 염료 분자 광학물성(Deep4Chem), 천연색소 λmax(DyeDactic), 천연염색 색좌표 집적(BioColour 664건) 수준이고 산업 레시피는 모두 기업 비공개임
- 미세섬유 탈락의 표준시험 데이터(TMC 포털)는 회원 한정이라 비공개이고, 문헌값은 시험법·단위(mg/kg, 개수, %w/w)가 달라 바로 합칠 수 없음(부족)
- 탄소섬유: 전구체 화학, 안정화·탄화 조건, CF 물성을 연결한 공개 데이터셋이 없음(부족). 바이오 전구체(리그닌·셀룰로오스·케라틴) 탄화 데이터는 리뷰 표 수준임
- 섬유 LCA: 공개 DB(Carbonfact CC BY-SA, Ecobalyse)는 방적·염색·편직 등 공정 중심임. 섬유 원료 생산(특히 바이오 기반 신소재), 전기방사, DES 용해 공정의 LCI는 공개된 것이 없음(부족). Higg MSI, ecoinvent, WALDB는 유료이거나 제한됨
- 천연섬유 인장: 게이지 길이·습도·직경 측정법을 명시한 단섬유 원시 데이터의 대규모 공개본이 부족함. 문헌은 범위값 위주이고 실험실 간 편차가 큼(대마·아마 round-robin)
- 한국 공개 데이터: 이번 실행의 WebSearch 예산(200회, 에이전트 간 공유)이 소진되어 AI허브, KDATA, 소재연구데이터플랫폼, 섬유산업연합회 데이터를 검증하지 못함. DYETEC의 공개 염색 데이터 플랫폼도 찾지 못함(미확인, 후속 검색 필요)
- 직물 결함 이미지 데이터는 풍부하지만(TILDA, AITEX, ZJU-Leaper, Tianchi, TSFabrics 등) 참가자 주제와는 무관함

## generic repository (Zenodo)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Zenodo (CERN 범용 저장소) — 고분자/전기방사 관련 레코드 묶음 | https://zenodo.org | 미확인 | 범용 데이터 저장소(DOI·버전 관리) | unknown (저장소 전체 규모 미확인). 세션에서 DOI 확인된 관련 레코드: Cogni-e-SpinDB 1.0 10.5281/zenodo.16455947, FEAD 10.5281/zenodo.10301664, SpinCastML 10.5281/zenodo.18557989, Pol… | 레코드별 상이 | 업로더가 레코드별 라이선스 선택(CC BY/CC0/GPL 등 혼재). REST 검색 API 존재는 일반 지식이며 이 세션에서는 zenodo.org 접속 차단(curl 000)으로 미검증 | 큐레이션·동료심사 없음, 메타데이터 품질 편차 큼. 키워드 검색은 이번 세션에서 불가 | 2 |

## generic repository (Figshare)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Figshare | https://figshare.com | 미확인 | 범용 저장소 | unknown | - | 레코드별 라이선스(일반적으로 CC BY/CC0). API v2 존재는 일반 지식, 세션 내 api.figshare.com 접속 차단으로 미검증 | 이번 세션에서 고분자·섬유·막 특정 Figshare 데이터셋을 하나도 확인하지 못함(검색 예산 소진+차단). Sci Data 연질자성복합재 데이터(10.1038/s41597-024-04286-w)가 Figshare 호스팅이라는 초록 문구만 확인 — 고분자 무관 | 1 |

## generic repository (Dryad)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Dryad | https://datadryad.org | 미확인 | 범용 저장소(생명·환경과학 중심) | unknown | - | CC0 일괄 적용(일반 지식, 세션 내 미검증). API v2 존재는 일반 지식, datadryad.org 접속 차단 | GitHub 코드검색 'datadryad.org'+fiber/silk/polymer 결과에서 관련 데이터셋 0건 | 1 |

## generic repository (Harvard Dataverse)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Harvard Dataverse — AqSolDB 등 | https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/OVHAW8 | 미확인 | 범용 저장소; 예: AqSolDB(수용해도 9개 데이터셋 병합·신뢰도 라벨) | AqSolDB: 9개 출처 병합(건수는 이 세션에서 미확인). 탄소섬유 자가감지 복합재 dataverse(dataverse.harvard.edu/dataverse/selfSensingCarbonfiberComposites)도 존재 | AqSolDB: SMILES, 용해도, 신뢰도 그룹, 2D 기술자 | Dataverse 기본 CC0(일반 지식, 미검증). Search API 존재는 일반 지식 | 고분자 공정 데이터는 확인 못함. AqSolDB는 소분자 | 1 |

## generic repository (Mendeley Data)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Mendeley Data — Data in Brief 연계 섬유 데이터 | https://data.mendeley.com/datasets/nxb4shgs9h/1 | 미확인 | 범용 저장소(Elsevier); Data in Brief 기사 데이터 주 저장처 | 확인 예: 직조 공장 데이터 121,148행×18변수(nxb4shgs9h/1, 불량 데이터 6mwgj7tms3/2), 니트 12,569행×38열, 섬유 ATR-FTIR 160 스펙트럼/137 시료 | 데이터셋별 상이 | 데이터셋별 CC 라이선스 선택(일반 지식, 미검증) | DIB 기반이라 단일 공장·단일 실험실 데이터가 다수 | 2 |

## generic repository (OSF)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| OSF (Open Science Framework) | https://osf.io | 미확인 | 범용 저장소/프로젝트 관리 | unknown | - | 프로젝트별 라이선스. API v2 존재는 일반 지식, 미검증 | 이번 세션에서 고분자·섬유·막 관련 OSF 데이터셋 0건 확인 | 0 |

## generic repository (Hugging Face)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Hugging Face Datasets — 고분자 관련(OPoly26, PolyReal, DemoDiff downstream) | https://huggingface.co/facebook/OMol25 | 미확인 | ML 데이터 허브. OPoly26=DFT 계산, PolyReal=LLM 평가 QA, demodiff_downstream=분자/고분자 설계 과제(기체분리 오라클 포함) | OPoly26: DFT 6.35M건(2,444 단량체, 1.2B 원자); PolyReal: 545 샘플; demodiff: unknown | OPoly26: 에너지·힘 등; PolyReal: 개방형 질문·랭킹 과제 | OPoly26 CC-BY-4.0(논문 명시), PolyReal Apache-2.0(README 배지). Hub API 존재는 일반 지식, huggingface.co 차단 | 공정·섬유·막 실험 데이터셋은 HF에서 찾지 못함; 계산·LLM 벤치마크 위주 | 1 |

## generic repository (Kaggle)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Kaggle — 고분자/섬유 데이터 | https://www.kaggle.com/competitions/neurips-open-polymer-prediction-2025 | 미확인 | 대회·사용자 업로드 데이터. 확인된 것: NeurIPS Open Polymer Prediction 2025, oleggromov/polymer-tg-density-excerpt(RhNet 데이터 발췌), nexus… | OPP 2025 train 7,973행(아래 별도 항목). 나머지 unknown | OPP: SMILES, Tg, FFV, Tc, Density, Rg | 대회 규칙/데이터셋별 라이선스(미확인). Kaggle API 존재는 일반 지식, kaggle.com 차단 | 사용자 업로드 데이터는 출처·라이선스 불명확한 재배포가 흔함 | 1 |

## generic repository (GitHub)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| GitHub (데이터 동봉 저장소) | https://github.com | 접속 확인 | 코드+CSV 동봉 저장소; 이번 세션에서 실제 내려받아 행 수를 센 데이터는 전부 GitHub | repo별 상이(아래 개별 항목) | - | repo별 LICENSE(MIT/Apache/CC0 등) — 단 코드 라이선스가 원데이터(문헌·PolyInfo 유래) 재배포권을 보장하지 않음 | README 수치와 실제 CSV 행 수 불일치 사례 있음(DES 2,651 vs 2,658) | 2 |

## Scientific Data Data Descriptor

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Scientific Data (Data Descriptor) — 고분자·섬유 관련 기사군 | https://www.nature.com/sdata/ | 미확인 | 데이터 기술 논문(데이터는 외부 저장소) | PubMed 검색: 'Sci Data' AND polymer 43건; membrane/textile/fiber/electrospinning/cellulose 108건(대부분 생의학) | - | OA 저널(CC BY로 알려짐, 세션 내 미검증); 데이터 라이선스는 저장소별 | 고분자 공정 데이터는 소수; 생물·지구과학 편중 | 2 |

## Data in Brief

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Data in Brief — 전기방사·섬유·막 기사군 | https://www.sciencedirect.com/journal/data-in-brief | 미확인 | 데이터 기사(소규모 실험 데이터, 기사 첨부 또는 Mendeley Data 등) | PubMed 검색: 전기방사/나노섬유 27건, 제목 textile/fabric/yarn 등 33건, 제목 fiber/fibre+고분자 키워드 69건 | - | OA(CC BY로 알려짐, 세션 내 미검증) | 대부분 단일 논문 보조 데이터로 수십 행 규모; 기계학습용 표 형식이 아닌 그림·이미지 다수 | 2 |

## generic repository (institutional)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 기관 저장소(CaltechDATA, TalTech Data Repository 등) | http://dx.doi.org/10.22002/D1.20048 | 미확인 | 논문 부속 데이터(학술지 SI 대체) | CaltechDATA: 기체분리막 데이터셋 A–D 전체+지문(8M SMILES 스크리닝 포함); TalTech: Cogni-e-Spin 예비 데이터 1,913건(결측 포함) | - | unknown | 기관별 영속성·검색성 차이 | 1 |

## Scientific Data / Zenodo / GitHub — elec

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Cogni-e-SpinDB 1.0 (전기방사 공정-나노섬유 형태 DB) | https://github.com/taltechloc/Cogni-e-SpinDB | 접속 확인 | 문헌 큐레이션 공정-구조 표(CSV) | 809건 완전 레코드, 12개 소재, 57개 출처, 14개 파라미터/20개 필드(예비 1,913건). PVDF 187건·PVA 133건 하위집합 | DOI, 고분자, 용매, 농도, 전압, 유량, 팁-컬렉터 거리, 바늘 직경 등 → 평균 섬유경·표준편차 | GitHub LICENSE 파일은 CC0 1.0(README 배지는 MIT로 불일치). Zenodo 데이터 라이선스 미확인. 웹 플랫폼으로 신규 기여 가능 | 바늘 직경 결측 다수(PVDF 88/187, PVA 96/133). 저자 보고 R² PVDF 0.70, PVA 0.43. EC-PEO 저장소 분석상 랜덤분할 R² 0.72 vs 연구단위 제외(leave-study-out) R² −0.11, 연구 식별자만으로 분산 44% 설명 → 실험실 효과 교란 심각 | 3 |

## Zenodo / arXiv — electrospinning

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| SpinCastML 데이터셋·앱 (전기방사 섬유경 분포) | https://doi.org/10.5281/zenodo.18557989 | 미확인 | 문헌 기반 섬유경 관측치+고분자-용매 용해성 표(OK/COND/NO), R Shiny 앱 동봉 | 섬유경 68,480 관측, 1,778 연구/데이터셋, 16개 고분자(CA 1,880, 젤라틴 1,680, PVA 6,920, PVDF 34,920, PCL 1,720 등) | DOI, 고분자, 용매 1~3 및 비율, 농도, 바늘 직경, 컬렉터 종류, 회전속도, 전압, 유량, 거리, 온도, 상대습도, 섬유경 분포 | GNU GPL 3.0(논문 명시) | 고분자별 총계가 모두 40의 배수 → 보고된 분포(평균·SD)에서 연구당 약 40개 값을 재표본한 의사 관측일 가능성(본 조사자의 추론). 실질 표본은 ~1.7k 조건. PVDF 51% 편중. FEAD·Cogni-e-Spin 병합 포함 | 3 |

## Zenodo — electrospinning

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|

## GitHub — electrospinning

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| EC-PEO 전기방사 ML 저장소(에틸셀룰로스-PEO) | https://github.com/DivyamVerma22/EC-PEO-electrospinning-ml-fiber-diameter | 접속 확인 | 코드+스키마+합성 샘플(실험 원자료는 미공개) | 실험실 자체 22회 운전(미공개); 공개분은 합성 예시 | 전압, PEO 비율, 드럼 속도 등 → 섬유경 | MIT(코드) | 실제 데이터 없음. 다만 README가 Cogni-e-SpinDB 809건에서 연구단위 교차검증 시 R² −0.11, 연구 식별자 설명력 44%, 공개 DB에 EC·PEO·블렌드 0건임을 보고 | 2 |

## Data in Brief — electrospinning

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| P(3HB-co-4HB) 전기방사 조건-형태 데이터 (DIB) | https://doi.org/10.1016/j.dib.2019.104777 | 미확인 | 농도·전압·주입속도 조합별 SEM 및 섬유경 분포 | unknown(소수 조건; 기사 내 포함) | 고분자 농도, 인가전압, 주입속도 → 섬유경 분포 | 기사 본문 포함(OA) | 단일 실험실 소규모 | 1 |
| 기타 소규모 DIB 전기방사 데이터(무바늘 방사, LiFePO4/PVP-PEO 탄화, 젤라틴 경사 스캐폴드, DegraPol 메쉬) | https://doi.org/10.1016/j.dib.2015.08.005 | 미확인 | 공정 조건별 섬유경·생산율, 열처리 온도별 형태, 섬유경+인장 등 | 각 소규모(unknown) | 전압·거리·유량·PVP/PEO 농도·열처리 온도 등 | 기사 포함 | 표 형태 아님(그림 중심), 단일 실험실 | 1 |

## Data in Brief — electrospinning/metrolog

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| DiameterJ 검증 데이터셋 (나노섬유 직경 측정) | https://doi.org/10.1016/j.dib.2015.07.012 | 미확인 | 합성 디지털 이미지+SEM 이미지+분할 결과+섬유반경·기공·배향 히스토그램 | 합성 이미지 130장, 강선 SEM 24장 + 전기방사 고분자 섬유 SEM | 섬유 반경, 기공 크기, 배향, 분할 알고리즘별 결과 | 기사에 zip 첨부(OA) | 측정 도구 검증용 | 2 |

## Data in Brief — electrospinning/membrane

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| PAN/할로이사이트 전기방사 막 건·습 상태 기계물성 (DIB) | https://doi.org/10.1016/j.dib.2018.11.039 | 미확인 | 건조/수화 상태 인장·파괴 물성, 섬유경·기공경 | unknown(소규모) | 항복강도·변형, 강성, 파괴인성, 섬유경, 기공경 | 기사 포함 | 단일 조성계 | 1 |

## Data in Brief — electrospinning/composit

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 정렬 전기방사 PVOH-에폭시 나노복합재 특성 (DIB) | https://doi.org/10.1016/j.dib.2016.01.046 | 미확인 | SEM, DMA, TGA, DSC, FTIR, 인장 | unknown(소규모) | 섬유 함량, 제조법 → 열·기계 물성 | 기사 포함 | 단일 연구 | 1 |

## Kaggle — polymer property

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| NeurIPS Open Polymer Prediction 2025 (Kaggle) | https://www.kaggle.com/competitions/neurips-open-polymer-prediction-2025 | 미확인 | MD 시뮬레이션 물성 + SMILES | train 7,973 고분자(Tg 511, FFV 7,030, Tc 737, Rg 614, 밀도 613); 전체 11,475 고유 고분자 중 9,625 라벨 | SMILES, Tg, FFV, 열전도도, 밀도, Rg | Kaggle 대회 규칙(라이선스 미확인); 테스트셋은 kaggle 데이터셋 alexliu99/neurips-open-polymer-prediction-2025-test-data로 공개, 생성 파이프라인 github.com/sobinalosious/A… | 두 연구그룹 시뮬레이션 간 Tg 적합법(쌍곡선 vs 이중선형) 차이로 공개·비공개 리더보드 Tg 평균 102.9→179.8 이동, K/°C 단위 오류, 데이터 누출 사건 | 1 |

## Zenodo / GitHub — polymer property

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| PolyMetriX 큐레이션 Tg 데이터셋 | https://github.com/lamalab-org/PolyMetriX | 접속 확인 | 다출처 실험 Tg 병합(중앙값)+신뢰도 등급 | 약 7,367 고분자(문서의 22개 고분자 클래스 수 합산; PolyBench26 논문은 7,362) | PSMILES, Exp_Tg(K), 출처 목록, Tg 범위·SD, 데이터점 수, 신뢰도(Gold/Yellow/Red/Black), 고분자 클래스 | 패키지 MIT(PyPI). 데이터는 zenodo.org/records/15210035(라이선스 미확인) | 폴리이미드·폴리옥사이드 편중; 원출처(Bicerano 계열 등) 중복 보정 | 2 |
| polyVERSE (Ramprasad 그룹 데이터 모음) | https://github.com/Ramprasad-Group/polyVERSE | 접속 확인 | 정보학용 고분자 데이터셋 모음 | PolyBench26 논문 서술: 약 30,000 값, 59개 양(본 세션에서 직접 계수 안 함) | 실험·DFT·시뮬레이션 물성 | Zenodo DOI 10.5281/zenodo.13352643(라이선스 미확인) | 합성고분자 중심 | 1 |

## GitHub — polymer property

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|

## Hugging Face — polymer DFT

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| OPoly26 (Open Polymers 2026) | https://huggingface.co/facebook/OMol25 | 미확인 | DFT 단일점 계산(MLIP 학습용) | 6.35M DFT(학습 5,902,827/검증 201,865/시험 248,391), MD 셀 94k | 에너지, 힘, 전하, 스핀 등 | CC-BY-4.0 | 가교·블록·그래프트 구조 없음, 합성 가능성 미보장 | 0 |

## GitHub — polymer structure

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| PI1M / POINT2 | https://github.com/RUIMINMA1996/PI1M | 접속 확인 | 생성모델로 만든 가상 고분자 p-SMILES | 약 100만 구조(PolyInfo 약 12,000종으로 학습) | p-SMILES, SA score | repo LICENSE는 MIT이나 README에 'Data for academic purpose only' | 가상 구조, 물성 라벨 없음 | 0 |

## GitHub — text

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| PolyIE (고분자 문헌 정보추출 데이터셋) | https://github.com/jerry3027/PolyIE | 접속 확인 | 전문가 주석 NER·N-ary 관계 코퍼스 | 146편 전문, 41,635 개체 언급, 4,443 관계(고분자 막 논문 5편 포함) | Material, Property, Value, Condition 및 관계 | Apache-2.0 | 고분자 태양전지 100편 편중; 표·그림 미포함; GPT-4 few-shot RE F1 44% | 2 |

## arXiv — text

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| PolyLM 코퍼스(문헌 공정 서술 기반 물성 예측) | https://arxiv.org/abs/2605.08255 | 미확인 | LLM 추출 문헌 코퍼스(공정·합성 서술 + 22개 물성) | 약 185,000편, 276,400 시료, 시험셋 68,283 관측 | Tg, Tm, 인장강도, 탄성률, 신율, 결정화도, 점도 등 22개 | 공개 여부 unknown(논문에 공개 위치 미기재 확인) | 추출 감사 120건 기준 엄격 정밀도 0.842; 공정 서술 제거 시 기계물성 R² 평균 0.062 하락 | 1 |
| PHA 문헌 RAG 코퍼스(Polymer Literature Scholar) | https://arxiv.org/abs/2602.16650 | 미확인 | PHA 논문 문단·지식그래프 튜플 | 1,028편, 44,609 문단, GPT-4o-mini 추출 390,864 튜플→36,757 정규 개체 | 고분자-공정-물성 관계 튜플 | unknown(공개 여부 미기재) | 출판사 코퍼스 기반이라 재배포 제한 가능 | 1 |

## Scientific Data — polymer representation

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 자동 BigSMILES 변환 데이터셋 (Sci Data 2024) | https://doi.org/10.1038/s41597-024-03212-4 | 미확인 | 단일중합체 SMILES→BigSMILES | unknown(초록에 건수 없음) | SMILES, BigSMILES | unknown | 단일중합체 한정 | 1 |

## Scientific Data — biopolymer

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 리그닌 구조 데이터셋 LGS / SP-LCC 리그닌-탄수화물 복합체 | https://doi.org/10.1038/s41597-025-05327-8 | 미확인 | LGS: 생성 구조 60K; SP-LCC: NMR 구조·분자량분포·항산화·Tg·열특성 | LGS 60,000 구조(10.1038/s41597-022-01709-4); SP-LCC 건수 unknown | 결합 종류, 분자량, Tg, 열안정성 | unknown | 활엽수 유래 한정 | 1 |

## Scientific Data — formulation

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| PLGA 미립자/나노입자 제형 데이터셋 (Sci Data 2025) | https://doi.org/10.1038/s41597-025-04621-9 | 미확인 | 문헌 큐레이션 제형-방출 데이터 | 미립자 321 방출연구·89 약물; 나노입자 433 제형·65 분자(10.1038/s41597-025-05520-9) | 고분자 특성, 공정 조건, 방출 곡선 | unknown | 약학 도메인 | 1 |

## Scientific Data — fiber composite

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 열가소성(PSU) 함침 탄소섬유 인장 DB (Sci Data 2026) | https://doi.org/10.1038/s41597-026-07333-w | 미확인 | 인장 시험 응력-변형 곡선, 파괴 코드, SEM | 600건 이상 인장시험 | PSU 용액 농도(NMP, 20/30/40 wt%), 시험 조건, 파괴 모드 | unknown | 단일 재료계 | 1 |

## Scientific Data — polymer morphology

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 블록공중합체 자기조립 SEM DB (Sci Data 2025) | https://doi.org/10.1038/s41597-025-05379-w | 미확인 | 공정 파라미터가 메타데이터로 내장된 SEM 이미지 | unknown | 공정 조건, 구조 특성 | unknown | 블록공중합체 한정 | 1 |

## GitHub / CaltechDATA — membrane

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 기체분리 고분자막 데이터셋 A (pgmML) | https://github.com/jsunn-y/PolymerGasMembraneML | 접속 확인 | 고분자 구조-기체 투과도(일부 결측 대치) | 778행, 고유 SMILES 353, CO2 측정 482행; 스크리닝용 B(100만)/C(800만) SMILES | Smiles, Details(측정법: time-lag, ASTM D1434 등), Condition, Reference, Year, He/H2/O2/N2/CO2/CH4 투과도 | MIT형 허가 문구(LICENSE). 원자료 PID(P010001 형식)는 PolyInfo 유래로 보임 → 재배포권 별도 확인 필요 | 측정법·온도가 섞인 다출처 값, 결측 대치값 포함 | 1 |

## GitHub — membrane/sorption

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| RhNet 고분자 내 기체/용매(물 포함) 흡착 데이터 | https://github.com/Shorku/rhnet | 접속 확인 | 실험 흡착량(무게분율) 표 + 반복단위 구조 | 16,004 측정, 108 고분자, 84 용매/기체, 276 DOI; 물 흡착 841행(PMMA 107, PLA 81, PEI 78, PVAc 40, PVP 20 등) | 고분자, 용매, Mn, Mw, 결정화도, Tg, 밀도, 압력, 온도, 흡착 무게분율, DOI | MIT. 후속 데이터 저장소(Shorku/SorptionByPolymers)는 이번 세션에서 접근 불가 | 합성고분자 중심, 셀룰로스·케라틴 없음 | 2 |

## GitHub — membrane

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 유기용매 나노여과(OSN) 문헌 시험 데이터 | https://github.com/ignaczgerg/osn-solvent-model | 접속 확인 | 막-용매-용질 배제율 | 120행 | DOI, 연도, 막, MWCO, 용매, 배제율, 온도, 공정 구성, 용질 SMILES | LICENSE 파일 없음 | 외부 시험셋 용도, 소규모 | 1 |

## Data in Brief — membrane

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 거대기공 PVDF 평막(VNIPS) 막증류 데이터 (DIB 2026) | https://doi.org/10.1016/j.dib.2026.112588 | 미확인 | 공정 변수·성능 엑셀 + 형태 이미지 | unknown | NMP/물 상분리 조건, 막 특성, 막증류 성능 | 저장소명 미확인('linked repository') | 단일 캠페인 | 2 |

## Data in Brief — membrane/cellulose deriv

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 셀룰로스아세테이트 UF 중공사막 제조 모델 파라미터 (DIB 2020) | https://doi.org/10.1016/j.dib.2020.106363 | 미확인 | 공정 모델 식·파라미터(LCA 연계) | unknown | 운전 조건별 물질·에너지 흐름 | 기사 포함 | 모델 파라미터 중심 | 1 |

## GitHub — biopolymer/solvent

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 이온성 액체 내 셀룰로스 용해도 데이터 (ML4IL) | https://github.com/Mengyang2024/ML4IL | 접속 확인 | 문헌 큐레이션 용해도 표 | 674행, IL 331종, 문헌 33편, 온도 20–200 °C(셀룰로스 종류: MCC 423, cellulose 167, Avicel 84); 물 함량 <1% 하위집합 별도 | IL SMILES, 양이온, 음이온, 셀룰로스 종류, 온도, 가열 시간, 용해도, 문헌 | MIT | 용해도 정의·측정법이 문헌별로 다를 수 있음; IL 융점 데이터셋도 동봉 | 3 |
| DES 융점 통합 데이터셋 (Odegova 2024 + Luu 2023 병합) | https://github.com/srampinogroup/des-ml-exploration | 접속 확인 | HBA/HBD 조성-융점 표 | CSV 2,658행(README는 2,651); DES 유형 III 1,188, V 711, IL 199 등. 원천 Odegova 데이터는 융점 2,303·밀도 4,369·점도 4,216건(README 서술) | HBA/HBD 이름·SMILES·융점, 몰분율, 혼합 융점, 출처 DOI | MIT | 유형 III 편중, 중복 처리(±10 K 평균화) | 2 |

## Scientific Data / Zenodo — solvent

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| BigSolDB 2.0 및 이원 혼합용매 용해도 (Sci Data) | https://doi.org/10.1038/s41597-025-05559-8 | 미확인 | 유기화합물 용해도 | BigSolDB 2.0: 103,944값, 1,448 화합물, 213 용매, 1,595편; 이원용매: 175,166값, 810 화합물, 3,001계, 1,115편(10.1038/s41597-026-07047-z) | 용질·용매 SMILES, 온도, 용해도 | Zenodo 10.5281/zenodo.15094979(라이선스 미확인) | 소분자 한정 | 1 |

## Scientific Data — solvent

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 이온성 액체 세포독성 데이터셋 (Sci Data 2024) | https://doi.org/10.1038/s41597-024-04190-3 | 미확인 | 문헌 큐레이션 독성값 | IL 1,227종, 3,837건, 151편 | 이름, 화학식, CAS, SMILES, 세포독성값, 세포주·배양시간·분석법 | unknown('freely available') | 시험 조건 이질성 | 1 |

## Scientific Data — fiber/textile

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| NIST 섬유 NIR 분광 데이터셋 (Sci Data 2026) | https://doi.org/10.1038/s41597-026-07434-6 | 미확인 | 벤치탑 NIR-FTIR, 휴대형 NIR 2종, 직물 현미경 이미지 | 직물 113종, 섬유 시편 61종 | 스펙트럼, 섬유 조성(출처 확인), 이미지 | unknown(저장소명 본문에서 링크 제거됨) | 출처 확인된 시료 위주, 소규모 | 2 |

## Data in Brief — fiber/textile

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| OpenTextile-NIR 초분광 데이터 (DIB 2026) | https://doi.org/10.1016/j.dib.2026.112559 | 미확인 | NIR 초분광 이미지(ENVI), RGB 사진, 평균 스펙트럼 CSV | 산업 후 섬유 시료 71종, 스펙트럼 1,100만+(600만+ 주석) | 섬유 조성, 색상, 스펙트럼 | 저장소명 미확인 | 핀란드 단일 공급처 | 2 |

## Data in Brief / Mendeley Data — fiber/te

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 천연·합성 섬유 ATR-FTIR 스펙트럼 (DIB 2026) | https://doi.org/10.1016/j.dib.2026.112594 | 미확인 | 원시·전처리 ATR-FTIR 스펙트럼 | 160 스펙트럼, 검증된 시료 137종 | 섬유 아형, 4000–550 cm⁻¹ 스펙트럼(원시/베이스라인 보정/평균/전처리) | Mendeley Data(라이선스 미확인) | 소규모 | 2 |

## Data in Brief / Mendeley Data — textile 

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 니트 공정 ML 데이터셋 (DIB 2025) | https://doi.org/10.1016/j.dib.2025.111873 | 미확인 | 공장 생산 기록 정제 표 | 12,569행×38열 | 원사 종류·번수, 기계, 스티치 길이, 타이트니스 팩터, GSM | Mendeley Data(라이선스 미확인) | 단일 공장 | 1 |
| 직조 공장 생산·불량 데이터 (DIB 2023) | https://data.mendeley.com/datasets/6mwgj7tms3/2 | 미확인 | 9개월 일일 생산 보고 | 121,148행, 18변수(원자료 22열) | EPI, PPI, 경·위사 번수, 생산량, 불량 | Mendeley Data(라이선스 미확인) | 단일 공장(방글라데시) | 1 |

## Data in Brief / Zenodo — textile composi

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 의류 조성 데이터(북유럽 텍스타일 아나토미 DB, 패스트패션 조화 데이터) | https://doi.org/10.1016/j.dib.2026.113017 | 미확인 | 의류 섬유 조성·부속 구조 | 북유럽 DB 5,000+ 의류(PCTWM 1,248); 패스트패션 47,522 색상별 변형 레코드 | 섬유 조성(%), 의류 분류, 부속품, 출처 | 패스트패션: 데이터 CC BY 4.0, 코드 MIT(Zenodo) | 소매 웹페이지 기반(검증 안 된 표시 조성) | 1 |

## Data in Brief — keratin fiber

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 곱슬 모발 단섬유 인장 데이터 (DIB 2023) | https://doi.org/10.1016/j.dib.2023.109943 | 미확인 | 단섬유 인장 시험 | unknown | 변형률 속도, 건조/식염수 침지, 온도 | 기사 연계(미확인) | 인체 모발 한정 | 2 |

## Data in Brief — keratin spectra

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 표백 모발 Raman/IR 스펙트럼 (DIB 2021) | https://doi.org/10.1016/j.dib.2021.107439 | 미확인 | Raman·ATR-IR | unknown(표백 3·4회 조건) | 과황산염/H2O2 처리 횟수 → 스펙트럼 | 기사 연계 | 소규모 | 1 |

## Data in Brief — protein fiber processing

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 누에 실크 알칼리 정련 DoE tidy 데이터 (DIB 2021) | https://doi.org/10.1016/j.dib.2021.107294 | 미확인 | 실험계획법 스크리닝 결과 표 | unknown | 정련 조건 → 결과 지표 | 기사 연계 | 소규모 | 2 |

## Scientific Data — protein fiber

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 거미줄 나노구조·콜라겐 피브릴 인장 데이터 (Sci Data 2014/2018) | https://doi.org/10.1038/sdata.2014.40 | 미확인 | 나노스케일 구조 데이터, AFM 단일 피브릴 인장 | unknown | 구조 특징, 파단 거동 | unknown | 생물 시료 | 1 |

## GitHub / Scientific Data / Kaggle — text

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 직물 결함 이미지(Industrial Textile Dataset, TSFabrics, AITEX 등) | https://github.com/SimonThomine/IndustrialTextileDataset | 접속 확인 | 직물 이미지(정상/결함) | ITD: 10개 유형 합계 약 5,662장(README 표 합산); TSFabrics·AITEX unknown | 이미지, 결함 라벨 | ITD: Google Drive 배포(라이선스 미기재) | 비전 과제 | 0 |

**이 조사 블록에서 확인된 데이터 공백**

- 비대칭(일방향) 수분이동·Janus 막: Data in Brief/Scientific Data(PubMed)와 GitHub에서 일방향 수분이동 지수, AATCC 195 수분관리 시험(OMMC), 투습도 측정 데이터셋을 하나도 찾지 못함. 가장 가까운 것은 RhNet의 고분자 수분 흡착 841행(PVAc 40행 포함)뿐
- 케라틴: 추출 조건-수율, 재생 케라틴 필름·섬유·전기방사 공정-물성 데이터셋이 공개 저장소에 없음. 인체 모발 인장, 표백 모발 Raman/IR, 캐시미어 유전체 정도만 존재
- DES/IL 바이오고분자 용해·가공: 셀룰로스-IL 용해도(674행)는 있으나 셀룰로스/케라틴의 DES 용해도, DES 기반 방사·전기방사 데이터셋은 미확인. DES 데이터는 융점·밀도·점도 위주
- PVA/PVAc: Cogni-e-SpinDB(PVA 133행)와 SpinCastML(PVA 6,920 의사관측)이 전부. PVAc 전기방사, PVA 가교·검화도별 물성 데이터는 없음
- 셀룰로스 유도체 전기방사: SpinCastML의 CA(1,880 의사관측)가 유일한 규모 있는 공개원. EC/HPC/CMC 등은 없음(EC-PEO 저장소는 원자료 미공개)
- 전기방사 섬유 탄화(PAN/리그닌/셀룰로스→탄소섬유): 안정화·탄화 조건-수율·전도도 정형 데이터셋 없음. 소규모 DIB 그림 데이터뿐
- 전기방사 데이터의 구조적 결함: 바늘 직경·습도·용액 점도/전도도 결측이 흔하고, 연구 식별자 하나로 섬유경 분산의 44%가 설명되며 연구 단위 교차검증 R²가 −0.11로 무너짐(EC-PEO 저장소 분석). 문헌 데이터만 쓰면 실험실 효과 보정이 필수
- SpinCastML의 68,480 관측은 고분자별 총계가 모두 40의 배수여서 보고된 분포를 재표본한 의사관측일 가능성이 큼(조사자 추론). 실질 독립 조건은 약 1.7k로 봐야 함
- Figshare·Dryad·OSF: 이번 세션에서는 고분자·섬유·막 관련 구체 데이터셋을 하나도 확인하지 못함. 해당 저장소 접속이 차단됐고 웹검색 예산(턴당 200회, 에이전트 공유)이 첫 호출에서 이미 소진돼 저장소 자체 검색 API를 쓸 수 없었음. 존재하지 않는다는 뜻이 아니라 미확인이라는 뜻
- Hugging Face·Kaggle: 계산 물성(OPoly26, Open Polymer Challenge)과 LLM 평가(PolyReal) 외에 공정·섬유·막 실험 데이터셋은 확인 안 됨
- 라이선스: GitHub 저장소 다수는 코드 라이선스(MIT 등)만 있고, PolyInfo·문헌에서 온 원자료 재배포권은 불명확(예: pgmML의 PolyInfo PID). Cogni-e-SpinDB는 README 배지(MIT)와 LICENSE 파일(CC0)이 서로 다름. Zenodo 데이터 라이선스는 접속 차단으로 하나도 직접 확인 못함
- URL 검증 한계: DOI 대부분은 PubMed MCP 메타데이터나 alphaXiv 본문으로 실재를 확인했지만 해당 URL을 직접 열지는 못해 'unverified'로 표시함. 'direct'는 GitHub(git/raw)로 받은 것만 해당
- PolyLM(18.5만 편 코퍼스)과 PHA RAG 코퍼스는 데이터 공개 여부가 확인되지 않음

## biopolymer/solvent

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| IL 중 셀룰로오스 용해도 + IL 융점 데이터셋 (ML4IL; Qu et al., J Cheminform 2025) | https://github.com/Mengyang2024/ML4IL | 접속 확인 | 문헌에서 모은 셀룰로오스 용해도 실측값과 IL 융점 | 셀룰로오스 용해도 674행(고유 IL 331종, 출처 33편), 수분 1% 미만 부분집합 379행. IL 융점 2,276행(CSV 직접 집계) | IL SMILES(양이온·음이온), 셀룰로오스 종류(MCC 423/일반 167/Avicel 84), T, 가열시간, 용해도(wt%, 0–29.3), 출처. 융점 데이터는 이름·Tm·SMILES·출처 | MIT(LICENSE 직접 확인). 원 문헌 수치 인용 | 아세테이트 음이온이 213/674(32%)로 편중. DP, 수분, 용해 판정법(현미경 vs 중량)이 대부분 기록되지 않음. 출처 33편이라 연구실 효과가 큼 | 3 |
| NIST ILThermo 2.0 (이온성 액체 열물성 DB) | https://ilthermo.boulder.nist.gov/ | 미확인 | 실험 열물리·상평형 데이터(순수 IL, 이성분·삼성분 혼합물), 문헌 출처 연결 | 공식 총건수는 이번 세션에서 확인 못 함. 2차 근거: jnitlion/il-property-explorer README에 'ILThermo에서 8,314 data sets 수집 → 정제 후 약 89k points, 1,828 compounds'(일부 물성만). CheMixHub RE… | 밀도, 점도, 전기전도도, 열용량, 표면장력, 융점·Tg, 활동도계수·상평형, T/P/조성. 화합물은 이름 위주이고 SMILES는 없음(ILThermoPy가 보강) | 무료 웹 DB. 안정적인 공식 API는 없음(ILThermoPy README). 재배포 조건 미확인 | 동일 계에서 서로 충돌하는 값이 있음(HedayatHaddadi/ILThermo_Activity가 activity coefficient 충돌 해소용으로 만들어짐). 이미다졸륨계 편중이 흔함. 고분자(셀룰로오스·케라틴) 용질 데이터는 사실상 없음 | 2 |
| DESignSolvents DES 물성 DB (Odegova et al., Green Chem 2024) | https://github.com/acid-design-lab/DESignSolvents | 접속 확인 | 문헌에서 모은 DES 실험 물성(2·3성분)과 RDKit 기술자, CatBoost 모델 | 저장소 CSV 직접 집계: Density 4,309행(445개 계, 133 DOI), Viscosity 4,457행(508개 계, 113 DOI), Melting_temperature 2,259행(114 DOI). 논문 보고치는 Tm 2,303·밀도 4,369·점도 4,216(sram… | 성분명 1~3, DES Type(I–V), 몰분율, T(K), 밀도(g/cm3)·점도(cP)·Tm(K), 참고 DOI, 성분 SMILES와 성분 융점(Tm 파일) | LICENSE 파일 없음 → 기본 저작권 유보 상태. 사용 전 저자 확인 권장. 웹 플랫폼 URL은 미확인 | 밀도 행의 61%가 Type III, 39%가 component#1=choline chloride. Tm에서 Type II는 11행뿐. 측정법(점도계 종류, 수분 함량)이 기록되지 않음 | 2 |
| openCOSMO-RS (오픈소스 COSMO-RS 구현) | https://github.com/TUHH-TVT/openCOSMO-RS_py | 접속 확인 | COSMO-RS 활동계수·용해 계산 코드(데이터 생성기). conformer pipeline과 C++ 버전 별도 | 해당 없음(도구) | σ-profile 기반 활동계수, H^E 등 | LGPL(LICENSE 직접 확인) | 상용 COSMOtherm과 파라미터 차이가 있음. ORCA 같은 QM 계산이 별도로 필요 | 2 |
| 고처리량 폴리에스터·폴리카보네이트 생분해 데이터 (Fransen et al., PNAS 2023) | https://doi.org/10.1073/pnas.2220021120 | 미확인 | clear-zone 기반 고처리량 생분해 판정과 구조 기술자 | 화학적으로 다른 폴리에스터·폴리카보네이트 642종(초록) | 반복단위 구조, 생분해 여부·속도. ML 정확도 >82% | PNAS(OA 여부와 데이터 공개 형태 미확인) | 단일 균주 colony와 현탁 입자 조건. 표준 시험(OECD/ISO 광물화)과 다름. PVA·셀룰로오스·단백질 없음 | 2 |
| PVA 하이드로겔 인장 물성 문헌 데이터 (Gels 2025) | https://doi.org/10.3390/gels11070550 | 미확인 | 체계적 문헌조사로 모은 PVA 하이드로겔 조성·공정-인장변형 | 350 data points(초록). 관련 소규모 자료: 동결해동 PVA 강성 DoE-ML(JMBBM 2026, DOI 10.1016/j.jmbbm.2026.107380) | PVA 농도, 가교·동결해동 조건 등, 인장변형(XGBoost R² 시험 0.80) | MDPI OA. 데이터 공개 여부 미확인 | 문헌별 시험 규격 혼재 | 2 |
| 바이오매스 열분해 생성물 통합 데이터 (Bioresour Technol 2026)와 바이오차 수율 데이터셋 | https://doi.org/10.1016/j.biortech.2026.135221 | 미확인 | 문헌에서 모은 근사·원소 분석, 리그노셀룰로오스 조성, 열분해 조건 → 생성물 수율 | 100편 이상에서 1,400 records 이상(basis 표준화·질량수지 필터, 2026). 바이오차: 바이오매스 44종 423 관측(DOI 10.1016/j.biortech.2024.131321), 211 샘플(DOI 10.1186/s40643-026-01058-9) | 휘발분, 고정탄소, 회분, C/H/O/N, 셀룰로오스·헤미셀룰로오스·리그닌 함량, 온도, 승온속도 → char/oil/gas 수율 | 미확인 | 벌크 바이오매스 열분해라 섬유·나노섬유 안정화·탄화와는 다름 | 2 |
| 케라틴 IL/DES 용해·추출 문헌 코퍼스 (데이터셋 아님) | https://pubmed.ncbi.nlm.nih.gov/?term=keratin+deep+eutectic+solvent | 미확인 | 개별 실험 논문(용해 조건, 수율, 재생물성) | PubMed 검색 기준 'keratin ionic liquid dissolution' 15건, 'keratin deep eutectic solvent' 18건(리뷰·비관련 포함). 예: [Emim][OAc] 중 양모 용해 시간-온도 중첩(DOI 10.3390/ma17010244), 시… | 원료(양모·깃털·발굽), 용매 조성, 몰비, T, 시간, 수율, 분자량, 재생 섬유·필름 물성(논문마다 다름) | 각 논문 저작권 | 표준화된 수율 정의가 없음(WSK/WIK 구분 등). 원료 전처리 편차가 큼 | 2 |
| IL 세포독성 데이터셋 (Arakelyan et al., Sci Data 2024) | https://doi.org/10.1038/s41597-024-04190-3 | 미확인 | 문헌에서 모은 IL 세포독성 값 | 1,227개 IL, 3,837 entries, 논문 151편(PubMed 초록) | 물질명, 분자식, CAS, SMILES, 분자량, 세포독성 값, 세포주, assay, 배양시간, 원문 참고 | 초록에 '모든 연구자에게 무료 공개'. 구체 라이선스 미확인 | 세포주와 assay가 제각각이라 값 간 비교 가능성이 낮음 | 1 |
| BigSolDB 2.x (유기물 용해도 DB) | https://github.com/levakrasnovs/BigSolDBv2.0 | 접속 확인 | 실험 용해도(저분자 용질 × 단일 유기용매 × 온도) | README: v2.2에 125,752 값, 1,627 화합물, 221 용매, 논문 1,842편. Sci Data 2025(v2.0) 초록은 103,944 값, 1,448 화합물, 213 용매 | 용질·용매 SMILES, T(243–425 K), 용해도, 출처, 용매 밀도표 | 저장소에 LICENSE 파일 없음. Zenodo DOI 10.5281/zenodo.22648301(미열람) | 약물 유사 저분자 위주. 고분자 없음. DES 용매는 거의 없을 것으로 보임(미검증) | 1 |
| 이성분 혼합용매 용해도 데이터셋 (Malikov et al., Sci Data 2026) | https://doi.org/10.1038/s41597-026-07047-z | 미확인 | 이성분 혼합용매 중 저분자 실험 용해도 | 175,166 값, 810 화합물, 3,001 용질-혼합용매 계, 750 혼합용매, 논문 1,115편(PubMed 초록) | 용질·용매 구조, 혼합 조성, T(252–383 K), 용해도 | 미확인 | 약물 저분자 중심 | 1 |
| COSMO-RS 바이오매스 용해 스크리닝 결과 (논문 SI 묶음) | https://doi.org/10.1016/j.foodchem.2026.148195 | 미확인 | COSMO-RS 계산값(ln γ∞, H^E, σ-profile)과 소수 실험 검증 | 박테리아 셀룰로오스: IL 792종(Lv et al. Food Chem 2026). 리그닌: IL 5,670종(Mohan et al. Sci Rep 2023, DOI 10.1038/s41598-022-25372-2). 헤미셀룰로오스: IL 1,368종(Zhao et al. RSC Ad… | 용매 구조, 모델 용질(셀로비오스·자일란 이량체·리그닌 모델화합물), ln γ, H^E, 수소결합 에너지, 일부 실측 용해도 | 출판사별. RSC Adv와 Sci Rep는 OA. SI 공개 범위는 미확인 | 용질 모델(올리고머 길이)에 따라 순위가 바뀜. 계산 순위와 실측 용해도의 대응 데이터가 매우 적음. 정형 데이터셋으로 공개된 것은 미확인 | 1 |
| 효소 고처리량 폴리에스터 생분해 + 전이학습 (Jacob et al., Chem Sci 2025) | https://doi.org/10.1039/d5sc05380c | 미확인 | 효소 기반 생분해 assay 결과와 문헌 데이터 | 폴리에스터 48종(초록) | 구조, 생분해성. 랜덤포레스트 정확도 71%. transfer learning·model chaining 시도 | Chem Sci(OA로 추정, 미확인) | 소규모 | 1 |
| PHB/PHBV 열물성 통합 데이터베이스 (Polymers 2026) | https://doi.org/10.3390/polym18131559 | 미확인 | 문헌 558건과 자체 실험 14건의 PHB/PHBV 조성-열물성 | 572 instances. 학습 가능한 수는 Tg·Tm 118, Tc 201(초록) | 조성, 분자 특성, Tg/Tm/Tc | MDPI(OA). 데이터 공개 여부 미확인 | 결측이 많아 사용 가능 비율이 21~35% | 1 |
| 초접착 하이드로겔 데이터 기반 설계 (Liao et al., Nature 2025) / 하이드로겔 레올로지-프린팅성 DB (Jeong et al., Adv Sc… | https://doi.org/10.1038/s41586-025-09269-4 | 미확인 | 단백질 서열 통계 기반 랜덤 공중합 하이드로겔 조성-접착강도 / 3D 프린팅 하이드로겔 비선형 레올로지(LAOS)-프린팅성 | 초기 하이드로겔 180종(Nature). 하이드로겔 150종 DB(Adv Sci, 숙명여대·KICET, DOI 10.1002/advs.202507639) | 단량체 조성 기술자와 접착강도 / LAOS 지표와 수평·수직 프린팅성 | 미확인 | 단일 랩, 설계 공간이 좁음 | 1 |
| PVA 나노복합체 유전율 문헌 데이터 (Discov Nano 2026) | https://doi.org/10.1186/s11671-026-04832-y | 미확인 | 문헌에서 모은 PVA/나노필러 유전율 측정 | 1,698 측정(초록) | 필러 종류(CuO, TiO2, ZnO, Al2O3, GO 등), 함량, 주파수 등 → 유전율 | 미확인 | 특정 기능물성에 한정 | 1 |
| PlasticDB / PlaszymeDB (플라스틱 분해 미생물·효소 DB) | https://github.com/Tsutayaaa/PlaszymeDB | 접속 확인 | 플라스틱 분해 효소 서열과 메타데이터(PlaszymeDB). 미생물·단백질 DB(PlasticDB, plasticdb.org) | PlaszymeDB v0.1.5 2,233 entries(PET 505, PHB 189, PLA 153, PHA 118, PCL 113 등). PlasticDB 규모 미확인 | plastic, label, sequence, GenBank/UniProt/PDB ID, EC, host, taxonomy, reference | PlaszymeDB LICENSE 없음. PlasticDB 조건 미확인(Database 2022 논문) | 효소 단위 데이터라 재료 물성과 연결되지 않음 | 0 |

## GitHub dataset

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Hansen 핸드북 Table A.2 고분자 HSP 전사본 (jtreeder/Materialism) | https://github.com/jtreeder/Materialism | 접속 확인 | 고분자·수지 Hansen 구(δD, δP, δH, R0) 표와 HSPiP 고분자 표 | hansen_a2 466항목, hspip_polymers 458항목(CSV 직접 집계). 정제 변형본 hsp_polymers_2~8 포함 | 이름, δD/δP/δH, 상호작용 반경 R0, 카테고리(출처 신뢰도 주석 포함), CAS(대부분 빈칸) | LICENSE 없음. CRC 핸드북 표를 옮긴 것이라 저작권 위험 → 재배포 대신 인용 형태 권장 | 셀룰로오스 아세테이트·CAB·CAP·니트로셀룰로오스·에틸셀룰로오스·PVAc·리그닌(2건)은 있음. PVOH는 'NOT GOOD' 주석. keratin·wool·silk·chitosan 항목 0건. 'Not too reliable' 주석 다수 | 3 |
| ILThermoPy (비공식 ILThermo 2.0 클라이언트 + SMILES 보강) | https://github.com/muCommons/ILThermoPy | 접속 확인 | ILThermo 레코드 수집 패키지와 IL 성분→SMILES 수동 검증 매핑 | 매핑 규모는 README에 없음(unknown). PyPI ilthermopy 1.1.2 | ILThermo 레코드, 성분 SMILES | MIT(PyPI JSON으로 직접 확인). 데이터 자체는 NIST 소관 | ILThermo 웹 동작에 의존해서 업데이트 시 깨질 수 있음 | 2 |
| DES 융점 통합 데이터셋 (srampinogroup/des-ml-exploration; Odegova + Luu 병합) | https://github.com/srampinogroup/des-ml-exploration | 접속 확인 | 서로 다른 두 문헌 DES Tm 데이터셋을 단위 변환·중복 처리해 병합한 것 | DES_TMELT.csv 2,658행(README상 병합 결과 2,651). 구성: Odegova 2,259 + Luu et al. 2023(APL 122:234103; lamm-mit/MoleculeDiffusionTransformer) 401행 | HBA/HBD 이름·SMILES, 성분 융점, 몰분율, DES 융점, DES Type, 참고 DOI | MIT(LICENSE 직접 확인). 원천 데이터 라이선스는 별도 | 중복 8건 중 7건은 ±10 K 범위에서 평균 처리. 병합분에는 DES type 정보가 없어 Type III/V 편중이 그대로 남음 | 2 |
| Type III/V DES 6개 물성 데이터셋 (9970507/ML_for_multiple_property_prediction_of_DESs) | https://github.com/9970507/ML_for_multiple_property_prediction_of_DESs | 접속 확인 | 문헌에서 모은 DES 물성, 학습/테스트 분할(mixtures-out)과 XGBoost 모델 | Melting_point 2,601, Density 4,817, Viscosity 3,035, Heat_capacity 1,941, Electrical_conductivity 1,192, Refractive_index 1,059행(CSV 직접 집계) | DES Type, 성분명·SMILES, 몰분율, T, 각 물성(점도·전도도는 로그값 포함) | MIT(LICENSE 직접 확인) | Type III/V만 포함. 출처 DOI 컬럼은 학습 CSV에 없음(병합 추적이 어려움). DESignSolvents와 원천이 상당히 겹칠 가능성 있음(미검증) | 2 |
| DES 통합 GOLD 데이터셋 (hakimfaraji/DES-ML-audit-benchmark) | https://github.com/hakimfaraji/DES-ML-audit-benchmark | 접속 확인 | 여러 코퍼스를 하나로 합친 DES 물성 표. 출처·측정조건 메타데이터 포함 | Unified_DES_dataset_GOLD_descriptor_ready_subset.csv 2,808행. README에는 데이터 미동봉 가능성이 적혀 있으나 실제 파일은 있음 | source_corpus/period/origin, article_title, journal, year, doi, molar_ratio_raw, ratio_basis, stability_flag, tm_c, density, viscosity, conductivity, surface_t… | MIT(저장소 LICENSE). 원천 문헌 데이터 라이선스는 별도 | 누설(leakage)·불균형·적용영역 감사를 목적으로 만든 세트. 'GOLD'는 기술자 계산 가능한 부분집합이라 선택 편향이 있음 | 2 |
| PubChemQC COSMO σ-profile DB (361,583 분자) | https://github.com/Danny-Taehyun-Kim/PySCF-Sigmaprofile-COSMO-SAC | 접속 확인 | PySCF BP86/def2-SVP σ-profile(NHB/OH/OT)과 COSMO-SAC 재보정 파라미터 | 361,583개 유기분자(MW 약 250 이하, README) | σ-profile 3종, 분자 인덱스, COSMO-SAC 파라미터 | 저장소 MIT. data/LICENSE가 따로 있으나 열람하지 않음 | PM6 구조를 재최적화하지 않음. 저분자 한정(고분자·이온쌍 처리 제한) | 2 |
| HSPiPy 용매 HSP 표 (Gnpd/HSPiPy) | https://github.com/Gnpd/HSPiPy | 접속 확인 | 용매 HSP와 HSP 구 피팅 라이브러리 | examples/HSP_dataset.csv 1,206개 용매 | Name, δD, δP, δH, 몰부피, CAS, SMILES | MIT(LICENSE 직접 확인). 수치 원출처는 Hansen 계열로 추정(미확인) | 분자 용매만 있고 IL/DES는 없음 | 2 |
| 분자 HSP ML 데이터셋 (darjacvetkovic/HSP-predictions; Chemolab 2024) | https://github.com/darjacvetkovic/HSP-predictions | 접속 확인 | 분자 HSP 실측(문헌)과 XGBoost/GNN 모델 | HSP_SMILES.csv 1,192 분자 | 이름, CAS, SMILES, δD, δP, δH | MIT(LICENSE). 원 데이터 출처 라이선스는 별도 | 저분자만 있음. 고분자 HSP 예측에는 반복단위 근사가 필요 | 2 |
| autoHSP (능동학습 기반 HSP 자동 결정) | https://github.com/SijieFu/autoHSP | 접속 확인 | 이원 혼합용매 설계, 바이알 이미지 CV 판정, 배치 능동학습 코드와 실험 설정 데이터 | data/R0_prior.csv, computer_vision_summary.csv 등(행수 미집계) | 용매·혼합비, 혼화 판정, HSP 추정치 | Apache-2.0(LICENSE 직접 확인) | 원격 자동화 랩 전제 | 2 |
| CheMixHub (혼합물 물성 벤치마크) | https://github.com/chemcognition-lab/chemixhub | 접속 확인 | 7개 공개 데이터셋에서 정제한 11개 task와 ILThermo 신규 2개 task(전도도·점도) | 논문 기준 총 약 500,000 points. ILThermo task 116,896 points(README). ILThermo 원자료는 fetch 스크립트로 직접 받아야 함 | 성분 SMILES, 몰분율, 온도, 물성(로그 변환). Croissant 메타데이터. random/분자제외(LMO)/혼합물 크기/온도 외삽 split | MIT(LICENSE 직접 확인). 하위 원천 데이터는 각 출처 조건을 따름 | 바이오고분자 없음. 고분자는 단량체로 단순화됨. 결측 온도를 298.15 K로 가정하고 플래그 처리 | 1 |
| LVPP sigma-profile DB / NIST COSMO-SAC | https://github.com/lvpp/sigma | 접속 확인 | COSMO 표면전하밀도, COSMO-SAC 파라미터, 최적화 구조. NIST 구현(usnistgov/COSMOSAC) 포함 | LVPP: 2,500개 이상 분자(README), 파일 11,272개. NIST: VT2005/UD 프로파일 포함(규모 미집계) | σ-profile, 기하구조, 모델 파라미터 | LVPP MIT. NIST 코드는 MIT이나 profiles/UD·VT2005의 .cosmo 파일은 학술·비상업 전용(README) | 저분자 용매 중심 | 1 |
| PHBV 생분해 큐레이션 데이터셋 (FSL-AUA; Kotzabasaki et al., Polymers 2026) | https://github.com/FSL-AUA/Biodegradation-model | 접속 확인 | 문헌 랩스케일 광물화 생분해 시계열 | 1,364행, 단 13개 연구에서 나옴. 환경별 퇴비 545 / 해양 392 / 토양 368 / 랩배지 59 | 시간(일), 생분해 %, HB/HV 몰비, 조건, 메커니즘, 첨가제 3종과 함량, 형태, 미생물 | LICENSE 없음 | 연구 13편에 의존해 연구 간 효과가 지배적. 시계열 점이라 독립 표본 수가 과대계상됨 | 1 |
| 과립형 하이드로겔 실험 데이터셋 (Verheyen et al., Matter 2023 + meta-learning) | https://github.com/connor-verheyen/ML_MetaLearning_SoftMatter | 접속 확인 | 마이크로겔 형성·크기·형상, 압출성, 레올로지 실험 데이터(분류·회귀 약 30개 task) | basic_dataset_info.xlsx: 실험 20~291건/task(예: 압출 이진 291, 레올로지 101, 마이크로겔 크기진화 74실험/5,504관측) | 조성·공정 변수 6~14개, 출력(압출 결과, G'/G'', 항복응력, 직경 등) | 두 저장소 모두 LICENSE 없음. Zenodo DOI 10.5281/zenodo.7506819(미열람) | 단일 랩, 단일 재료계. 일반화가 제한됨 | 1 |
| PVA 전기방사 소규모 데이터 (AriadneD/electrospinningdata, PVA-electrospinning) | https://github.com/AriadneD/electrospinningdata | 접속 확인 | 논문 3편의 PVA 전기방사 조건-섬유경 | data1 26행(Elkasaby), data2 9행(Teixeira), data3 17행(Kusumawati) | 전압, 농도, 회전속도, 거리, 유량 → 직경(파일마다 컬럼 다름) | LICENSE 없음 | 파일마다 변수 집합과 단위가 달라 바로 합칠 수 없음 | 1 |
| 키토산-TPP 나노입자 문헌 데이터셋 (hw8891877-source/chitosan-ml-nanoparticle) | https://github.com/hw8891877-source/chitosan-ml-nanoparticle | 접속 확인 | 문헌에서 모은 이온겔화 키토산 나노입자 조성-특성 | 342행 | DOI, 제목, 연도, 약물, 키토산 MW(kDa), 탈아세틸화도(%), 키토산·TPP 농도, 질량비, 교반, pH → 입경, PDI, 제타전위, 봉입률, 담지량 | MIT(LICENSE) | 약물전달 용도 한정. 섬유·막 가공 데이터 아님 | 1 |

## generic repository

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| COSMO-RS 계산 χ 데이터 (figshare, Aoki et al.) | https://figshare.com/articles/dataset/Flory-Huggins_interaction_parameter_calculated_by_COSMO-RS_simulation/25448056 | 미확인 | COSMO-RS로 계산한 고분자-용매 χ | unknown(figshare 접속 차단으로 미확인) | 고분자·용매 쌍, T, χ(계산) | figshare 라이선스 미확인 | 올리고머 모델 근사. 실측 대비 계통오차 | 2 |
| NIST ThermoML Archive (학술지 열물성 데이터 아카이브) | https://trc.nist.gov/ThermoML/ | 미확인 | JCED, JCT 등 학술지 게재 열물성 데이터의 XML 아카이브 | unknown(이번 세션에서 미확인) | 순수·혼합물 물성, 조건, 불확도(ThermoML 스키마) | 공개 아카이브. 인용 DOI 10.18434/mds2-2422(Garren-H 도구 README). 세부 이용조건 미확인 | 분자 용매 중심. DES·IL 데이터 비중과 고분자 용액 포함 여부는 미확인 | 1 |

## polymer DB

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 실험 Flory-Huggins χ 데이터셋 (yoshida-lab/MTL_ChiParameter; Aoki et al., Macromolecules 2023) | https://github.com/yoshida-lab/MTL_ChiParameter | 접속 확인 | Orwoll & Arnold 『Physical Properties of Polymers Handbook』 보충표에서 뽑은 실험 χ와 같은 쌍의 COSMO-RS χ | data_Chi.csv 1,190점(고분자 46종 × 용매 140종, 온도 포함). 클래스 분포: polystyrenes 199, polyvinylx 189, polyester 131, cellulose 55 등. data_COSMO.csv 1,206행 | 고분자_용매 SMILES 쌍, 온도, χ, 고분자 클래스, 기술자(desc_*.csv) | MIT(LICENSE). 단 PoLyInfo 용해성 라벨은 재배포 제한 때문에 인공 데이터로 대체되어 있음(README 경고) | 고분자 46종뿐이고 합성고분자 위주. 셀룰로오스계는 55점(유도체). 단백질·키토산·PVA 순수 데이터는 미확인. 측정법(증기압, 삼투압, IGC) 혼재 | 3 |
| PolyOmics (RadonPy 컨소시엄 계산 고분자 DB) | https://github.com/RadonPy/RadonPy | 접속 확인 | 전원자 MD 자동계산 물성(RadonPy). PolyOmics 본체는 Hugging Face 공개(링크 미확인) | arXiv 2511.11626 기준 730만 건 이상, 62개 물성, 고분자 10^5종 이상. 이 중 셀룰로오스 유도체 약 50,000종, 생분해성 후보 383종, ML 예측 χ(유기용매·가소제 19종 × 고분자 약 93,000종) | 밀도, Cp/Cv, 압축률, 굴절률, 유전율, 용해도 파라미터(CED), 자유부피, Rg, 열전도도 등과 χ | RadonPy 코드 BSD-3(README 직접 확인). PolyOmics 데이터 라이선스 미확인 | GAFF2 비정질 MD라 결정성·수소결합 네트워크 재현에 한계가 있음. 셀룰로오스 유도체는 치환 패턴으로 가상 생성한 것 | 3 |
| PoLyInfo (NIMS 고분자 DB) | https://polymer.nims.go.jp/ | 미확인 | 문헌 기반 고분자 실험 물성(용해성, 용해도 파라미터, 열물성 등) | unknown(이번 세션 미확인). RadonPy 논문은 PoLyInfo의 실험 물성 61개 데이터셋을 미세조정에 사용 | 고분자 구조, 물성, 측정조건, 문헌 | 회원가입 필요. 재배포 제한(MTL_ChiParameter README: 'data sharing restriction by the PoLyInfo database') | 합성고분자 중심. 바이오고분자 커버리지는 미확인 | 2 |
| Hildebrand/Hansen 파라미터 정확도 평가 (Venkatram et al., JCIM 2019) | https://doi.org/10.1021/acs.jcim.9b00656 | 미확인 | 고분자 용매·비용매 실측과 SP 모델 비교 | Hildebrand 평가 75개 고분자, Hansen 평가 25개 고분자(초록) | 고분자, 용매/비용매 라벨, δ | 미확인(ACS) | 초록 결론: 극성 고분자에서 Hildebrand 정확도 57%, 고분자 Hansen 데이터셋이 '상당히 작다' | 1 |
| MD 보정 고분자 용해도 대규모 계산 (Zhou et al., Green Chem 2023) | https://doi.org/10.1039/D3GC00404J | 미확인 | 실험으로 보정한 MD 기반 용해도 예측(SI) | 8개 고분자(EVOH, PE, PP, PS, PET, PVC, Nylon6, Nylon66) × 1,007 용매 × 2 온도. arXiv 2512.09784는 25 °C의 8,049 조합을 사용 | 용매 CAS, 고분자, wt% 용해도, T | SI(출판사 조건) 미확인 | 바이오고분자 없음(EVOH만 PVA 계열에 근접) | 1 |
| 고분자 용해도 농도·온도 ML 데이터 (Amrihesari et al., JPCB 2024) | https://doi.org/10.1021/acs.jpcb.4c06500 | 미확인 | 고분자-용매 용해도 실험 데이터(SI xlsx) | unknown | 고분자, 용매, 농도, 온도, 용해 여부(추정) | ACS SI 조건 미확인 | 미확인 | 1 |
| PolyBench26 (LLNL 고분자 물성 벤치마크) | https://github.com/rlearsch/PolymerBenchmark2026 | 접속 확인 | 실험·DFT·MD 고분자 물성(단일·공중합체) | 약 250,000 datapoints, 8개 물성(Tg 실험 7,362. 나머지는 DFT/MD, OPoly26·VIPEA 출처) | Tg, EA, IP, 굴절률, 밀도, Cp, Cv, Rg | MIT(LICENSE 직접 확인) | 용해도·χ·탄화수율·생분해 물성은 없음 | 1 |

## patents/text

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 펩타이드 자기조립·하이드로겔 상 DB와 LLM 추출 (Yang et al., arXiv 2411.05421; SAPdb) | https://arxiv.org/abs/2411.05421 | 미확인 | 전문(full-text)에서 수작업 추출한 실험조건-상(hydrogel, fiber 등)과 미세조정 GPT-3.5 추출 평가 | 논문 75편에서 1,012 entries(8개 상). 원천 SAPdb 1,049 entries(PubMed PMID 33892308) | 서열, 말단수식, 용매·용액, 농도, pH, 온도, 열처리 → 상 | 미확인 | di·tri-peptide 한정. 'solution' 필드 추출이 가장 어려웠음 | 2 |
| 고분자 내화학성 데이터 (Kunieda et al., arXiv 2509.05344) | https://arxiv.org/abs/2509.05344 | 미확인 | 여러 제조사 내화학성 표를 병합해 이진화한 라벨과 MD·COSMO-RS 기술자 | 2,200개 이상 고분자-용매 조합(본문) | 고분자, 용매, 내성/비내성 라벨, COSMO-RS χ, MD 물성 16종 | 데이터 공개 여부 미확인 | 출처마다 평가 기준이 달라 '가장 엄격한 기준 = 내성'으로 이진화함(조화 손실) | 1 |

## fiber/textile

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| FibreCastML (전기방사 섬유경 메타데이터셋·웹 플랫폼) | https://doi.org/10.3389/fbioe.2026.1713804 | 미확인 | 문헌에서 모은 전기방사 조건 → 섬유경 분포 | 연구 1,778편에서 섬유경 측정 68,538개, 생의학 고분자 16종(PVA, 셀룰로오스 아세테이트, PAN, PLA, PCL 계열 등)(초록) | 고분자, 용매, 농도, 전압, 유량, 거리 등 → 섬유경 분포 | 오픈 웹 플랫폼으로 표기. 원자료 다운로드와 라이선스는 미확인 | 생의학 고분자 편향. 케라틴·키토산 포함 여부 미확인 | 3 |

**이 조사 블록에서 확인된 데이터 공백**

- 케라틴: 용해도, 추출수율, 재생섬유 물성, HSP, χ, 탄화수율 중 어느 것도 정형 공개 데이터셋이 없음. PubMed 검색 기준 keratin+IL 용해 15건, keratin+DES 18건(리뷰·비관련 포함)이 전부이고, GitHub 'keratin' 검색 249건 중 재료 데이터는 0건임. Hansen 고분자 표(466항목)에도 keratin/wool/silk 항목이 없고, 실험 χ 1,190점(46개 고분자)에도 단백질계가 없음. 결국 수십 편 논문에서 LLM으로 추출하는 방법과 openCOSMO-RS(시스틴·펩타이드 모델) 계산으로만 메울 수 있는데, 검증용 실측점은 극소수임.
- 셀룰로오스-DES 용해도: IL 중 셀룰로오스 용해도는 674점(331개 IL, 출처 33편, MIT)이 있으나 DES 중 셀룰로오스나 셀룰로오스 유도체 용해도의 공개 정형 데이터셋은 찾지 못함. COSMO-RS 스크리닝(IL 792~5,670종)은 논문 SI에 흩어져 있고 실험 검증점은 각 수~수십 개뿐임.
- 셀룰로오스 용해의 핵심 기술자인 Kamlet–Taft β(용매 수소결합 염기도)를 IL·DES에 대해 모아 놓은 공개 DB를 찾지 못함. Laurence 2022의 α 척도도 분자 용매 101종과 IL 30종 수준에 그침.
- 바이오고분자 HSP와 χ: 공개 HSP 표의 셀룰로오스계는 에스터·에틸셀룰로오스 위주이고, PVOH 값은 'NOT GOOD' 주석으로 신뢰성이 낮음. 키토산·케라틴은 없음. Venkatram 2019에서 Hansen 파라미터가 있는 고분자는 25개뿐이었음. 실험 χ의 공개분은 Orwoll & Arnold 유래 1,190점이고, PoLyInfo 용해성 라벨은 재배포 제한이 있음. IL/DES-고분자 χ 데이터는 사실상 없음. 핸드북 전사본은 저작권 위험이 있어 대회 제출물에 원자료를 첨부하기 어려움.
- DES 물성 데이터 편향: 밀도 데이터의 61%가 Type III이고 39%가 choline chloride 기반이며, 융점 데이터에서 Type II는 11건뿐임. 여러 공개 세트(Odegova, Luu, Type III/V 6물성, GOLD 통합)가 같은 원천을 공유할 가능성이 있어 단순 합산은 중복과 누설을 부를 수 있음(중복 정도는 미검증). 고분자 용질, 방사 적합성, 재생 거동과 연결된 데이터는 없음.
- 생분해: 대규모 공개분은 폴리에스터·폴리카보네이트(642종, clear-zone 판정)와 PHBV(13개 연구, 1,364점)에 몰려 있음. PVA/PVAc, 치환도별 셀룰로오스 유도체, 케라틴 섬유의 표준 시험(OECD 301/ISO 14855) 생분해 데이터셋은 찾지 못함. 시험법(clear-zone, 효소, 광물화 CO2, 질량감소)이 섞여 있어 바로 합칠 수 없음.
- 하이드로겔: 공개 데이터는 단일 랩 소규모(task당 20~300 실험)이거나 논문 내 데이터(180종, 150종, PVA 350점)뿐임. 대규모 큐레이션 하이드로겔 문헌 DB는 확인하지 못함.
- 탄화수율/TGA: 여러 고분자의 char yield를 모은 공개 데이터셋을 찾지 못함. PubMed에서 'char yield'+ML/QSPR은 5건이고, TGA-ML 논문은 대부분 단일 재료(PVA, 폐플라스틱, 바이오매스) 곡선 피팅임. 바이오매스 바이오차 수율 문헌 세트(423~1,400건 이상)만 있음. 전기방사 나노섬유(케라틴, 셀룰로오스, PVA)의 안정화·탄화 수율과 조건 데이터는 없음.
- 키토산: 용해(산 농도, DD, MW), 방사, 막 가공 공개 데이터셋을 찾지 못함. 약물전달 나노입자 문헌 세트(342행)만 확인함.
- 이번 세션은 시작 시점에 WebSearch 예산(turn당 200회, 에이전트 공유)이 이미 소진되어 웹 검색 결과를 하나도 쓰지 못함. ILThermo 공식 규모·라이선스, ThermoML, PoLyInfo, PlasticDB, Zenodo/figshare/Hugging Face 레코드는 접속 차단으로 직접 열지 못했고, 해당 수치는 GitHub README와 논문 초록 같은 2차 출처 기준임. Phyllis2, CROW, Polymer Handbook, DDBST처럼 널리 알려진 원천도 실재 확인을 못 해서 목록에서 뺐음.
- 비대칭(일방향) 수분이동 막, 한국 공공데이터(국가연구데이터 등), 특허 데이터는 이번 하위조사 범위에서 검색하지 않음.

## Korean public

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| DYETEC 섬유분야 가상공학플랫폼(소재데이터) – 섬유 특화 MDF 공공실험 데이터·AI 모델 (ai.dyetec.or.kr) | http://ai.dyetec.or.kr/intro/Intro.do | 미확인(검색 색인에만 존재) | MDF(소재데이터 생성 장비)로 표준 양식에 따라 만든 공공실험 데이터, 소재개발 AI 표준모델(전처리·학습 코드 포함), 전문가 풀을 활용한 컨설팅·기술지원 서비스 | unknown. 데이터셋 목록과 건수를 공개 문서에서 찾지 못함. 2025년 기술지원 규모는 10건(공고문) | 원료-조성-공정-물성 연계 구조. 섬유 특화 MDF 공정은 중합, 방사, 염색·가공. 공고문의 지원 예시: (1) 리사이클 염색·가공(버진 소재 수준의 공정성·물성, 저배출 공정) (2) 생분해성 PLA 섬유화(방사) 과정의 물성 저하 개선 (3) 석유계 대체 Bio-PET의 중합·방… | 기업 대상(신청 시 사업자등록증 제출). 1단계 컨설팅을 거쳐 2단계 기술지원으로 진행. 지원 조건: 기술지원에 쓰인 데이터의 일부를 플랫폼에 제공하는 데 사전 동의해야 함. '기업 특화 데이터/AI' 분야를 신청하려면 원료-조성-공정-물성이 연계된… | 표준화된 장비와 양식으로 생성해 측정 일관성은 높을 것으로 예상. 다만 소재 범위가 PET·PLA 등 DYETEC 장비와 산업 소재 중심. 기업이 제공한 비공개 데이터가 섞여 있음. 공개 건수가 없어 규모와 커버리지를 평가할 수 없음 | 2 |
| KoMaP 소재 디지털 데이터 플랫폼 – 섬유 AI 서비스(DYETEC: 염색색상예측, 용융방사 공정) | https://komap.ai/front/packages/ai_service/fiber_ai | 미확인(검색 색인에만 존재) | MDF 실험 데이터(원료, 조성, 공정변수, 시편, 시편 물성)의 저장·표준화·검색·시각화. AI 서비스로 조성·공정 입력 시 목표 물성 분포 추론. 실험 최적화 AI, JupyterLab 분석환경 | 4대 소재(화학·세라믹·섬유·금속) 데이터 14만8,702건과 AI 시범모델 8건: 2024년 7월 보도의 '지난해 말 기준' 수치로, WebSearch 요약에서만 확인. 'MDF 데이터 311,830건으로 학습한 물성 분포 추론 모델'(komap.ai 색인 요약)도 있으나 이 중 섬… | 섬유: 염색 공정조건→색상, 용융방사 공정조건→물성(세부 변수 미확인). 공통 스키마: 원료-조성-공정-시편-물성 | 서비스 신청 방식으로, 기업 대상으로 추정. URL에 auth_fail 파라미터가 보여 로그인이 필요한 것으로 추정. 외부 다운로드 가능 여부와 라이선스는 unknown | 4대 소재은행(섬유는 DYETEC, 금속은 KIMS 등)이 표준 장비로 생성해 형식 일관성은 높음. 섬유 데이터는 DYETEC 장비와 산업 소재(폴리에스터 등)로 편향되어 있을 가능성이 큼. 건수 수치는 기사 요약에 의존 | 2 |
| NTIS 국가과학기술지식정보서비스 (국가R&D 과제·성과·연구보고서 + OpenAPI) | https://www.ntis.go.kr/ | 미확인(검색 색인에만 존재) | 국가 R&D 과제, 성과(논문·특허·연구시설장비·보고서), 연구보고서 메타와 원문 URL, 수행기관 현황, 분류코드 | unknown | 과제번호, 사업명, 수행기관, 연구비, 기간, 키워드, 성과 유형, 보고서 원문 링크, 과학기술표준분류·국가중점기술 코드 | OpenAPI는 API마다 활용신청이 따로 필요하고 유효기간은 승인일로부터 1년. 신청 시 IP를 등록하므로 IP 제한이 걸릴 수 있음. 이용자격(전체용, 기관용, 전문기관용)에 따라 제공 필드가 다름. 웹 검색은 공개 | 보고서 품질이 들쭉날쭉함. 실험 데이터는 PDF 표 형태 | 2 |
| VEPOTEX (Virtual Engineering Platform of Textile Complex structure) – DYETEC 가상공학 시뮬레이션 플… | https://www.vepotex.or.kr | 미확인 | 시뮬레이션 SW 인프라, 'DB 라이브러리' 메뉴, 전문가 컨설팅. 실측 데이터 공개 여부는 불명 | unknown. 공고문 OCR에 홈페이지 '주요통계' 숫자가 있으나 판독 불가라 인용하지 않음. 2025년 지원 규모: 컨설팅 20건, 기술지원 10건 | 보유 SW: GeoDict(섬유 미세구조 3D 모델링·물성 예측), Digimat(장·단섬유 복합재 비선형 물성), Moldex(사출·압축·RTM), Simulia Abaqus, Ansys Mechanical/Fluent, BIOVIA Materials Studio(분자 모델링), M… | 회원사 가입 신청 후 온라인 또는 이메일로 접수. 기업 대상이며 직접적인 예산 지원은 없음. 라이선스 unknown | 결과가 시뮬레이션 산출물이라 실측 데이터가 아님. DB 라이브러리의 공개 범위와 내용을 확인하지 못함 | 1 |
| KoMaP 2024 AI 경진대회 데이터 – 염색 가공 공정(수송기기용 고기능성 섬유소재 색상·내광성 등급 예측) | https://komap.ai/front/competition/process | 미확인(검색 색인에만 존재) | 염색·후가공 공정조건 → 색상(L*a*b*)과 내광성 등급의 표 형식 데이터 | unknown(행 수 미확인). 대회에는 86팀이 지원해 6팀이 수상 | 염액 제조. 시작온도(예: 40°C), 승온(예: #3 120–140°C), 유지(레벨링) 시간(예: 10–80 min), 강온속도(예: 1.97°C/min), 강온온도(예: 64°C). 텐터 열세팅. 분광광도계 L*a*b*, 내광성 시험 전후 색차, 내광성 등급 | 대회 참가자에게 제공됨. 지금 재배포·다운로드가 가능한지와 라이선스는 unknown | 단일 기관이 생산한 데이터이며 수송용 폴리에스터 소재 중심으로 추정. 라벨이 등급형(순서형)이라 해상도가 낮음 | 1 |
| DYETEC Fabric Dive – 가상 원단 소싱 플랫폼 + GPT 챗봇 | https://dive.dyetec.or.kr/?lng=ko | 미확인(검색 색인에만 존재) | 원단과 기업 DB, 이미지·3D 소재물성 기반 가상의류, GPT 기반 조회 챗봇 | unknown | 혼용률, 직물 종류, 색상, 패턴, 폭, 중량. 검색 요약에는 소재물성(인장강도, 염색견뢰도 등)과 공인 시험분석 데이터도 언급됨 | 웹 조회 서비스. 로그인 요건, 대량 추출 허용 여부, 라이선스 모두 unknown | 상업 원단 카탈로그 성격. 측정 조건 메타데이터와 시험법 표기가 있는지 불명. 기업 자기신고 정보가 섞였을 수 있음 | 1 |
| DYETEC 섬유염색 현장지식 기반 통합 데이터 플랫폼(제조 지식베이스·정보은행) | https://www.tinnews.co.kr/27902 | 미확인(검색 색인에만 존재) | 염색 공장 현장 데이터 통합, 제조 지식베이스, AI·GPT 조회(스마트제조혁신 기술개발사업) | unknown | 염색 공정의 반복 데이터 원천과 요인을 표준화(세부 미확인) | 참여기업 중심의 비공개 구축사업으로 추정. unknown | 현장 데이터라 노이즈와 기업별 이질성이 큼. 공개 여부 불명 | 1 |
| DYETEC 섬유산업 AI 기반 탄소발자국 플랫폼(개발사업 선정) | https://www.news1.kr/local/daegu-gyeongbuk/5762054 | 미확인(검색 색인에만 존재) | 섬유 공정의 탄소발자국 산정 플랫폼(개발 중) | unknown | unknown | unknown | 기사 제목 수준의 정보만 있음 | 1 |
| 섬유 전문지식 생성형 AI 구축 및 활용 사업 (DYETEC·한국섬유개발연구원·KOTITI·아이씨엔아이티) | unknown | 미확인 | 섬유 전문지식 기반 생성형 AI 챗봇(지식 코퍼스) | unknown | unknown | unknown | 검색 요약 한 줄에만 근거가 있어 원문 링크를 특정하지 못함 | 1 |
| K-MDS 국가 소재 데이터 스테이션 (Korea Materials Data Station) | https://kmds.re.kr/en/ | 미확인(검색 색인에만 존재) | 부처·사업·연구자별로 흩어진 소재 연구데이터의 수집·공유·활용. 표준 스키마와 용어 표준화 | unknown(실적 건수 미확인). 참고로 2020년 4월 보도의 계획 수치는 '640억 투입, 연내 200만건 정보 수집'으로, 실적이 아님 | unknown. 소재 분야별 표준 스키마로 추정 | unknown(회원가입 방식으로 추정) | 국가 R&D 성과 데이터 위주라 금속·세라믹·에너지 소재 비중이 클 가능성이 있음(추정). 섬유·바이오고분자 커버리지 불명 | 1 |
| 국가소재연구데이터센터 (NCMRD) | https://www.ncmrd.re.kr/ | 미확인(검색 색인에만 존재) | 소재 연구데이터의 지속적·체계적 수집, 관리, 공유 인프라. 표준 스키마와 데이터 어휘 표준화. AI 기반 지능형 활용 | unknown | unknown | unknown | 내용을 확인하지 못함 | 1 |
| 2026 KoMaP AI 경진대회 (산업통상부·KIAT·ETRI·한국재료연구원) | https://komap.ai/front/competition2026 | 미확인 | KoMaP 축적 소재 데이터를 활용한 AI 모델 개발 대회(주제 미확인) | unknown | unknown(KIMS 공동주관이라 금속 주제 가능성 있음, 추정) | 무료. 온라인 진행, 오프라인 행사는 경기 고양. 접수 2026-09-03(목)~10-15(목) 23:59 | 이벤트 정보 출처는 개발자 행사 큐레이션 README(제3자) | 1 |
| 2025 KoMaP AI 경진대회 (세라믹: 양방향 SOFC 전극 고온성능 / 화학: 미래 모빌리티 경량복합재 조성→물성) | https://komap.ai/front/competition2025 | 미확인(검색 색인에만 존재) | 조성·공정→물성 예측용 정형 데이터(KRICT 화학, KICET 세라믹) | unknown | 화학 주제: 경량복합재 조성 → 물성(세부 미확인) | 대회 참가자에게 제공. 현재 접근 가능 여부 unknown | 대회용으로 정제된 데이터 | 1 |
| KIAT 가상공학플랫폼구축사업(소재데이터) 시행계획·RFP (2025) | https://www.kiat.or.kr/front/board/boardContentsView.do?board_id=90&MenuId=&contents_id=218ba759c4c04db58c44a94dfacb7f93 | 미확인(검색 색인에만 존재) | 사업 공고와 과제별 RFP(소재 데이터 축적, AI·데이터 기반 기업 지원, AX) | unknown(검색 요약에 '공고금액 1,740억원'이 있었으나 다른 사업 금액이 섞였을 수 있어 신뢰하지 않음) | 해당 없음(정책 문서) | 공개 공고문 | 데이터가 아니라 정책 문서 | 1 |
| 공공데이터포털 (data.go.kr) | https://www.data.go.kr/ | 미확인 | 공공기관 파일데이터와 OpenAPI(특허청 KIPO API 게이트웨이 포함) | unknown. 섬유·소재 관련 세부 데이터셋 목록을 이번 세션에서 확인하지 못함 | 데이터셋별 상이 | 회원가입 후 활용신청을 하면 인증키(ServiceKey) 발급. 라이선스는 데이터별 공공누리 유형(제3자 정리 기준) | 섬유 분야 실험 물성 데이터는 드물 것으로 추정(미확인). 기관 행정 데이터 위주 | 1 |
| AI허브 (aihub.or.kr) – 플랫폼 전체 | https://www.aihub.or.kr/ | 미확인 | AI 학습용 데이터셋(영상, 음성, 텍스트, 센서 등) | aihubshell 목록 기준 데이터셋 브리프 797개(제3자 저장소가 2026-03-17에 수집). 2024년 시점 목록(iNotePal 노트북)은 694개 | 데이터셋별 | 회원가입 후 내국인 실명인증(외국 IP·법인 불가)이 필요하고 데이터셋별로 승인. 다운로드는 aihubshell CLI. 라이선스는 데이터셋별 이용조건(일부 '공공누리(NIA)' 표기와 상업적 사용 여부는 데이터셋별 확인. 둘 다 제3자 정리) | 대부분 비전·NLP 데이터. 소재 실험 물성 데이터는 극소수 | 1 |
| AI허브 71339 실험기반 재료 물성 데이터 | https://www.aihub.or.kr/aihubdata/data/view.do?dataSetSn=71339 | 미확인 | 재료 분석 원천과 라벨 데이터(Training/Validation 분리) | 파일 14개, 알려진 총 용량 6.29 MB(aihubshell 메타데이터) | EDS, 비저항(Resistance), XRD, 두께(Thickness), 나노인덴테이션, SEM | AI허브 공통 조건(내국인 실명인증, 승인) | 용량이 매우 작음. 박막이나 무기재료로 추정되며(미확인) 고분자·섬유가 아님 | 1 |
| AI허브 71501 의류 통합 데이터(착용 이미지, 치수 및 원단 정보) | https://www.aihub.or.kr/aihubdata/data/view.do?dataSetSn=71501 | 미확인 | 의류 상품·착용 이미지와 메타데이터 | 파일 48개, 327.7 GB | 의류 카테고리, 계절, 촬영 형태, 치수, 색상, 디자인 정보, 원단 정보(혼용률 등으로 추정), 취급주의, 모델 신체치수 | AI허브 공통 조건 | 이미지 중심 데이터. 원단 정보는 라벨 수준이며 물성 측정값이 아님 | 1 |
| AI허브 71822 폐의류 재활용 분류 및 선별 데이터 | https://www.aihub.or.kr/aihubdata/data/view.do?dataSetSn=71822 | 미확인 | 폐의류 이미지와 분류 라벨(YOLO, MDETR 등) | 파일 353개, 554.2 GB | 의류 종류(블라우스, 코트, 드레스 등), 처리구분(dispose, recycle, reusable) | AI허브 공통 조건 | 이미지 분류용. 소재 성분이나 물성 측정은 없음(확인 범위 내) | 1 |
| KAMP 의류 공정최적화 AI 데이터셋 (염색 공정, 중기부·스마트제조혁신추진단) | https://www.kamp-ai.kr | 미확인 | 염색설비 PLC 시계열, CCM 색차 측정, LOT 물량(xlsx/csv) | 약 3,180만 데이터포인트, 157 MB(제3자 프로젝트 README). 공개일 2023-08-18 | 염색 가동 길이, 온도, 속도, 색차(DE) 등 11개 변수 | KAMP 이용약관(출처 표기: 중소벤처기업부, KAMP, 스마트제조혁신추진단, ㈜임픽스). 회원가입 필요로 추정 | 단일 기업의 현장 데이터. 소재와 레시피 정보는 거의 없고 공정 운전변수 중심 | 1 |
| 한국섬유공학회 (fiber.or.kr) – 대회 공지·학술대회·학회지 | https://fiber.or.kr/ | 미확인(검색 색인에만 존재) | 공지와 학술대회 초록. 학회지는 KCI로 이어짐 | 해당 없음 | 해당 없음 | 공개 웹(첨부 서식은 공지 게시글) | 데이터 플랫폼이 아님 | 1 |
| KCI 논문 「우리나라 공공데이터의 소재정보」 | https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART002510299 | 미확인(검색 색인에만 존재) | 공공데이터 속 소재정보를 분석한 논문 | unknown | unknown | KCI(원문 접근은 학술지별) | 제목만 확인함 | 1 |
| DYETEC 염색산업용 AI 에너지 최적화 플랫폼(2020) | https://newsis.com/view/?id=NISX20201113_0001232881 | 미확인(검색 색인에만 존재) | 염색 공정 빅데이터 DB와 머신러닝 기반 에너지 최적화 | unknown. 보도에 '에너지 절감 효과 약 10%' | 공정 빅데이터(세부 미확인) | 비공개로 추정. unknown | 기업 현장 데이터 | 0 |
| AI허브 51 K-Fashion 이미지 (외 패션 이미지 계열 75, 78, 71445, 71648, 71535) | https://www.aihub.or.kr/aihubdata/data/view.do?dataSetSn=51 | 미확인 | 패션 이미지와 속성 라벨 | K-Fashion 파일 10개 64.4 GB. 71445 의류 디자인 패턴 73.4 GB. 71648 의류 스케치-패턴 도면 쌍 1.39 GB. 75 의류 가상착용 3D 8.89 TB. 78 패션상품 및 착용 영상 35.7 GB | K-Fashion 소재 카테고리(패딩, 데님, 저지, 합성섬유, 니트, 린넨, 메시, 플리스, 네오프렌, 실크, 스판덱스, 면, 시폰, 우븐 등 28종) 등 시각 속성 | AI허브 공통 조건 | 시각 라벨일 뿐 물성 데이터가 아님 | 0 |
| 한국섬유개발연구원 (KTDI) | https://thevc.kr/textile | 미확인(검색 색인에만 존재) | 공개 데이터 플랫폼은 확인 못함 | unknown | unknown | unknown(공식 사이트 URL도 이번 세션에서 확인 못함. 위 링크는 제3자 기관 프로필) | 해당 없음 | 0 |
| KOTITI시험연구원 (섬유·의류 시험) | http://www.kotiti-global.com/ko/inspection/textile_clothing.do | 미확인(검색 색인에만 존재) | 시험 서비스 안내. 공개 시험결과 DB는 확인 못함 | unknown | unknown | 성적서는 의뢰자 소유로 비공개(일반 관행, 미검증) | 해당 없음 | 0 |
| FITI시험연구원 | unknown | 미확인 | 공개 데이터 확인 못함 | unknown | unknown | unknown | 이번 세션에서 실재 정보를 확보하지 못함(WebSearch 한도 소진) | 0 |
| 한국섬유소재연구원(KOTERI) / 한국섬유기계융합연구원(KOTMI) / 부산섬유소재진흥센터 | https://kotmi.re.kr/ | 미확인(검색 색인에만 존재) | 공개 데이터 플랫폼 확인 못함 | unknown | unknown | unknown | 해당 없음 | 0 |
| 한국섬유산업연합회 (KOFOTI) | unknown | 미확인 | 산업 통계로 추정. 미확인 | unknown | unknown | unknown | 이번 세션에서 확인 못함 | 0 |
| KISTI 2026 DATA·AI 분석 경진대회 (DataON 기반) | https://aida.kisti.re.kr/competition/main/overview.do | 미확인(검색 색인에만 존재) | DataON 연구데이터 기반 문제발굴·문제해결 대회 | 7회째. 문제해결 부문 접수는 11/6까지(검색 요약) | 2026 과제: 도로결빙, 녹조, 감염병, 하천수위 등. 소재 과제 없음 | 공개 대회 | 해당 없음 | 0 |

## patents/text

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| KIPRIS / KIPRIS Plus (특허청·한국특허정보원 특허 정보 및 OpenAPI) | https://plus.kipris.or.kr/portal/main/contents.do?menuNo=210180 | 미확인(검색 색인에만 존재) | 국내 특허·실용신안·디자인·상표와 해외특허(US, EP, WO, JP, CN 등 13개국) 서지·요약·청구항·IPC·인용 | 전체 건수 unknown. 제3자 README 데모에서 '인공지능' 키워드 검색 결과가 106,285건 | 발명의 명칭, 출원번호, 출원인, 등록권자, 상태, IPC, 청구항, 발명자, 요약. 해외특허는 국제공개·출원번호 | KIPRIS Plus 회원가입 후 accessKey 발급. 일부 KIPO API는 공공데이터포털 ServiceKey로 이용. 무료 한도는 제3자 정보끼리 충돌: '1,000회/월'(korean-patent-mcp README)과 '계정당 ~50,00… | 특허 실시예는 효과를 과장하는 경향과 선택적 보고 편향이 있음. 측정법이 불균일하고, 물성표가 이미지나 PDF에 묻혀 있는 경우가 많음 | 2 |
| ScienceON (KISTI 과학기술 지식인프라) + OpenAPI | https://scienceon.kisti.re.kr/ | 미확인 | 국내외 논문(SCIE, SCOPUS, 국내 과학기술논문), 특허, 국가 R&D·기술동향 보고서, 연구자·기관 정보, 기술트렌드 | unknown(README에 '논문 데이터 99.7% 포함'이라는 정성 문구만 있음) | DOI, 소속, 발행기관, ISSN, 키워드, 초록 전문, 원문 URL. 특허 출원·공개·등록번호, IPC, 인용. 보고서 주관·공동연구기관, 표준분류, 초록 | 회원가입 후 API Key, Client ID, MAC 주소를 한 세트로 발급받으면 17개 API를 모두 쓸 수 있음. 저작권은 문헌별. 라이선스 unknown | 메타데이터와 초록 중심이라 본문 물성표는 원문을 따로 받아야 함. 국내 문헌 커버리지는 높음 | 2 |
| KCI 한국학술지인용색인 (한국섬유공학회지 등 국내 학술지) | https://www.kci.go.kr/kciportal/po/search/poCitaView.kci?sereId=000008 | 미확인(검색 색인에만 존재) | 국내 학술지 논문 메타데이터, 인용, 학회·학술지 정보. 원문 PDF 제공 여부는 학술지별 | unknown | 서지정보, 초록, 키워드, 인용관계, 학술지·학회 정보 | REST OpenAPI는 키 발급 필요. OAI-PMH는 공식 설명상 키 불필요. 데이터셋 배포도 있음. 원문 권리는 논문별 | 메타데이터 중심. 국문 논문은 단위와 시험법 표기가 다양해 harmonization이 필요함 | 2 |
| AI허브 71739 국가중점기술 대응 특허 데이터 / 71531 과학기술표준분류 대응 특허 데이터 (외 113 특허 지식베이스, 547 특허 분야 자동분류) | https://www.aihub.or.kr/aihubdata/data/view.do?aihubDataSe=data&dataSetSn=71739 | 미확인 | 특허 명칭, 요약, 청구항 텍스트와 기술분류 라벨 | 71739: 619,844건(제3자 조사 문서), 파일 481개, 948 MB. 71531: 파일 752개, 415.1 MB. 113: 2.29 GB. 547: 280 MB(aihubshell 메타) | 국가중점기술 대·중·소분류(소재 등 10개 대분류), 과학기술표준분류(EB 재료 계열, 예: EB02 세라믹재료) | AI허브 공통 조건. 71739 라이선스는 '공공누리(NIA)'로 제3자가 표기 | 분류 라벨이 자동 또는 반자동 부여일 가능성. 출처는 KIPRIS DB | 1 |
| AI허브 71845 학술논문 이해 데이터 / 71565 표 정보 질의응답 / 71532·71533·90 기술과학 요약·기계독해 | https://www.aihub.or.kr/aihubdata/data/view.do?dataSetSn=71845 | 미확인 | 한국어 학술논문 이해·QA, 표 질의응답, 기술과학 요약과 기계독해 말뭉치 | 71845: 파일 12개 23.5 GB(과학기술 ST 포함). 71565: 216 MB. 71532: 305.7 MB. 71533: 91.6 MB. 90: 1.44 GB | 논문 원문, 질의응답 라벨, 표, 요약 | AI허브 공통 조건 | 범용 과학기술 텍스트라 섬유·고분자 비중은 unknown | 1 |

## generic repository

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| DataON 국가연구데이터플랫폼 (KISTI) | https://dataon.kisti.re.kr/ | 미확인(검색 색인에만 존재) | 국내외 연구데이터 메타데이터, DOI, 포맷, 권리정보. 외부 리포지토리 메타데이터 통합 | unknown | 제목, 작성자, svcId, 포맷, 라이선스, DOI | 웹 검색은 공개. OpenAPI 신규 신청과 연장은 2026년 3월부터 기관사용자만 가능하고, 검색 API와 상세조회 API 키를 따로 발급. 공식 MCP가 있음(Bearer Token). 레코드별 라이선스 | DataON이 모든 파일을 직접 보유하지는 않음. kisti-mcp README는 'OpenAPI 점검·이용제한 상태'라고 기록 | 1 |

## biopolymer/solvent

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| AI허브 71816 화학물질 위험성 예측 데이터 (외 71642 화학물질 유전독성 유해성 예측) | https://www.aihub.or.kr/aihubdata/data/view.do?dataSetSn=71816 | 미확인 | 화학물질 구조와 물성·위험성 라벨 | 71816: 파일 12개, 281 MB. 71642: 파일 5개, 1.16 GB | 증기압, 연소열, 인화점(71816), 유전독성(71642) | AI허브 공통 조건 | 일반 화학물질 위주. DES 구성성분이나 이온성 액체 포함 여부는 unknown | 1 |

## Korean competition (민간 플랫폼)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 데이콘 합성 미세구조 기반 재료 물성 예측 AI 경진대회 (2026) | https://daker.ai/public/hackathons/synthetic-microstructure-property-prediction-ai | 미확인 | 합성 미세구조 이미지 → 재료 물성(세부 미확인) | unknown | unknown | 무료, 온라인. 접수 2026-09-29 10:00 ~ 10-19 10:00 | 합성(시뮬레이션) 데이터 | 1 |

## GitHub dataset/tool

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| kisti-mcp (ScienceON·NTIS·DataON OpenAPI 통합 MCP 서버) | https://github.com/ansua79/kisti-mcp | 접속 확인 | API 래퍼(MCP 서버) 32종 도구 | ScienceON 17종, NTIS 13종, DataON 2종(v0.3.32.2, 2026-06-23) | 논문·특허·보고서 검색, 상세, 인용. 국가R&D 과제, 성과, 보고서. 연구데이터 메타 | PyPI에서 'uvx kisti-mcp'로 실행. 각 플랫폼 API 키는 이용자가 따로 발급. 저장소 라이선스는 미확인 | 제3자 도구. DataON API는 이용제한 상태라고 표기 | 2 |
| KIPRIS Plus 접근 도구 (nuri428/kipris_skill, nuri428/mcp_kipris, chrisryugj/korean-patent-mcp) | https://github.com/nuri428/kipris_skill | 접속 확인 | KIPRIS Plus OpenAPI 래퍼(Claude Code skill, MCP 서버) | 49개 서비스, 540개 오퍼레이션 문서화(kipris_skill README). korean-patent-mcp는 7개 도구 | 자유검색, 항목검색, 출원인·권리자 검색, 서지상세(청구항, IPC), 해외특허 13개국 | kipris_skill은 MIT 배지. API 키는 KIPRIS Plus 무료 회원가입으로 발급. mcp_kipris는 분당 60건 자체 제한. korean-patent-mcp는 무료 한도 1,000회/월로 기술 | 제3자 도구. README 간 한도 수치가 서로 다름 | 2 |
| aihub-korea-metadata-scout (AI허브 전 데이터셋 메타데이터 카탈로그) | https://github.com/YoungseokOh/aihub-korea-metadata-scout | 접속 확인 | 공식 aihubshell의 목록·파일트리 메타데이터만으로 만든 데이터셋별 Markdown 브리프와 카탈로그(다운로드 없음) | 브리프 797개. 카탈로그 생성 2026-03-17 | 데이터셋 키, 파일 수, 총 용량, 대표 파일 경로, 추정 태그 | 공개 저장소(라이선스 미확인). 실제 데이터는 AI허브 조건을 따름 | 메타데이터 기반이라 내용 품질은 판단하지 않음. 2026-03-17 이후 신규 데이터셋은 빠져 있음 | 1 |

**이 조사 블록에서 확인된 데이터 공백**

- DYETEC 플랫폼(ai.dyetec.or.kr, KoMaP 섬유, VEPOTEX)의 데이터셋 목록과 건수, 대학(원)생 개인의 열람·다운로드 가능 여부, 라이선스를 어느 공개 문서에서도 찾지 못했다. 공고문상 지원 대상은 기업(사업자등록증)이며, 기술지원에 쓰인 데이터의 일부를 플랫폼에 제공하는 데 동의해야 한다.
- 이번 대회에서 DYETEC이 참가자에게 소재데이터를 제공하는지, 공개 문헌 데이터만으로 제안해도 되는지는 미확인이다. 공지 첨부 서식은 fiber.or.kr이 EGRESS_BLOCKED라 열지 못했다.
- 국내 공개 전기방사 데이터는 확인 범위에서 0건이다. 공정(전압·거리·유량·습도·용액 점도·전도도)→섬유경·형태·물성 정형 데이터가 없다. KoMaP의 방사 서비스는 '용융방사'뿐이다.
- 케라틴, PVA/PVAc, 셀룰로오스 유도체 등 바이오 고분자 섬유와 필름의 국내 공개 정형 데이터는 확인 못했다. DYETEC MDF 예시에 등장하는 바이오 계열은 PLA 방사와 Bio-PET뿐이다.
- 비대칭(일방향) 수분이동막과 투습·방수막 시험 데이터(KS K, ISO 11092, JIS L 1099, ASTM E96 등 시험법별 투습도·내수압·일방향 전달지수)를 모은 국내 공개 DB는 없다. 시험기관(FITI, KOTITI, KTDI) 성적서는 비공개로 보이며 공식 확인은 못했다. 따라서 시험법이 다른 값을 맞추는 harmonization(seed b)은 문헌 추출에 의존해야 한다.
- DES와 이온성 액체 용매 물성(점도, 극성, Kamlet-Taft, 고분자 용해도)의 국내 공개 DB는 확인 못했다. AI허브 화학물질 위험성 데이터는 일반 화학물질의 증기압, 연소열, 인화점 수준이다.
- 공공데이터포털(data.go.kr)의 섬유·소재 관련 세부 데이터셋 목록은 확인 불가였다. 포털이 EGRESS_BLOCKED이고 WebSearch 한도가 소진되었다.
- KRICT 화학소재 데이터 플랫폼과 '화학소재정보은행'의 정확한 명칭·URL·내용은 검증하지 못했다. KRICT 데이터로 확인된 것은 2025 KoMaP 화학(경량복합재 조성→물성) 대회 주관 사실뿐이다.
- 'KISTI 소재데이터'라는 별도 플랫폼은 확인 못했다. 확인된 KISTI 자산은 ScienceON, NTIS, DataON이다. K-MDS와 NCMRD의 운영 주체·보유 건수·접근 조건도 미확인이다(K-MDS 오픈 공지는 KIMS dmi 게시판에서 색인됨).
- KITECH의 섬유 관련 DB, 한국섬유산업연합회 통계 DB, FITI와 KTDI의 공식 데이터 서비스는 이번 세션에서 존재 자체를 검증하지 못했다.
- KoMaP의 '14만8,702건'과 'MDF 311,830건'은 기사·검색 요약 수치다. 이 중 섬유 데이터 비중, 갱신 시점, 외부 다운로드 가능 여부는 unknown이다.
- AI허브 데이터셋 목록은 2026-03-17 제3자 수집본 기준이다. 그 이후 공개된 섬유·소재 데이터셋은 반영되지 않았을 수 있다.
- 이번 에이전트 차례에서 WebSearch는 한 번도 실행되지 않았다. 세션 공유 한도 200회가 이미 소진된 상태였다. search_index 등급은 같은 세션의 다른 에이전트가 앞서 실행한 WebSearch 결과에 근거한다. 추가 검색이 필요하면 사용자가 후속 메시지를 보내거나 CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION을 늘려야 한다.

## patents / Korean public

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| KIPRIS Plus Open API (키프리스플러스, 지식재산처) | https://plus.kipris.or.kr | 미확인 | REST API(XML/JSON)와 일부 BULK 제공. 국내 특허·실용 공개/등록공보 서지·초록·청구항, 행정처리·청구항 변동 이력, 인용·패밀리, 해외특허(US/EP/WO/JP/CN 등) 검색, '특허 합금조성… | 레코드 건수 unknown. 서드파티 문서 기준 49개 서비스·540개 오퍼레이션(nuri428/kipris_skill), 다른 서드파티 목록은 API 50건(2026-05-27 수집) | 출원/공개/등록번호, 발명의 명칭, 초록, 청구항, IPC/CPC, 출원인/권리자, 법적상태, 인용, 패밀리, 합금조성비(금속만 구조화) | 회원가입 후 서비스별로 신청하고 API 키를 받아야 함. 서드파티 문서 기준 무료 가입자는 월 1,000회 호출이고 초과분은 유료 플랜. 텍스트마이닝·재배포 조건은 공식 약관을 확인하지 못함(사이트 EGRESS 차단) | 서지 중심. 실시예 표(조성·공정조건·물성)는 구조화 필드가 없고, 구조화된 조성 데이터는 합금뿐임. 전문 본문 접근 형식(XML 또는 이미지)은 미확인. 무료 호출량이 대량 추출의 병목. 서드파티 목록(ojc1234)은 문자 깨짐·오기가 있어 공식 포털에서 재확인 필요. 특허 수치는 권리범위 확보용 범위 표기와 최적 실시예 위주(출판편향과 같은 양의 편… | 2 |

## patents

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Google Patents Public Datasets on BigQuery | https://github.com/google/patents-public-data | 접속 확인 | BigQuery SQL 테이블: patents.publications(전세계 서지와 US 전문), google_patents_research.publications, patentsview.*, uspto_oce_*… | patents.publications 98,176,830행·899.4GB(repo 문서의 'Last updated 2018-11-26' 기준, 현재 규모는 미확인). marec.publications는 1976~2008.6의 EP·WO·US·JP 1,900만 건 이상 | publication_number, application_number, country_code, title/abstract/claims/description(localized), CPC/IPC, assignee, inventor, citation, family_id, priority/… | 'Google Patents Public Data' by IFI CLAIMS Patent Services and Google, CC BY 4.0(repo 표 문서 인용). MAREC은 CC BY 4.0. BigQuery를 쓰려면 GCP 계정과 과금 … | 전문은 US 위주이고 KR·JP 섬유특허 본문 커버는 약함. 실시예 표가 이미지이거나 OCR 오류가 있음. 단위·시험법이 특허마다 제각각임(예: 투습도 g/m²·24h 대 g/m²·h). 권리범위용 넓은 수치 범위 기재 | 2 |
| USPTO Open Data Portal(ODP) / Bulk Data | https://data.uspto.gov | 미확인 | REST API(ODP, X-API-KEY) + Bulk Data products(grant/pgpub XML 전문), Office Action 텍스트·거절이유·인용, Enriched Citations, PTAB | unknown(참고: HUPD는 BDSS XML로 2004~2018 출원 4,518,263건을 구축) | 청구항, 상세설명, 초록, CPC, 출원·등록일, 심사이력(office action), 인용 | ODP 키가 필요한 엔드포인트가 다수. HUPD 논문 인용: 'Per the USPTO's Electronic Information Products Division's Terms and Conditions, bulk data products are … | US 출원만. XML 버전별 스키마가 달라 파싱 부담이 큼. 표·화학식 일부가 이미지 | 2 |
| PatentsView (bulk download tables + PatentSearch API) | https://github.com/PatentsView/PatentsView-Code-Examples | 접속 확인 | USPTO 데이터 기반 정제 테이블(TSV)과 PatentSearch API. 발명자·출원인 disambiguation, 위치, CPC, claim·brief summary text(BigQuery 미러) | BigQuery 미러 patentsview.patent 6,366,664행(문서 기준 2017-10-13). 현행 규모 unknown | patent_id, 날짜, 발명자/양수인(정규화 ID), 위치, CPC/USPC, 청구항, 요약문 | CC BY 4.0(BigQuery 문서 인용). PatentSearch API는 키 필요 여부를 미확인 | US 등록특허 한정. 텍스트보다 서지·네트워크 분석에 강함 | 1 |
| EPO Open Patent Services (OPS) | https://github.com/ip-tools/python-epo-ops-client | 접속 확인 | REST(XML/JSON): published-data(biblio 등), published-data/search(CQL), family(INPADOC), legal, register, images, number-… | unknown | 서지, 패밀리, 법적상태, 등록부, 도면 이미지(전문 description/claims 제공 범위는 미확인) | key/secret 등록 필요. 시간당·주간 할당량 존재(클라이언트 예외 IndividualQuotaPerHourExceeded, RegisteredQuotaPerWeekExceeded). 구체 수치·약관은 미확인 | 패밀리·법적상태 정규화에 강함. 대량 전문 수집에는 할당량 병목 | 1 |
| WIPO PATENTSCOPE | https://patentscope.wipo.int | 미확인 | PCT 공개 및 각국 특허 검색(전문 포함 여부·API 조건 미확인) | unknown | unknown(이 세션에서 미확인) | unknown | 이 세션에서 내용을 전혀 확인하지 못함(curl 차단, WebSearch 예산 소진) | 1 |

## patents/text

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| SureChEMBL (BigQuery 미러: patents-public-data.ebi_surechembl) | https://github.com/google/patents-public-data/blob/master/tables/dataset_European%20Bioinformatics%20Institute.md | 접속 확인 | 특허 전문·이미지·첨부에서 자동 추출한 화합물과 특허 간 매핑 테이블 | ebi_surechembl.map 278,559,964행·37.3GB(Last updated 2018-11-01) | schembl_id, 특허 publication_number, 출현 위치(필드), 화합물 구조 식별자 | 'SureChEMBL' by EMBL-EBI, CC BY-SA 3.0(BigQuery 문서 인용) | 소분자 중심이고 고분자 반복단위·블렌드·복합재는 사실상 표현되지 않음. 자동 추출이라 노이즈 큼. 2018년 스냅샷 | 1 |
| 특허 표 스크래핑 사례: oxide glass 조성–물성(Google Patents HTML 표) | https://arxiv.org/abs/2511.16366 | 미확인 | Google Patents HTML의 실시예 표를 Selenium과 정규식으로 추출한 조성–물성 데이터셋(방법론 선례) | 9,432 조성(액상선온도 5,696, 굴절률 4,298, Abbe수 1,771) | 산화물 조성(mol%/wt%), Tliq, nD, νd, patent_id, 단위 라벨 | 코드 repo(thiagorr162/glass_patents)는 '출판 후 공개'로 현재 비공개(git ls-remote 실패). 데이터 라이선스 unknown | HTML 표만 대상(스캔 PDF·이미지 표 누락). 조성 합 100±0.5 필터. 기존 DB(SciGlass+INTERGLAD) 대비 신규 기여는 4.9~10.4% | 1 |
| Open Reaction Database: USPTO grants 반응 데이터(Lowe 유래) | https://github.com/open-reaction-database/ord-data | 접속 확인 | 특허에서 텍스트마이닝한 유기반응(Protobuf/Parquet) | uspto-grants 월별 데이터셋 489개, 약 180만 반응(1.1GB) | 반응물, 생성물, 조건(용매·온도 일부), 수율, 특허 출처(provenance.patent) | 데이터 CC-BY-SA-4.0, 코드 Apache-2.0 | 소분자 유기합성 중심이고 고분자 공정·섬유 가공은 거의 없음. 부산물·화학양론 누락(CompleteRXN 논문이 지적) | 0 |

## patents / generic repository

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| The Lens (Lens.org) Scholarly & Patent API | https://docs.api.lens.org/ | 미확인 | 학술문헌과 특허를 함께 다루는 REST API(Elasticsearch DSL, cursor pagination, field projection, patent family grouping), bearer token… | unknown | 특허 서지·청구항·인용, 학술문헌 메타, 특허→논문 인용(NPL) 연결 | Lens 프로필에서 발급하는 토큰 필요. 무료·유료 범위와 승인 조건은 미확인 | 서드파티 프로필로만 확인했고 공식 문서는 열지 못함 | 1 |

## patents / text corpus

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| HUPD (Harvard USPTO Patent Dataset) | https://github.com/suzgunmirac/hupd | 접속 확인 | USPTO 실용특허 출원 원문(JSON), 34개 필드와 메타데이터 CSV | 4,518,263건(2004~2018 출원) | title, abstract, claims, background, summary, description, IPC/CPC, 심사관, 출원·공개일, 결정(accepted/rejected/pending) | CC BY 4.0(README 'Licensing and Contact'). HuggingFace HUPD/hupd로 배포(HF는 차단되어 미확인) | US·영어 한정. 도면·이미지 표 제거. 2018년 이후 없음. 출원 시점 원문이라 등록본과 차이 있음 | 1 |
| BIGPATENT | https://arxiv.org/abs/1906.03741 | 미확인 | US 특허 description→abstract 요약 데이터셋 | 1,341,362건(1971~2018). HUPD 논문 Table 1 기준 | description, abstract, CPC 섹션 | unknown(이 세션에서 미확인) | 요약 과제용. 물성·조성 구조 없음. Google Patents Public Datasets에서 파생 | 0 |

## OA literature corpus

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| PMC Open Access Subset / PMC Article Datasets on AWS | https://s3.amazonaws.com/pmc-oa-opendata | 접속 확인 | 논문 버전별 JATS XML, 평문 txt, JSON 메타, (허용 시) PDF·그림·보충자료 | 약 800만 article version(README 'roughly 8 million PMC article versions') | pmcid, pmid, doi, title, citation, is_pmc_openaccess, is_manuscript, is_retracted, license_code(CC 코드 또는 'TDM'), xml/txt/pdf/media URL | 익명 S3 접근. 논문별 license_code. 'TDM' 코드는 author manuscript로 텍스트마이닝은 허용되나 재배포는 제한. NLM 출처 표기 의무, 재배포 시 재배포 허용 라이선스만 가능 | 생의학 저널 편향이 강해 일반 고분자 가공 저널은 거의 없음. 대신 전기방사 스캐폴드, 상처드레싱, 케라틴·젤라틴 바이오소재, 약물전달 섬유가 많음. 성공 결과 위주 | 2 |
| Europe PMC (REST API, OA full text, FTP) | https://europepmc.org | 미확인 | 검색 API, OA 전문 JATS XML, FTP 대량 PDF. 프리프린트 포함 | unknown | 메타, 초록, OA 전문(섹션·표·그림 캡션), 라이선스 | OA 전문은 논문별 라이선스를 따름. Annotations API 제공 여부와 약관은 이 세션에서 미확인 | 생명과학 편향(PMC와 상당 부분 중복) | 2 |
| S2ORC / Semantic Scholar Datasets API | https://github.com/allenai/s2orc | 접속 확인 | 파싱된 논문 전문(JSON: 섹션, 인용 링크), S2AG 메타·초록. 현재는 S2 API 'Bulk Dataset'으로 배포 | peS2o README 인용: S2ORC 비필터 1,130만 편·469억 단어(2023-01-03), S2AG 9,110만 편. 구버전 S2ORC 2020은 전문 1,200만 | title, abstract, body_text(섹션), bib_entries, 인용 링크, 분야 | ODC-By 1.0(README). 대량 다운로드는 API 키 필요. 개별 원문 저작권은 별도 | PDF 파싱(GROBID) 오류로 표·수식이 손상됨. 분야 커버는 S2 크롤 편향(CS·생의학 강세) | 2 |
| arXiv bulk data (S3 requester-pays + Kaggle/GCS arxiv-dataset) | https://storage.googleapis.com/arxiv-dataset | 접속 확인 | 전체 PDF(카테고리별), OAI 메타데이터 JSON, (S3) 원본 tar | metadata-v5/arxiv-metadata-oai.json 4.5GB(2020-08-19). LeMat-Synth 논문은 1992~2025 arXiv 200만 편을 처리했다고 기술 | arXiv id, 제목, 초록, 저자, 카테고리, 버전, PDF 전문 | GCS는 익명 접근 가능. s3://arxiv는 Requester Pays(익명 거부). 논문별 라이선스는 arXiv 기본 비독점 라이선스 또는 CC로 혼재하며 재배포 가능 범위가 다름 | cond-mat·물리 편향. 고분자 가공·섬유 실험 논문은 매우 적음. 동료심사 전 원고 | 1 |
| ChemRxiv Public API (Cambridge Engage) | https://chemrxiv.org/engage/chemrxiv/public-api/v1/ | 미확인 | 프리프린트 메타·초록·PDF 링크 API | paperscraper README 기준 전체 덤프 '+50K papers'. LeMat-Synth(2025~2026)는 'all 30K papers'를 수집했다고 기술(시점 차이) | DOI, 제목, 초록, 저자, 카테고리, 라이선스명, PDF URL | 항목별 라이선스 필드(CC-BY 등) 존재. 이용약관 URL(chemrxiv.org/engage/assets/public/chemrxiv/term/terms-of-use.htm)은 코드에서만 확인 | 화학·재료 프리프린트로 고분자 화학 일부 포함. 규모가 작고 심사 전 원고 | 1 |
| peS2o (AllenAI) | https://github.com/allenai/peS2o | 접속 확인 | LM 사전학습용으로 정제한 학술 텍스트(S2ORC 전문 + S2AG 초록) | v2: 3,897만 문서·420.1억 토큰. v1: 6,756만 문서·473.7억 토큰 | text, 출처, 연도, 분야 | ODC-By(README 인용 표기) | 표·수치 맥락을 정제 과정에서 상당 부분 제거. 물성 추출용으로는 부적합 | 1 |
| CORE (core.ac.uk) API v3 | https://core.ac.uk | 미확인 | 기관 리포지터리·OA 저널 집계 검색 API(메타와 일부 전문) | unknown | 메타, 초록, 전문 링크·텍스트(가용 시), 유형(research/thesis) | API 키 필요(서드파티 README 기준). 데이터 약관은 미확인 | 리포지터리 품질 편차가 크고 중복이 많음. 학위논문(실패 실험 포함 가능)이 섞여 있는 것은 장점 | 1 |
| unarXive | https://github.com/IllDepence/unarXive | 접속 확인 | arXiv 전문 구조화(JSONL), 인용 링크(OpenAlex 연계) | 전문 190만 편, 참고문헌 6,300만, 그림 캡션 900만, 표 캡션 200만 | 섹션 텍스트, 인용 마커, 캡션, 수식(LaTeX) | Zenodo에 전체판과 permissively licensed subset을 따로 배포(라이선스 세부는 미확인) | arXiv 편향(물리·CS) | 0 |

## OA literature corpus / metadata

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| OpenAlex snapshot | https://s3.amazonaws.com/openalex | 접속 확인 | 전 학술 그래프 스냅샷(JSONL/Parquet): works, authors, institutions, sources, topics, funders, awards, licenses | 2026-09-23 스냅샷 works 476,196,327건, 전체 레코드 626,069,032건(manifest.json) | DOI, 제목, 초록(inverted index), 주제·키워드, OA 상태·라이선스, 인용, 저자·기관, 펀더, has_content(PDF/GROBID 파싱 여부) | CC0(LICENSE.txt). 분기별 공개 | 전문은 없음(초록과 메타). 초록 누락·저자 병합 오류가 릴리스 노트에서 반복 수정되고 있음 | 2 |

## OA literature corpus / license metadata

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Unpaywall (데이터 스냅샷 및 API) | https://s3-us-west-2.amazonaws.com/unpaywall-data-snapshots | 접속 확인 | DOI별 OA 위치·라이선스·버전 JSONL 스냅샷 | 공개 스냅샷 19개, 최신 unpaywall_snapshot_2024-11-27. 2018년 파일은 약 16~18GB. 레코드 수 unknown | doi, is_oa, oa_status, best_oa_location(url, license, version, host_type) | 공개 S3 스냅샷(익명 listing 가능). 현행 API·스냅샷 약관은 미확인 | OA 위치 오탐과 라이선스 미기재가 있음. 2024-11 이후 공개 스냅샷 없음 | 2 |
| Crossref REST API (license·TDM 링크 필터) | https://github.com/CrossRef/rest-api-doc | 접속 확인 | DOI 메타데이터 API. 출판사가 제공한 license_ref와 full-text 링크(intended application: text-mining) | unknown(이 세션에서 미확인) | DOI, 제목, 저널, license.url, license.delay, link(content-type, intended-application), funder | 문서는 CC BY 4.0. 메타데이터 라이선스 조항이 별도 존재. 필터: has-license, license.url, has-full-text, full-text.application=text-mining | 출판사가 제출한 메타에 의존해 라이선스·TDM 링크 누락이 흔함 | 2 |

## OA literature corpus / publisher TDM

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 출판사 TDM API(Elsevier, Springer Nature, Wiley, ACS, RSC 등) 기반 기관 코퍼스 | https://dev.elsevier.com | 미확인 | 구독 기관이 TDM 계약으로 받는 전문 XML/HTML | 선례: Shetty 2023은 7개 출판사에서 약 240만 편, Gupta 2026(PHA RAG)은 약 300만 문서(~2025)를 확보 | 전문(본문·표·캡션) | 기관 구독과 출판사별 TDM 약관을 따름. 추출한 사실 데이터는 공개 가능하나 원문 재배포는 불가(일반적 관행이며 약관은 개별 확인 필요) | 고분자 주류 저널(Polymer, Carbohydrate Polymers, J. Membrane Sci., ACS) 커버가 가장 좋음. 구독 범위에 따라 편향 | 2 |

## Korean public

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| KISTI ScienceON OpenAPI | https://scienceon.kisti.re.kr | 미확인 | 국내외 논문(ARTI)·보고서(REPORT)·동향(ATT)·연구자·연구기관 서지·초록 API | unknown | 제어번호(CN), 제목, 초록, 저자, 기관, 연도, 보고서 서지 | API Gateway 인증키·Client ID 발급, MAC 주소와 공인 IP 등록 필요. 계정 구독 범위에 따라 제공 티켓이 다름. 재배포·마이닝 약관은 미확인 | 메타·초록 중심이고 원문 전문 대량 제공 여부는 미확인. 국문 보고서는 수치 표가 PDF 이미지인 경우가 많을 것으로 예상됨(미검증) | 2 |
| NTIS 국가과학기술지식정보서비스(국가R&D 과제·성과·보고서) | https://www.ntis.go.kr | 미확인 | 국가R&D 과제·성과(논문·특허)·최종보고서 메타(원문 제공 범위는 미확인) | unknown | unknown(이 세션에서 미확인) | unknown | 이 세션에서 접근·확인 불가(curl 000, WebSearch 예산 소진) | 2 |
| KCI 한국학술지인용색인 | https://www.kci.go.kr | 미확인 | 국내 학술지 논문 메타·초록(한국섬유공학회지 등 포함 예상, 미검증) | unknown | unknown | unknown | 이 세션에서 확인 불가 | 1 |

## text

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Polymer Scholar (Shetty et al., npj Comput Mater 9, 52, 2023) | https://polymerscholar.org | 미확인 | 초록 기반 NER(MaterialsBERT)과 휴리스틱 관계 결합으로 만든 고분자 물성 레코드. 웹 검색 인터페이스 | 약 30만 물성 레코드(약 13만 초록). 240만 편 코퍼스 중 고분자 관련 초록은 약 65만 | POLYMER, POLYMER_CLASS, MONOMER, ORGANIC, INORGANIC, MATERIAL_AMOUNT, PROPERTY_NAME, PROPERTY_VALUE(최빈 단위로 변환). 물성별 레코드 예: Tg 6,155, 인장강도 4,382, 신율 1,499, wate… | 웹 탐색 제공. 대량 다운로드와 라이선스는 미확인. 코드·데이터 repo는 '학술 비상업 전용'(GTRC 라이선스) | 초록만 사용해 측정 조건·시험법이 없음(논문 스스로 한계로 명시). 물질–값 연결은 '같은 문장의 가장 가까운 물질' 휴리스틱. 정규화하지 않은 고분자명이 남아 있고 SMILES는 수동 변환 필요. 초록에 보고된 '최고값' 편향. NER F1은 POLYMER 79.6, ORGANIC 26.2 | 2 |
| MaterialsBERT + PolymerAbstracts 주석 데이터(Ramprasad-Group/polymer_information_extraction) | https://github.com/Ramprasad-Group/polymer_information_extraction | 접속 확인 | 고분자 초록 NER 주석(JSONL: words, ner)과 추출 파이프라인 코드. 모델은 HF pranav-s/MaterialsBERT, pranav-s/PolymerNER | repo 기준 train 652, dev 38, test 75 = 765 레코드(논문은 750 초록). MaterialsBERT는 재료 초록 240만 편으로 추가학습 | 8개 엔티티(POLYMER, POLYMER_CLASS, PROPERTY_VALUE, PROPERTY_NAME, MONOMER, ORGANIC, INORGANIC, MATERIAL_AMOUNT) | 'academic non-commercial use only'(README), Georgia Tech Research Corp. GENERAL PUBLIC USE LICENSE | 초록 단위. 'poly' 문자열 필터로 선정. 예시에 sericin/PVA 투과증발막 초록이 포함되어 있어 도메인 관련성은 있음 | 2 |
| Gupta et al., 'Data extraction from polymer literature using large language models' (Comm… | unknown (DOI 미확인; Commun. Mater. 5, 269 (2024)) | 미확인 | 전문 기반 LLM 추출 고분자 물성 레코드(NER 필터와 GPT-3.5/LlaMa 계열 조합으로 알려짐) | 2차 문헌 인용 기준 '681,000편에서 106,000+ 고분자에 대한 100만+ 물성 레코드'. 원문은 미확인 | unknown(원문 미확인). 고분자명, 물성명, 값, 단위로 추정 | unknown. Polymer Scholar로 제공된다는 언급이 있으나 원문 미확인 | 출판사 TDM 코퍼스 기반이라 원문 재배포 불가. LLM 환각·단위 오류 가능성. 정확도 수치는 원문 미확인 | 2 |
| PolyLM 코퍼스(Liu et al., arXiv 2605.08255, 2026) | https://arxiv.org/abs/2605.08255 | 미확인 | 전문에서 LLM으로 추출한 '시료 설명 + 합성·공정 서술 + 물성값' 자연어 레코드 | 약 18.5만 편, 고유 고분자 시료 약 27.64만, 22개 물성, 테스트셋 68,283 관측 | Tg, Tm, Tc, Td5, Td onset, 인장강도, 영률, 신율, 굴곡강도·탄성률, 압축·충격·항복강도, 전기·열전도도, 유전상수, 밀도, Mn, Mw, Đ, 결정화도, 점도. 입력은 [Sample]·[Synthesis] 텍스트 | 공개 여부 unknown(확인한 본문에서 데이터·코드 공개 문구를 찾지 못함) | 추출 감사 n=120: strict record precision 0.842, 단위 0.942. 출처 shard·출판사 구성이 불명확. 전기전도도·점도는 성능 낮음(로그 R² 0.57~0.70) | 2 |
| MatViX (Polymer Nanocomposites + Polymer Biodegradation 멀티모달 추출 벤치마크) | https://github.com/ghazalkhalighinejad/matvix | 접속 확인 | 전문(텍스트·표·그림)에서 전문가가 만든 계층형 JSON과 곡선 데이터(PlotDigitizer) | 324편(PNC 231, PBD 93), JSON 1,688, 샘플 PNC 1,396·PBD 292 | PBD: Polymer Type, Substitution Type, Degree of Substitution, Comonomer Type, Degree of Hydrolysis, Molecular Weight, Biodegradation Test Type, 생분해 곡선(x,y). PN… | 웹사이트는 CC BY-SA 4.0. 데이터셋 라이선스는 별도 확인 필요 | PNC는 NanoMine 유래(엑셀 템플릿 편차). 곡선 추출 난도가 높아 최고 VLM도 PNC CAS 약 6.6. 단위를 평가에 반영하지 않음 | 2 |
| PolyIE (Cheung et al., NAACL 2024) | https://github.com/jerry3027/PolyIE | 접속 확인 | 전문 146편에 전문가가 단 NER과 가변길이 N-ary 관계 주석(Doccano JSONL) | 146편(PSC 100, ROP 21, Li배터리 20, 고분자막 5), 엔티티 언급 41,635, 관계 4,443 | Material, Property, Value, Condition과 <Material, Property, Value, Condition> 튜플 | repo Apache-2.0(원문 텍스트 일부를 포함하므로 저작권 해석에 주의) | 태양전지 편향(100/146). 막은 5편뿐. 텍스트만(표·그림 제외). Condition 엔티티 1.7%로 희소 | 1 |
| Polymer Literature Scholar: PHA 코퍼스·지식그래프(Gupta et al., arXiv 2602.16650) | https://arxiv.org/abs/2602.16650 | 미확인 | PHA(폴리하이드록시알카노에이트) 전문 문단 임베딩과 LLM 추출 지식그래프 튜플 | PHA 논문 1,028편, 문단 44,609, GPT-4o-mini 튜플 390,864(Llama-3.1-70B 311,475), 정규화 엔티티 36,757 | <주어, 관계, 목적어> 튜플(예: PHB–has property–Tg), 문단 출처 | unknown(원 코퍼스는 출판사 TDM 약 300만 문서에서 필터. 재배포 불가로 추정) | 수치 레코드보다 관계 튜플 중심. 표·그림은 미포함(후속 논문 2609.34051에서 한계로 명시) | 1 |
| CDE 기반 자동생성 DB군: Stress–strain(Kumar & Cole, Sci Data 2024), Battery(Huang & Cole 2020), … | https://github.com/gh-PankajKumar/chemdataextractorv2.3-stresseng | 접속 확인 | CDE로 자동 생성한 물성 DB(코드는 GitHub, 데이터는 주로 figshare/Zenodo·저널 SI에 있다고 알려짐, 이 세션에서 미확인) | unknown(각 DB의 레코드 수를 이 세션에서 확인하지 못함) | Stress-strain: 항복강도, 인장강도, 영률, 연신 등 기계물성 + 재료명 + DOI 메타. Battery: 용량, 전압, 쿨롱효율, 전도도 | battery 코드 MIT. 데이터 라이선스는 미확인 | Elsevier·Springer Nature 스크래핑 코퍼스 기반. 금속·무기 편향이고 고분자 섬유는 매우 적을 것으로 예상(미검증) | 1 |
| Text-mined synthesis recipes (Ceder group: solid-state, sol-gel, solution, AuNP) | https://github.com/CederGroupHub/text-mined-synthesis_public | 접속 확인 | 합성 문단을 '코드화된 레시피'(목표물, 전구체, 단계, 조건, 반응식)로 변환한 데이터 | 2020-07-13 버전: 고상반응 31,782건 + sol-gel 9,518건(초기 공개 30,031건, 문단 95,283) | target, precursors, operations(가열·혼합 등)와 온도·시간·분위기, balanced reaction | unknown(README에 명시 없음) | 무기 세라믹 편향. 출판사 TDM 코퍼스 기반 | 1 |
| LeMat-Synth (Lederbauer et al., arXiv 2510.26824v2, 2026) | https://arxiv.org/abs/2510.26824 | 미확인 | OA 논문(arXiv, ChemRxiv, OMG24)에서 LLM으로 추출한 합성 절차와 VLM으로 디지타이즈한 성능 그래프 | 80,940편 → 합성 절차 58,345건(고품질 부분집합 30.2K), 합성법 35종, 소재군 16종. 'polymers & soft matter' 2,431건 | 목표물, 전구체(순도), 단계(T, t, P), 장비, 분위기, 합성법 라벨(electrospinning 포함), 그래프 시리즈 | GitHub과 Hugging Face에 공개했다고 기술(라이선스는 미확인). OA 원문만 사용 | 무기 중심. LLM-as-judge 평균 3~4/5점. 심판 모델마다 편향 존재(ICC 0.07~0.28) | 1 |
| MatKG (Venugopal & Olivetti) | https://github.com/olivettigroup/MatKG | 접속 확인 | 초록·그림 캡션 NER(MatBERT) 기반 공출현 지식그래프(트리플) | README: 500만+ 논문, 엔티티 15만+, 고유 트리플 350만+(Zenodo record 10022727). NeurIPS'22 v1: 400만 편, 엔티티 8만, 트리플 200만 | Material, Property, Application, Synthesis/Characterization Method, Descriptor, Symmetry/Phase와 공출현 가중치 | unknown(Zenodo는 차단) | 공출현 기반이라 수치값·인과관계 없음. 무기 합성 편향 | 1 |
| MatScholar (Weston et al.) | https://github.com/materialsintelligence/matscholar | 접속 확인 | 재료 초록 NER 결과 검색 API | 약 350만 초록에서 엔티티 추출(README) | MAT, PRO, APL, SMT, CMT, DSC, SPL 엔티티와 초록 텍스트 | API 키는 'LBNL 내부 협력자에게만'(README) | 무기 편향. 접근이 막혀 있음 | 0 |
| SuperMat (초전도체 주석 코퍼스) | https://github.com/lfoppiano/SuperMat | 접속 확인 | 수동 연결 주석 코퍼스(INCEpTION, TEI-XML) | unknown | 재료, Tc, 압력 등 연결 엔티티 | 'The annotations are not public due to copyright'(README). 엔티티 CSV만 공개 | 도메인 무관(초전도) | 0 |

## NLP tool (text

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| ChemDataExtractor v2 (CDE2) | https://github.com/CambridgeMolecularEngineering/chemdataextractor2 | 접속 확인 | 규칙·ML 기반 화학 정보추출 툴킷(HTML·XML·PDF reader, 화학 NER, 표 파서, 물성 파싱 문법) | 툴(데이터 아님). PyPI chemdataextractor2 2.4.0 | 사용자 정의 property model(값, 단위, 화합물, 조건) | MIT(PyPI 메타) | 무기·저분자 명명에 최적화되어 고분자명·블렌드 인식이 약함. 규칙 작성 부담이 큼 | 1 |

## NLP model

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| MatSciBERT | https://github.com/M3RG-IITD/MatSciBERT | 접속 확인 | 재료과학 도메인 BERT(HF m3rg-iitd/matscibert) | unknown(사전학습 코퍼스 규모는 이 세션에서 미확인) | (모델) | unknown | PolyIE에서 NER·RE 최고 성능 인코더였음(PolyIE 논문) | 1 |

## NLP benchmark

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| MatSci-NLP / HoneyBee (MatSci-Instruct) | https://github.com/BangLab-UdeM-Mila/NLP4MatSci-HoneyBee | 접속 확인 | 재료 NLP 벤치마크와 LLM instruction 데이터 | unknown | NER, RE, 이벤트 추출 등 과제 | unknown | 일반 재료 위주 | 0 |

## literature

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| SpinCastML 전기방사 섬유직경 데이터셋 (Roldán & Sabir, arXiv 2602.09120) | https://doi.org/10.5281/zenodo.18557989 | 미확인 | 문헌(Scopus·Google Scholar)에서 수동 큐레이션한 전기방사 조건–섬유직경 분포 데이터. 앱에 내장 | 1,778 연구, 섬유직경 관측 68,480, 고분자 16종(셀룰로오스 아세테이트, 젤라틴, 나일론6, PAN, PCL, PDLLA, sPEEK, PET, PLA, PMMA, PS, PU, PVA, PVDF, PVP, γ-PGA) | DOI, 고분자, 용매1~3과 비율, 농도, 니들 직경, 컬렉터 종류, 회전수, 전압, 유량, TCD, 온도, 상대습도, 섬유직경 분포. 보조자료로 고분자–용매 용해도(OK/COND/NO, max_pct), 용매–용매 비혼화 목록 | 보충자료와 Zenodo 공개로 기술(라이선스는 미확인). FEAD·Cogni-e-SpinDB를 통합 | '안정적 섬유 형성' 실험만 포함(실패 제외 → 성공 편향). 단일 고분자 논문만. 고분자 불균형(PVDF·PVP 꼬리 분포 심함). 무작위 분할 R² 0.92는 DOI 그룹 누수 가능성이 있어 낙관적일 수 있음 | 3 |
| DES 물성 문헌 집계 데이터(Odegova et al. Green Chem 2024 + Luu et al. APL 2023, 통합본) | https://github.com/srampinogroup/des-ml-exploration | 접속 확인 | 문헌에서 수집한 DES 녹는점·밀도·점도와 성분 SMILES | Odegova: 녹는점 2,303 / 밀도 4,369 / 점도 4,216 항목(2003년~). Luu: 402 항목. 통합 녹는점 데이터 2,651 항목 | 성분 SMILES, 성분 녹는점, 몰비, DES 녹는점, 성분명, DES type, DOI | unknown(repo LICENSE를 확인하지 않음). 원 데이터 repo는 lamm-mit/MoleculeDiffusionTransformer(존재 확인) | 단위 변환과 ±10 K 중복 병합 처리. 녹는점 측정법(DSC 대 육안) 혼재 가능성 | 2 |

## GitHub dataset / LLM

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| DES for phenolics extraction: LLM 보조와 수동 검증 문헌 데이터셋 파이프라인 | https://github.com/chem-data-extraction/des-for-phenolics-extraction | 접속 확인 | PDF → LLM(Gemini 2.5 Flash) 후보 추출 → 수동 검증 → DESignSolvents 웹 물성 병합 → 검증 스키마로 이어지는 재현 파이프라인과 데이터 | unknown(레코드 수 미확인) | DES 조성, 식물원료, 추출조건, 페놀 추출 결과(1 레코드 = 1 실험 결과) | LICENSE, CITATION.cff 존재(종류 미확인) | 교육용 과제 규모. 페놀 추출 도메인 | 1 |

**이 조사 블록에서 확인된 데이터 공백**

- 케라틴(양모·깃털 유래), PVA/PVAc, 셀룰로오스 유도체를 DES나 이온성 액체로 용해·방사·성형한 레시피–물성 데이터는 텍스트마이닝본과 수동 큐레이션본 모두 찾지 못함. MatViX PBD 스키마(치환도, 가수분해도)와 SpinCastML의 CA·PVA·젤라틴 하위집합이 가장 가까운 대체재임
- 비대칭(일방향) 수분이동 막·원단의 평가지표(AATCC 195 계열 OMMC, 누적 일방향 이동지수, 양면 접촉각 차이, 투습도 WVTR)를 구조화한 공개 데이터셋을 찾지 못함. Polymer Scholar의 water contact angle(3,932건)과 water flux(1,371건)는 초록 단위라 '면별' 정보가 없음
- 전기방사 후 탄화(안정화·탄화 온도, 승온속도, 탄소수율, 전도도, 비표면적) 문헌 데이터셋을 찾지 못함
- 고분자 용해도(특히 바이오고분자–DES/IL 쌍) 정량 데이터셋은 공백. DES 데이터는 용매 자체 물성(녹는점·밀도·점도)뿐이고 SpinCastML의 용해도 테이블은 범주형(OK/COND/NO)
- 특허 쪽은 KIPRIS Plus가 금속 '합금조성비'만 구조화해 제공하고, 고분자·섬유 가공 실시예(조성, 가공조건, 물성 표)를 구조화한 공개 데이터는 없음. Google Patents·USPTO 원문 표를 직접 추출해야 함(oxide glass 선례 정도)
- 측정조건·시험법 메타가 거의 없음: Shetty 2023 온톨로지는 측정 조건을 다루지 않고(논문이 한계로 명시), PolyIE도 Condition 엔티티가 1.7%뿐임. 단위는 '최빈 단위' 변환에 그침. 섬유 분야 고유 단위(데니어/텍스, cN/dtex, g/m²·24h)를 다룬 정규화 사례를 찾지 못함
- 출판편향과 성공편향: 전기방사 문헌 312편 중 정량 보고 가능한 것은 44%이고 실패 데이터는 거의 없음(Electrospinning-Data.org 저자 분석). SpinCastML은 '안정 섬유 형성'만 포함. 문헌 추출 데이터 전반이 낙관적 상한값 쪽으로 치우침
- 텍스트마이닝 법적 공백: 대형 고분자 추출 코퍼스(Shetty 240만, Gupta 68.1만, PHA 약 300만, PolyLM 18.5만)는 모두 출판사 TDM 경로라 원문 재배포가 불가하고 데이터 공개 범위도 불명확(PolyLM·PHA는 공개 여부 미확인). Polymer Scholar 코드·데이터는 비상업 한정. SuperMat은 저작권 때문에 주석을 비공개. OA만으로 제한하면(PMC, arXiv, ChemRxiv, S2ORC) 고분자 가공 저널 커버가 크게 줄어듦
- 국문 문헌·보고서(KCI 한국섬유공학회지, NTIS 국가과제 보고서, ScienceON 보고서)를 텍스트마이닝한 공개 데이터는 찾지 못함. 이 세션에서는 KCI·NTIS 접근 조건조차 확인하지 못함
- 표·그림 속 수치: 고분자 물성의 상당 부분이 표와 그래프에 있으나 공개 멀티모달 추출 성능은 낮음(MatViX PNC 곡선 CAS 7 미만). 초록 기반 데이터는 구조적으로 이 정보를 놓침
- 고분자 정체성 표준화 공백: 고분자명→SMILES/BigSMILES 변환이 여전히 수동이고(Shetty 논문 한계), 천연고분자(케라틴, 셀룰로오스 유도체)는 반복단위 표현 자체가 부적합해 구조 기반 전이학습 특징을 만들기 어려움
- 검증 한계(본 조사): WebSearch 예산이 소진되어(세션 공유 200회 한도) Europe PMC·CORE·Lens·EPO 할당량·KIPRIS 약관·NTIS·KCI·PATENTSCOPE는 공식 페이지로 검증하지 못함. Gupta 2024의 수치는 2차 인용(arXiv 2609.34051)으로만 확인

## patents/text

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| LitXBench / LitXAlloy (Radical AI, 2026, ICML'26 AI4Science) - 문헌 '실험' 추출 벤치마크 | https://github.com/Radical-AI/litxbench | 접속 확인 | 수작업 정답 주석(코드 기반 Experiment 객체) + 평가 프레임워크(pip 패키지 litxbench) | LitXAlloy: 합금 논문 19편, 측정값 1,426개, 재료 101개(고유 조성 68개). 출처: arXiv 2604.07649 본문(alphaXiv MCP로 확인), README에 '19 papers' 명시 | 재료=조성이 아니라 공정 이력(synthesis group DAG, 공정 순서), 측정값(kind/value/unit/uncertainty/method), 미세조직 configuration, canonical enum(MeasurementKind 등), 출처 필드 | 공개, 코드 MIT(LICENSE 파일 확인) | 합금 전용 스키마(고분자/섬유로 옮기려면 enum·검증규칙 재설계 필요). 그림 제외, 텍스트만 사용. 주석자 1인 + LLM 검토라 오류가 남아 있을 수 있다고 저자가 명시. 유효숫자는 보존하지 않음 | 3 |
| LLM-NERRE (Dagdelen et al., Nat. Commun. 15, 1418, 2024) - LLM 기반 개체·관계 공동 추출 주석 데이터와 코드 | https://github.com/lbnlp/NERRE | 접속 확인 | 주석 데이터(초기 입력·중간·최종 출력), 학습/검증 분할, 주석 UI, 평가 스크립트(GPT-3/Llama-2 미세조정) | unknown(정확한 주석 건수 미확인). 과제 3종: 도펀트-호스트, MOF, 일반 재료(조성/상/형태/용도) | 문장/문단 단위 JSON 레코드(재료, 조성, 상, 형태, 응용, 도펀트 관계) | 공개, LICENSE 파일 미확인(unknown) | 무기·MOF 중심이라 고분자 공정변수 스키마가 없다. GPT-3 미세조정 기반이라 현재 모델로 재현하면 결과가 다를 수 있음 | 3 |
| MaTableGPT (KIST·고려대·LLNL, 2024) - GPT 기반 재료 논문 표 데이터 추출기 + 추출 데이터 | https://github.com/KIST-CSRC/MaTableGPT | 접속 확인 | 표 추출 코드(TSV/JSON 표현, 표 분할, 후속질문 기반 환각 필터) + 추출 결과 데이터(OER 촉매 성능, Zenodo) | unknown(건수 미확인). 논문 기준 total F1 최대 96.8%, few-shot GPT 비용 5.97 USD. 데이터 위치는 논문 본문의 zenodo.org/doi/10.5281/zenodo.11362347 | 논문 DOI, 촉매명, 성능·물성 값(수전해 OER) | 코드 공개(git lfs로 데이터 포함), LICENSE unknown. Zenodo 데이터 라이선스 unknown | 수전해 촉매 표에 특화되어 있다. 표만 다루고 본문·그림은 다루지 않는다 | 2 |
| Text-to-Battery Recipe (T2BR, KIST CSRC) - 문헌 기반 end-to-end 레시피 추출 프로토콜과 주석 데이터 | https://github.com/KIST-CSRC/Text-to-BatteryRecipe | 접속 확인 | 논문 초록·문단, 문단분류 라벨, 토픽 할당, NER 주석(cathode_synthesis.json, cell_assembly.json), 사전학습 NER 모델, 레시피 검색 결과 | unknown(README에 파일 목록만 있고 건수 없음). README의 데이터 다운로드 링크가 비어 있음 | 합성 레시피 엔터티(전구체·조건·공정 단계), 셀 조립 엔터티, 문단-토픽 | 코드 공개, LICENSE unknown. 데이터 링크 미기재로 접근성 불확실 | LiFePO4 양극 배터리 도메인 한정. MatBERT 기반이라 LLM 이전 세대 방법 | 2 |
| ChemTables (Zhai et al., J. Cheminform. 13, 97, 2021) - 화학 특허 표 의미분류 데이터셋 | https://github.com/zenanz/ChemTables | 접속 확인 | 특허 표 + 내용유형 라벨(분광·물성·약리 등), 베이스라인 코드(Table-BERT 등) | 화학 특허 표 788개(PubMed 초록) | 표 셀 내용, 표 유형 라벨 | 데이터 Mendeley doi:10.17632/g7tjh7tbrj.3, CC BY-NC 3.0(초록 명시). 코드 Apache-2.0(LICENSE 확인) | 제약·유기화학 특허 중심(Elsevier 협업). 고분자·섬유 특허 표는 적을 가능성이 크고, 비상업 라이선스 | 2 |
| ChEMU 2020 화학특허 정보추출 코퍼스 (CLEF 2020 평가 랩) | https://doi.org/10.3389/frma.2021.654438 | 미확인 | 화학 특허 반응 서술 주석 코퍼스(NER + 이벤트 추출) | unknown(코퍼스 건수는 초록에 없음). 대회 등록 37팀, 제출 46 run(PubMed 초록) | 화학 개체와 반응 내 역할, 반응조건(온도·시간 등), 반응 단계 이벤트 | unknown(대회 데이터 배포 조건 미확인) | 유기합성·제약 특허 중심. 주석자 간 일치도는 매우 높다고 보고됨. 데이터 누출 영향이 논의됨 | 2 |

## Korean public (기관 GitHub) / harmonizatio

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| DATUM (KIST 계산과학연구센터, 2026) - 문헌 추출 합성 데이터의 실험실 인식(laboratory-aware) 조화 | https://github.com/KIST-CSRC/DATUM | 접속 확인 | 모델 코드 + 별도 호스팅 데이터셋(문헌 보고값과 타깃 실험실 측정값 쌍, Methods 절 텍스트) | unknown(README에 '데이터셋은 별도 저장소'라고만 적혀 있고 링크·건수 미기재) | 수치 합성조건, 논문 Methods 절차 텍스트, 실험실 텍스트, 문헌 보고 결과값 y0와 실험실 측정값 y1(flow matching으로 변환) | 코드 공개, LICENSE 파일 미확인(unknown). 데이터 접근 경로 unknown | 나노입자 합성 분야라 고분자·섬유가 아니다. 인용 정보는 2026년, 저자 Nayeon Kim, 게재처 공란이라 정식 출판 여부 미확인 | 3 |

## polymer DB / 재활용·첨가제 안전성

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| PlastChem DB (플라스틱 화학물질·우려 고분자 DB, 2024) | https://github.com/PlastChem/DB | 접속 확인 | 플라스틱 함유 화학물질(단량체·첨가제·가공보조제)과 위해성 분류를 통합한 DB. 데이터 본체는 Zenodo record 10701706 | unknown(README에 건수 없음). 원천 데이터 7종 통합(5종 공개, 2종 비공개라 해당 스크립트 생략) | 화학물질 식별자, 플라스틱 내 기능·용도, 위해성 기준 분류, 우려 고분자 | 저장소 LICENSE.md = CC BY 4.0. Zenodo 데이터 라이선스는 미확인 | 베타 버전을 수작업 큐레이션해 v1.00 공개. 비공개 원천 2종은 재현 불가. README에는 공개일이 2023-03-14로 적혀 있으나 저장소 생성일은 2024-03이라 날짜 표기 불일치 가능 | 2 |

## polymer DB (화학적 재활용·바이오 폴리에스터)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| TROPIC - Thermodynamics of Ring-Opening Polymerisation Informatics Collection (Imperial C… | https://doi.org/10.1039/d5fd00098j | 미확인 | 문헌 기반 개환중합 열역학 파라미터 DB(실험값과 계산값 모두), 웹사이트 + API | unknown | 중합 엔탈피 ΔHp, 엔트로피 ΔSp, 천장온도 Tc, 측정 실험조건(농도·상태 등) 또는 계산 방법론 메타데이터 | 오픈소스로 기술됨(초록). 구체 라이선스 unknown | 문헌 집계형이라 측정법·표준상태가 이질적이다. 이를 조건 메타데이터로 연결해 둔 것이 특징. ROP 단량체(락타이드·락톤 등)로 한정 | 2 |

## general chemical DB (물성·독성, 염료·용매·DES/IL

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| US EPA CompTox Chemicals Dashboard (DSSTox) | https://comptox.epa.gov/dashboard | 미확인 | 구조 큐레이션된 물질 DB + 물리화학·환경거동·노출·용도·생체 내 독성·시험관 생물검정 데이터, 일괄 다운로드 | 약 760,000 물질(2017년 논문 기준, 이후 증가 추정치는 미확인) | 구조 식별자 매핑, 물리화학 물성(실측/예측), 환경거동, 독성(ToxCast, ToxRefDB), 규제 목록 | 화학 콘텐츠 public domain 다운로드(초록 명시) | 환경·독성 중심이라 고분자 자체 데이터는 빈약하다. 예측값과 실측값이 섞여 있음 | 2 |

## fiber/textile (염색·가공 약품, 폐수)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 섬유산업 유래 미량오염물·미세플라스틱 DB (Gambino et al., Environ. Sci.: Processes Impacts 27, 297, 2025) | https://doi.org/10.1039/d4em00639a | 미확인 | 리뷰에 동반된 화학물질 DB(물리화학 물성, 생태독성, 검출 위치) | 500종 이상 화합물(PubMed 초록) | 물리화학 물성, 생태독성, 섬유 공정 단계별 검출 위치(원료→최종제품), 하수처리장·지표수·퇴적물, 국제기관 분류, PNEC 기반 예비 위해성 | unknown(논문 SI로 제공 추정, 미확인) | 문헌 리뷰 집계. 이탈리아 코모 실크 산업 협업이라 지역 편향 가능. 검출 농도는 연구마다 측정법이 다름 | 2 |

## biopolymer/재활용 (효소 분해)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| PAZy - Plastics-Active Enzymes Database (Buchholz et al., Proteins 90, 1443, 2022) | https://doi.org/10.1002/prot.26325 | 미확인 | 검증된 플라스틱 분해 효소 목록 + 문헌 활성 데이터 + 상동체 서열 | PET 활성 효소 상동체 약 3,000개(HMM), PUR 활성 상동체 2,000개 이상(BLAST). 당시 검증 효소는 50종 미만(초록) | 효소 서열, 기질 고분자(PET, PUR, PA 올리고머), 문헌 활성값, 보존 모티프 | 오픈 액세스 DB로 기술됨. 세부 라이선스 unknown | 석유계 고분자(PET/PUR) 중심이라 바이오 폴리에스터는 적다. 상동체는 예측이며 활성 미검증 | 1 |

## biopolymer (탄화)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 합성 바이오매스 성분비(리그닌·셀룰로오스·헤미셀룰로오스) 열분해 바이오차 데이터 (Data in Brief 2025, 111296) | https://doi.org/10.1016/j.dib.2025.111296 | 미확인 | 통제된 성분비 혼합물의 저온~중온 열분해 실험값 + VOC 분석 | 바이오차 204개 + 원료 혼합물 12종, 200~600 °C(PubMed 초록) | 성분비, 열분해 온도, 질량수율(MY), 에너지밀도비(EDr), 에너지수율(Ey), 겉보기밀도, 함수율, 휘발성 유기화합물 | unknown(DIB 연계 저장소 라이선스 미확인) | 실제 바이오매스가 아닌 시약 혼합물. 600 °C 이하라 섬유 탄화(800 °C 이상) 영역은 없음 | 2 |

## fiber/textile 재활용 (열적 재활용·탄화)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 폐마스크(PP 부직포) 온도별 열분해 데이터 (Sci. Data 12, 894, 2025) | https://doi.org/10.1038/s41597-025-05269-1 | 미확인 | 원료 물성 + 열분해 생성물(고체·오일·가스) 특성 | 마스크 2종(FFP2, 일반) × 5개 온도(350/400/450/500/550 °C)(PubMed 초록). 레코드 수 unknown | 원료 물리화학 물성, 반응온도, 생성물별 수율과 성상 | unknown(Sci Data 기사는 오픈, 데이터 저장소 라이선스 미확인) | 폴리올레핀 부직포 한정이라 셀룰로오스·단백질 섬유와는 열분해 거동이 다름 | 2 |

## biopolymer (가소화 필름)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 한천-글리세린 바이오고분자 필름 기계물성 참조 데이터셋 (Materials 15, 3954, 2022) | https://doi.org/10.3390/ma15113954 | 미확인 | 실험계획법(DoE) 조성-인장물성 데이터 + 신경망 회귀 모델 | unknown(조성 수 미확인) | 한천 함량, 글리세린(가소제) 함량, 영률, 인장강도, 파단신율 | unknown(MDPI 기사는 CC BY, 데이터 파일 라이선스 미확인) | 단일 연구실, 단순 2성분 조성. 습도 조건 의존성 정보 제한 가능 | 2 |

## fiber/textile (시험평가: 통기도)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 패턴 니트 원단 현미경 이미지-통기도(공극) 분류 데이터셋 (Sci. Rep. 2026) | https://doi.org/10.1038/s41598-026-47596-2 | 미확인 | 고해상도 현미경 컬러 이미지 + 전문가 검증 공극 등급 라벨 | 원단 45그룹 × 그룹당 20장(약 900장), 12개 클래스(PubMed 초록) | 원단 이미지, 공극률·구조밀도·패턴 기반 통기도 등급 | unknown(데이터 공개 경로 미확인) | 통기도 실측값이 아닌 등급 라벨. 클래스 불균형(Focal Loss 사용). 터키 단일 출처 | 2 |

## fiber/textile (산업 표준 시험: 서멀 마네킹)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 네덜란드 소방복 의류 단품·앙상블 열저항·증발저항(Ret) DB (Kuklane et al., Biology 11, 1813, 2022) | https://doi.org/10.3390/biology11121813 | 미확인 | 서멀 마네킹 측정 열저항·증발저항(전신·국부·부위별) | 단품 37개(변형 포함)와 앙상블 25개 열저항, 그중 12개 앙상블 증발저항(PubMed 초록) | 정적 열저항, 증발저항, 의복 면적계수, 국부·부위별 값, 단품→앙상블 합산식 | unknown(MDPI 기사 CC BY, 데이터 라이선스 미확인) | 소방 보호복 한정. 마네킹 프로토콜에 의존(장비·실험실 간 차이 존재) | 2 |

## fiber/textile (탄소섬유·시험조건 효과)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 단섬유 탄소섬유 1,200개 인장 Weibull 데이터 (PYROFIL TRW40, Data in Brief 2024, 110717, DTU) | https://doi.org/10.1016/j.dib.2024.110717 | 미확인 | 단섬유 인장 응력-변형 곡선, 섬유경 분포, Weibull 해석 | 단섬유 약 1,200개, 게이지 길이 8종(20~80 mm, 길이당 약 150개)(PubMed 초록) | 게이지 길이, 등가 섬유경(7.37±0.34 µm), 초기 탄성률(220±3 GPa), 곡률계수, 파단응력, Weibull 파라미터 | unknown(DIB 연계 저장소 라이선스 미확인) | 상용 섬유 1종이라 조성·공정 다양성이 없다. 목록의 2021 DIB 단섬유 대용량 데이터(Mendeley ygyym4vy6b)와 같은 DTU 그룹일 수 있으나 별개 기사 | 2 |

## fiber/textile (재활용 선별·혼용률)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| CottonFabricImageBD - 면 혼용률별 원단 이미지 (Data in Brief 2024, 110712) | https://doi.org/10.1016/j.dib.2024.110712 | 미확인 | 원단 RGB 이미지 + 면 함량 클래스 라벨 | 원본 1,300장, 13개 클래스(면 30~99%), 증강 후 27,300장(PubMed 초록) | 이미지, 면 함량 범주 | unknown | RGB만 있고 분광 정보가 없다. 방글라데시 단일 출처. 증강 이미지 비중이 큼 | 1 |

## polymer DB (상용 핸드북)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Wypych, Handbook of Polymers 3판 (ChemTec Publishing, 2022) - 공정조건 포함 고분자 물성 핸드북 | https://www.alphaxiv.org/abs/2607.17925 | 미확인 | 고분자별 물성 + 가공 조건(온도·시간·압력·가공법) 수록 핸드북 | unknown(핸드북 전체 수록 고분자 수 미확인). 2026 연구가 여기서 공정정보가 있는 43종(온도 35, 압력 15, 시간 13개 값)을 추출 | Tg 등 열·기계 물성, 가공 온도/시간/압력, 가공법 범주(용융/용액캐스팅 등) | 상용 서적(유료) | 핸드북 집계라 측정 조건 표기가 불균일하고 결측이 많다(해당 연구는 평균 대치 사용) | 2 |

## fiber/textile (산업 공급망 데이터)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| Open Supply Hub (구 Open Apparel Registry) - 글로벌 의류·섬유 생산시설 오픈 레지스트리 | https://github.com/opensupplyhub/open-supply-hub | 접속 확인 | 생산시설 식별·위치·업종 레지스트리 플랫폼(오픈소스 코드 + API) | unknown | 시설명, 주소·좌표, 업종(제조 공정), 연계 브랜드, 고유 ID | 코드 MIT(LICENSE.txt 확인). 데이터 라이선스 unknown | 자가보고·기여 기반이라 중복·누락 가능. 소재 물성 정보는 없음 | 1 |

## polymer 공정 데이터 (산업 센서)

| 이름 | 링크 | 링크 확인 | 데이터 종류 | 규모 | 변수 | 접근·라이선스 | 품질·편향 | 활용도 |
|---|---|---|---|---|---|---|---|---|
| 폴리머 압출기 필터 잔여수명(RUL) 런투페일 데이터 (Data in Brief 2026, 113254) | https://doi.org/10.1016/j.dib.2026.113254 | 미확인 | 단축 압출기 시계열 센서 데이터(오염 실험) | 런투페일 60회, LDPE 압출, 1 Hz 온도·전압·전류 + 1 kHz 전류(PubMed 초록) | 배럴 구간 온도, 스크류 모터 전압·전류, 고장 모드(필터 막힘 / 파열) | unknown | LDPE 단일 소재·단일 장비. 방사 공정이 아닌 압출 | 1 |

**이 조사 블록에서 확인된 데이터 공백**

- 비대칭(일방향) 수분이동 막·원단(Janus): 공개 데이터셋을 찾지 못했다. PubMed에서는 2026년 리뷰(Grillo·Weder 외, ACS Appl. Polym. Mater. 8, 6050, DOI 10.1021/acsapm.6c00561)만 확인되었다. MMT(AATCC 195)·투습도 원자료는 논문 SI와 특허 표에 흩어져 있어 문헌 추출(a)이 사실상 유일한 경로다
- 케라틴(양모·깃털) 재생 섬유·필름의 공정-물성 데이터: Data in Brief와 Sci Data에서 케라틴 관련 공개 데이터는 유전체·법과학(동위원소, 모발) 쪽뿐이고, 재료 물성 데이터셋은 확인되지 않았다
- PVA/PVAc 섬유·필름, 셀룰로오스 유도체(CA, CMC)의 조성-공정-물성 공개 데이터셋: 2022년 이후 DIB·Sci Data에서 직접 해당하는 기사를 찾지 못했다. 한천 필름 같은 유사 시스템만 있다
- DES/IL로 가공한 바이오고분자의 최종 섬유·막 물성 데이터: 용해도·물성 DB는 있으나 '용매 조성→재생 섬유/필름 물성'을 잇는 데이터는 없다
- 섬유 산업표준 시험의 실험실 간 비교(ring test) 원자료(KS K/ISO/AATCC 견뢰도·인장·투습): 공개 데이터를 찾지 못했다. 시험조건 효과를 정량화한 공개 사례는 탄소섬유 게이지 길이 데이터 정도다
- 원단 태(KES-FB)·드레이프·방염(LOI, 콘칼로리미터) 섬유 데이터: PubMed·GitHub 검색으로 공개 데이터셋이 확인되지 않았다(방염 데이터는 FRP-콘크리트 보 화재저항 DB뿐)
- 전기방사 바이오고분자 섬유의 탄화 조건→탄소섬유 물성 데이터: 목록의 소규모 DIB·ANN 연구 외에 신규 공개 데이터는 발견되지 않았다
- 한국 기관 신규 데이터: WebSearch 한도 소진으로 KOSHA MSDS OpenAPI, 화학물질정보시스템(NCIS), 국가참조표준센터, 한국소비자원 기능성 의류 비교시험 결과, 제품안전정보센터(safetykorea) 섬유 시험·리콜 데이터의 실재와 내용을 검증하지 못했다. 이번 조사에서 확인된 한국 기관 자료는 GitHub로 검증한 KIST CSRC 저장소 3건(DATUM, MaTableGPT, T2BR)뿐이다
