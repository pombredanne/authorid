#!/bin/bash

python src/eval_pan.py data/pan14_train/pan14-author-verification-training-corpus-dutch-essays-2014-04-22/truth.txt data/pan14_train/pan14-author-verification-training-corpus-dutch-essays-2014-04-22/answers_sparse.txt
python src/eval_pan.py data/pan14_train/pan14-author-verification-training-corpus-dutch-reviews-2014-04-22/truth.txt data/pan14_train/pan14-author-verification-training-corpus-dutch-reviews-2014-04-22/answers_sparse.txt
python src/eval_pan.py data/pan14_train/pan14-author-verification-training-corpus-english-novels-2014-04-22/truth.txt data/pan14_train/pan14-author-verification-training-corpus-english-novels-2014-04-22/answers_sparse.txt
python src/eval_pan.py data/pan14_train/pan14-author-verification-training-corpus-english-essays-2014-04-22/truth.txt data/pan14_train/pan14-author-verification-training-corpus-english-essays-2014-04-22/answers_sparse.txt
python src/eval_pan.py data/pan14_train/pan14-author-verification-training-corpus-greek-articles-2014-04-22/truth.txt  data/pan14_train/pan14-author-verification-training-corpus-greek-articles-2014-04-22/answers_sparse.txt
python src/eval_pan.py data/pan14_train/pan14-author-verification-training-corpus-spanish-articles-2014-04-22/truth.txt  data/pan14_train/pan14-author-verification-training-corpus-spanish-articles-2014-04-22/answers_sparse.txt
