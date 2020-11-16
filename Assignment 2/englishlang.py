import spacy
import pandas as pd
from collections import defaultdict

class my_0_iq_nlp:
    """
    I tried to do something clever, but I failed :D
    """

    def __init__(self):
        # Stas is `fast` ...
        self.property2subject = defaultdict(set)
        self.subject2property = defaultdict(set)
        # Stas has a `car`
        self.ownership = defaultdict(set)
        self.reverse_ownership = defaultdict(set)
        # [stas][drinks] = ('beer',...)
        # [stas][lives] = ('in inno'...)
        self.subject_verb_object = defaultdict(lambda : defaultdict(set))
        self.object_verb_subject = defaultdict(lambda : defaultdict(set))
        self.subject_verb_position = defaultdict(lambda : defaultdict(set))
        self.position_verb_subject = defaultdict(lambda : defaultdict(set))
        self.nlp = spacy.load("en_core_web_sm")

    def add_ownership(self , subj , obj):
        self.ownership[subj].add(obj)
        self.reverse_ownership[obj].add(subj)
        print(subj , " ++ " , obj)

    def add_property(self , subj , prop):
        self.subject2property[subj].add(prop)
        self.property2subject[prop].add(subj)
        print(subj , " !! " , prop)

    def add_action(self , subj , verb , obj):
        self.subject_verb_object[subj][verb].add(obj)
        self.object_verb_subject[obj][verb].add(subj)
        print(subj , " " , verb , " % " , obj)

    def add_adposition(self , subj , verb , prepositional):
        self.subject_verb_position[subj][verb].add(prepositional)
        self.position_verb_subject[prepositional][verb].add(subj)
        print(subj , " " , verb , " -> " , prepositional)


    def get_subject(self , doc , root):
        subject = None
        for token in doc:
            # look for a subject such that its head in the tree is the have verb
            if token.dep_ == 'nsubj' and token.head == root:
                subject = token
        assert subject
        for token in doc:
            # look for adjective modifier or compounds which describe subject
            if (token.dep_ == 'compound' or token.dep_ == 'amod') and token.head == subject:
                self.add_property(subject.lower_ , token.lower_)

        return subject

    def get_object(self , doc , root):

        object = None
        for token in doc:
            # look for an object
            if  (token.dep_ == 'obj' or token.dep_ == 'dobj') and token.head == root:
                object = token

        if not object:
            return None , None

        num_mod = None
        for token in doc:
            # look for numeral modifiers for the object and
            if token.dep_ == 'nummod' and token.head == object:
                num_mod = token
        return object , num_mod

    def process_ownership(self , doc , root):

        subject  = self.get_subject(doc , root)
        object , nummod = self.get_object(doc , root)

        assert subject and object

        # add ownership along with numeral modifier
        if nummod:
            self.add_ownership(subject.lower_, nummod.lower_ + ' ' + object.lower_)

        # add the object lemma anyway to account for singular case (if it was preceded by a numeral modifier)
        self.add_ownership(subject.lower_ , object.lemma_)

    def get_property(self , doc , root):
        property = None
        for token in doc:
            # look for attribute or adjectival complement
            if (token.dep_ == 'acomp' or token.dep_ == 'attr') and token.head == root:
                property = token
        negated = False
        for token in doc:
            # look for the negation token
            if token.dep_ == 'neg' and token.head == root:
                negated = True
        return property , negated

    def process_property(self , doc , root):
        subject = self.get_subject(doc , root)
        property , negated = self.get_property(doc , root)

        # make sure we have a property
        assert subject and property

        if negated:
            self.add_property(subject.lower_ , 'not ' + property.lower_)
        else:
            self.add_property(subject.lower_ , property.lower_)

    def process_action(self , doc , root):
        subject = self.get_subject(doc , root)
        object , nummod = self.get_object(doc , root)

        # if there's object
        if object:
            # add action along with numeral modifier
            if nummod:
                self.add_action(subject.lower_, root.lemma_ , nummod.lower_ + ' ' + object.lower_)
            # add the object lemma anyway to account for singular case (if it was preceded by a numeral modifier)
            self.add_action(subject.lower_, root.lemma_ , object.lemma_)

        preposition = None
        for token in doc:
            if token.dep_ == 'prep' and token.head == root:
                preposition = token
        if preposition:
            for token in doc:
                if token.dep_ == 'pobj' and token.head == preposition:
                    self.add_adposition(subject.lower_ , root.lemma_ , preposition.lower_ + ' ' + token.lower_)


    def process_sentence(self , sentence):

        doc = self.nlp(sentence)

        # first look for the root token (of tree of dependencies)
        # it's either the main verb (eat,drink...) or verb `be` or verb `has`
        for token in doc:
            if token.dep_ == 'ROOT':
                if token.pos_ == 'AUX':
                    if token.lemma_ == 'have':
                        self.process_ownership(doc , token)
                    if token.lemma_ == 'be':
                        self.process_property(doc , token)
                if token.pos_ == 'VERB':
                    self.process_action(doc , token)


    def answer_ownership(self , doc , root):

        subject = self.get_subject(doc , root)
        object , nummod = self.get_object(doc , root)
        objtok = object.lower_
        if nummod:
            objtok = nummod.lower_ + ' ' + object.lower_
        if subject.pos_ == 'PRON':
            return self.reverse_ownership[objtok]
        if object.pos_ == 'PRON':
            return self.ownership[subject.lower_]

        return "weird stuff"

    def answer_action(self , doc , root):
        subject = self.get_subject(doc , root)
        object , nummod = self.get_object(doc , root)
        objtok = None

        if object:
            if nummod:
                objtok = nummod.lower_ + ' ' + object.lower_
            else:
                objtok = object.lower_

        preposition , prep_tok = None , None
        for token in doc:
            if token.dep_ == 'prep' and token.head == root:
                preposition = token
        if preposition:
            for token in doc:
                if token.dep_ == 'pobj' and token.head == preposition:
                    prep_tok =  preposition.lower_ + ' ' + token.lower_

        if subject.pos_ == 'PRON':
            if objtok:
                return self.object_verb_subject[objtok][root.lemma_]
            if prep_tok:
                return self.position_verb_subject[prep_tok][root.lemma_]

        if objtok and object.pos_ == 'PRON':
            return self.subject_verb_object[subject.lower_][root.lemma_]

        return "unknown"

    def answer_property(self , doc , root):
        subject = self.get_subject(doc , root)
        property , negated = self.get_property(doc , root)

        assert subject and property

        if negated:
            property_tok = 'not ' + property.lower_
        else:
            property_tok = property.lower_
        if subject.pos_ == 'PRON':
            return self.property2subject[property_tok]
        if property in self.subject2property[subject.lower_]:
            return "YES!"
        else:
            return "NO!"

    def process_query(self , question):

        doc = self.nlp(question)

        # first look for the root token (of tree of dependencies)
        # it's either the main verb (eat,drink...) or verb `be` or verb `has`
        for token in doc:
            if token.dep_ == 'ROOT':
                if token.pos_ == 'AUX':
                    if token.lemma_ == 'have':
                        return self.answer_ownership(doc, token)
                    if token.lemma_ == 'be':
                        return self.answer_property(doc, token)
                if token.pos_ == 'VERB':
                    return self.answer_action(doc, token)



