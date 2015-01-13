/*************************************************************************
	> File Name: text2vec.cpp
	> Author: bright
	> Mail: luzihao@software.ict.ac.cn
	> Created Time: Mon 12 Jan 2015 04:36:01 PM CST
 ************************************************************************/

#include <iostream>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>

#include "glMember.h"
#include "Vocab.h"
#include "Model.h"

using namespace std;

int main(int argc, char **argv)
{
    if(argc == 1)
    {
        printf("TEXT WORD VECTOR estimation toolkit v0.1\n");
        printf("Options:\n");
        printf("\t-predict <0 or 1>\n");
        printf("\t\tindicate run for training or predicting.\n");
        printf("\t-trainDataPath <train data directory path>\n");
        printf("\t\tindicate the path for train data.\n");
        printf("\t-testDataPath <test data directory path>\n");
        printf("\t\tindicate the path for test data. In training stage, this paramter can be ignored "
                "in training stage.\n");
        return 0;
    }

    strcpy(trainDataPath, "../python/des/");
    strcpy(testDataPath, "../python/test/");
    
    int pos;
    if((pos = argPos((char *)"-predict", argc, argv)) > 0) glPredictStage = atoi(argv[pos+1]);
    if((pos = argPos((char *)"-trainDataPath", argc, argv)) > 0) strcpy(trainDataPath, argv[pos+1]);
    if((pos = argPos((char *)"-testDataPath", argc, argv)) > 0) strcpy(testDataPath, argv[pos+1]);
    
    initExpTable();

    vector<string> paths = readDir(trainDataPath);
    
    char *filePath = (char *)malloc(sizeof(char) * 1000);
    if(filePath == NULL) { printf("allocate memory for filePath failed in main.\n"); exit(-1); }
    char *content = (char *)malloc(sizeof(char) * MAX_TEXT_LENGTH);
    LL contentSize = (LL)MAX_TEXT_LENGTH;
    if(content == NULL) { printf("allocate for content failed.\n"); exit(-1); }
    
    strcpy(content, " </beg> </end>");
    vocabulary.addText2Vocab(content);
    //printf("index for </beg> </end> %d %d\n", \
    //        vocabulary.searchVocab("</beg>"), vocabulary.searchVocab("</end>"));
    for(int i=0; i<paths.size(); ++i)
    {
        strcpy(filePath, paths[i].c_str());
        printf("read file: %s\n", filePath);
        LL length = readFile(filePath, content, contentSize);
        vocabulary.addText2Vocab(content);
        vocabulary.addDoc(paths[i]);
    }

    cout << "vocabSize: " << vocabulary.get_vocabSize() << endl;
    vocabulary.sortVocab();
    if(glPredictStage) 
    {
        paths = readDir(testDataPath);
        vocabulary.chage2Test(paths);
    }
    
    trainModel();
    writeWordvec((char *)"./wordvecs.out");
    writeParameter((char *)"./parameters.out");
    writeDocvec((char *)"./docvecs.out");
    free(syn0); free(syn1); free(docvecs);
    return 0;
}

