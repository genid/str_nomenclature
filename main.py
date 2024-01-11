import re

import streamlit as st

input_seqs = st.text_area("Paste your sequence(s) and/or nomenclatures here. Each sequence on a separate line.", height=100, key="seq").strip().upper().split("\n")
accepted_chars = ["A", "C", "G", "T", "N"]
rev_comp = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
min_len = {1: 5, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2}

min_repeats = st.number_input("Minimum number of repeats", min_value=2, value=6, step=1, key="min_repeats", help="Minimum number of repeats to be considered as a motif. Note that the minimum number of repeats for mono-nucleotide motifs is always 5.")
convert_to_base_motif = st.checkbox("Convert to base motif", value=True, key="convert_to_base_motif", help="Reverse complement base motifs are indicated by ~ (tilde) symbol")


def convert_nomenclature_to_sequence(input_seq):
    motifs = re.findall(r'(~?[ATCGN]+)\[(\d+)\]', input_seq)
    sequence = ""

    for motif, count in motifs:
        if motif.startswith("~"):
            motif = motif.replace("~", "")
            motif = ''.join(rev_comp[nt] for nt in reversed(motif))

        sequence += motif * int(count)

    return sequence


for input_seq in input_seqs:
    if "[" in input_seq or "]" in input_seq:
        input_seq = convert_nomenclature_to_sequence(input_seq)

    for char in input_seq:
        if char not in accepted_chars:
            st.error("Invalid characters are ignored")
            break

    input_seq = "".join([char for char in input_seq if char in accepted_chars])

    motifs_list = [line.rstrip('\n') for line in open("motifs.txt")]
    base_motifs_list = [line.rstrip("\n").split(",") for line in open("motifs_dict.txt")]
    base_motifs_dict = {key: value for key, value in base_motifs_list}

    str_repeat_list = []

    for str_motif in motifs_list:
        repeat_num = max(min_len[len(str_motif)], min_repeats)
        if str_motif * repeat_num in input_seq:
            pattern = f"((?:{str_motif}){{{repeat_num},}})"

            for match in re.finditer(pattern, input_seq):
                str_repeat_list.append({"start": match.start(1), "end": match.end(1), "motif": str_motif,
                                        "repeats": match.group(1).count(str_motif)})
        else:
            continue

    sorted_str_repeat_list = sorted(str_repeat_list, key=lambda d: d['start'])

    nomenclature = ""
    cursor = 0

    for motif in sorted_str_repeat_list:
        if convert_to_base_motif:
            if motif['motif'] in base_motifs_dict:
                use_motif = base_motifs_dict[motif['motif']]
            else:
                use_motif = motif['motif']
        else:
            use_motif = motif['motif']

        if motif["start"] == cursor:
            nomenclature += f"{use_motif}[{motif['repeats']}]"
            cursor = motif['end']
        else:
            nomenclature += f"N[{motif['start'] - cursor}]"
            nomenclature += f"{use_motif}[{motif['repeats']}]"
            cursor = motif['end']
    if cursor < len(input_seq):
        nomenclature += f"N[{len(input_seq) - cursor}]"
    nomenclature += ""

    st.header(input_seq)
    st.write(nomenclature)

    unique_motifs = set([motif['motif'].replace("~", "") for motif in sorted_str_repeat_list])
    st.write(f"Unique motifs: {unique_motifs}")
