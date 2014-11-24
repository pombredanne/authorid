#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Author ID main using a sparse representation
# ----------------------------------------------------------------------
# Ivan V. Meza
# 2014/IIMAS, México
# ----------------------------------------------------------------------
# authorid_sparse.py is free software: you can redistribute it and/or modify
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

# System libraries
import argparse
import sys
import os
import os.path
import sklearn.preprocessing as preprocessing
import numpy as np
#import matplotlib.pyplot as pl
import random
import itertools
from collections import Counter
from oct2py import octave
from oct2py.utils import Oct2PyError
octave.addpath('src/octave')

# Local imports
import docread

def verbose(*args):
    """ Function to print verbose"""
    if opts.verbose:
        print >> out, "".join(args)

def info(*args):
    """ Function to print info"""
    print >> out, "".join(args)

def muestreo(counter,reps,percentage=.80):
    final_count={}
    for rep in reps:
        list_counter=list(counter[rep].elements())
        random.shuffle(list_counter)
       
        size=len(list_counter)
        final_list=list_counter[0:int(size*percentage)]  
      
        final_count[rep]=Counter(final_list)  
    return final_count

def get_master_impostors(id,nimpostors,ndocs,nknown,problems,sw=[],mode="test",cutoff=0):
    if mode.startswith("test"):
        id=id+"___"
    master_impostors=[]
    pat=id[:2]
    ids_candidates=[]
    for i,(id_,(ks,uks)) in enumerate(problems):
        if id_.startswith(pat) and id != id_ and i < len(problems)-nknown:
            ids_candidates.append(i)
    pos=range(len(ids_candidates))
    random.shuffle(pos)
   
   
    for i in range(nimpostors):
        for j in range(ndocs):
            id_=pos[i*nimpostors+j]
            for k in range(nknown):
                master_candidate={}
                doc=problems[ids_candidates[id_]+k]
                for repname in opts.reps:
                    try:
                        exec("f=docread.{0}".format(repname))
                        rep=f(doc[1][0][0][1],cutoff=cutoff,sw=sw)
                    except:
                        rep=Counter()
                    try:
                        master_candidate[repname].update(rep)
                    except KeyError:
                        master_candidate[repname]=Counter(rep)

                master_impostors.append(master_candidate)
    return master_impostors
 

def project_into_vectors(examples,full_voca,unknown,reps,nmost=100):
    vectors=[[] for e in examples]
    uvec=[]
    mass=[]
    N=len(examples)+1
    for rep in reps:
        full=Counter()
        for example in examples:
            full.update(example[rep])
            mass.append(sum(example[rep].values()))
        umass=sum(unknown[rep].values())
        full.update(unknown[rep])
        idx=[p[0] for p in full.most_common()]
        idf={}
        t=0
        for id_ in idx:
            t=0
            for example in examples:
                try:
                    example[rep][id_]
                    t+=1
                except KeyError:
                    pass
            try:
                unknown[id_]
                t+=1
            except KeyError:
                pass
            idf[id_]=np.log(1.0*abs(N)/abs(t))

        for i,example in enumerate(examples):
            if mass[i]>0:
                arr=[1.0*example[rep][k]*idf[k] for k in idx]
            else:
                arr=[1.0*example[rep][k]*idf[k] for k in idx]
            vectors[i].append(arr)
        if umass>0:
           uvec.append([1.0*unknown[rep][k]*idf[k] for k in idx])
        else:
           uvec.append([1.0*unknown[rep][k]*idf[k] for k in idx])
    return [list(itertools.chain(*vec)) for vec in vectors], list(itertools.chain(*uvec))

codes=docread.codes


