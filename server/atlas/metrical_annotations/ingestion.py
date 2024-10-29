import csv
import os

from atlas import settings

from .models import MetricalAnnotation


# @@@ move these constants out to the data
COPYRIGHT_FRAGMENT = "© 2016 David Chamberlain under CC BY 4.0 License, https://creativecommons.org/licenses/by/4.0/"

ANNOTATIONS_DATA_PATH = os.path.join(
    settings.ATLAS_DATA_DIR, "annotations", "metrical-annotations"
)

CITE_IDENTIFIER = "urn:cite2:exploreHomer:metrical_annotation.v1:"


def pad_list(lst, n):
    # pads the given list to be exactly length n (truncating or adding None)
    return (lst + [None] * n)[:n]


class MetricalAnnotationProcessor:
    START_LINE = 0

    def lines(self, filename):  # noqa: C901
        with open(filename, newline="") as f:
            book_reader = csv.reader(f)
            book_reader.__next__()  # skip first line
            prev_line = self.START_LINE
            for row in book_reader:
                (
                    line,
                    text,
                    length,
                    word,
                    foot,
                    half_line,
                    speaker,
                    newpara,
                    speech,
                    extra,
                ) = pad_list(row, 10)

                line = int(line)
                if line != prev_line:
                    # new line

                    if prev_line > self.START_LINE:
                        if line_data[-1]["length"] == "long":  # noqa: F821
                            foot_code += "b"  # noqa: F821
                        else:
                            foot_code += "a"  # noqa: F821

                        if line_data[-1]["word_pos"] == "c":  # noqa: F821
                            line_data[-1]["word_pos"] = "l"  # noqa: F821
                        else:
                            line_data[-1]["word_pos"] = None  # noqa: F821

                        yield (prev_line, foot_code, line_data)  # noqa: F821

                    assert line == prev_line + 1

                    prev_word = 0
                    prev_foot = 0
                    prev_half_line = 0

                    line_data = []
                    foot_code = ""

                assert length in ["long", "short"]

                word = int(word)
                if word != prev_word:
                    # new word
                    assert word == prev_word + 1
                    word_pos = "r"
                    if word > 1:
                        if line_data[-1]["word_pos"] == "c":
                            line_data[-1]["word_pos"] = "l"
                        else:
                            line_data[-1]["word_pos"] = None
                else:
                    word_pos = "c"

                foot = int(foot)
                if foot != prev_foot:
                    assert foot == prev_foot + 1
                    if foot > 1:
                        if line_data[-1]["length"] == "long":
                            foot_code += "b"
                        else:
                            foot_code += "a"

                half_line = {"hemi1": 1, "hemi2": 2}[half_line]
                caesura = False
                if half_line != prev_half_line:
                    assert half_line == prev_half_line + 1
                    if half_line == 2:
                        caesura = True

                assert speaker in [
                    "",
                    "Achilles",
                    "Agamemnon",
                    "Nestor",
                    "Thetis",
                    "Zeus",
                    "Hephaistos",
                    "Hera",
                    "Chryses",
                    "Kalchas",
                    "Athena",
                    "Odysseus",
                ]
                assert newpara in [None, "newpara"]
                assert speech in [None, "speech"]
                assert extra in [None, "Chryses"]  # what is this?

                line_data.append(
                    {
                        "text": text,
                        "length": length,
                        "word_pos": word_pos,
                        "caesura": caesura,
                    }
                )

                prev_line = line
                prev_word = word
                prev_foot = foot
                prev_half_line = half_line

            if line_data[-1]["word_pos"] == "c":
                line_data[-1]["word_pos"] = "l"
            else:
                line_data[-1]["word_pos"] = None

            if line_data[-1]["length"] == "long":
                foot_code += "b"
            else:
                foot_code += "a"
            yield (line, foot_code, line_data)


def ingest_metrical_annotations(reset=False):
    if reset:
        MetricalAnnotation.objects.all().delete()
    version_urn = "urn:cts:greekLit:tlg0012.tlg001.perseus-grc2:"
    raw_path = os.path.join(ANNOTATIONS_DATA_PATH, "raw", "iliad1.csv")

    if not os.path.exists(raw_path):
        return

    processor = MetricalAnnotationProcessor()

    header = ["line_num", "foot_code", "line_data"]
    to_create = []
    idx = 0
    for line in processor.lines(raw_path):
        data = {}
        data.update(zip(header, line))
        data.update(
            {
                "references": [f'{version_urn}1.{data["line_num"]}'],
                # @@@ consider normalizing out to an attribution model
                "attribution": COPYRIGHT_FRAGMENT,
            }
        )
        urn = f"{CITE_IDENTIFIER}{idx + 1}"
        ma = MetricalAnnotation(data=data, idx=idx, urn=urn)
        ma.html_content = ma.generate_html()
        ma.short_form = ma.generate_short_form()
        to_create.append(ma)
        idx += 1

    created = len(MetricalAnnotation.objects.bulk_create(to_create, batch_size=500))
    print(f"Created metrical annotations [count={created}]")

    for metrical_annotation in MetricalAnnotation.objects.all():
        metrical_annotation.resolve_references()
