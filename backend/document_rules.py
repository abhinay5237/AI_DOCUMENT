# document_rules.py

REQUIRED_DOCUMENTS = {

    "aadhaar": {
        "keywords": [
            "aadhaar", "uidai", "unique identification authority of india",
            "Government of India","your Aadhaar No","aadhaar","uid"
        ],
        "must_have": [
        "aadhaar", "uidai", "unique identification authority of india",
            "Government of India","your Aadhaar No","aadhaar"
        ],
        "forbidden": [
            "passport", "account number", "bank", "ifsc", "statement",
        ]
    },

      "Pancard": {
        "keywords": [
            "income tax department", "govt of india", "permanent account number card",
            "date of birth","name","pan","fathers name"
        ],
        "must_have": [
        "income tax department", "govt of india", "permanent account number card",
            "pan","date of birth","fathers name"
        ],
        "forbidden": [
            "passport","bank","ifsc", "statement","employment"
        ]
    },

    "passport": {
        "keywords": [
            "passport", "republic of india", "nationality", "passport number","Name",
            "date of birth","sex","Country","Place of birth","Date of issue","Date of expiry"
        ],
        "must_have": [
            "passport", "republic of india", "nationality", "passport number","Name",
            "date of birth","sex","Country","Place of birth","Date of issue","Date of expiry"
        ],
        "forbidden": [
            "bank", "ifsc", "statement"
        ]
    },

    "academic_transcript": {
        "keywords": [
           "transcript","memorandum of grades","result",
           "subjects registered","credits","appeared","passed","semester grade point average","subject code",
           "memo no","cgpa","result","degree certificate","name of the college", 
             "Consolidated Memo Of Marks Grades And Credits","Hall Ticket No",
             "Serial. No","Month & Year of Final Exam","class awarded","number of credits registered and secured are",
             "aggregate marks"

        ],
        "must_have": [
          "transcript","memorandum of grades","result",
          "subjects registered","credits","appeared","passed","semester grade point average","subject code",
          "memo no","cgpa","result","degree certificate","name of the college", 
             "Consolidated Memo Of Marks Grades And Credits","Hall Ticket No",
             "Serial. No","Month & Year of Final Exam","class awarded","number of credits registered and secured are",
             "aggregate marks"
        ],
        "forbidden": [
            "passport", "bank", "ifsc"
        ]
    }, 

    "english_test": {
        "keywords": [
            "ielts", "toefl", "pte", "duolingo",
            "listening", "reading", "writing", "speaking","overallscore","literacy","comprehension","production"
        ],
        "must_have": [
            "listening", "reading", "writing", "speaking","ielts", "toefl", "pte", "duolingo","overallscore","literacy","comprehension","production"
        ],
        "forbidden": [
            "passport", "nationality", "bank", "account number","income tax department", "govt of india", "permanent account number card"
        ]
    },
    
    "bank_statement": {
        "keywords": [
            "bank", "statement", "account number","account name","account type","balance","home branch","branch code","mobile number",
            "transaction details","ifsc code","address","credit","debit","date"
        ],
        "must_have": [
            "account number","bank", "statement","account name","account type","balance","branch","ifsc","cif no"
        ],
        "forbidden": [
            "passport", "nationality", "degree", "university", "cgpa","pancard"
        ]
    },

    "offer_letter": {
        "keywords": [
            "offer letter", "employment", "date of joining", "company","Sincerely","University Name","Intake Term: Fall","Program Offered",
            "offical offer of admission"
        ],
        "must_have": [
            "offer letter","employment", "date of joining", "company","Sincerely","University Name","Intake Term: Fall","Program Offered","offical offer of admission"
        ],
        "forbidden": [
            "passport", "bank", "account number"
        ]
    },

    "sop": {
        "keywords": [
            "statement of purpose", "sop","Name"
        ],
        "must_have": [
            "statement of purpose","sop","Name"
        ],
        "forbidden": [
            "passport", "bank","cgpa"
        ]
    },

    "resume": {
        "keywords": [
           "education", "career objective", "@gmail.com","projects",
            "skills"
        ],
        "must_have": [
            "education", "career objective", "@gmail.com","projects",
            "skills"
        ],
        "forbidden": [
            "passport", "sop", "statement of purpose"
        ]
    },
    
   
    "Inter Memo": {
        "keywords": [
            "INTERMEDIATE PASS CERTIFICATE-CUM-MEMORANDUM OF MARKS","intermediate public examination",
            "Telangana State Board of Intermediate Education","This is to certify that",
            "Optional Subjects","In Words","Maximum Marks"," Marks Secured","mathematics -A","mathematics -B",
            "physics", "chemistry", "physics practicals", "chemistry practicals", "biology","histroy","economics"
            ],
        "must_have": [
            "INTERMEDIATE PASS CERTIFICATE-CUM-MEMORANDUM OF MARKS","intermediate public examination",
            "Telangana State Board of Intermediate Education","This is to certify that",
            "Optional Subjects","In Words","Maximum Marks"," Marks Secured","mathematics -A","mathematics -B",
            "physics", "chemistry", "physics practicals", "chemistry practicals", "biology","histroy","economics"
        ],
        "forbidden": [
            "bank", "passport", "ifsc", "statement"
        ]
    }
}