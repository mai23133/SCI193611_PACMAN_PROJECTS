# คู่มือติดตั้งตั้งแต่ศูนย์จนได้ไฟล์ส่งงาน

คู่มือนี้ใช้กับโค้ดใน repository นี้โดยตรง คำสั่งรันของ Project 0, 1 และ 2
ต่างกัน จึงควรคัดลอกจากหัวข้อของโปรเจกต์นั้น

กลุ่มมี **3 คนตามข้อกำหนดใหม่ที่ผู้ใช้แจ้ง** วันที่ 23 กันยายน 2026
README ต้นฉบับยังมีข้อความ “สูงสุด 2 คน” และกำหนดส่งปี 2025
ให้ใช้ประกาศล่าสุดของอาจารย์สำหรับจำนวนสมาชิก กำหนดส่ง และช่องทางส่ง
รายงาน PDF เว้นชื่อผู้จัดทำตามที่ผู้ใช้ขอ

## 1. สิ่งที่ต้องเตรียม

1. คอมพิวเตอร์ Windows, macOS หรือ Linux
2. Python 3 พร้อม `pip` และ `venv` หรือใช้ Conda
3. Terminal และโปรแกรมแก้ไขโค้ด เช่น VS Code
4. โฟลเดอร์ repository นี้จาก Git หรือไฟล์ ZIP ที่แตกแล้ว
5. อินเทอร์เน็ตสำหรับติดตั้งแพ็กเกจครั้งแรก

สภาพแวดล้อมที่ใช้ตรวจงานครั้งนี้คือ Linux, Python 3.14.7
รุ่นแพ็กเกจที่ทดสอบจริงอยู่ใน `requirements-lock.txt`
ยังไม่ได้ทดสอบระบบ Windows/macOS จริง คำสั่งสำหรับระบบเหล่านั้นเป็นแนวทางติดตั้ง

ถ้ามีเฉพาะ Python แต่ไม่มี pip ให้ใช้ตัวติดตั้ง Python ที่รวม pip,
สภาพแวดล้อม Conda หรือ `uv` ตามวิธีด้านล่าง
บน Linux บางระบบต้องติดตั้งแพ็กเกจ `python3-venv` แยกต่างหาก

## 2. เปิดโฟลเดอร์ให้ถูกที่

เปิด Terminal ที่โฟลเดอร์ `SCI193611_PACMAN_PROJECTS`
ควรเห็น `README.md`, `requirements.txt`, `project0`, `project1`, `project2`
ในคำสั่งต่อไปนี้ คำว่า “root” หมายถึงโฟลเดอร์นี้

ไม่ต้องแตก `project0.zip`, `project1.zip`, `project2.zip` ทับโฟลเดอร์เดิม
ไฟล์ ZIP เหล่านั้นเป็นชุดเริ่มต้น ส่วนโค้ดที่ทำเสร็จอยู่ในโฟลเดอร์โปรเจกต์

## 3. สร้างสภาพแวดล้อม Python

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

หาก PowerShell ไม่อนุญาต activation ไม่จำเป็นต้องเปลี่ยนนโยบายทั้งเครื่อง
เรียก Python ของสภาพแวดล้อมโดยตรงได้ เช่น

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

เมื่อเข้า `project0` ให้เปลี่ยน path เป็น `..\.venv\Scripts\python.exe`
แทนคำว่า `python` ในตัวอย่าง

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

### ทางเลือก Conda

```bash
conda create -n pacman python=3.14
conda activate pacman
python -m pip install -r requirements-dev.txt
```

### ทางเลือก uv

หากเครื่องติดตั้ง `uv` ไว้แล้ว:

```bash
uv venv .venv
uv pip install --python .venv/bin/python -r requirements-dev.txt
source .venv/bin/activate
```

บน Windows ใช้ `.venv\Scripts\python.exe` และ activation แบบ Windows

เลือกวิธีใดวิธีหนึ่งก็เพียงพอ อย่าสร้าง Conda และ venv ซ้อนกันโดยไม่จำเป็น

## 4. เลือกแพ็กเกจตามงาน

| ไฟล์ | ใช้ทำอะไร |
|---|---|
| `requirements.txt` | รันเอเจนต์: NumPy และ SciPy |
| `requirements-dev.txt` | รันเกม ทดสอบ ตรวจสไตล์ สร้างกราฟ และตรวจ PDF |
| `requirements-lock.txt` | รุ่นแพ็กเกจทั้งหมดที่ติดตั้งในการตรวจครั้งนี้ |

หากต้องการแค่เล่นเกม ใช้ `python -m pip install -r requirements.txt`
หากต้องการทำครบทุกขั้นตอน ใช้ `requirements-dev.txt`
หากต้องการทำซ้ำด้วยรุ่นเดียวกับผลทดสอบ ใช้ `requirements-lock.txt`
ไฟล์ lock เป็นรายการที่ freeze จาก Linux/Python 3.14.7
ความพร้อมของ wheel บน Python หรือระบบอื่นอาจต่างกัน