def process_corpus(problems,impostor_problems,opts,mode,sw):
	#Iterating over problems

        if opts.nmax>0:
            problems=problems[:opts.nmax]

        for id,(ks,uks) in problems:
            master_author={}
            docs_author=[]
            master_unknown={}
            full_voca={}
            ks_=ks
            for filename,doc in ks:
                doc_author={}
                for repname in opts.reps:
                    try:
                        exec("f=docread.{0}".format(repname))
                        rep=f(doc,cutoff=opts.cutoff,sw=sw)
                    except:
                        rep=Counter()
                    doc_author[repname]=rep
                    try:
                        master_author[repname].update(rep)
                    except KeyError:
                        master_author[repname]=Counter(rep)
                    try:
                        full_voca[repname].update(rep)
                    except KeyError:
                        full_voca[repname]=Counter(rep)
                docs_author.append(doc_author)

            for filename,doc in uks:
                 for repname in opts.reps:
                    try:
                        exec("f=docread.{0}".format(repname))
                        rep=f(doc,sw=sw)
                    except:
                        rep=Counter()
                    try:
                        master_unknown[repname].update(rep)
                    except KeyError:
                        master_unknown[repname]=Counter(rep)
                    try:
                        full_voca[repname].update(rep)
                    except KeyError:
                        full_voca[repname]=Counter(rep)

            results=[]
            iters=opts.iters
            #print "============"
            #print id, master_author
            #print ">>>", master_unknown

            for iter in range(iters):
                #Extracting Examples
                examples= []
                lens=[]
                # Adding impostors

                master_impostors=get_master_impostors(id,opts.nimpostors,opts.documents,len(ks),impostor_problems,mode=mode,sw=sw,cutoff=opts.cutoff)
                #print ">>>>>>>>>",len(master_impostors)
                #for mi in master_impostors:
                   #print ">>>>",mi
                for j,master_impostor in enumerate(master_impostors):
                     examples.append(muestreo(master_impostor,opts.reps,percentage=opts.percentage))

                for j in range(opts.documents):
                    for i in range(len(ks)):
                        doc_author=docs_author[i]
                        examples.append(muestreo(doc_author,opts.reps,percentage=opts.percentage))
                        lens.append(len(ks_))
                #print "<<<<<<<<<<<<",len(examples)

                sample_unknown=muestreo(master_unknown,opts.reps,percentage=1.0)

                # Sparce algorithm
                # Proyecting examples into a vector
                example_vectors,unknown=project_into_vectors(examples,full_voca,sample_unknown,opts.reps)
                #print unknown
                #for example in enumerate(example_vectors):
                #    print len(example),example


                # Creating matrix A
                # First samples represent to author, rest impostors
                # Normalizing the data
                A=np.matrix(example_vectors)
                
                A_=A.T
                A=preprocessing.normalize(A,axis=0)
                y=np.matrix(unknown)
                y_=y.T
                nu=0.0000001
                tol=0.0000001
                #AA=[v for v in example_vectors]
                #AA.append(unknown)
                #AAA=np.matrix(AA)
                #AAA=preprocessing.normalize(AAA,axis=0)
                #AAA.shape

                #pl.pcolor(AAA,cmap=pl.cm.Blues)
                #pl.title("A")
                #pl.show()

                stopCrit=3
                answer=False
                nanswers=0
                while not answer:
                    if nanswers>4:
                        results=[0.0 for i in range(iters)]
                        break
                    try:
                        x_0, nIter = octave.SolveHomotopy(A_, y_, 'lambda', nu, 'tolerance', tol, 'stoppingcriterion', stopCrit)
                        #ind=np.arange(x_0.shape[0])
                        #pl.bar(ind,[np.float(x) for x in x_0])
                        #pl.title("X_0")
                        #pl.show()
                    
                        # Calculating residuals
                        residuals=[]
                        d_is=[]
                        k=len(examples)/len(ks)*opts.documents
                        for i in range(k):
                            n=opts.documents*len(ks)
                            d_i= np.matrix([[0.0 for x in x_0[:i*n]]+\
                                 [np.float(x) for x in x_0[i*n:(i+1)*n]]+\
                                 [0.0 for x in x_0[(i+1)*n:]]]).T
                            d_is.append(np.linalg.norm(d_i,ord=1))
                            #print "y",y
                            #print "y_",(A_*d_i).T
                            r_is=y_-A_*d_i
                            r_i=np.linalg.norm(r_is,ord=2)
                            residuals.append(r_i)
                        #print residuals
                        
                        sci=(k*np.max(d_is)/np.linalg.norm(x_0,ord=1)-1)/(k-1)
                        identity=np.argmin(residuals)
                        #print sci, identity
                        scith=0.1
                        if sci<scith:
                            results.append(0.0)
                        else:
                            if identity==(k-1):
                                results.append(1.0)
                            else:
                                results.append(0.0)
                        #ind=np.arange(len(residuals))
                        #pl.bar(ind,residuals)
                        #pl.title(str(sci)+"---"+id+"----"+str(results[-1])+"---"+str(scith))
                        #pl.show()
                        nanswers+=1
                        answer=True
                    except Oct2PyError:
                        pass
            print id, sum(results)/iters


