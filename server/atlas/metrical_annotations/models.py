import io

from django.db import models

from sortedm2m.fields import SortedManyToManyField

from atlas.texts.models import Node


class MetricalAnnotation(models.Model):
    # @@@ in the future, we may ingest any attributes into
    # `data` and query via JSON
    data = models.JSONField(default=dict, blank=True)

    html_content = models.TextField()
    short_form = models.TextField(
        help_text='"|" indicates the start of a foot, ":" indicates a syllable boundary within a foot and "/" indicates a caesura.'
    )

    idx = models.IntegerField(help_text="0-based index")
    text_parts = SortedManyToManyField(
        Node, related_name="metrical_annotations"
    )

    urn = models.CharField(max_length=255, blank=True, null=True)

    @property
    def metrical_pattern(self):
        """
        alias of foot_code; could be denormed if we need to query
        """
        return self.data["foot_code"]

    @property
    def line_num(self):
        return self.data["line_num"]

    @property
    def foot_code(self):
        return self.data["foot_code"]

    @property
    def line_data(self):
        return self.data["line_data"]

    def generate_html(self):
        buffer = io.StringIO()
        print(
            f'        <div class="line {self.foot_code}" id="line-{self.line_num}" data-meter="{self.foot_code}">',
            file=buffer,
        )
        print("          <div>", end="", file=buffer)
        index = 0
        for foot in self.foot_code:
            if foot == "a":
                syllables = self.line_data[index : index + 3]
                index += 3
            else:
                syllables = self.line_data[index : index + 2]
                index += 2
            if syllables[0]["word_pos"] in [None, "r"]:
                print("\n            ", end="", file=buffer)
            print('<span class="foot">', end="", file=buffer)
            for i, syllable in enumerate(syllables):
                if i > 0 and syllable["word_pos"] in [None, "r"]:
                    print("\n            ", end="", file=buffer)
                syll_classes = ["syll"]
                if syllable["length"] == "long":
                    syll_classes.append("long")
                if syllable["caesura"]:
                    syll_classes.append("caesura")
                if syllable["word_pos"] is not None:
                    syll_classes.append(syllable["word_pos"])
                syll_class_string = " ".join(syll_classes)
                print(
                    f'<span class="{syll_class_string}">{syllable["text"]}</span>',
                    end="",
                    file=buffer,
                )
            print("</span>", end="", file=buffer)
        print("\n          </div>", file=buffer)
        print("        </div>", file=buffer)
        buffer.seek(0)
        return buffer.read().strip()

    def generate_short_form(self):
        """
        |μῆ:νιν :ἄ|ει:δε :θε|ὰ /Πη|λη:ϊ:ά|δεω :Ἀ:χι|λῆ:ος
        """
        index = 0
        form = ""
        for foot in self.foot_code:
            if foot == "a":
                syllables = self.line_data[index : index + 3]
                index += 3
            else:
                syllables = self.line_data[index : index + 2]
                index += 2
            form += "|"
            for i, syllable in enumerate(syllables):
                if i > 0 and syllable["word_pos"] in [None, "r"]:
                    form += " "
                if syllable["caesura"]:
                    form += "/"
                elif i > 0:
                    form += ":"
                form += syllable["text"]
        return form

    def resolve_references(self):
        if "references" not in self.data:
            print(f'No references found [urn="{self.urn}"]')
            return
        desired_urns = set(self.data["references"])
        reference_objs = list(Node.objects.filter(urn__in=desired_urns))
        resolved_urns = set([r.urn for r in reference_objs])
        delta_urns = desired_urns.symmetric_difference(resolved_urns)

        if delta_urns:
            print(
                f'Could not resolve all references [urn="{self.urn}" unresolved_urns="{",".join(delta_urns)}"]'
            )
        self.text_parts.set(reference_objs)