ตรวจว่าเปิดสภาพแวดล้อมถูกตัว:

```bash
python -c "import sys, numpy, scipy; print(sys.executable); print(numpy.__version__, scipy.__version__)"
```

## 5. รัน Project 0: BFS และ A*

จาก root:

```bash
cd project0
python run.py --help
python run.py --agentfile bfs.py --layout small --silentdisplay
python run.py --agentfile astar.py --layout medium --silentdisplay
python run.py --agentfile astar.py --layout large --silentdisplay
python run.py --agentfile dfs.py --layout small --silentdisplay
cd ..
```

ผลลัพธ์มีข้อความชนะ คะแนน เวลาคำนวณ และจำนวนโหนดที่ขยาย
คำว่า `--silentdisplay` หมายถึงไม่เปิดหน้าต่างเกม
ถ้าต้องการดูภาพ ให้เอาตัวเลือกนี้ออก

BFS หาเส้นทางที่ใช้จำนวนก้าวน้อยที่สุด ส่วน A* ที่เขียนนี้คิดค่าปรับแคปซูลด้วย
ดังนั้นคะแนนของสองวิธีอาจต่างกันแม้จะชนะทั้งคู่
ตัวอย่างผลจริง: แผนที่ `small` ได้ BFS 497 และ A* 500
รายละเอียดการคิดต้นทุนอยู่ใน `CODE_EXPLANATION_TH.md`

## 6. รัน Project 1: Minimax และ H-Minimax

```bash
cd project1
python run.py --help
python run.py --agent minimax --ghost dumby --layout small_adv --seed 42 --nographics
python run.py --agent minimax --ghost smarty --layout small_adv --seed 42 --nographics
python run.py --agent hminimax --ghost greedy --layout medium_adv --seed 42 --nographics
python run.py --agent hminimax --ghost smarty --layout large_adv --seed 42 --nographics
cd ..
```

Project 1 ใช้ชื่อโมดูล เช่น `minimax` โดย **ไม่ใส่ `.py`**
ใช้ `--ghost` และ `--nographics` ไม่ใช่ `--ghostagent` / `--silentdisplay`

Minimax เต็มรูปแบบสร้างกราฟที่เข้าถึงได้ทั้งหมด จึงเหมาะกับแผนที่เล็กตามโจทย์
สำหรับ `medium_adv` และ `large_adv` ใช้ H-Minimax
โจทย์ยกเว้นการรัน Minimax บนสองแผนที่นี้
ทั้งสองเอเจนต์ออกแบบตามโจทย์ที่มีผีหนึ่งตัว และไม่ใช้แคปซูลในการประเมิน

## 7. รัน Project 2: Bayes filter และโบนัสล่าผี

```bash
cd project2
python run.py --help
python run.py --agentfile pacmanagent.py --bsagentfile bayesfilter.py --ghostagent scared --nghosts 3 --layout large_filter --sensorvariance 1 --seed 42 --silentdisplay
python run.py --agentfile pacmanagent.py --bsagentfile bayesfilter.py --ghostagent afraid --nghosts 3 --layout large_filter_walls --sensorvariance 4 --seed 42 --silentdisplay
cd ..
```

เปลี่ยนผีเป็น `confused`, `afraid`, `scared` ได้
ผีทั้งหมดในหนึ่งเกมใช้ชนิดเดียวกันตามข้อกำหนด
`--nghosts` กำหนดจำนวนสูงสุด แต่จำนวนจริงไม่เกินจุดเริ่มผีในแผนที่
ใช้ seed เดิมเพื่อทำซ้ำการสุ่ม และต้องระบุ `--bsagentfile bayesfilter.py`
คู่กับโบนัส `pacmanagent.py` เพราะ controller รับ belief เป็นอาร์กิวเมนต์ตัวที่สอง

หากต้องการควบคุม Pacman เองและดู belief:

```bash
cd project2
python run.py --agentfile humanagent.py --bsagentfile bayesfilter.py --ghostagent scared --nghosts 1 --layout large_filter --seed 42 --hiddenghosts
cd ..
```

## 8. เปิดหน้าต่างเกมและแก้ปัญหา Tk

เกมใช้ Tkinter ของ Python ซึ่งไม่ใช่แพ็กเกจที่ติดตั้งด้วย `pip install tkinter`
ทดสอบด้วย `python -m tkinter` ควรมีหน้าต่างเล็กเปิดขึ้น

ถ้าขาด Tk ให้ติดตั้งส่วน Tk/Tcl ที่เข้ากับ Python:

