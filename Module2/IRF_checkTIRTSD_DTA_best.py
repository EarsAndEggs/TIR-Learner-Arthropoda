import sys
import os
import subprocess
from Bio.Seq import Seq
from Bio import SeqIO
import pandas as pd
import os
from os.path import basename
import multiprocessing
from multiprocessing import Pool
import time



TIR={}
#
TSD={}
TSD["DTA"]=8
TSD["DTT"]=2
TSD["DTM"]=9
TSD["DTH"]=3
TSD["DTC"]=3


def compare(tir1,tir2):
    d=0
    for i in range(0,len(tir1)):
        if(tir1[i]!=tir2[i]):
            d+=1
    return d

def slidingWindow(seq1,seq2,tsdlength):
    set1=[]
    set2=[]
    for i in range(0,len(seq1)-tsdlength+1):
        set1.append(seq1[i:i+tsdlength])
        set2.append(seq2[i:i+tsdlength])
    return set1,set2


def GetDiff(set1,set2):
    tsd_diff={}
    for i in range(0,len(set1)):
        for j in range(0,len(set2)):
            name=str(i)+":"+str(j)
            diff=compare(set1[i],set2[j])
            tsd_diff[name]=diff
    return tsd_diff

def isTSD(tsd_dffset,fam):
    for i in tsd_dffset:
        if tsd_dffset[i]<TSD[fam]*0.2:
            return True
    return False


def getTIR(rec):
    s = str(rec.seq)
    id=rec.id
    l_id=id.split("|")
    if (l_id[0] in [str(i) for i in range(1,13)]):
        tirLength=int(l_id[-2])
    else:
        tirLength = int(l_id[-1])
    return s[0:tirLength], s[:-tirLength]


def CheckTIR(rec):
    dic={}
    noTIR=[]
    withTIR=[]
    FinalTIRlist=[]
    s = str(rec.seq)[8:-8]
    if (len(s)>20):
       l_List=list(range(10,int(len(s)/2)))
       l_List=sorted(l_List, reverse=True)
       for l in l_List:
           s1 = s[0:l]
           s2_ = s[-l:]
           s2 = Seq(s2_).reverse_complement()
           d = compare(s1, s2)
           if d < l*0.2:
               dic[str(rec.id)] = l
               withTIR.append(dic)
               break
       noTIR.append(dic)
       FinalTIRlist.append(noTIR)
       FinalTIRlist.append(withTIR)
       return FinalTIRlist
    else:
        FinalTIRlist.append(noTIR)
        FinalTIRlist.append(withTIR)
        return FinalTIRlist

def CheckTSD(rec):
    noTSD=[]
    withTSD=[]
    FinalTSDlist=[]
    s = str(rec.seq)
    l=8
    s1 = s[0:8]
    last20=s[-8:]
    s2 = last20[0:8]
    set1,set2=slidingWindow(s1,s2,8)
    dff=GetDiff(set1,set2)
    TSDexist=isTSD(dff,"DTA")
    if(TSDexist==True):
        withTSD.append(rec.id)
    else:
        noTSD.append(rec.id)
    FinalTSDlist.append(noTSD)
    FinalTSDlist.append(withTSD)
    return FinalTSDlist


def TIRpercent(seq1,seq2):
    d=compare(seq1,seq2)
    l=len(seq1)
    p=(l-d)/l
    p=p*100
    p=round(p, 2)
    return p


def TSDpercent(seq1,seq2):
    d=compare(seq1,seq2)
    l=len(seq1)
    p=(l-d)/l
    p=p*100
    p=round(p, 2)
    return p

def getTSD(tsd_dffset,fam,set1,set2):
    for i in tsd_dffset:
        if tsd_dffset[i]<TSD[fam]*0.2:
            seq1=set1[int(i.split(":")[0])]
            seq2=set2[int(i.split(":")[1])]
            return seq1,seq2


