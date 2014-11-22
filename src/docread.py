#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Experiment defition manager
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2013/IIMAS/UNAM
# Paola Ledesma 
# 2013/ENAH
# Gibran Fuentes
# 2013/IIMAS/UNAM
# Gabriela Jasso
# 2013/FI/UNAM
# Ángel Toledo
# 2013/FC/UNAM
# ----------------------------------------------------------------------
# docread.py is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# -------------------------------------------------------------------------

import re
import os
import os.path
import codecs
from collections import Counter
from nlpcore import  fulltagger



spaces=re.compile('\W+',re.UNICODE)
spaces_=re.compile('[ \t]+',re.UNICODE)
period=re.compile('[.;!?]',re.UNICODE)
rcapital=re.compile(u'[\u0391-\u03A9][^ ]+|[A-Z][^ ]+',re.UNICODE)
rfullcapital=re.compile(u'[\u0391-\u03A9]+$|[A-Z]+$',re.UNICODE)
#rcapital=re.compile(r'[A-Z][^W]+',re.UNICODE)
rpar2 = re.compile(u'[.:].?\r?\n[A-Z]|[.:].?\r?\n[\u0391-\u03A9]',re.UNICODE)
rterm=re.compile('[.,]',re.UNICODE)
rpar = re.compile('\'''',re.UNICODE)
renter = re.compile('\r?\n',re.UNICODE)
renterer =re.compile('\r?\n',re.UNICODE)
#wordpunct=re.compile('\w+\W+',re.UNICODE)
wordpunct=re.compile(u'\W+$',re.UNICODE)
rcomposed=re.compile(u'.+\W+.+',re.UNICODE)
rwordcomposed=re.compile(u'\w+\W+\w+',re.UNICODE)
rcoma=re.compile(r',',re.UNICODE)
rdot=re.compile(r'\.',re.UNICODE)
rdeli=re.compile(r'[.?!]',re.UNICODE)
rspc=re.compile(r'[/]',re.UNICODE)
rwspc=re.compile(r'\s',re.UNICODE)
rnumbers=re.compile(r'\d+',re.UNICODE)
ryear=re.compile(r'\d\d\d\d$',re.UNICODE)
rrange=re.compile(r'\d+(-|:)\d+',re.UNICODE)
rdecimal=re.compile(r'\d+(\.|,)\d+$',re.UNICODE)

# Codes for problems
codes={
    'en': {
        'essays': re.compile('^[^\w]*EE'),
        'novels': re.compile('^[^\w]*EN'),
        'all': re.compile('^[^\w]*E')
        },
    'nl': {
        'essays': re.compile('^[^\w]*DE'),
        'reviews': re.compile('^[^\w]*DR'),
        'all': re.compile('^[^\w]*D')
        },
    'gr': {
        'news': re.compile('^[^\w]*GR'),
        'all': re.compile('^[^\w]*GR')
        },
    'es': {
        'news': re.compile('^[^\w]*SP'),
        'all': re.compile('^[^\w]*SP')
        },
    'all': {
        'all': re.compile('.*')
    }
}

def check(exp,doc,doc_,pref):
    wds = [ pref+x for x,y,z in doc if exp.match(x)]
    wds_ = Counter(wds)
    doc_.update(wds_)
    doc_[pref+"T"]=len(wds_)
    doc_[pref+"M"]=len(wds)


    

def none(docs,filename):
    return None

# Functions for representation extraction
def numbers(doc,sw=[],cutoff=0):
    doc_=Counter([])
    check(rnumbers,doc,doc_,"")
    check(ryear,doc,doc_,"year")
    check(rrange,doc,doc_,"range")
    check(rdecimal,doc,doc_,"dec")
    postprocess(doc_)
    return doc_

def capital(doc,sw=[],cutoff=0):
    doc_=Counter([])
    check(rcapital,doc,doc_,"")
    check(rfullcapital,doc,doc_,"f")
    postprocess(doc_)
    return doc_

def bow(doc,sw=[],cutoff=0):
    wds = [ x.lower() for x,y,z in doc if z not in sw]
    doc_=Counter([x.encode('utf-8') for x in wds])
    hist=[]
    for v in doc_.values():
        hist.append(v)
    doc_.update(hist)
    postprocess(doc_,sw=sw,cutoff=cutoff)
    return doc_

