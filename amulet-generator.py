import hashlib
import pandas as pd

"""
Its complete Unicode text is 64 bytes or less. The hexadecimal SHA-256 hash of the text includes four or more 8s in a row.

https://at.amulet.garden/

8888: common
88888: uncommon
888888: rare
8888888: epic
88888888: legendary
888888888: mythic
8888888888+: ✦✦✦
"""
rarity_mapping = {
'common': 1,
'uncommon': 2,
'rare': 3,
'epic': 4,
'legendary': 5,
'mythic': 6,
'✦✦✦': 7,
}

def utf8len(s):
    return len(s.encode('utf-8'))

def get_amulet_rarity(poem):
    if utf8len(poem) > 64:
        # print ("Amulet is too long {}".format(utf8len(poem)))
        return None

    sha_hash = hashlib.sha256(poem.encode('utf-8')).hexdigest()

    eights_counter = 0
    eights_counter_max = 0

    for c in sha_hash:
        if c == '8':
            eights_counter += 1
        else:
            if eights_counter > eights_counter_max:
                eights_counter_max = eights_counter
            eights_counter = 0

    if eights_counter_max < 4:
        return None
    elif eights_counter_max == 4:
        return 'common'
    elif eights_counter_max == 5: 
        return 'uncommon'
    elif eights_counter_max == 6: 
        return 'rare'
    elif eights_counter_max == 7: 
        return 'epic'
    elif eights_counter_max == 8: 
        return 'legendary'
    elif eights_counter_max == 9: 
        return 'mythic'
    elif eights_counter_max > 9: 
        return '✦✦✦'

def flatten(t):
    return [item for sublist in t for item in sublist]

def try_words(): 
    df = pd.read_csv('./antonyms.csv')
    print ("running over {} words".format(df.shape[0]))
    poem_bases = [
        '{}',
        '{}.',
        'the {}',
        'a {}',
        'The {}',
        'A {}',
        'An {}',
        'This {}',
        'this {}'
    ]
    word_set = set()
    for index, row in df.iterrows():
        lemma = row['lemma']
        antonyms = set(flatten([group.split(';') for group in row['antonyms'].split('|')]))

        words = set([lemma] + list(antonyms))
        words = [word for word in words if word not in word_set]
        word_set.update(words)
        words = flatten([[word, word.capitalize()] for word in words])

        for poem_format in poem_bases:
            for word in words:
                final_poem = poem_format.format(word)
                amulet_rarity = get_amulet_rarity(final_poem)
                if amulet_rarity:
                    print ("{}: {}".format(amulet_rarity, final_poem))

def try_antonyms():
    df = pd.read_csv('./antonyms.csv')
    poem_bases = [
        '{} | {}',
        '{} <> {}',
        '{} >< {}',
        '{} hates {}',
        '{} is {}',
        '{} not {}',
        '{} and {}',
        '{} against {}',
        '{} + {}',
        '{} = {}',
        '{} x {}',
        '{} vs {}',
        '{} ✖️  {}',
        '{} ➕ {}',
        '{} ➗ {}',
        '{} loves {}',
        '{} ⚖️  {}'
    ]
    nouns = df[df['part_of_speech'] == 'noun']
    print ("running over {} nouns".format(nouns.shape[0]))
    for index, row in nouns.iterrows():
        lemma = row['lemma']
        antonyms = set(flatten([group.split(';') for group in row['antonyms'].split('|')]))

        for poem_format in poem_bases:
            for antonym in antonyms:
                final_poem = poem_format.format(lemma, antonym)
                amulet_rarity = get_amulet_rarity(final_poem)
                if amulet_rarity:
                    print ("{}: {}".format(amulet_rarity, final_poem))

def try_amulet(poem, rarity_filter=None, output_file=None):
    amulet_rarity = get_amulet_rarity(poem)
    if amulet_rarity:
        if rarity_filter is not None and rarity_mapping[amulet_rarity] < rarity_filter:
            return
        print ("{}: {}".format(amulet_rarity, poem), file=output_file)

def try_code():
    with open('./code.txt') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            try_amulet(line)
            if i < len(lines) - 1:
                try_amulet(line + '\n' + lines[i+1])
            if i+1 < len(lines) - 1:
                try_amulet(line + '\n' + lines[i+1] + '\n' + lines[i+2])
            if i+2 < len(lines) - 1:
                try_amulet(line + '\n' + lines[i+1] + '\n' + lines[i+2] + '\n' + lines[i+3] )
        
        words = [word for word in line.split(' ') for line in lines]

        for i, word in enumerate(words):
            poem = word
            try_amulet(poem)
            idx = i + 1
            while utf8len(poem) < 64 and idx < len(words):
                poem += ' ' + words[idx]
                try_amulet(poem)
                idx += 1
        
        for i, ch in enumerate('\n'.join(lines)):
            poem = ch
            try_amulet(poem)
            idx = i + 1
            while utf8len(poem) < 64 and idx < len(lines):
                poem += lines[idx]
                try_amulet(poem)
                idx += 1
                

def try_emojis(output_file=None): 
    bases = [
        '{} : {}',
        '{} {}',
        '{} | {}',
        '{} means {}',
    ]

    emojis = set()
    with open('./emojis.csv') as f:
        for line in f.readlines():
            linesplit = line.index(',')
            emoji = line[:linesplit]
            emojis.add(emoji)
            text = line[linesplit + 1:]
            # emoji, text = linesplit
            text = text.strip()
            text_variations = [text, text.strip('"'), text.strip('"').lower(), text.lower()]
            for base in bases:
                for txt in text_variations:
                    try_amulet(base.format(emoji, txt), output_file=output_file)

    for emoji in emojis:
        try_amulet(emoji, output_file=output_file)
        for emoji2 in emojis:
            try_amulet('{} {}'.format(emoji, emoji2), rarity_filter=rarity_mapping['uncommon'], output_file=output_file)
            # try_amulet('{}{}'.format(emoji, emoji2), rarity_filter=rarity_mapping['uncommon'], output_file=output_file)
    

# try_code()
with open('emojis_output.txt', 'w') as f: 
    try_emojis(f)