# MAIN program
if __name__ == "__main__":

    # Command line options
    p = argparse.ArgumentParser("Author identification")
    p.add_argument("DIR",default=None,
            action="store", help="Directory with examples")
    p.add_argument("Answers",default=None,
            action="store", help="File with the key answers")
    p.add_argument('--version', action='version', version='%(prog)s 0.2')
    p.add_argument("-o", "--output",default=None,
            action="store", dest="output",
            help="Output [STDOUT]")
    p.add_argument("-m", "--mode",default='test',
            action="store", dest="mode",
            help="test|train|devel [test]")
    p.add_argument("--language",default='all',
            action="store", dest="language",
            help="Language to process [all]")
    p.add_argument("--genre",default='all',
            action="store", dest="genre",
            help="Genre to process [all]")
    p.add_argument("-r","--rep",default=[],
            action="append", dest="reps",
            help="adds representation to process")
    p.add_argument("--cutoff",default=5,type=int,
            action="store", dest="cutoff",
            help="Minimum frequency [5]")
    p.add_argument("--iters",default=100,type=int,
            action="store", dest="iters",
            help="Total iterations [100]")
    p.add_argument("--impostors",default=None,
            action="store", dest="impostors",
            help="Directory of imposter per auhtor")
    p.add_argument("--max",default=0,type=int,
            action="store", dest="nmax",
            help="Maximum number of problems to solve [All]")
    p.add_argument("--nimpostors",default=8,type=int,
            action="store", dest="nimpostors",
            help="Total of imposter per auhtor [8]")
    p.add_argument("--documents",default=1,type=int,
            action="store", dest="documents",
            help="Documents per author [1]")
    p.add_argument("--percentage",default=.60,type=float,
            action="store", dest="percentage",
            help="Sampling percentage [.60]")
    p.add_argument("--model",default=".",
            action="store", dest="model",
            help="Model to save training or to test with [None]")
    p.add_argument("--random",default=True,
            action="store_false", dest="random",
            help="Use random seed [True]")
    p.add_argument("--concatenate",default=False,
            action="store_true", dest="concatenate",
            help="Concatenate [False]")
    p.add_argument("--cvs",default=False,
            action="store_true", dest="csv",
            help="Save matrices into a .csv file [False]")
    p.add_argument("--method",default="lp",
            action="store", dest="method",
            help="lp|avp|svm|ann [lp]")
    p.add_argument("--stopwords", default="data/stopwords.txt",
            action="store", dest="stopwords",
            help="List of stop words [data/stopwords.txt]")
    p.add_argument("--answers", default="answers.txt",
            action="store", dest="answers",
            help="Answers file [answers.txt]")
    p.add_argument("-v", "--verbose",
            action="store_true", dest="verbose",
            help="Verbose mode [Off]")
    opts = p.parse_args()

    if not opts.random:
        random.seed(9111978)

    # Managing configurations  --------------------------------------------
    # Check the correct mode
    if not opts.mode in ["train","test","devel"]:
        p.error('Mode argument not valid: devel, train  test')

    # Parameters
    # Patterns for files
    known_pattern=r'known.*\.txt'
    unknown_pattern=r'unknown*.txt'

    dirname = opts.DIR

    # Defines output
    out = sys.stdout
    if opts.output:
        try:
            out = open(opts.output)
        except:
            p.error('Output parameter could not been open: {0}'\
                    .format(opts.output))
    verbose("Running in mode:",opts.mode)

    if opts.csv:
        import csv
        file_A=open("A.csv","w")
        csv_A=csv.writer(file_A,delimiter=',',quotechar=",")
        file_b=open("b.csv","w")
        csv_b=csv.writer(file_b,delimiter=',',quotechar=",")


    # Loading configuration files ----------------------------------------
    # - .ignore   : files to ignore some files
    # - stopwords : words to ignore from the documents

    # Loading ignore if exists
    _ignore=[]
    if os.path.exists('.ignore'):
        verbose('Loading files to ignore from: .ignore')
        with open('.ignore') as file:
            for line in file:
                _ignore.append(line.strip())


    # Loading stopwords if exits
    stopwords=[]
    if os.path.exists(opts.stopwords):
        verbose('Loading stopwords: ',opts.stopwords)
        stopwords=docread.readstopwords(opts.stopwords)
    else:
        info('Stopwords file not found assuming, emtpy',opts.stopwords)

    # Loading main files -------------------------------------------------
    # load problems or problem
    verbose('Loading files')
    problems=docread.problems(
             docread.dirproblems(dirname,known_pattern,unknown_pattern,_ignore,
                                 code=codes[opts.language][opts.genre]))

    if opts.concatenate:
        nproblems=[]
        for idd,(ks,uks) in problems:
            ndocs=[]
            for filename,doc in ks:
                ndocs.append(doc)
            ks_=list(itertools.chain(*ndocs))
            nproblems.append((idd,([(ks[0][0],ks_)],uks)))
        problems=nproblems


    # Load impostors from directory
    impostors=None
    if opts.impostors:
        impostors=[]
        verbose('Loading impostors')
        files  =[(i,x,"{0}/{1}".format(opts.impostors,x)) for i,x in
                                enumerate(os.listdir(opts.impostors))]
        random.shuffle(files)
        for i,id,f in files[:3000]:
                impostors.append(
                    (opts.impostors[-2:]+"__"+str(i),
                    ([(f,docread.readdoc(f)[:900])],[])))
    else:
        verbose('Using problems as impostors')
        impostors=problems

    # Loading answers file only for DEVELOPMENT OR TRAINNING MODE
    if opts.mode.startswith("train") or opts.mode.startswith('devel'):
        if opts.Answers:
            answers_file=opts.Answers
        else:
            answers_file="{0}/{1}".format(dirname,opts.answers)
        verbose('Loading answer file: {0}'.format(answers_file))
        answers = docread.loadanswers(answers_file,_ignore,
                code=codes[opts.language][opts.genre])

        # Checking for consistency
        if not len(problems) == len(answers):
            p.error("Not match for number of problems({0}) and \
                    answers({1})".format(len(problems),len(answers)))

    # Development model 
    if opts.mode.startswith("devel"):
        verbose('Starting the process')
        process_corpus(problems,impostors,opts,"devel",sw=stopwords)
      
    # TRAINING - Save examples
    elif opts.mode.startswith("train"):
        import pickle
        
        stream_model = pickle.dumps(impostors)
        verbose("Saving model into ",opts.model)
        with open(opts.model,"w") as modelf:
            modelf.write(stream_model)

 
    elif opts.mode.startswith("test"):
        import pickle
        
        impostors = pickle.load(open(opts.model))
        verbose("Reading model",opts.model)
        process_corpus(problems,impostors,opts,"test",sw=stopwords)
