import unicodedata

from collections import defaultdict

from django.db import models

from .utils import sort_key, strip_accents, human_pos, human_parse, parse_sort_key


class Lemma(models.Model):
    lang = models.CharField(max_length=10)
    text = models.CharField(max_length=100)
    pos = models.CharField(max_length=2)
    sort_key = models.TextField()
    unaccented = models.CharField(max_length=100)
    count = models.IntegerField(default=0)

    class Meta:
        unique_together = [("lang", "text", "pos")]

    def calc_sort_key(self):
        self.sort_key = sort_key(self.text)
        self.save()

    def calc_unaccented(self):
        self.unaccented = strip_accents(self.text).lower()
        if self.unaccented:
            if self.unaccented[-1] in "12345":
                self.unaccented = self.unaccented[:-1]
            self.save()

    def display_pos(self):
        return human_pos(self.pos, self.lang)

    def paradigm(self):
        if self.lang == "grc":
            return self.paradigm_grc()
        elif self.lang == "ang":
            return self.paradigm_ang()
        elif self.lang == "lat":
            return self.paradigm_lat()

    def paradigm_ang(self):
        pass

    def paradigm_grc(self):
        count = 0
        if self.pos[0] in ["a", "l", "n", "p"]:
            # degree gender case number
            p = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
            for form in self.forms.order_by("-count"):
                degree = form.parse[7]
                gender = form.parse[5]
                number = form.parse[1]
                case = form.parse[6]
                if number != "-" and case != "-":
                    if gender == "-":
                        gender = "x"
                    if degree == "-":
                        degree = "p"
                    p[degree][gender][case][number].append(form)
                    if case not in p[degree][gender]["case_subtotals"]:
                        p[degree][gender]["case_subtotals"][case] = 0
                    p[degree][gender]["case_subtotals"][case] += form.count
                    if number not in p[degree][gender]["number_subtotals"]:
                        p[degree][gender]["number_subtotals"][number] = 0
                    p[degree][gender]["number_subtotals"][number] += form.count
                    count += 1
        elif self.pos[0] in ["v"]:
            p_n = defaultdict(lambda: defaultdict(list))
            p_p = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))))
            p_f = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))))
            p = defaultdict(dict)
            for form in self.forms.order_by("-count"):
                if form.parse[2] == "i":
                    tense_voice = "p" + form.parse[4]
                    assert form.parse[3] == "i"
                    mood = "x"
                elif form.parse[2] == "l":
                    tense_voice = "r" + form.parse[4]
                    assert form.parse[3] == "i"
                    mood = "x"
                else:
                    tense_voice = form.parse[2] + form.parse[4]
                    mood = form.parse[3]

                gender = form.parse[5]
                number = form.parse[1]
                case = form.parse[6]
                person = form.parse[0]
                if mood == "n":
                    p_n[tense_voice][mood].append(form)
                    p[tense_voice][mood] = p_n[tense_voice][mood]
                elif mood == "p":
                    p_p[tense_voice][mood][gender][case][number].append(form)
                    p[tense_voice][mood] = p_p[tense_voice][mood]
                else:
                    p_f[tense_voice]["f"][number][person][mood].append(form)
                    p[tense_voice]["f"] = p_f[tense_voice]["f"]
                count += 1

        if count:
            return p


    def paradigm_lat(self):
        count = 0
        if self.pos[0] in ["a", "l", "n", "p"]:
            # degree gender case number
            p = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
            for form in self.forms.order_by("-count"):
                degree = form.parse[7]
                gender = form.parse[5]
                number = form.parse[1]
                case = form.parse[6]
                if number != "-" and case != "-":
                    if gender == "-":
                        gender = "x"
                    if degree == "-":
                        degree = "p"
                    p[degree][gender][case][number].append(form)
                    if case not in p[degree][gender]["case_subtotals"]:
                        p[degree][gender]["case_subtotals"][case] = 0
                    p[degree][gender]["case_subtotals"][case] += form.count
                    if number not in p[degree][gender]["number_subtotals"]:
                        p[degree][gender]["number_subtotals"][number] = 0
                    p[degree][gender]["number_subtotals"][number] += form.count
                    count += 1
        elif self.pos[0] in ["v"]:
            p_n = defaultdict(lambda: defaultdict(list))
            p_p = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))))
            p_f = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))))
            p = defaultdict(dict)
            for form in self.forms.order_by("-count"):
                if form.parse[2] == "i":
                    tense_voice = "p" + form.parse[4]
                    # assert form.parse[3] == "i", form.parse[3]
                    mood = "x"
                elif form.parse[2] == "l":
                    tense_voice = "r" + form.parse[4]
                    # assert form.parse[3] == "i", form.parse[3]
                    mood = "x"
                else:
                    tense_voice = form.parse[2] + form.parse[4]
                    mood = form.parse[3]

                gender = form.parse[5]
                number = form.parse[1]
                case = form.parse[6]
                person = form.parse[0]
                if mood == "n":
                    p_n[tense_voice][mood].append(form)
                    p[tense_voice][mood] = p_n[tense_voice][mood]
                elif mood == "p":
                    p_p[tense_voice][mood][gender][case][number].append(form)
                    p[tense_voice][mood] = p_p[tense_voice][mood]
                else:
                    p_f[tense_voice]["f"][number][person][mood].append(form)
                    p[tense_voice]["f"] = p_f[tense_voice]["f"]
                count += 1

        if count:
            return p



