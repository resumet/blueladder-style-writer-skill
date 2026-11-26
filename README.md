# 블루래더 콘텐츠 스튜디오

키워드와 주제를 받아 **블루래더 문체의 한국어 블로그 글, 대표 이미지, 섹션별 이미지·도표, HTML·이미지 ZIP**을 만드는 AI 에이전트용 스킬입니다. 문체 작성 지침과 실제 블로그 글 100편을 함께 제공하므로, 다른 사람도 같은 작성 기준을 참고해 사용할 수 있습니다.

**[설치용 ZIP 다운로드](https://github.com/resumet/blueladder-style-writer-skill/raw/refs/heads/main/dist/blue-ladder-content-studio.zip)** · [저장소](https://github.com/resumet/blueladder-style-writer-skill) · [스킬 지침](SKILL.md)

## 빠르게 사용하기

### 스킬 설치를 지원하는 환경

1. 위 링크에서 `blue-ladder-content-studio.zip`을 내려받습니다.
2. 스킬 설치를 지원하는 ChatGPT 환경에 ZIP을 첨부하고 다음과 같이 요청합니다.

   ```text
   첨부한 블루래더 콘텐츠 스튜디오 스킬을 설치해줘.
   참고 글모음과 스크립트도 함께 사용할 수 있도록 설치해줘.
   ```

3. 설치 완료를 확인한 뒤 키워드와 주제를 전달합니다.

   ```text
   @블루래더 콘텐츠 스튜디오
   키워드: 공유오피스 선택 기준
   주제: 2~4인 기업이 사무실 계약 전에 확인할 사항
   독자: 처음 사무실을 구하는 대표
   글과 대표 이미지, 섹션별 이미지를 만들어줘.
   HTML과 이미지를 함께 담은 10MB 이내 ZIP으로 제공해줘.
   ```

설치 지원 여부와 사용할 수 있는 도구는 계정·실행 환경에 따라 달라집니다. 다른 스킬 지원 에이전트에서는 해당 환경의 설치 방식에 따라 ZIP 안의 `blue-ladder-content-studio` 폴더를 등록합니다. 폴더 안의 `SKILL.md`, `references`, `scripts`, `assets`, `agents` 구조를 유지해 주세요.

### 스킬 설치 기능이 없는 환경

ZIP 파일을 첨부하고 압축을 읽을 수 있는 환경이라면, 아래처럼 **현재 대화의 참고 자료로 사용**하도록 요청할 수 있습니다. ZIP을 읽지 못하는 환경에서는 압축을 푼 뒤 `SKILL.md`와 `references` 폴더의 문서를 첨부합니다.

```text
첨부한 블루래더 콘텐츠 스튜디오의 SKILL.md와 문체 지침을 읽고,
글모음에서 주제와 목적이 비슷한 글 2~3편을 참고해 작성해줘.

키워드: EBITDA
주제: 영업이익과 다른 점, 기업을 비교할 때의 장점과 한계
분량: 공백 포함 약 2,500자
이번에는 글만 작성해줘.
실제 경험은 내가 제공한 내용만 사용해줘.
```

이 방식은 해당 대화에서 자료를 참고하는 방법입니다. 스킬의 영구 설치나 AI 모델의 파인튜닝을 수행하는 절차는 아닙니다.

## 기본 제작 규칙

| 항목 | 기본값 |
| --- | --- |
| 글 | 친근한 존댓말의 한국어 블로그 글, 공백 포함 약 2,000~3,000자 |
| 구성 | 제목, 도입, 주제에 맞는 소제목과 본문, 마무리, 별도 문단 `끝.` |
| 대표 이미지 | 정사각형 1:1 이미지 1장 |
| 섹션 이미지 | 본문의 각 `##` 소제목마다 고유한 이미지 1장, 기본 16:9 |
| 이미지 위치 | 대표 이미지는 도입 앞, 섹션 이미지는 해당 제목 아래 또는 첫 설명 문단 뒤 |
| 기본 파일 | `index.html`과 `images/`의 별도 이미지 파일을 담은 ZIP |
| 글·이미지 ZIP 용량 | ZIP 자체의 실제 크기 **10,000,000바이트 이하** |

예를 들어 본문에 `##` 소제목이 5개라면 대표 이미지 1장과 섹션 이미지 5장, 총 6장을 제작합니다. `###` 하위 제목은 기본 이미지 수에 포함하지 않습니다. 사용자가 글만, 이미지 수, 비율, 분량 등을 지정하면 그 조건을 우선합니다.

HTML은 ZIP 내부 이미지 파일을 상대경로로 참조합니다.

```html
<img src="images/대표이미지.png" alt="공유오피스 선택 기준을 설명하는 이미지">
```

이미지 데이터를 HTML에 base64로 넣지 않습니다. ZIP을 풀어 폴더를 옮겨도 이미지가 표시되도록 만들며, 글을 업로드하거나 전달할 때는 HTML과 이미지 폴더를 함께 사용합니다.

## 어떤 자료와 기능이 들어 있나요?

| 파일 | 역할 |
| --- | --- |
| [SKILL.md](SKILL.md) | 요청 해석, 근거 확인, 글쓰기, 이미지 제작, HTML·ZIP 납품 지침 |
| [references/style-guide.md](references/style-guide.md) | 말투, 문단 구성, 제목, 도입·마무리, 표현 기준 |
| [references/stock-articles.md](references/stock-articles.md) | 문체 참고용 블로그 글 100편 |
| [references/article-index.md](references/article-index.md) | 참고 글 제목 목록 |
| [references/visual-guide.md](references/visual-guide.md) | 사진·일러스트·차트 선택과 검수 기준 |
| [scripts/select_examples.py](scripts/select_examples.py) | 키워드와 글 유형에 맞는 참고 글 선택 |
| [scripts/make_kpi_infographic.py](scripts/make_kpi_infographic.py) | 입력한 수치로 2000×1125px 한글 KPI 도표 PNG 제작 |
| [scripts/validate_html_zip.py](scripts/validate_html_zip.py) | 글·이미지 ZIP의 용량과 이미지 참조 검사 |
| [assets/infographic-input-example.json](assets/infographic-input-example.json) | KPI 도표 입력 형식을 보여주는 가상 데이터 |
| [agents/openai.yaml](agents/openai.yaml) | 스킬 표시 이름과 기본 호출 안내 |
| [requirements.txt](requirements.txt) | Python 스크립트의 외부 라이브러리 의존성 |

문체 참고 글은 **과거에 작성된 예시**입니다. 현재 주가·금리·세율·정책·실적을 확인하는 자료로 사용하지 않습니다. 새 글에 필요한 최신 사실은 공식 발표와 원자료 등을 새로 확인하고, 근거와 작성자의 해석을 구분합니다. 참고 글의 개인 경험을 다른 사용자의 경험으로 바꾸거나, 제공받지 않은 투자·방문·가족 이야기를 만들어 쓰지 않습니다.

## 실행 환경에 필요한 기능

| 사용할 기능 | 필요한 실행 환경 |
| --- | --- |
| 문체를 참고한 글쓰기 | 첨부 문서나 스킬 파일을 읽을 수 있는 AI 에이전트 |
| 최신 뉴스·주가·정책 확인 | 웹 검색 또는 최신 공식 자료에 접근할 수 있는 도구 |
| 사진·일러스트 생성 및 편집 | 이미지 생성·편집 도구 |
| 도표 생성, HTML·ZIP 제작 및 검사 | Python·파일 실행 기능 또는 이에 해당하는 도구 |

검색이나 이미지 생성은 실행 환경이 제공하는 도구를 사용합니다. 필요한 도구가 없으면 가능한 범위와 미완료 항목을 구분해 안내하도록 스킬에 명시되어 있습니다.

## 사용 예시

**경제 용어 설명**

```text
@블루래더 콘텐츠 스튜디오
키워드: EBITDA
주제: 뜻, 영업이익과의 차이, 기업 분석에 사용할 때 주의할 점
독자: 주식투자를 시작한 직장인
2,500자 내외의 글과 섹션별 설명 이미지를 만들어줘.
```

**상품 비교**

```text
@블루래더 콘텐츠 스튜디오
키워드: ISA 연금저축
주제: 가입 조건과 절세 구조, 장단점 비교
현재 기준 공식 자료를 확인하고 기준일과 출처를 표시해줘.
숫자는 확인된 조건만 사용하고, 글과 비교 도표를 함께 만들어줘.
```

**기존 글 수정**

```text
@블루래더 콘텐츠 스튜디오
첨부한 글을 블루래더 문체로 다듬어줘.
오래된 숫자와 정책은 최신 자료로 확인해서 수정하고,
내가 적은 경험과 사실은 보존해줘.
이번에는 글만 제공해줘.
```

## Python 스크립트 직접 실행하기

Python 3.10 이상을 기준으로 사용합니다. 아래 명령은 저장소를 내려받거나 ZIP을 푼 뒤 `SKILL.md`가 있는 폴더에서 실행합니다. 시스템에서 명령 이름이 `python3`인 경우 `python`을 `python3`로 바꿉니다.

### 준비

```bash
python -m pip install -r requirements.txt
```

`make_kpi_infographic.py`는 **Pillow**와 한글을 지원하는 글꼴이 필요합니다. 참고 글 선택기와 글·이미지 ZIP 검증기는 Python 표준 라이브러리만 사용합니다.

### 참고 글 선택

```bash
python scripts/select_examples.py --query "ETF 장점 단점 비교" --mode compare --top 3
```

`--mode`는 `auto`, `issue`, `explain`, `compare`, `howto`를 지원합니다. 제목만 확인하려면 `--titles-only`를 추가합니다. 결과는 글쓰기 참고용이며 해당 글의 숫자나 제도가 현재도 유효하다는 뜻은 아닙니다.

### KPI 도표 만들기

```bash
python scripts/make_kpi_infographic.py --input assets/infographic-input-example.json --output output/summary.png
```

동봉된 JSON은 **가상 데이터**입니다. 실제 글에 사용할 때는 확인한 수치·단위·기준일·출처로 새 입력 JSON을 작성합니다. 스크립트는 입력값을 그림으로 만들며 자료의 사실관계를 자동 확인하지 않습니다.

글꼴을 자동으로 찾지 못하면 `--font`로 한글 글꼴의 실제 경로를 지정합니다. 굵은 글꼴은 `--bold-font`로 별도 지정할 수 있습니다. Windows에 맑은 고딕이 설치되어 있다면 다음과 같이 실행합니다.

```powershell
python scripts/make_kpi_infographic.py --input assets/infographic-input-example.json --output output/summary.png --font "C:/Windows/Fonts/malgun.ttf" --bold-font "C:/Windows/Fonts/malgunbd.ttf"
```

Linux와 macOS에서도 한글을 지원하는 `.ttf`, `.otf`, `.ttc` 파일의 실제 경로를 같은 옵션으로 지정할 수 있습니다. 예를 들어 Noto Sans CJK KR 등의 한글 글꼴을 사용할 수 있습니다.

### 완성된 글·이미지 ZIP 검사

```bash
python scripts/validate_html_zip.py output/article.zip
```

검증 대상은 설치용 스킬 ZIP이 아니라 **완성된 HTML 글과 이미지를 담은 ZIP**입니다. 루트 HTML 한 개, 별도 이미지 파일, 상대경로 참조, 10,000,000바이트 용량 제한 등을 검사합니다. 본문 이미지는 `<img>` 사용을 권장하며, CSS 이미지는 정적인 `url(...)` 참조를 사용합니다. 검사 후에는 HTML을 열어 이미지 배치와 한글·숫자의 가독성도 확인합니다.

## 배포용 ZIP 다시 만들기

저장소의 스킬 파일을 수정한 뒤 다음 명령으로 설치용 ZIP을 다시 만들 수 있습니다.

```bash
python scripts/build_skill_zip.py
python scripts/build_skill_zip.py --check
```

`dist/blue-ladder-content-studio.zip`과 `dist/blue-ladder-content-studio.zip.sha256` 체크섬 파일이 생성됩니다. `--check`는 배포 파일이 현재 소스와 일치하는지 확인합니다.

설치용 ZIP에는 `SKILL.md`, `agents`, `assets`, `references`, 실행용 스크립트, `requirements.txt`가 들어 있습니다. 저장소 안내 문서, ZIP 생성 스크립트, `dist`, 캐시·임시 파일은 설치 패키지에 포함하지 않습니다.