def writeTofa(file,output,both,List_seqwithTIR,fam):
    used=[]
    w=open(output,"a+")
    record=list(SeqIO.parse(file,"fasta"))
    key=[list(dic.keys())[0] for dic in List_seqwithTIR]
    newDic={}
    for d in List_seqwithTIR:
        newDic.update(d)
    for rec in record:
        if str(rec.id) in both and str(rec.id) not in used:
            s = str(rec.seq)[8:-8]
            l=newDic[str(rec.id)]
            s1 = s[0:l]
            s2_ = s[-l:]
            s2 = Seq(s2_).reverse_complement()
            s2=str(s2)
            p_tir=TIRpercent(s1,s2)
            s = str(rec.seq)
            l=8
            s1tsd = s[0:8]
            last20=s[-8:]
            s2tsd = last20[0:8]
            set1,set2=slidingWindow(s1tsd,s2tsd,8)
            dff=GetDiff(set1,set2)
            seq1,seq2=getTSD(dff,"DTA",set1,set2)
            pTSD=TSDpercent(seq1,seq2)
            w.write(">"+str(rec.id)+"_TIR:"+str(s1)+"_"+str(s2_)+"_"+str(p_tir)+"_"+"TSD:"+str(seq1)+"_"+str(seq2)+"_"+str(pTSD)+"\n"+str(rec.seq)[8:-8]+"\n")
            used.append(str(rec.id))


if __name__ == '__main__':
     for i in range(1,13):
         records = list(SeqIO.parse("chr%s_DTA_allCheckIRFHomo.fa"%(i),"fasta"))
         pool1 = multiprocessing.Pool(16)
         L_tir=pool1.map(CheckTIR,records)
         pool1.close()
         pool1.join()
         noTIR=[i[0] for i in L_tir]
         withTIR=[i[1] for i in L_tir]
         noTIR=[i[0] for i in noTIR if len(i)!=0]
         withTIR=[i[0] for i in withTIR if len(i)!=0]
         pool2 = multiprocessing.Pool(16)
         L_tsd=pool2.map(CheckTSD,records)
         pool2.close()
         pool2.join()
         noTSD=[i[0] for i in L_tsd]
         withTSD=[i[1] for i in L_tsd]
         noTSD=[i[0] for i in noTSD if len(i)!=0]
         withTSD=[i[0] for i in withTSD if len(i)!=0]
         print(len(noTIR))
         print(len(withTIR))
         print(len(noTSD))
         print(len(withTSD))

         TIRlist=[list(dic.keys())[0] for dic in withTIR]
         both=set(TIRlist).intersection(set(withTSD))
         print(len(both))
         writeTofa("chr%s_DTA_allCheckIRFHomo.fa"%(i),"chr%s_DTA_irfhomo.fa" % (i),both,withTIR,"DTA")


#if __name__ == '__main__':
#     for i in range(1, 13):
#         records = list(SeqIO.parse("chr%s_DTA_allCheckIRFHomo.fa" % (i), "fasta"))
#         pool1 = multiprocessing.Pool(16)
#         L_tir = pool1.map(CheckTIR, records)
#         pool1.close()
#         pool1.join()
#         noTIR = [i[0] for i in L_tir]
#         withTIR = [i[1] for i in L_tir]
#         noTIR = [i[0] for i in noTIR if len(i) != 0]
#         withTIR = [i[0] for i in withTIR if len(i) != 0]
#         pool2 = multiprocessing.Pool(16)
#         L_tsd = pool2.map(CheckTSD, records)
#         pool2.close()
#         pool2.join()
#         noTSD = [i[0] for i in L_tsd]
#         withTSD = [i[1] for i in L_tsd]
#         noTSD = [i[0] for i in noTSD if len(i) != 0]
#         withTSD = [i[0] for i in withTSD if len(i) != 0]
#         both = set(withTIR).intersection(set(withTSD))
#         writeTofa("chr%s_DTA_allCheckPre.fa" % (i),  "chr%s_irfml_DTA_withTIRTSD_Seq.fa" % (i))
#
#







