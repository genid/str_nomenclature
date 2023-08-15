import re

import streamlit as st

input_seq = st.text_area("Paste your sequence here", height=100, key="seq").upper()
accepted_chars = ["A", "C", "G", "T"]

for char in input_seq:
    if char not in accepted_chars:
        st.error("Invalid characters are ignored")

input_seq = "".join([char for char in input_seq if char in accepted_chars])

min_repeats = st.number_input("Minimum number of repeats", min_value=2, value=6, step=1, key="min_repeats")
convert_to_base_motif = st.checkbox("Convert to base motif", value=True, key="convert_to_base_motif")

motifs_list = [line.rstrip('\n') for line in open("motifs.txt")]
base_motifs_list = [line.rstrip("\n").split(",") for line in open("motifs_dict.txt")]
base_motifs_dict = {key: value for key, value in base_motifs_list}

str_repeat_list = []

for str_motif in motifs_list:
    if str_motif * min_repeats in input_seq:
        pattern = f"((?:{str_motif}){{{min_repeats},}})"

        for match in re.finditer(pattern, input_seq):
            str_repeat_list.append({"start": match.start(1), "end": match.end(1), "motif": str_motif,
                                    "repeats": match.group(1).count(str_motif)})
    else:
        continue

sorted_str_repeat_list = sorted(str_repeat_list, key=lambda d: d['start'])

nomenclature = "[START]"
cursor = 0

for motif in sorted_str_repeat_list:
    if convert_to_base_motif:
        use_motif = base_motifs_dict[motif['motif']]
    else:
        use_motif = motif['motif']

    if motif["start"] == cursor:
        nomenclature += f"[{use_motif}]{motif['repeats']}"
        cursor = motif['end']
    else:
        nomenclature += f"[N]{motif['start'] - cursor}"
        nomenclature += f"[{use_motif}]{motif['repeats']}"
        cursor = motif['end']
if cursor < len(input_seq):
    nomenclature += f"[N]{len(input_seq) - cursor}"
nomenclature += "[END]"

st.write(nomenclature)