def lemma(doc,sw=[],cutoff=0):
    wds = [ z for x,y,z in doc]
    doc_=Counter([x.encode('utf-8') for x in wds])
    postprocess(doc_,sw=sw,cutoff=cutoff)
    return doc_

def pos(doc,sw=[],cutoff=0):
    wds = [ y for x,y,z in doc if z not in sw]
    doc=Counter([x.encode('utf-8') for x in wds])
    postprocess(doc,cutoff=cutoff)
    return doc

def poslemma(doc,sw=[],cutoff=0):
    wds = [ "{0}_{1}".format(y,z) for x,y,z in doc if z not in sw]
    doc_=Counter([x.encode('utf-8') for x in wds])
    postprocess(doc_,cutoff=cutoff)
    return doc_


def stopwords(doc,sw=[],cutoff=0):
    wds = [ x for x,y,z in doc if x in sw]
    doc_=Counter(wds)
    postprocess(doc_,sw=[],cutoff=cutoff)
    return doc_


def prefix(doc,sw=[],cutoff=0):
    wds = [ x.lower()[:5] for x,y,z in doc if len(x)>5]
    doc_=Counter(wds)
    postprocess(doc_,sw=sw,cutoff=cutoff)
    return doc_

def sufix(doc,sw=[],cutoff=0):
    wds = [ x.lower()[-5:] for x,y,z in doc if len(x)>5]
    doc_=Counter(wds)
    postprocess(doc_,cutoff=cutoff)
    return doc_


def letters(doc,sw=[],cutoff=0):
    wds = "".join([ x.lower() for x,y,z in doc if x in sw])
    doc_=Counter(wds)
    postprocess(doc_,cutoff=cutoff)
    return doc_

def coma(doc,sw=[],cutoff=0):
    wds = [ x for x,y,z in doc if rcoma.search(x)]
    values=[x.encode('utf-8')[:-1] for x in wds]
    doc_=Counter(values)
    postprocess(doc_,sw=sw,cutoff=cutoff)
    return doc_


def punct(doc,sw=[],cutoff=0):
    doc_=Counter([])
    check(wordpunct,doc,doc_,"")
    check(rcomposed,doc,doc_,"comp_")
    check(rwordcomposed,doc,doc_,"wcomp_")
    postprocess(doc_)
    return doc_

def dot(doc,sw=[],cutoff=0):
    doc_=Counter([])
    check(rdot,doc,doc,"")
    postprocess(doc_,cutoff=cutoff)
    return doc_

def dotpos(doc,sw=[],cutoff=0):
    doc_=Counter()
    dp=[]
    for wd,nwd in zip(doc,doc[1:]):
        if rdot.match(wd[0]):
            dp.append(nwd[1])
    doc_.update(dp)
    postprocess(doc_,cutoff=cutoff)
    return doc_

def nstcs(doc,sw=[],cutoff=0):
    doc_=Counter()
    l=0
    ls=[]
    for wd in (doc):
        if rdeli.match(wd[0]):
            ls.append(l)
            l=0
        else:
            l+=1
    doc_.update([str(l/5) for l in ls])
    postprocess(doc_,cutoff=cutoff)
    return doc_



def sqrbrackets(doc,sw=[],cutoff=0):
    wds = [ x for x,y,z in doc if rspc.search(x)]
    doc_=Counter([x.encode('utf-8') for x in wds])
    postprocess(doc_,cutoff=cutoff)
    return doc_

def whitespc(doc,sw=[],cutoff=0):
    wds = [ x for x,y,z in doc if rwspc.search(x)]
    doc_=Counter([x.encode('utf-8') for x in wds])
    postprocess(doc_,cutoff=cutoff)
    return doc

def bigramlemma(doc,sw=[],cutoff=0):
    wds = [ z for x,y,z in doc]
    wds = preprocess(wds)
    bigram = zip(wds, wds[1:])
    values=["{0} {1}".format(x.encode('utf-8'),
                                    y.encode('utf-8')) for x, y in bigram]
    doc_ = Counter(values)
    postprocess(doc_,cutoff=cutoff)
    return doc_


