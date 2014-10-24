import difflib

dicts=[
  {
    "name": "TO LT15",
    "id": 57,
    "SUID": "1"
  },
  {
    "name": "Seminar Room 6",
    "id": 58,
    "SUID": "6"
  },
  {
    "name": "P2",
    "id": 59,
    "SUID": "2"
  },
  {
    "name": "Linkway",
    "id": 60,
    "SUID": "3"
  },
  {
    "name": "P4",
    "id": 61,
    "SUID": "4"
  },
  {
    "name": "P5",
    "id": 62,
    "SUID": "5"
  },
  {
    "name": "lobby ",
    "id": 63,
    "SUID": "7"
  },
  {
    "name": "P8",
    "id": 64,
    "SUID": "8"
  },
  {
    "name": "Seminar Room 2",
    "id": 65,
    "SUID": "9"
  },
  {
    "name": "P10",
    "id": 66,
    "SUID": "10"
  },
  {
    "name": "Student Area",
    "id": 67,
    "SUID": "11"
  },
  {
    "name": "Seminar Room 1",
    "id": 68,
    "SUID": "12"
  },
  {
    "name": "P13",
    "id": 69,
    "SUID": "13"
  },
  {
    "name": "P14",
    "id": 70,
    "SUID": "14"
  },
  {
    "name": "P15",
    "id": 71,
    "SUID": "15"
  },
  {
    "name": "P16",
    "id": 72,
    "SUID": "16"
  },
  {
    "name": "P17",
    "id": 73,
    "SUID": "17"
  },
  {
    "name": "P18",
    "id": 74,
    "SUID": "18"
  },
  {
    "name": "Executive Classroom",
    "id": 75,
    "SUID": "19"
  },
  {
    "name": "Tutorial Room 8",
    "id": 76,
    "SUID": "20"
  },
  {
    "name": "P21",
    "id": 77,
    "SUID": "21"
  },
  {
    "name": "P22",
    "id": 78,
    "SUID": "22"
  },
  {
    "name": "Seminar Room 9",
    "id": 79,
    "SUID": "23"
  },
  {
    "name": "P24",
    "id": 80,
    "SUID": "24"
  },
  {
    "name": "Tutorial Room 9",
    "id": 81,
    "SUID": "25"
  },
  {
    "name": "P26",
    "id": 82,
    "SUID": "26"
  },
  {
    "name": "Seminar Room 11",
    "id": 83,
    "SUID": "27"
  },
  {
    "name": "P28",
    "id": 84,
    "SUID": "28"
  },
  {
    "name": "P29",
    "id": 85,
    "SUID": "29"
  },
  {
    "name": "DB1",
    "id": 86,
    "SUID": "30"
  },
  {
    "name": "Store Room 1",
    "id": 87,
    "SUID": "31"
  },
  {
    "name": "Data Communications",
    "id": 87,
    "SUID": "31"
  },
  {
    "name": "Active Learning Lab",
    "id": 88,
    "SUID": "-1"
  }
]

def match_location(string):

    if string == "" or string == " ":
        return ""

    prev_percent = 0
    winner = ""

    print "--------"
    print string
    
    # Loop through
    for item in dicts:
        name = item["name"]
        curr_percent = difflib.SequenceMatcher(None, string, name).ratio()

        print name + " " + str(curr_percent)

        if curr_percent > prev_percent:
            prev_percent = curr_percent
            winner = name

    
    print winner
    print "--------"

    if prev_percent < 0.4:
      winner = ""

    return winner
