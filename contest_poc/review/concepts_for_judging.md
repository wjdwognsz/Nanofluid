# 후보 컨셉 목록 (5개 관점 에이전트 + 참가자 제안을 병합, 중복 통합)

C01 가상 라운드로빈(Virtual Round-Robin) 데이터 감사 — 여러 논문·기관·시험법에서 모인 소재데이터를 '계획되지 않은 실험실간 비교시험(ISO 5725)'으로 재해석. 혼합모형 y=f(x)+b_출처+b_시험법+ε로 분산 분해 → (a) 데이터셋별 달성가능 정확도(노이즈 천장) 품질 라벨, (b) 시험법 등화(환산식+불확도, 소재군 조건부), (c) 새 실험실/기업이 플랫폼에 합류할 때 필요한 기준시료 수(k-기준시료 보정 곡선), (d) 논문 단위 평가 의무화(DOI 맞히기 감사). 선행: Crusius 2025 Faraday Discuss.(noise ceiling), Landrum&Riniker 2024 JCIM, Jablonka 2026 arXiv 2602.17730(Clever Materials), Wang 2026 arXiv 2609.01621, Ohno 2020 ACS Energy Lett(인터랩). 섬유 적용은 찾지 못함.

C02 투습·수분전달 시험법 로제타석 — ASTM E96(정립/도립/흡습제), JIS L1099 A-1/B-1, ISO 11092(Ret), ISO 15496, AATCC 195(MMT, OWTC) 값을 물리 직렬저항 모델 + 계층 베이지안 errors-in-variables로 '시험법 불변 잠재량(고유 수증기 저항)'과 신뢰구간으로 환산, '비교 불가' 판정, 시험법 측정 천장 감사, 방향차(Janus) 지문. 데이터: 동일 직물 다시험법 문헌표(McCullough 2003 Meas Sci Technol 직물 26종×5방법, Huang&Qian 2008 TRJ, Kar 2007 Meas Sci Technol, Gibson 1993 TRJ), Janus 논문 LLM 추출. 선행: 쌍별 상관 비교연구만 있고 ML/베이지안 통합 환산은 찾지 못함. GitHub 다운로드 가능한 직물 투습 데이터는 없음(문헌 표 디지타이즈 필요).

C03 PFAS-free 투습방수: 고분자→막→원단 징검다리 전이 — polyVERSE 기체·H2O 고분자 고유 투과 데이터 → 막 → 원단 시험값(DYETEC)으로 물리 저항망을 통해 연결, 불소 고분자 마스킹 평가, 비불소 대체 후보 랭킹. 선행: Phan 2024 npj Comput Mater(polyVERSE sim-exp MTL). 위험: H2O 데이터가 폴리이미드 편중, 원단 구조가 고분자 효과를 덮음.

C04 미세섬유 탈락 '가공 승수' — 이질 측정(필터 공경, 세탁기 종류, 단위 mg/kg vs fibers/g, ISO 4484-1:2023 이전 레거시)을 계층 베이지안으로 조화, 가공 공정별 승수를 Ecobalyse(프랑스 정부 오픈소스 환경비용 도구; 미세섬유 항이 섬유 기원 상수×질량뿐)·DPP에 연결. 선행: The Microfibre Consortium 2025 Root Cause Analysis(1,000+ 원단 RF, 가공 인자 지목), Hazlehurst 2023 ESPR. GitHub에 탈락 데이터셋 없음 → 문헌 추출 필요.

C05 염색가공 데이터 협동조합 — 연합학습 + 계통수 부분 풀링 + Data Shapley 기여도 정산으로 기업 레시피 비공개 상태에서 DPP·LCA 1차 데이터 생산. 선행: MELLODDY(제약 연합학습). 공개 데이터 PoC 약함(대리 데이터 시연만).

C06 역염색(design-for-decolorization) — 염착 평형·견뢰도 데이터를 열역학 사이클로 재해석해 재활용 탈색 용이성 예측, '사용 시 견뢰·폐기 시 탈색' 염료–섬유–용매(DES 포함) 조합. 공개 데이터: polyVERSE 용매 흡착·확산, HSP 데이터. 직접 선행 찾지 못함(검색 제한). 핵심 주장은 DYETEC 데이터 필요.

C07 징검다리 용매 전이 IL→콜린계→DES→케라틴·폐섬유 재생 — ML4IL(GitHub, IL–셀룰로오스 용해도 674행/331 IL/33편, 녹는점 2,276행) 기반, 기전 게이트(β, 이황화결합)로 음전이 차단, 가열시간 보정 라벨 조화. 선행: Qu 2025 J Cheminform(IL 셀룰로오스 ML), Asaadi 2016 ChemSusChem(Ioncell). DES/케라틴 데이터 희소.

