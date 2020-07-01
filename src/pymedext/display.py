from spacy import displacy

def convert_to_displacy(document, entity_type, source_id):
    ents= []
    annots = document.get_annotations(entity_type, source_id = source_id)
    if len(annots) > 0:
        for annot in annots:
            ents.append({"start": annot.span[0], 'end':annot.span[1], "label": entity_type.upper()})
            drug_id = annot.ID
    return ents


def display_annotations(document, root = "sentence", entities = ["drug", "dose"], 
                        palette = [ '#ffb3ba','#ffdfba','#ffffba','#baffc9','#bae1ff']):

    to_disp = []

    for sent in document.get_annotations(root):
        tmp = {"text": sent.value, "uuid": sent.ID, "ents": []}

        for entity in entities:
            tmp['ents'] += convert_to_displacy(document, entity, sent.ID)

        to_disp.append(tmp)

        
    options = {"colors" : {}}
    i = 0
    for entity in entities: 
        options['colors'][entity.upper()] = palette[i]
        i += 1

    displacy.render(to_disp, manual=True, style = 'ent', options = options , jupyter=True)