def bigram(doc,sw=[],cutoff=0):
    wds = [ x.lower() for x,y,z in doc]
    bigram = zip(wds, wds[1:])
    values=["{0} {1}".format(x.encode('utf-8'),
                                    y.encode('utf-8')) for x, y in bigram]
    doc_ = Counter(values)
    postprocess(doc_,cutoff=cutoff)
    return doc_

def bigrampref(doc,sw=[],cutoff=0):
    wds = [ z[:5] for x,y,z in doc if x in sw]
    wds = preprocess(wds)
    bigram = zip(wds, wds[1:])
    values=["{0} {1}".format(x.encode('utf-8')[:5],
                                    y.encode('utf-8')[:3]) for x, y in bigram]
    doc_ = Counter(values)
    postprocess(doc_,cutoff=cutoff)
    return doc_

def bigramsuf(doc,sw=[],cutoff=0):
    wds = [ z[5:] for x,y,z in doc if x in sw]
    wds = preprocess(wds)
    bigram = zip(wds, wds[1:])
    values=["{0} {1}".format(x.encode('utf-8')[-5:],
                                    y.encode('utf-8')[:3]) for x, y in bigram]
    doc_ = Counter(values)
    postprocess(doc_,cutoff=cutoff)
    return doc_



def trigram(doc,sw=[],cutoff=0):
    wds = [ x for x,y,z in doc]
    wds = preprocess(wds)
    tri = zip(wds, wds[1:], wds[2:])
    values = ["{0} {1} {2}".format(x.encode('utf-8'),
                                    y.encode('utf-8'),
                                    z.encode('utf-8')) for x, y,z in tri]
    doc_ = Counter(values)
    postprocess(doc_,cutoff=cutoff)
    return doc_


def skipgram(doc,sw=[],skip=5,cutoff=0):
    wds = [ x.lower() for x,y,z in doc]
    doc_=Counter()
    for s in range(2,skip):
        skip_ = zip(wds, wds[s:])
        values=["{0} {1}".format(x.encode('utf-8'),
                                    y.encode('utf-8')) for x, y in skip_]
        doc_.update(values)
    postprocess(doc_,cutoff=cutoff)
    return doc_

def skipposgram(doc,sw=[],skip=5,cutoff=0):
    wds = [ x.lower() for x,y,z in doc]
    pos = [ z.lower() for x,y,z in doc]
    doc_=Counter()
    for s in range(2,skip):
        skip_ = zip(wds, pos[s:])
        values=["{0} {1}".format(x.encode('utf-8'),
                                    y.encode('utf-8')) for x, y in skip_]
        doc_.update(values)
    postprocess(doc_,cutoff=cutoff)
    return doc_



def ngramword(doc,sw=[],ngram=5,cutoff=0):
    pos = [ x.lower() for x,y,z in doc]
    doc_=Counter()
    for n in range(ngram):
        args=[]
        pat=[]
        for j in range(n+1):
            args.append(pos[j:])
            pat.append('{{{0}}}'.format(j))
        val= zip(*args)
        values = [" ".join(pat).format(*v) for v in val]
        doc_.update(values)
    postprocess(doc_,cutoff=cutoff)
    return doc_


def ngrampos(doc,sw=[],ngram=5,cutoff=0):
    pos = [ y for x,y,z in doc]
    doc_=Counter()
    for n in range(ngram):
        args=[]
        pat=[]
        for j in range(n+1):
            args.append(pos[j:])
            pat.append('{{{0}}}'.format(j))
        val= zip(*args)
        values = [" ".join(pat).format(*v) for v in val]
        doc_.update(values)

    postprocess(doc_,cutoff=cutoff)
    return doc_

def ngramlemma(doc,sw=[],ngram=5,cutoff=0):
    pos = [z for x,y,z in doc]
    doc_=Counter()
    for n in range(ngram):
        args=[]
        pat=[]
        for j in range(n+1):
            args.append(pos[j:])
            pat.append('{{{0}}}'.format(j))
        val= zip(*args)
        values = [" ".join(pat).format(*v) for v in val]
        doc_.update(values)

    postprocess(doc_,cutoff=cutoff)
    return doc_

