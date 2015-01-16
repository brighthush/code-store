/*************************************************************************
	> File Name: Model.cpp
	> Author: bright
	> Mail: luzihao@software.ict.ac.cn
	> Created Time: Tue 06 Jan 2015 01:12:45 PM CST
 ************************************************************************/

#include "Model.h"

#include <string>
#include <pthread.h>

#include "Vocab.h"
using namespace std;

Vocab vocabulary;
real *syn0, *syn1;
real *docvecs;

void initNet()
{
    LL vocabSize = vocabulary.get_vocabSize();
    LL trainDocCnt = vocabulary.get_trainDocCnt();
    ULL next_random = 1;
    int flag = posix_memalign((void **)&syn0, 128, (LL)vocabSize * vectorSize * sizeof(real));
    if(flag!=0) { printf("syn0 allocation failed.\n"); exit(-1); }
    flag = posix_memalign((void **)&docvecs, 128, (LL)trainDocCnt * docvecSize * sizeof(real));
    if(flag!=0) { printf("docvecs allocation failed.\n"); exit(-1); }
    if(hs_flag>0)
    {
        int projSize = docvecSize + window * 2 * vectorSize;
        flag = posix_memalign((void **)&syn1, 128, (LL)vocabSize * projSize * sizeof(real));
        if(flag!=0) { printf("syn1 allocation failed.\n"); exit(-1); }
        
        if(!glPredictStage)
        {
            for(LL i=0; i<vocabSize; ++i) for(LL j=0; j<projSize; ++j)
                syn1[i * projSize + j] = 0;
        }
        else
        {
            printf("read inner node vector from parameters.out\n");
            exit(-1);
        }
    }

    if(!glPredictStage)
    {
        // initialize word vectors to random small real numbers
        for(LL i=0; i<vocabSize; ++i) for(LL j=0; j<vectorSize; ++j)
        {
            next_random = next_random * (ULL)25214903917 + 11;
            real r = ((next_random & 0xFFFF)/(real)(0xFFFF) - 0.5) / (real)vectorSize;
            syn0[i * vectorSize + j] = r;
        }
    }
    else
    {
        printf("read word vectors from wordvecs.out");
        exit(-1);
    }

    for(LL i=0; i<trainDocCnt; ++i) for(LL j=0; j<docvecSize; ++j)
    {
        next_random = next_random * (ULL)25214903917 + 11;
        real r = ((next_random & 0xFFFF)/(real)(0xFFFF) - 0.5) / (real)docvecSize;
        docvecs[i * docvecSize + j] = r;
    }
}