C08 소재 계통수 기반 계층 전이(참가자 제안) — 생물 계통 비교법처럼 '유래→주쇄 화학→극성→용매계→계열→종' 트리 위에서 부분 풀링/트리 거리를 연관도 사전으로. 확장안: 전기방사→바이오 전구체 탄화. 선행: 계층 베이지안·TAXOGAN·HGTL(일반 ML), Polymer Genome 계층 지문(분자 내부 계층), HiPoly(arXiv 2609.02746). 소재 간 분류 트리를 전이 경로로 쓴 소재 연구는 찾지 못함.

C09 전이 지도(Transfer Atlas) + 음전이 차단(참가자 씨앗 c) — 소스→타깃 쌍마다 값싼 사전 점수(LogME류 증거, 프록시 상관, 도메인 커버리지, 트리 거리)로 연계 가치 예측, conformal 하한>0일 때만 전이, widest-path 징검다리. 선행: Yamada 2019 ACS Cent Sci(shotgun TL), Yao 2024 Commun Chem(PGM transferability map), MoTSE, LogME, LEEP, TTL(KDD 2015), DDTL(AAAI 2017), Chang 2022 npj(MoE). 방법론 신규성 낮음.

C10 기상 고고학 — DOI 소속(위치)·투고일(시점)을 ERA5/기상청 ASOS와 결합해 미보고·기본값 실험실 습도를 확률적으로 복원(실내 절대습도는 실외를 추종: Nguyen 2014 Indoor Air). 선행 찾지 못함. 위험: 공조로 실내외 분리, 실험 시점 불확실.

C11 실패 데이터 고고학 / 생존자 편향 — 성공만 보고된 문헌의 선택편향 정량화(PU/one-class vs 실패 포함 지도학습), 숨은 변수(Mw, 점도) LLM 복원, Heckman/IPW 보정, 실패 1건의 Shapley 가격 → 실패 데이터 기탁 제도. 선행: Raccuglia 2016 Nature, Jia 2019 Nature, Strieth-Kalthoff 2022 Angew, Electrospinning-Data.org(Mahdian 2026 arXiv 2603.27841, 실패 포함 FAIR 플랫폼 — 통계 보정은 없음), SpinCastML(안정 레코드만 사용).

C12 문헌 수치 신용등급 — 물리 항등식(P=D·S), 범위(0≤활동도≤1), 기본값 의심, 유효숫자, 출처 일치로 레코드별 AAA–D 등급, 인공 오류 주입으로 재현율 검증, 등급 가중 학습의 일반화 효과 측정. 선행: Wang 2026 arXiv 2609.01621, Athar 2025 arXiv 2512.18653, Hargreaves 2023 npj.

C13 소재데이터 가격표·유통기한 — 논문/기관/레코드 유형별 Data Shapley·LOO 가치, 출판연도별 가치 감쇠(반감기), 기여 크레딧·격리 규칙. 선행: Ghorbani&Zou 2019, Li 2023 npj(redundancy), Temporal-decay Shapley 2026.

C14 3층 충실도 사다리 — MD 시뮬레이션·문헌 추출·자체 측정을 다른 충실도로 묶는 비용인지 다중충실도 BO로 비대칭 수분이동 막 소재 선별, 소재→소자 층저항 물리 모델을 중간 충실도로. 선행: Phan 2024 npj(polyVERSE sim-exp 융합), Sabanza-Gil 2024, Takeno 2020. 위험: 증기(WVTR)↔액체(OWTC) 기전 불일치.

C15 LLM 문헌 추출 → 물리·화학 규칙 필터 → 소규모 능동학습 추천(참가자 씨앗 a 기본형) — 선행 다수(Polymer Scholar/Shetty 2023 npj, LLM 추출 2024–2026 다수). 차별화 어려움.

(전략가 관점 컨셉은 아래에 추가)

C16 능동 독서(Active Reading) — 능동학습의 오라클을 '실험'이 아니라 '다음에 읽을 논문'으로: LLM 추출(근거 문장 추적) + 규칙 필터(단위 wt%/w/v%, 범위, 몰비 합, 스케일링 이상치) + 불확실성 기반 다음 논문 선정으로 DES/IL 기반 바이오고분자 용해·방사 DB를 최소 독서량으로 구축. Cogni-e-SpinDB를 정답세트로 추출 정확도 검증. 선행: Polak&Morgan 2024 Nat Commun, Gupta 2024 Commun Mater, Kang 2025 JACS. '능동 독서' 직접 선행은 찾지 못함.

C17 (통합안) 섬유 시험·소재데이터 '조화·신뢰·연계' 3단 체계 — C01(가상 라운드로빈: 출처·시험법 효과 분해, 노이즈 천장, 앵커 k점 보정) + C02(투습·수분전달 시험법 로제타) + C12(레코드 신뢰등급: 파생값/기본값/물리위반 감사) + C09(연계 전 음전이 게이트)를 하나의 파이프라인으로. 적용 앵커: 비대칭(Janus) 수분이동 막·직물(참가자 전문) + DYETEC 공인시험 데이터. 위험: 범위가 넓어 초점이 흐려질 수 있음.
