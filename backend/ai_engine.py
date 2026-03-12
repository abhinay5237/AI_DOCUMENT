
import os
import re
import hashlib
import gdown
from rapidfuzz import fuzz
from document_rules import REQUIRED_DOCUMENTS
from ocr_utils import extract_text_from_pdf
TOTAL_REQUIRED_DOCS = len(REQUIRED_DOCUMENTS)
# ---------------- CLEAN TEXT ----------------
def clean_text(text):
    text = re.sub(r"[^a-zA-Z0-9\s:/-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.lower()
# ---------------- DOCUMENT TYPE DETECTOR ----------------
def detect_document_type(text):
    t = clean_text(text)
    # ---------------- AADHAAR ----------------
    if re.search(r"\d{4}\s?\d{4}\s?\d{4}", text):
        if "aadhaar" in t or "uidai" in t or "government of india" in t:
            return "aadhaar"
        
     # ---------------- PASSPORT ----------------
    if "passport" in t and "republic of india" in t:
        return "passport"
    
    # MRZ detection
    if re.search(r"P<IND", text) or re.search(r"PSIND", text):
        return "passport"
    # Passport number (1 letter + 7 digits)
    if re.search(r"\b[A-Z][0-9]{7}\b", text):
        return "passport"
    
    # ---------------- PAN STRONG ----------------
    # perfect PAN
    if re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", text):
        return "Pancard"
    # OCR broken PAN (last char missing)
    if re.search(r"[A-Z]{5}[0-9]{4}", text):
        if "income" in t or "tax" in t or "permanent" in t:
            return "Pancard"
    # PAN with name + DOB pattern
    if ("income" in t or "tax" in t) and re.search(r"\d{2}[/-]\d{2}[/-]\d{4}", text):
        return "Pancard"
    # PAN fallback — name + DOB only
    if re.search(r"[A-Z]{3,}\s[A-Z]{3,}", text) and re.search(r"\d{2}[/-]\d{2}[/-]\d{4}", text):
        if len(text) < 1200:  # small document → usually PAN
            return "Pancard"
   
    # ---------------- BANK ----------------
    if "account" in t and ("statement" in t or "ifsc" in t or "bank" in t or "name of the account holder" in t):
        return "bank_statement"
    
    # ---------------- OFFER LETTER ----------------
    if "official offer of admission" in t and "dear" in t:
        return "offer_letter"
    
    # ---------------- SOP ----------------
    if "statement of purpose" in t and ("name" in t or "sop" in t):
        return "sop"
    
    # ----------------english_test ----------------
    if any (word in t for word in [ 
        "ielts","toefl","pte","duolingo",
        "listening", "reading", "writing", "speaking","overallscore",
        "literacy","comprehension","production"]):
        return "english_test"
    

     # ----------------Inter Memo ----------------
    if any (word in t for word in [ 
        "INTERMEDIATE PASS CERTIFICATE-CUM-MEMORANDUM OF MARKS","intermediate public examination",
        "Telangana State Board of Intermediate Education","This is to certify that",
        "Optional Subjects","In Words","Maximum Marks"," Marks Secured","mathematics -A","mathematics -B",
        "physics", "chemistry", "physics practicals", "chemistry practicals", "biology","histroy","economics"]):
        return "Inter Memo"
    
    # ---------------- academic_transcript ----------------
    if any(word in t for word in [
        "transcript","memorandum of grades","result",
       "subjects registered","credits","appeared","passed","semester grade point average","subject code",
       "memo no","cgpa","result","degree certificate","name of the college", 
        "Consolidated Memo Of Marks Grades And Credits","Hall Ticket No",
       "Serial. No","Month & Year of Final Exam","class awarded","number of credits registered and secured are",
       "aggregate marks" ]):

        return "academic_transcript"

    
    # ---------------- RESUME ---------------- 
    if any(word in t for word in [
        "education", "career objective", "@gmail.com",
        "projects", "skills"]):
        return "resume"

    return None

# ---------------- DOWNLOAD FROM DRIVE ----------------
def download_drive_folder(drive_link, download_path="uploads"):
    print("\nDOWNLOADING FROM DRIVE LINK:", drive_link)
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    try:
        # convert drive folder link to gdown format
        if "folders" in drive_link:
            folder_id = drive_link.split("folders/")[1].split("?")[0]
            url = f"https://drive.google.com/drive/folders/{folder_id}"
        else:
            print("Invalid drive folder link")
            return []
        gdown.download_folder(url=url, output=download_path, quiet=False, use_cookies=False)
        # collect files
        files = []
        for root, dirs, filenames in os.walk(download_path):
            for f in filenames:
                if f.lower().endswith((".pdf", ".jpg", ".jpeg", ".png")):
                    files.append(os.path.join(root, f))
        print("DOWNLOADED FILES:", files)
        return files
    except Exception as e:
        print("DRIVE DOWNLOAD ERROR:", str(e))
        return []

# ---------------- GET FILES ----------------
def collect_all_files(upload_folder=None, drive_link=None):
    all_files = []
    if upload_folder and os.path.exists(upload_folder):
        for f in os.listdir(upload_folder):
            all_files.append(os.path.join(upload_folder, f))
    if drive_link:
        drive_folder = download_drive_folder(drive_link)
        if drive_folder:
            for f in os.listdir(drive_folder):
                all_files.append(os.path.join(drive_folder, f))
    return all_files
# ---------------- NAME VALIDATION ----------------
def is_valid_person_name(name):
    if not name:
        return False
    n = name.lower().strip()
    if len(n.split()) < 2:
        return False
    if re.search(r"\d", n):
        return False
    if not re.search(r"[a-z]{3,}\s[a-z]{3,}", n):
        return False
    return True
# ---------------- NAME EXTRACT ----------------
def extract_name(text, doc_type=None):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    clean = []
    for l in lines:
        cl = re.sub(r"[^A-Za-z\s]", " ", l)
        cl = re.sub(r"\s+", " ", cl).strip()
        if len(cl) > 2:
            clean.append(cl)
    lines = clean
    raw_text = text 
    
# =====================================================
# 🔥 INTER MEMO (TSBIE)
# =====================================================
    if doc_type == "Inter Memo":

    # Extract only the line that contains the phrase
        for line in raw_text.splitlines():
            if "This is to certify that" in line:

            # Extract name after the phrase (same line only)
                name_part = line.split("This is to certify that")[-1]

            # Clean unwanted characters
                name_part = re.sub(r"[^A-Za-z\s]", "", name_part)

                return name_part.strip().title()

    # =====================================================
    # 🔥 DEGREE CERTIFICATE
    # =====================================================
    if doc_type == "degree_certificate":
        m = re.search(r"Name\s*:?\s*([A-Z]+(?: [A-Z]+)*)", raw_text)
        if m:
            name = m.group(1)
        
            return name.strip().title()

    # =====================================================
    # 🔥 TRANSCRIPT
    # =====================================================
    if doc_type == "academic_transcript":
        m = re.search(r"Name\s*:?\s*([A-Z]+(?: [A-Z]+)*)", raw_text)
        if m:
            name = m.group(1)

            return name.strip().title()
    # =====================================================
    # 🔥 PASSPORT FINAL UNIFIED VERSION (CLEAN & STRONG)
    # =====================================================
    if doc_type == "passport":

        lines_raw = raw_text.split("\n")
        raw_upper = raw_text.upper()

       # =========================
        # 1️⃣ JSON STYLE PASSPORT (STRONG FIX)
        # =========================
        g = re.search(r'\[\s*"Given Name"\s*,\s*"([^"]+)"\s*\]', raw_text, re.IGNORECASE)
        s = re.search(r'\[\s*"Surname"\s*,\s*"([^"]+)"\s*\]', raw_text, re.IGNORECASE)

        if g and s:
            given = g.group(1).strip()
            surname = s.group(1).strip()

            full = f"{given} {surname}".strip()

            if is_valid_person_name(full):
                return full.title()
        # =========================
        # 2️⃣ MRZ (STRONGEST)
        # =========================
        for line in lines_raw:

            if "P<IND" in line or "PSIND" in line:

                clean = re.sub(r"[^A-Z<]", "", line.upper())
                clean = clean.replace("PSIND", "P<IND")
                clean = re.sub(r"^P<IND", "", clean)

                parts = clean.split("<<")

                if len(parts) >= 2:
                    surname = parts[0].replace("<", "").strip()
                    given = parts[1].replace("<", "").strip()

                    if len(surname) >= 2 and len(given) >= 2:
                        full = f"{given} {surname}".strip()
                        if is_valid_person_name(full):
                            return full.title()

        # =========================
        # 3️⃣ GIVEN / SURNAME LABEL
        # =========================
        given = None
        surname = None

        g = re.search(r"(?i)given\s*name[:\s\"']+([A-Z][A-Z\s]{2,})", raw_upper)
        if g:
            given = g.group(1).strip()

        s = re.search(r"(?i)surname[:\s\"']+([A-Z][A-Z\s]{2,})", raw_upper)
        if s:
            surname = s.group(1).strip()

        if not given:
            for i, l in enumerate(lines_raw):
                if "given name" in l.lower() and i + 1 < len(lines_raw):
                    given = re.sub(r"[^A-Z\s]", "", lines_raw[i+1].upper()).strip()
                    break

        if not surname:
            for i, l in enumerate(lines_raw):
                if "surname" in l.lower() and i + 1 < len(lines_raw):
                    surname = re.sub(r"[^A-Z\s]", "", lines_raw[i+1].upper()).strip()
                    break

        if given and surname:
            full = f"{given} {surname}".strip()
            if is_valid_person_name(full):
                return full.title()

        # =========================
        # 4️⃣ VISUAL STACKED TEXT
        # =========================
        blocked = [
            "INDIA", "TELANGANA", "WARANGAL",
            "HYDERABAD", "PASSPORT"
        ]

        clean_lines = []

        for l in lines_raw:
            cl = re.sub(r"[^A-Za-z\s]", "", l).strip().upper()
            if cl and not any(b in cl for b in blocked):
                clean_lines.append(cl)

        for i in range(len(clean_lines) - 1):
            l1 = clean_lines[i]
            l2 = clean_lines[i + 1]

            if re.fullmatch(r"[A-Z]{3,}", l1) and \
               re.fullmatch(r"[A-Z]{3,}", l2):

                candidate = f"{l2} {l1}".strip()

                if is_valid_person_name(candidate):
                    return candidate.title()

        return None
    
    # =====================================================
    # 🔥 BANK STATEMENT NAME
    # =====================================================
    if doc_type == "bank_statement":
        m = re.search(
            r"Name of the Account Holder\s*\n?\s*(Mr|Mrs|Ms|Miss|Dr)\.?\s*([A-Za-z\s]+)",
            raw_text,
            re.IGNORECASE
        )
        if m:
            candidate = m.group(2).strip()

            candidate = re.sub(r"\s+", " ", candidate)
            if is_valid_person_name(candidate):
                return candidate.title()
    # =====================================================
    # 🔥 OFFER LETTER NAME
    # =====================================================
    if doc_type == "offer_letter":
        m = re.search(r"Dear\s+([A-Za-z]+\s+[A-Za-z]+)", raw_text)
        if m:
            candidate = m.group(1).strip()
            if is_valid_person_name(candidate):
                return candidate.title()

   
    # =========================================================
    # 🔥 NEW: NAME FIELD
    # =========================================================
    nm = re.search(r"(?i)\bname[:\s]+([A-Z][A-Z\s]{3,})", raw_text)
    if nm:
        candidate = nm.group(1).strip()
        if is_valid_person_name(candidate):
            return candidate
    # ---------- PAN NAME ----------
    for i, line in enumerate(lines):
        if re.search(r"[A-Z]{5}[0-9]{4}[A-Z]", line) or re.search(r"[A-Z]{5}[0-9]{4}", line):
            for j in range(i-1, max(i-6, -1), -1):
                candidate = lines[j]
                if any(x in candidate.lower() for x in ["income","tax","department","govt"]):
                    continue
                if is_valid_person_name(candidate):
                    return candidate
    # =====================================================
    # 🔥 AADHAAR SPECIAL LOGIC
    # =====================================================
    if doc_type == "aadhaar":
        for i, line in enumerate(lines):
            # Find English name after "To"
            if line.lower().startswith("to"):
                # Next 3 lines normally:
                # Telugu Name
                # English Name
                # Father Name
                if i + 2 < len(lines):
                    english_name = lines[i + 1]
                    father_name = lines[i + 2]
                    # Clean both
                    english_name = re.sub(r"[^A-Za-z\s]", "", english_name).strip()
                    father_name = re.sub(r"[^A-Za-z\s]", "", father_name).strip()
                    if is_valid_person_name(english_name):
                        return english_name
        # Fallback: name near DOB
        for i, line in enumerate(lines):
            if re.search(r"\d{2}[/-]\d{2}[/-]\d{4}", line):
                if i > 0:
                    possible = re.sub(r"[^A-Za-z\s]", "", lines[i - 1]).strip()
                    if is_valid_person_name(possible):
                        return possible
    
    # ---------- ALL CAPS ----------
    for line in lines:
        if re.fullmatch(r"[A-Z]{3,}\s[A-Z]{3,}", line):
            return line
    return None


# -------------------------------------------------
# HELPER: Clean text lines
# -------------------------------------------------
def clean_line(line):
    line = line.strip()
    line = re.sub(r"[^A-Za-z ]", "", line)
    return line.strip()


# -------------------------------------------------
# HELPER: Check if looks like real human name
# -------------------------------------------------
def looks_like_name(text):

    if not text:
        return False

    text = text.replace(" ", "").upper()

    # Too short
    if len(text) < 5:
        return False

    # Contains digits
    if any(char.isdigit() for char in text):
        return False

    # Must contain at least 2 vowels
    vowels = sum(1 for c in text if c in "AEIOU")
    if vowels < 2:
        return False

    # Reject too many consonants in a row (OCR garbage filter)
    if re.search(r"[BCDFGHJKLMNPQRSTVWXYZ]{5,}", text):
        return False

    # Reject repeating random patterns
    if len(set(text)) < 4:
        return False

    garbage_words = [
        "INCOME", "TAX", "DEPARTMENT", "GOVT",
        "INDIA", "PERMANENT", "ACCOUNT", "NUMBER"
    ]

    if any(word in text for word in garbage_words):
        return False

    return True

# -------------------------------------------------
# HELPER: Split joined names like ABHINAYJAMBULA
# -------------------------------------------------
def split_joined_name(name):
    if " " in name:
        return name.upper()

    # Try split in middle
    for i in range(3, len(name)-2):
        left = name[:i]
        right = name[i:]

        if looks_like_name(left) and looks_like_name(right):
            return f"{left.upper()} {right.upper()}"

    return name.upper()


def normalize_pan_name(name):
    if not name:
        return None

    # 1️⃣ Remove all unwanted spaces
    name = re.sub(r"\s+", "", name.upper())

    return name


def smart_merge_pan_names(person_name, father_name):
    """
    Dynamically detect surname using father's name.
    Works for any surname length.
    """

    if not person_name:
        return None, None

    person = normalize_pan_name(person_name)
    father = normalize_pan_name(father_name)

    # If father exists, try extracting surname from father
    surname = None

    if father and len(father) > 4:
        
        for i in range(4, min(15, len(father))):
            possible_surname = father[-i:]
            if person.endswith(possible_surname):
                surname = possible_surname
                break

    # If surname found dynamically
    if surname:
        first_name = person[:-len(surname)]
        father_first = father[:-len(surname)]
        return f"{first_name} {surname}", f"{father_first} {surname}"

    # Fallback: just return cleaned full names
    return person, father

# -------------------------------------------------
# MAIN PAN EXTRACTION FUNCTION
# -------------------------------------------------
def extract_pan_details(text):

    details = {
        "pan_number": None,
        "name": None,
        "father_name": None,
        "dob": None
    }

    if not text:
        return details

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # -------------------------------------------------
    # PAN NUMBER
    # -------------------------------------------------
    pan_match = re.search(r"[A-Z]{5}[0-9]{4}[A-Z]", text.upper())
    if pan_match:
        details["pan_number"] = pan_match.group()

    # -------------------------------------------------
    # DOB
    # -------------------------------------------------
    dob_pattern = r"\b\d{2}[-/]?\d{2}[-/]?\d{4}\b"
    dob_index = None

    for i, line in enumerate(lines):
        m = re.search(dob_pattern, line)
        if m:
            dob_raw = m.group()

            if len(dob_raw) == 8:
                dob_raw = f"{dob_raw[0:2]}-{dob_raw[2:4]}-{dob_raw[4:]}"
            else:
                dob_raw = dob_raw.replace("/", "-")

            details["dob"] = dob_raw
            dob_index = i
            break

    # =====================================================
    # 🔥 STRONG PAN STRUCTURE LOGIC (WITH OR WITHOUT DOB)
    # =====================================================

    search_start = dob_index if dob_index is not None else len(lines)

    all_candidates = []

    for i in range(search_start - 1, max(search_start - 15, -1), -1):
        candidate_raw = clean_line(lines[i])
        candidate = split_joined_name(candidate_raw)

        if looks_like_name(candidate):
            all_candidates.append(candidate.upper())

    # Remove duplicates
    seen = set()
    filtered = []
    for name in all_candidates:
        if name not in seen:
            filtered.append(name)
            seen.add(name)

    # -------------------------------------------------
    # SURNAME MATCHING
    # -------------------------------------------------

    if len(filtered) >= 2:

        filtered_no_space = [n.replace(" ", "") for n in filtered]
        surname = None

        for length in range(10, 2, -1):
            endings = {}

            for name in filtered_no_space:
                if len(name) >= length:
                    end = name[-length:]
                    endings[end] = endings.get(end, 0) + 1

            for end, count in endings.items():
                if count >= 2:
                    surname = end
                    break

            if surname:
                break

        if surname:
            matched = [n for n in filtered_no_space if n.endswith(surname)]

            if len(matched) >= 2:
                father_raw = matched[0]
                person_raw = matched[1]

                person_first = person_raw[:-len(surname)]
                father_first = father_raw[:-len(surname)]

                details["name"] = f"{person_first} {surname}".strip()
                details["father_name"] = f"{father_first} {surname}".strip()

    # =====================================================
    # 🔥 FINAL FALLBACK (FULL TEXT SCAN)
    # =====================================================

    if not details["name"]:

        fallback = []

        for line in lines:
            candidate_raw = clean_line(line)
            candidate = split_joined_name(candidate_raw)

            if looks_like_name(candidate):
                fallback.append(candidate.upper())

        fallback = list(dict.fromkeys(fallback))  # remove duplicates

        if len(fallback) >= 2:
            details["father_name"] = fallback[0]
            details["name"] = fallback[1]

    return details

# ---------------- DOB EXTRACT ----------------
def extract_dob(text):
    # 1️⃣ Direct DOB match (DOB: 12/08/2001 or 12-08-2001)
    m = re.search(
        r"(?i)(dob|date of birth)[^\d]*(\d{2}[/-]\d{2}[/-]\d{4})",
        text
    )
    if m:
        return m.group(2)

    # 2️⃣ Find all date patterns
    dates = re.findall(r"\d{2}[/-]\d{2}[/-]\d{4}", text)

    for d in dates:
        # Split using both / and -
        parts = re.split(r"[/-]", d)

        if len(parts) == 3:
            try:
                year = int(parts[2])
                if 1950 < year < 2015:
                    return d
            except ValueError:
                continue  # skip bad formats safely

    # 3️⃣ Year of birth only
    m = re.search(r"(?i)year of birth[:\s]*(\d{4})", text)
    if m:
        return m.group(1)

    return None
# ---------------- ADDRESS EXTRACT ----------------
def extract_aadhaar_details(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    name = None
    dob = None
    address = None
    # ================= FIND FIRST DOB =================
    dob_index = None
    for i, line in enumerate(lines):
        if "dob" in line.lower() or "date of birth" in line.lower():
            match = re.search(r"\b\d{2}/\d{2}/\d{4}\b", line)
            if match:
                dob = match.group()
                dob_index = i
                break  # IMPORTANT: only first DOB

 # ================= NAME (STRICT: ABOVE DOB) =================
    if dob_index is not None:
        for i in range(dob_index - 1, max(dob_index - 7, -1), -1):
            candidate = lines[i]
            candidate_clean = re.sub(r"[^A-Za-z\s]", "", candidate).strip()
            words = candidate_clean.split()
            # Remove single-letter words (like stray 'O')
            words = [w for w in words if len(w) > 1]
            candidate_clean = " ".join(words)
            if (
                len(words) >= 2
                and not any(word in candidate_clean.lower() for word in [
                    "government", "india", "aadhaar",
                    "authority", "uidai", "vid",
                    "male", "female","Mobile"
                ])
            ):
                name = candidate_clean.title()
                break
    # ================= ADDRESS (FIRST BLOCK ONLY) =================
    address_lines = []
    capture = False
    for line in lines:
        # Start capturing when house number found
        if re.search(r"\d+-\d+/\d+", line):
            capture = True
        if capture:
            # Stop at disclaimer
            if "proof of identity" in line.lower():
                break
            address_lines.append(line)
            # Limit to 10 lines max
            if len(address_lines) >= 10:
                break
    if address_lines:
        address = " ".join(address_lines)
    return {
        "name": name,
        "dob": dob,
        "address": address
    }

# =====================================================
# 🔥 FINAL STRONG BANK ADDRESS EXTRACTOR
# =====================================================
def extract_bank_address(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    address_lines = []

    for i, line in enumerate(lines):

        # Detect house number pattern like 1-460/5
        if re.search(r"\d+-\d+/\d+", line):

            for j in range(i, len(lines)):

                current = lines[j]

                # 🚨 STOP CONDITIONS
                if re.search(r"\b\d{6}\b", current):  # Stop after PIN
                    address_lines.append(current)
                    break

                if re.search(r"\b\d{2}X{4,}\d{2}\b", current):  # masked mobile
                    break

                if any(word in current.lower() for word in [
                    "silver", "gold", "platinum",
                    "mode of operation",
                    "branch",
                    "ifsc",
                    "micr",
                    "account",
                    "transaction"
                ]):
                    break

                address_lines.append(current)

            break  # stop outer loop once address captured

    if address_lines:
        address = " ".join(address_lines)
        address = re.sub(r"\s+", " ", address).strip()
        return address

    return None

# ---------------- NORMALIZE NAME ----------------
def normalize_name(name):
    if not name:
        return None
    name = re.sub(r"[^A-Za-z\s]", " ", name)
    name = re.sub(r"\s+", " ", name).strip().lower()
    words = name.split()
    if len(words) < 2:
        return None
    # 🔥 SORT WORDS (CRITICAL FIX)
    words = sorted(words)
    return " ".join(words)

# ---------------- HASH ----------------
def text_fingerprint(text):
    return hashlib.md5(text.encode()).hexdigest()

# ---------------- NORMALIZE DOB ----------------
def normalize_dob(dob):
    if not dob:
        return None
    dob = dob.replace("/", "-").strip()
    return dob

# ---------------- SAME PERSON CHECK ----------------
def check_same_person(person_data):

    names = [p["name"] for p in person_data if p["name"] and p["name"] != "unknown"]
    dobs = [
        normalize_dob(p["dob"])
        for p in person_data
        if p["dob"] and p["dob"].lower() != "unknown"
    ]

    if len(names) <= 1:
        return "Not enough data", None

    # 🔥 Find most common name (majority voting)
    name_counts = {}
    for n in names:
        name_counts[n] = name_counts.get(n, 0) + 1

    majority_name = max(name_counts, key=name_counts.get)

    mismatch_names = []

    for n in names:
        score = fuzz.token_sort_ratio(majority_name, n)
        if score < 75:
            mismatch_names.append(n)

    # DOB check
    dob_same = len(set(dobs)) == 1 if dobs else True
    dob_variation = list(set(dobs)) if not dob_same else []

    insights = []

    if mismatch_names:
        name_varition = list(set(names))
       
        return "DIFFERENT PERSON", {
            "name_mismatch": True,
            "name_varition": name_varition,        
            "dob_mismatch": not dob_same,
            "dob_variation": dob_variation
        }

    if not dob_same:
        return "POSSIBLE SAME PERSON", {
            "name_mismatch": False,
            "name_variation": [],
            "dob_mismatch": True,
            "dob_variation": dob_variation
        }

    return "VERIFIED SAME PERSON", {
        "name_mismatch": False,
        "name_variation": [],
        "dob_mismatch": False,
        "dob_variation": []
    }

# ================= MAIN ENGINE =================
def analyze_documents(upload_folder=None, drive_link=None):
    print("\n ANALYZE FUNCTION STARTED \n", flush=True)
    detected = {}
    weak_docs = []
    missing = []
    person_data = []
    content_hashes = {}
    uploaded_required_docs = set()
    insights = []
    all_files = collect_all_files(upload_folder, drive_link)
    print("FILES RECEIVED:", all_files)
    for path in all_files:
        file = os.path.basename(path)
        if not file.lower().endswith(".pdf"):
            weak_docs.append({"file": file, "reason": "Upload PDF only"})
            continue
        raw = extract_text_from_pdf(path)
        print("\n========= OCR TEXT =========\n")
        print(raw)
        print("\n============================\n")
        if not raw.strip():
            weak_docs.append({"file": file, "reason": "Unreadable PDF"})
            continue
        text = clean_text(raw)
        fp = text_fingerprint(text)
        if fp in content_hashes:
            weak_docs.append({"file": file, "reason": "Duplicate file"})
            continue
        content_hashes[fp] = file
        # -------- DOCUMENT TYPE DETECT --------
        best_match = detect_document_type(raw)
        print("DETECTED TYPE:", best_match)
        # =====================================================
        # 🔥 AADHAAR SPECIAL HANDLING
        # =====================================================
        if best_match == "aadhaar":
            aadhaar_data = extract_aadhaar_details(raw)
            raw_name = aadhaar_data["name"] if aadhaar_data["name"] else "Unknown"
            dob = aadhaar_data["dob"]
            address = aadhaar_data["address"]
        elif best_match == "Pancard":
            pan_data = extract_pan_details(raw)
            print("DEBUG PAN DATA:", pan_data)   # ✅ ADD THIS LINE
            raw_name = pan_data["name"]
            dob = pan_data["dob"]
            address = None

        else:
            raw_name = extract_name(raw, best_match)
            dob = extract_dob(raw)
            address = None

            if best_match == "bank_statement":
                address = extract_bank_address(raw)

        # -------- NORMALIZE NAME --------
        if not raw_name:
            raw_name = "Unknown"
        name_clean = normalize_name(raw_name)
        if not name_clean:
            name_clean = "unknown"
        print("\nAI DETECTED:", file)
        print("Raw Name:", raw_name)
        print("Clean Name:", name_clean)
        print("DOB:", dob)
        print("Address:", address)
        if not best_match:
            weak_docs.append({"file": file, "reason": "Unknown document"})
        else:
            detected[best_match] = file
            uploaded_required_docs.add(best_match)
        person_data.append({
            "file": file,
            "name": name_clean,
            "dob": dob,
            "address": address
        })
    # -------- CHECK MISSING DOCS --------
    for req_doc in REQUIRED_DOCUMENTS:
        if req_doc not in uploaded_required_docs:
            missing.append(req_doc)
    missing_count = len(missing)
    score = max(0, 100 - (missing_count * 10))
    same_person_result, consistency_data = check_same_person(person_data)

    insights = []

    if same_person_result == "DIFFERENT PERSON":
        if consistency_data["name_varition"]:
            insights.append(
                f"Name mismatch detected across documents:{consistency_data['name_varition']}"
            )

    elif same_person_result == "POSSIBLE SAME PERSON":
        if consistency_data["dob_mismatch"]:
            insights.append(
                f"DOB mismatch across documents: {consistency_data['dob_variation']}"
            )

    elif same_person_result == "VERIFIED SAME PERSON":
        insights.append("All documents belong to the same person")

    elif same_person_result == "Not enough data":
        insights.append("Insufficient documents to verify person consistency")
        
    status = "Ready" if score == 100 else "Partially Ready" if score >= 50 else "Not Ready"
    return {
        "detected_documents": detected,
        "missing_documents": missing,
        "weak_documents": weak_docs,
        "score": score,
        "status": status,
        "person_data": person_data,
        "same_person_result": same_person_result,
        "insights": {
            "consistency_issues": insights,
            "recommendations": [
                "Upload all required documents",
                "Upload documents of same person only",
                "Ensure clear scanned PDFs"
            ]
        }
    }