def run_sample_test():
    sentences = [
        'Fast Stas is cool', #0
        'Old Stas lives in Innopolis.', #1
        'Old Giancarlo lives in Zion.', #2
        'Stas has a bicycle.', #3
        'Alena has two bicycles.', #4
        'Stas eats pizza.', #5
        'Stas is not a doctor.', #6
        'Marina is a doctor.', #7
        'Hussain has a white vape', #8
        'big Alex is not nice', #9
        'Joe Biden is sleepy' #10
    ]


    menss = my_0_iq_nlp()


    for s in sentences:
        menss.process_sentence(s)

    print('\n\n\n\nThat was some debug log so you can see facts extracted\n\n')
    print("Facts ::")

    for s in sentences:
        print(s)

    assert menss.process_query('Who lives in Innopolis?') == {'stas'}
    assert menss.process_query('Who eats pizza?') == {'stas'}
    assert menss.process_query('Is Stas a doctor?') == "NO!"
    assert menss.process_query('Who is old?',) == {'giancarlo', 'stas'}
    assert menss.process_query('Who has a bicycle?') == {'stas', 'alena'}
    assert menss.process_query('What does Stas eat?') == {'pizza'}
    assert menss.process_query('What does Stas have?') == {'bicycle'}


    queries = [
        'Who lives in Innopolis?',
        'Who eats pizza?',
        'Is Stas a doctor?',
        'Who is old?',
        'Who has a bicycle?',
        'What does Stas eat?',
        'What does Stas have?'
    ]

    for q in queries:
        print("Query : " , q)
        print("Answer : " , menss.process_query(q))



run_sample_test()