def preprocess(wrds,sw):
    wrds_=[]
    for wrd in wrds:
        if not wrd in sw:
            wrds_.append(wrd)
    return wrds_

def postprocess(doc,cutoff=5,sw=[]):
    cutoff=[x for x,c in doc.iteritems() if c < cutoff ]
    for c in cutoff:
        del doc[c]
    for c in sw:
        del doc[c]

representations=[
    ('letters',letters),   #X
    ('bigram',bigram),
    ('bigrampref',bigrampref),
    ('bigramsug',bigramsuf),
    ('trigram',trigram), 
    ('punctuation',punct), 
    ('stopwords',stopwords), 
    ('numbers',numbers),
    ('coma',coma),
    ('skipgram',skipgram),
    ('skipposgram',skipposgram),
    ('dot',dot),           
    ('dotpos',dotpos),           
    ('bow',bow),
    ('lemma',lemma),
    ('poslemma',poslemma),
    ('prefix',prefix),
    ('sufix',sufix),
    ('capital',capital),   
    ('whitespc',whitespc),    #X
    ('ngramword',ngramword),
    ('ngrampos',ngrampos),
    ('ngramlemma',ngramlemma),
    ('nstcs',nstcs),

    ]


def problems(dirproblems_):
    return [(id,([(k,readdoc(k)) for k in ks],[(u,readdoc(u)) for u in uks])) \
                for id,(ks,uks) in dirproblems_ ]    

def dirproblems(dirname, rknown  =r"known.*\.txt",
                         runknown=r"unknown.*\.txt",ignore=[],code=re.compile('.*')):
    """Loads the directories containing problems"""
    dirnames=[(x,"{0}/{1}".format(dirname,x)) for x in os.listdir(dirname)  
                if not x in ignore and
                   code.match(x) and
                   os.path.isdir("{0}/{1}".format(dirname,x))]
    dirnames.sort()
    problems=[]
    for id,dirname in dirnames:
        problems.append((id,
                        dirproblem(dirname,rknown,runknown,ignore)))
    return problems


def dirproblem(dirname, rknown  =r"known.*\.txt",
                        runknown=r"unknown.*\.txt",ignore=[]):
    """Loads problem """
    r_known=re.compile(rknown)
    r_unknown=re.compile(runknown)
    known  =["{0}/{1}".format(dirname,x) for x in os.listdir(dirname) 
                        if not x in ignore and
                        r_known.match(x)]
    known.sort()
    unknown=["{0}/{1}".format(dirname,x) for x in os.listdir(dirname)
                        if not x in ignore and
                        r_unknown.match(x)]
    unknown.sort()
    return known,unknown

# Reading file functions
def readstopwords(filename):
    stopwords=[]
    with codecs.open(filename,'r','utf-8') as file:
        for line in file:
            line=line.strip()
            if len(line)>0 and not line[0]=='#':
                stopwords.append(line)
    return stopwords


def readdoc(filename):
    try:
        with codecs.open(filename,'r','utf-8') as fh:
            return  fulltagger.tag(fh.read())
    except UnicodeDecodeError:
        try:
            with codecs.open(filename,'r','ISO-8859-1') as fh:
                return fulltagger.tag(fh.read())
        except UnicodeDecodeError:
            return ""



def loadanswers(filename,ignore=[],code=re.compile('.*')):
    """Loads answers file"""
    r_answer=re.compile(r"[^\w]*(\w*) +(.*)$")
    answers={}
    for line in open(filename):
        line=line.strip()
        if len(line)==0:
            continue
        if code.match(line) is None:
            continue
        m=r_answer.match(line)
        if m:
            if not m.group(1) in ignore:
                try:
                    answers[m.group(1)]=float(m.group(2))
                except ValueError:
                    answers[m.group(1)]=m.group(2)

    return answers

def loadproba(filename,ignore=[]):
    """Loads probabilities file"""
    #r_answer=re.compile(r"[^\w]*(\w*) (Y|N)$")
    answers={}
    i=0
    for line in open(filename):
        line=line.strip()
        if len(line)==0 or not line.startswith("proba"):
            continue
       
        r_answer=line.split(' ')
	answers[i]=r_answer[1]
        i=i+1
    return answers