void *trainModelThread(void *id)
{
    LL trainDocCnt = vocabulary.get_trainDocCnt();
    LL trainWordCnt = vocabulary.get_trainWordCnt();
    LL leftIndex = (trainDocCnt / (LL)num_threads) * (LL)id;
    LL rightIndex = min((trainDocCnt / (LL)num_threads) * ((LL)id + 1), trainDocCnt);
    //printf("thread %lld: processing files [%lld, %lld)]\n", (LL)id, \
            leftIndex, rightIndex);
    int projSize = docvecSize + window * 2 * vectorSize;
    real *neu1 = (real *)calloc(projSize, sizeof(real));
    real *neu1e = (real *)calloc(projSize, sizeof(real));

    char *content = (char *)malloc(sizeof(char) * MAX_TEXT_LENGTH);
    LL contentSize = MAX_TEXT_LENGTH;
    LL length = 0;
    int *indexs = NULL;
    int indexsSize = MAX_TEXT_LENGTH / 6;
    indexs = (int *)malloc((LL)indexsSize * sizeof(int));
    
    LL localIter = 0, localTrainedWordCnt = 0;
    real localLearningRate = learningRate;
    while(localIter < numIteration)
    {
        printf("thread: %lld, iteration: %lld\n", (LL)id, localIter);
        for(LL doc=leftIndex; doc<rightIndex; ++doc)
        {
            string docName = vocabulary.getDocName(doc);
            length = readFile((char *)docName.c_str(), content, contentSize);
            //printf("thread %lld, %s\n", (LL)id, filePath);
            int wordCnt = vocabulary.text2Index(content, indexs, indexsSize);
            //printf("thread %lld, wordCnt %d\n", (LL)id, wordCnt);
            if(wordCnt == 0) continue;
            // every windows is a sample
            for(int word=window-1; word<=wordCnt-window; ++word)
            {
                int shift = 0;
                for(int i=0; i<projSize; ++i) { neu1[i] = 0; neu1e[i] = 0; }
                for(int i=0; i<docvecSize; ++i) neu1[shift++] = docvecs[doc*docvecSize + i];
                for(int offset=-window; offset<=window; ++offset) {
                    if(offset == 0) continue;
                    int temp = word+offset;
                    if(temp == -1) temp = vocabulary.searchVocab((char *)"</beg>");
                    else if(temp == wordCnt) temp = vocabulary.searchVocab((char *)"</end>");
                    else temp = indexs[temp];
                    if(temp == -1) printf("oh my god.\n");
                    for(int i=0; i<vectorSize; ++i) neu1[shift++] = syn0[temp * vectorSize + i];
                }
                if(cbow_flag) // train continuous bag of words
                {
                    int center = indexs[word];
                    int codelen = vocabulary.get_codelen(center);
                    LL *point = vocabulary.get_point(center);
                    char *code = vocabulary.get_code(center);
                    if(hs_flag) for(int i=0; i<codelen; ++i)
                    {
                        real sum = 0;
                        LL cnu = point[i] * projSize; // classifer neural unit
                        for(LL j=0; j<projSize; ++j) sum += (neu1[j] * syn1[cnu + j]);
                        if(sum <= -MAX_EXP) sum = 0;
                        else if(sum >= MAX_EXP) sum = 1;
                        else sum = getSigmoid(sum);
                        real g = (1 - code[i] - sum) * localLearningRate;
                        // propagate errors from output to hidden
                        for(LL j=0; j<projSize; ++j) neu1e[j] += g*syn1[cnu+j];
                        // update parameters for each classifier node in Huffman Tree
                        if(!glPredictStage)
                            for(LL j=0; j<projSize; ++j) syn1[cnu+j] += g*neu1[j];
                    }
                    // To do: Negative sampling
                    // if(ns_flag > 0) 
                    // hidden to input
                    shift = 0;
                    for(int i=0; i<docvecSize; ++i) docvecs[doc*docvecSize + i] += neu1e[shift++];
                    if(!glPredictStage) for(int offset=-window; offset<=window; ++offset) {
                        if(offset == 0) continue;
                        int temp = word+offset;
                        if(temp == -1) temp = vocabulary.searchVocab((char *)"</beg>");
                        else if(temp == wordCnt) temp = vocabulary.searchVocab((char *)"</end>");
                        else temp = indexs[temp];
                        for(int i=0; i<vectorSize; ++i) syn0[temp * vectorSize + i] += neu1e[shift++];
                    }
                }
                ++localTrainedWordCnt; ++word_count_actual;
                if(localTrainedWordCnt % 10000 == 0)
                {
                    localLearningRate = learningRate * \
                                        (1 - word_count_actual / (real)(numIteration * trainWordCnt + 1));
                    if(localLearningRate < learningRate * 0.0001) 
                        localLearningRate = learningRate * 0.0001;
                    printf("thread: %lld, localLearningRate: %.8lf\n", (LL)id, localLearningRate);
                }
            }
        }
        ++localIter;
    }
    printf("thread %lld finished.\n", (LL)id);
    free(content);
    free(indexs);
    free(neu1);
    free(neu1e);
    pthread_exit(NULL);
}

void trainModel()
{
    printf("begin to create huffman tree.\n");
    vocabulary.createBinaryTree();
    printf("finished create huffman tree.\n");
    // create threads for training
    pthread_t *threads = (pthread_t *)malloc(num_threads * sizeof(pthread_t));
#ifdef __DEBUG__INFO__
    printf("begin initNet\n");
#endif
    initNet();
    printf("starting training model using file %s\n", train_file);
    for(LL i=0; i<num_threads; ++i) 
    {
        threads[i] = NULL;
        int temp = pthread_create(&threads[i], NULL, trainModelThread, (void *)i);
        if(temp != 0) { printf("create thread %d failed.", i); exit(-1); }
    }
    for(int i=0; i<num_threads; ++i) pthread_join(threads[i], NULL);
    //free(syn0);
    //free(syn1);
}