class Form(models.Model):
    lang = models.CharField(max_length=10)
    text = models.CharField(max_length=100)
    parse = models.CharField(max_length=10)
    lemma = models.ForeignKey(Lemma, null=True, on_delete=models.CASCADE, related_name="forms")
    sort_key = models.TextField()
    parse_sort_key = models.CharField(max_length=12)
    unaccented = models.CharField(max_length=100)
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.text

    class Meta:
        unique_together = [("lang", "text", "parse", "lemma")]

    def update_parse_sort_key(self):
        if self.parse:
            self.parse_sort_key = parse_sort_key(self.parse, self.lang)
            self.save()

    def calc_sort_key(self):
        self.sort_key = sort_key(self.text)
        self.save()

    def calc_unaccented(self):
        self.unaccented = strip_accents(self.text).lower()
        if self.unaccented and self.unaccented[-1] in "12345":
            self.unaccented = self.unaccented[:-1]
        self.save()

    def display_parse(self):
        return human_parse(self.parse, self.lang)

    def others_same_text(self):
        """other forms with same text"""
        return Form.objects.filter(text=self.text).exclude(pk=self.pk)

    def others_same_lemma_parse(self):
        """other forms with lemma+parse"""
        if len(self.parse) == 8:
            return Form.objects.filter(parse=self.parse, lemma=self.lemma).exclude(pk=self.pk)
        else:
            return Form.objects.none()


def clear_data(lang=None):
    if lang:
        Form.objects.filter(lang=lang).delete()
        Lemma.objects.filter(lang=lang).delete()
    else:
        Form.objects.all().delete()
        Lemma.objects.all().delete()


def import_data(filename, lang):
    l = 0
    for line in open(filename):
        line = unicodedata.normalize("NFC", line)
        l += 1
        if l % 1000 == 0:
            print(l)
        form, postag, lemma, count = line.strip("\n").split("\t")
        if form == "":
            continue
        if lang == "grc":
            lemma_obj, _ = Lemma.objects.get_or_create(
                lang=lang,
                text=lemma,
                pos=postag[:1] + "-"
            )
        elif lang == "ang":
            lemma_obj, _ = Lemma.objects.get_or_create(
                lang=lang,
                text=lemma,
                pos=postag.split(".")[0]
            )
        elif lang == "lat":
            lemma_obj, _ = Lemma.objects.get_or_create(
                lang=lang,
                text=lemma,
                pos=postag[:1] + "-"
            )
        lemma_obj.count += int(count)
        lemma_obj.save()
        lemma_obj.calc_sort_key()
        lemma_obj.calc_unaccented()
        if lang == "grc":
            form_obj, _ = Form.objects.get_or_create(
                lang=lang,
                text=form,
                parse=postag[1:],
                lemma=lemma_obj,
                defaults={"count": int(count)}
            )
        elif lang == "ang":
            form_obj, _ = Form.objects.get_or_create(
                lang=lang,
                text=form,
                parse=postag.split(".")[1],
                lemma=lemma_obj,
                defaults={"count": int(count)}
            )
        elif lang == "lat":
            form_obj, _ = Form.objects.get_or_create(
                lang=lang,
                text=form,
                parse=postag[1:],
                lemma=lemma_obj,
                defaults={"count": int(count)}
            )
        form_obj.calc_sort_key()
        form_obj.update_parse_sort_key()
        form_obj.calc_unaccented()