- Ubuntu/Debian: แพ็กเกจ `python3-tk` ของระบบ
- Arch Linux: แพ็กเกจ `tk` ที่ตรงกับ Python ของระบบ
- Windows: เปิดตัวเลือก Tcl/Tk ในตัวติดตั้ง Python
- macOS: ใช้ Python ที่มี Tk หรือแพ็กเกจ Tk ที่ตรงกับ Python นั้น

สภาพแวดล้อมทดสอบครั้งนี้ไม่มีไลบรารี Tk จึงตรวจเกมแบบไม่มีหน้าต่าง
ได้ปรับ `graphicsUtils.py` ของทั้งสามโปรเจกต์ให้ import ได้แม้ไม่มี Tk
ถ้ารันแบบกราฟิกโดยไม่มี Tk จะมีข้อความแจ้งให้ติดตั้ง แทนการล้มตั้งแต่ import
เครื่องแบบ server/SSH ที่ไม่มีจอแสดงผลควรใช้โหมดไม่มีหน้าต่าง

## 9. รันทดสอบและตรวจรูปแบบโค้ด

รันจาก root:

```bash
python -m pytest -q
python -m pycodestyle project0/bfs.py project0/astar.py project0/dfs.py project1/minimax.py project1/hminimax.py project2/bayesfilter.py project2/pacmanagent.py project2/experiments.py scripts tests
python scripts/benchmark.py
```

`pytest` ตรวจคุณสมบัติอัลกอริทึมและกรณีขอบ
`pycodestyle` ถ้าผ่านจะไม่พิมพ์ข้อผิดพลาด
`benchmark.py` เรียก CLI เกมจริง 45 กรณีและบันทึก `docs/benchmark.json`
แต่ละเกมมี timeout 90 วินาที; สคริปต์คืนรหัสผิดพลาดถ้ามีเกมไม่ชนะหรือรันล้ม
จำนวนโหนดและคะแนนมีประโยชน์กว่าเวลาเมื่อต้องเปรียบเทียบข้ามเครื่อง
benchmark รันพร้อมกันได้สาม process จึงมีการแข่งขันใช้ CPU

## 10. สร้างผลทดลองและกราฟ Project 2

```bash
python project2/experiments.py --trials 30 --steps 1800 --ghosts 3 --seed 193611
```

ใช้เวลามากกว่าการเล่นเกมหนึ่งรอบ เพราะมี 18 เงื่อนไข:
2 แผนที่ × 3 ชนิดผี × 3 ระดับความแปรปรวนเซนเซอร์
แต่ละเงื่อนไขมี 30 trials และ 3 ผี
variance 0.25 และ 1 ใช้ 1,800 steps; variance 4 ใช้ 9,000 steps
เพราะการลดความกำกวมของเซนเซอร์ที่ noise สูงใช้เวลานานกว่า
เปลี่ยนระยะหลังด้วย `--high-noise-steps` ได้

ไฟล์ผลลัพธ์ใน `project2/results/`:

- `trials.npz`: เส้นข้อมูลของทุก trial เพื่อวิเคราะห์ซ้ำ
- `summary.json`: การตั้งค่า ค่าเฉลี่ย ช่วงความเชื่อมั่น และการเปลี่ยนแปลงช่วงท้าย
- `convergence.pdf` / `.png`: entropy และ Brier score ตามเวลา ที่ variance 1
- `variance.pdf` / `.png`: ผลของ variance 0.25, 1, 4 ต่อ entropy

สำหรับลองระบบเร็ว ๆ โดยไม่ทับผลจริง:

```bash
python project2/experiments.py --trials 3 --steps 12 --high-noise-steps 12 --output project2/results-smoke
```

ผลจากคำสั่งสั้นมีไว้ตรวจว่ารันได้เท่านั้น ไม่เพียงพอสำหรับข้อสรุปในรายงาน
การทดลองหลักให้ Pacman อยู่นิ่งและไม่กินผี เพื่อให้ทุก trial มีระยะเวลาเท่ากัน
การทดสอบ controller ที่เดินจริงและกินผีอยู่ใน benchmark อีกชุดหนึ่ง

## 11. สร้างรายงาน PDF

มี `project2/report.pdf` และ `project2/report.tex` ที่สร้างไว้แล้ว
รายงานใช้ภาษาอังกฤษและเว้นชื่อผู้จัดทำตามคำขอ
ไม่จำเป็นต้องติดตั้ง LaTeX เพื่อเปิด PDF ที่มีอยู่

หากต้องการสร้างใหม่ ให้ติดตั้ง Tectonic หรือ TeX Live/MiKTeX ที่มี `pdflatex`
จากนั้นรันจาก root:

```bash
python scripts/build_report.py
```

หาก executable ไม่อยู่ใน PATH:

