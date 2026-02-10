# Run this after making sure all of the annotations, commentaries,
# dictionaries, and texts are in test-data

./manage.py shell -c "from atlas.texts.ingestion import ingest_texts; ingest_texts(reset=True)"
./manage.py shell -c "from atlas.texts.ingestion import tokenize_all_text_parts; tokenize_all_text_parts(reset=True)"
./manage.py shell -c "from atlas.dictionaries.ingestion import ingest_dictionaries; ingest_dictionaries(reset=True)"
./manage.py shell -c "from atlas.alignments.ingestion import ingest_alignments; ingest_alignments(reset=True)"
./manage.py shell -c "from atlas.annotations.ingestion import ingest_syntaxtrees; ingest_syntaxtrees(reset=True)"
./manage.py shell -c "from atlas.morphology.models import import_data; import_data('../test-data/glaux_morph_counts2.tsv', 'grc')"
./manage.py shell -c "from atlas.morphology.models import import_data; import_data('../test-data/beowulf_morph.tsv', 'ang')"

./manage.py shell -c "from atlas.attributions.ingestion import ingest_attributions; ingest_attributions(reset=True)"
./manage.py shell -c "from atlas.named_entities.ingestion import ingest_named_entities; ingest_named_entities(reset=True)"
./manage.py shell -c "from atlas.metrical_annotations.ingestion import ingest_metrical_annotations; ingest_metrical_annotations(reset=True)"
./manage.py shell -c "from atlas.audio_annotations.ingestion import ingest_audio_annotations; ingest_audio_annotations(reset=True)"
./manage.py shell -c "from atlas.image_annotations.ingestion import ingest_image_annotations; ingest_image_annotations(reset=True)"

./manage.py shell -c "from atlas.commentaries.ingestion import ingest_commentaries; ingest_commentaries(reset=True)"

# ./manage.py shell -c "from atlas.morphology.models import import_data; import_data('../test-data/morphology/ola_morph_counts.tsv', 'lat')"
