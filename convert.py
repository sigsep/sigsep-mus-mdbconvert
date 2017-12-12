import medleydb as mdb
import medleydb.mix as mix
import os

named_sources = {
    'vocals': [
        "male singer", "female singer", "male speaker", "female speaker",
        "male rapper", "female rapper", "beatboxing", "vocalists", "choir"
    ],
    'drums': [
        "timpani", "toms", "snare drum", "kick drum", "bass drum",
        "bongo", "conga", "tambourine", "darbuka", "doumbek", "tabla",
        "auxiliary percussion", "drum set",
        "sleigh bells", "cowbell", "cabasa", "high hat", "gong", "guiro",
        "gu", "cymbal", "chimes", "castanet", "claps", "rattle", "shaker",
        "maracas", "snaps", "drum machine"
        ## removed from drums:
        # "xylophone", "vibraphone", "marimba", "glockenspiel", "whistle"
    ],
    'bass': [
        'double bass', 'electric bass'
    ]
}

ignore_sources = ['sampler']
# set output path
output_path = 'mdbstems'

# Load all multitracks
mtrack_generator = mdb.load_all_multitracks()
tracks = 0
for mtrack in mtrack_generator:
    if not mtrack.has_bleed and not mtrack.is_instrumental:
        dsd_stems = {
            'vocals': [],
            'bass': [],
            'drums': [],
            'other': [],
            'accompaniment': []
        }
        stem_indices = list(mtrack.stems.keys())
        for stem_id in stem_indices:
            mapped = False
            for key, value in named_sources.items():
                if mtrack.stems[stem_id].instrument[0] in value:
                    dsd_stems[key].append(stem_id)
                    mapped = True
                elif mtrack.stems[stem_id].component == key:
                    print(
                        "Matching component",
                        mtrack.stems[stem_id].instrument[0]
                    )
                    dsd_stems[key].append(stem_id)
                    mapped = True

            if not mapped and mtrack.stems[stem_id].instrument[0] not in ignore_sources:
                # add remaining stems to `other` component
                dsd_stems['other'].append(stem_id)

        # add accompaniment stems
        for key, values in dsd_stems.iteritems():
            if key != 'vocals' and values:
                dsd_stems['accompaniment'].extend(values)

        if all(len(value) > 0 for value in dsd_stems.values()):
            print(mtrack.track_id)
            print(dsd_stems)
            base_path = os.path.join(output_path, mtrack.track_id)
            if not os.path.exists(base_path):
                os.makedirs(base_path)
                for key, value in dsd_stems.items():
                    mix.mix_multitrack(
                        mtrack,
                        os.path.join(base_path, key + ".wav"),
                        stem_indices=dsd_stems[key]
                    )
        else:
            print("not included: ", dsd_stems)
