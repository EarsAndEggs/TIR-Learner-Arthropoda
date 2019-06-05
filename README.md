# TIR-Learner-Rice
# ** ** TIR-Learner: a new ensemble method for TIR Transposable Element annotation
## Introduction
TIR-Learner is a ensemble pipeline for Terminal Inverted Repeat (TIR) transposable elements annotation.  TIR-Learner combines homology-based detection using a newly curated TIR element library with a structure-based method to identify TIR elements de novo.  The structure-based component includes Machine Learning (ML) algorithms to classify the output sequences into five major TIR superfamilies.
## Modules
There are three modules in TIR-Learner.
The first module, called Homology Based, uses a library of TE reference sequences as query for BLAST with genomic sequence.  Only hits with 100% coverage were kept to generate a dataset of homologous TE candidates.  These candidate TEs were further checked to confirm the presence of both TIRs and TSDs, requiring at least 80% similarity as previously described.  The output of Module 1 is a set of high-quality intact TEs with significant homology to known TEs.  Importantly, partial TE copies  and TE internal fragments would not be included in this set.

The second module utilizes both sequence homology and structural features to identify TEs with partial but incomplete similarity to existing TEs.  First, genomic DNA was analyzed by software termed [GRF](https://github.com/weijiaweijia/GenericRepeatFinder) to detect sequences ranging in size from 50 bp to 10,000 bp that are flanked by inverted repeats (putative TIRs).  These candidate segments were then searched for homology using the reference TE library described in Module 1.  Sequences showing at least 80% similarity and 80% coverage of a reference TE were retained as putative TIR elements.

The third module (Structure-based de novo) processes the candidate sequences that were excluded from the second module because they did not have 80% similarity or coverage of a reference TE.  These sequences were analyzed by Machine Learning methods to identify sequence motifs conserved in each of the five major TIR superfamilies.  The Machine Learning component then classifies each candidate sequence into one of the five TIR superfamilies, or a nonTIR class.