void writeWordvec(char *filePath)
{
    FILE *fo;
    fo = fopen(filePath, "wb");
    if(fo == NULL) { printf("open output file %s failed.\n", filePath); exit(-1); }
    LL vocabSize = vocabulary.get_vocabSize(); 
    fprintf(fo, "%lld %lld\n", vocabSize, vectorSize);
    for(LL i=0; i<vocabSize; ++i)
    {
        fprintf(fo, "%s ", vocabulary.get_word(i));
        for(LL j=0; j<vectorSize; ++j) 
            fprintf(fo, "%.08lf%c", syn0[i*vectorSize + j], j==vectorSize-1?'\n':' ');
    }
    fclose(fo);
}

/*
 * parameter output file format:
 * windowSize vectorSize docvecSize vocabSize trainDocCnt
 * vocabSize-1 projSize
 * col_0_0 col_0_1 ... col_0_{projSize-1}
 * ...
 * col_{vocabSize-2}_0 col_{vocabSize-2}_1 ... col_{vocabSize-2}_{projSize-1}
 * 
 * note: The number of inner node for Hierarchical Softmax algorithm is vocabSize-1.
 * The size of projection layer is docvecSize+2*window*vectorSize.
 * The variable in program represent inner node is syn1.
 */
void writeParameter(char *filePath)
{
    if(strlen(filePath) == 0) { return ; }
    FILE *fo;
    fo = fopen(filePath, "wb");
    if(fo == NULL) { printf("open parameters file failed.\n"); exit(-1); }
    LL vocabSize = vocabulary.get_vocabSize();
    LL trainDocCnt = vocabulary.get_trainDocCnt();
    int projSize = docvecSize + window * 2 * vectorSize;
    
    // windowSize vectorSize docvecSize vocabSize trainDocCnt
    fprintf(fo, "%lld %lld %lld %lld %lld\n", \
            (LL)window, (LL)vectorSize, (LL)docvecSize, (LL)vocabSize, (LL)trainDocCnt);
    
    // inner node of huffman tree, each node represents a logistic classification
    fprintf(fo, "%lld %lld\n", (LL)vocabSize - 1, (LL)projSize);
    for(LL i=0; i<vocabSize-1; ++i) for(LL j=0; j<projSize; ++j)
        fprintf(fo, "%.8lf%c", syn1[i * projSize + j], j==projSize-1?'\n':' '); 
    fclose(fo);
}

/*
 * Read parameters for syn1, more information see comment for function writeParameter.
 */
void readParameter(char *filePath, real *syn1, LL projSize)
{
    if(strlen(filePath) == 0) { printf("parameter file is not specified.\n"); exit(-1); }
    FILE *fin;
    fin = fopen(filePath, "r");
    if(fin == NULL) { printf("open parameter file faild in readParamter function.\n"); exit(-1); }
    
    LL vocabSize = vocabulary.get_vocabSize();
    LL trainDocCnt = vocabulary.get_trainDocCnt();
    LL temp;
    fscanf(fin, "%lld", &temp); if(temp != window) { 
        printf("read parameter window is not same with current model.\n"); exit(-1); 
    }
    fscanf(fin, "%lld", &temp); if(temp != vectorSize) { 
        printf("read parameter vectorSize is not same with current model.\n"); exit(-1); 
    }
    fscanf(fin, "%lld", &temp); if(temp != docvecSize) {
        printf("read parameter docvecSize is not same with current model.\n"); exit(-1);
    }
    fscanf(fin, "%lld", &temp); if(temp != vocabSize) {
        printf("read parameter vocabSize is not same with current model.\n"); exit(-1);
    }
    fscanf(fin, "%lld", &temp); // This is parameter trainDocCnt.
    
    fclose(fin);
}

void writeDocvec(char *filePath)
{
    if(strlen(filePath) == 0) return;
    FILE *fo;
    fo = fopen(filePath, "wb");
    if(fo == NULL) { printf("open docvec file failed.\n"); exit(-1); }
    LL trainDocCnt = vocabulary.get_trainDocCnt();
    fprintf(fo, "%lld %lld\n", trainDocCnt, (LL)docvecSize);
    for(LL i=0; i<trainDocCnt; ++i) 
    {
        string fileName = vocabulary.getDocName(i);
        fprintf(fo, "%s ", fileName.c_str());
        for(LL j=0; j<docvecSize; ++j)
            fprintf(fo, "%.8lf%c", docvecs[i * docvecSize + j], j==docvecSize-1?'\n':' ');
    }
    fclose(fo);
}