```bash
python scripts/build_report.py --engine /path/to/tectonic
```

Tectonic อาจดาวน์โหลดแพ็กเกจ LaTeX และฟอนต์เมื่อใช้ครั้งแรก
สคริปต์อ่านตัวเลขจาก `summary.json`, เติมคำตอบในเทมเพลตเดิม และตรวจว่าไม่เกิน 5 หน้า
ไม่ได้เพิ่มชื่อสมมติ และคงหัวข้อ/ลำดับคำถาม/ช่องที่โจทย์ให้เว้นว่างไว้

สร้างเฉพาะ source โดยยังไม่มี LaTeX:

```bash
python scripts/build_report.py --source-only
```

หากจะใส่ชื่อในอนาคต ให้แก้ `\author{}` ใน `report.tex` แล้วคอมไพล์ไฟล์นั้นโดยตรง
การรัน `build_report.py` อีกครั้งจะสร้าง source ใหม่และเว้นชื่ออีกครั้ง
เทมเพลตต้นฉบับ `template-project2.tex` ไม่ถูกแก้

## 12. สร้างชุดส่งงาน

```bash
python scripts/package_submissions.py
```

จะได้:

| ไฟล์ | เนื้อหาที่บรรจุ |
|---|---|
| `deliverables/project0.tar.gz` | `bfs.py`, `astar.py` |
| `deliverables/project1.tar.gz` | `minimax.py`, `hminimax.py` |
| `deliverables/project2.tar.gz` | `bayesfilter.py`, `pacmanagent.py`, `report.pdf` |
| `deliverables/manifest.json` | SHA-256 ของ archive และไฟล์แต่ละตัว |

Project 0–1 โจทย์ขอไฟล์ Python โดยตรง ถ้าฟอร์มให้แนบแยกไฟล์
ให้เลือกไฟล์ในโฟลเดอร์โปรเจกต์ ไม่จำเป็นต้องใช้ archive
Project 2 ระบุ `.tar.gz` โดยตรง และโบนัส `pacmanagent.py` รวมให้แล้ว

หากแก้โค้ดหรือรายงานภายหลัง ต้องรันทดสอบและสร้าง archive ใหม่
สคริปต์ไม่ส่งงานให้อาจารย์อัตโนมัติ

## 13. รายการตรวจตอนจะส่งจริง

1. ตรวจประกาศอาจารย์ล่าสุดเรื่องสามคน วันส่ง และช่องทางส่ง
2. อ่านและอธิบายโค้ดส่วนที่ตนรับผิดชอบได้
3. รัน tests และเกมตัวอย่างได้จากเครื่องของสมาชิก
4. ตรวจว่า PDF เปิดได้ ไม่เกิน 5 หน้า และผลตรงกับกราฟ
5. ถ้าอาจารย์ต้องการชื่อ/รหัสใน PDF ให้เติมก่อนส่งจริง; ตอนนี้เว้นไว้ตามคำขอ
6. เลือกไฟล์ที่ชื่อถูกต้อง โดยเฉพาะ `report.pdf` และ `bayesfilter.py`
7. เก็บเครดิตและเงื่อนไขการใช้ต้นฉบับ UC Berkeley ที่อยู่ในไฟล์ไว้

## 14. อาการผิดพลาดที่พบบ่อย

| อาการ | วิธีตรวจและแก้ |
|---|---|
| `No module named numpy/scipy` | เช็ก `sys.executable` แล้วติดตั้งด้วย `python -m pip` ตัวเดียวกัน |
| `No module named pip` | ใช้ Python ที่รวม pip, Conda หรือ uv |
| `unrecognized arguments` | เช็ก project และ `python run.py --help`; flags ต่างกัน |
| ไม่พบ layout หรือ module | เข้าโฟลเดอร์ `project0/1/2` ก่อนเรียก `run.py` |
| human agent ใช้ headless ไม่ได้ | ใช้เอเจนต์อัตโนมัติ หรือเปิดกราฟิกพร้อม Tk |
| ไม่มี DISPLAY / TclError | ใช้ `--silentdisplay` หรือ `--nographics` ตามโปรเจกต์ |
| Minimax ใช้เวลามากบนแผนที่ใหญ่ | ใช้ H-Minimax ตามขอบเขตโจทย์ |
| สร้างรายงานไม่ได้ | ตรวจ LaTeX executable, อินเทอร์เน็ตครั้งแรก และผลทดลองที่ต้องมี |
| PDF/กราฟไม่ตรงหลังทดลองใหม่ | รัน `build_report.py` แล้ว `package_submissions.py` ใหม่ |

อ่านต่อ: [ขั้นตอนทำงานและแบ่งงานสามคน](WORKFLOW_TH.md)
และ [เหตุผล/การทำงานของโค้ด](CODE_EXPLANATION_TH.md)
