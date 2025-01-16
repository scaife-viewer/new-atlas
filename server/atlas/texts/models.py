import re
from collections import defaultdict

from django.conf import settings
from django.core import serializers
from django.db import models

from treebeard.mp_tree import MP_Node


CTS_URN_NODES = ["nid", "namespace", "textgroup", "work", "version", "exemplar"]
CTS_URN_DEPTHS = {key: idx for idx, key in enumerate(CTS_URN_NODES, 1)}


class NodeManager(models.Manager):
    """
    Overrides MP_NodeManager's custom delete method.

    This is needed because we aren't setting `numchild`, so
    the custom delete method fails.

    FIXME: Remove overrides
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by("path")


# TODO: Review https://docs.djangoproject.com/en/3.0/topics/db/multi-db/
# to see if there are more settings we can expose for "mixed"
# database backends
class Node(MP_Node):
    # @@@ used to pivot siblings; may be possible if we hook into path field
    idx = models.IntegerField(help_text="0-based index", blank=True, null=True)
    # @@@ if we expose kind, can access some GraphQL enumerations
    kind = models.CharField(max_length=255)
    urn = models.CharField(max_length=255, unique=True)
    ref = models.CharField(max_length=255, blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)
    # @@@ we may want to further de-norm label from metadata
    metadata = models.JSONField(default=dict, blank=True, null=True)

    # NOTE: We currently assume SQLite for ATLAS databases;
    # if we end up supporting other backends, there may be additional
    # configuration changes to ensure consistent sorting (e.g. Postgres collation)
    # https://github.com/django-treebeard/django-treebeard/pull/143#issuecomment-1871226772
    alphabet = settings.SV_ATLAS_TREE_PATH_ALPHABET

    objects = NodeManager()

    def __str__(self):
        return f"{self.kind}: {self.urn}"

    @property
    def label(self):
        return self.metadata.get("label", self.urn)

    @property
    def lsb(self):
        """
        An alias for lowest citation part, preserved for
        backwards-comptability with scaife-viewer/scaife-viewer
        https://github.com/scaife-viewer/scaife-viewer/blob/e6974b2835918741acca781c39f46fd79d5406c9/scaife_viewer/cts/passage.py#L58
        """
        return self.lowest_citable_part

    @property
    def lowest_citable_part(self):
        """
        Returns the lowest part of the URN's citation

        # @@@ may denorm this for performance
        """
        if not self.rank:
            return None
        return self.ref.split(".").pop()

    @classmethod
    def dump_tree(cls, root=None, up_to=None, to_camel=True):
        """Dump a tree or subtree for serialization rendering all
        fieldnames as camelCase by default.

        Extension of django-treebeard.treebeard.mp_tree `dump_bulk` for
        finer-grained control over the initial queryset and resulting value.
        """
        if up_to and up_to not in CTS_URN_NODES:
            raise ValueError(f"Invalid CTS node identifier for: {up_to}")

        # NOTE: This filters the queryset using path__startswith,
        # because the default `get_tree(parent=root)` uses `self.is_leaf
        # and the current bulk ingestion into ATLAS does not populate
        # `numchild`.
        qs = cls._get_serializable_model().get_tree()
        if root:
            qs = qs.filter(
                path__startswith=root.path,
                # depth__gte=parent.depth
            ).order_by("path")
        if up_to:
            depth = CTS_URN_DEPTHS[up_to]
            qs = qs.exclude(depth__gt=depth)

        tree, index = [], {}
        for pyobj in serializers.serialize("python", qs):
            fields = pyobj["fields"]
            path = fields["path"]
            depth = int(len(path) / cls.steplen)
            del fields["depth"]
            del fields["path"]
            del fields["numchild"]

            metadata = fields["metadata"]
            # if to_camel:
            #     fields = camelize(fields)
            #     metadata = camelize(metadata)
            fields.update({"metadata": metadata})

            newobj = {"data": fields}

            if (not root and depth == 1) or (root and len(path) == len(root.path)):
                tree.append(newobj)
            else:
                parentpath = cls._get_basepath(path, depth - 1)
                parentobj = index[parentpath]
                if "children" not in parentobj:
                    parentobj["children"] = []
                parentobj["children"].append(newobj)
            index[path] = newobj
        return tree

    def get_refpart_siblings(self, version):
        """
        Node.get_siblings assumes siblings at the same position in the Node
        heirarchy.

        Refpart siblings crosses over parent boundaries, e.g.
        considers 1.611 and 2.1 as siblings.
        """
        if not self.rank:
            return Node.objects.none()
        return version.get_descendants().filter(rank=self.rank)

    def get_descendants(self):
        # NOTE: This overrides `get_descendants` to avoid checking
        # `self.is_leaf`; current bulk ingestion into ATLAS
        # does not populate numchild.
        # TODO: populate numchild and remove override
        parent = self
        return (
            self.__class__.objects.filter(
                path__startswith=parent.path, depth__gte=parent.depth
            )
            .order_by("path")
            .exclude(pk=parent.pk)
        )

    def get_children(self):
        # NOTE: This overrides `get_children` to avoid checking
        # `self.is_leaf`; current bulk ingestion into ATLAS
        # does not populate numchild.
        # TODO: populate numchild and remove override

        return self.__class__.objects.filter(
            depth=self.depth + 1,
            path__range=self._get_children_path_interval(self.path),
        ).order_by("path")


class Token(models.Model):
    text_part = models.ForeignKey(
        "Node", related_name="tokens", on_delete=models.CASCADE
    )

    value = models.CharField(
        max_length=255,
        help_text="the tokenized value of a text part (usually whitespace separated)",
    )
    # @@@ consider JSON or EAV to store / filter attrs
    word_value = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="the normalized version of the value (no punctuation)",
    )
    subref_value = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="the value for the CTS subreference targeting a particular token",
    )

    position = models.IntegerField()
    idx = models.IntegerField(help_text="0-based index")

    ve_ref = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="a human-readable reference to the token via a virtualized exemplar",
    )

    space_after = models.BooleanField(default=True)

    @staticmethod
    def get_word_value(value):
        return re.sub(r"[^\w]", "", value)

    @classmethod
    def tokenize(cls, text_part_node, counters, as_dict=False):
        # @@@ compare with passage-based tokenization on
        # scaife-viewer/scaife-viewer.  See discussion on
        # https://github.com/scaife-viewer/scaife-viewer/issues/162
        #
        # For this implementation, we always calculate the index
        # within the text part, _not_ the passage. Also see
        # http://www.homermultitext.org/hmt-doc/cite/cts-subreferences.html
        idx = defaultdict(int)
        pieces = text_part_node.text_content.split()
        to_create = []
        for pos, piece in enumerate(pieces):
            # @@@ the word value will discard punctuation or
            # whitespace, which means we only support "true"
            # subrefs for word tokens
            w = cls.get_word_value(piece)
            wl = len(w)
            for wk in (w[i : j + 1] for i in range(wl) for j in range(i, wl)):
                idx[wk] += 1
            subref_idx = idx[w]
            subref_value = f"{w}[{subref_idx}]"

            position = pos + 1
            # TODO: Further decouple `as_dict` so we could
            # for example append to a file buffer using CSV
            data = dict(
                text_part_id=text_part_node.pk,
                value=piece,
                word_value=w,
                position=position,
                ve_ref=f"{text_part_node.ref}.t{position}",
                idx=counters["token_idx"],
                subref_value=subref_value,
                space_after=True,
            )
            if as_dict:
                to_create.append(data)
            else:
                to_create.append(cls(**data))
            counters["token_idx"] += 1
        return to_create

    def __str__(self):
        return f"{self.text_part.urn} :: {self.value}"
