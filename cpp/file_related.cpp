/*
 * Created by brighthush at sina dot com
 * This file shows how to operate file, including read file content into char array.
 */

#include <iostream>
#include <cstdio>
#include <cstdlib>

using namespace std;

#define MAX_TEXT_LENGTH 1000
typedef long long LL;

// Description: using fseek to set the read cursor to the end of the file, then use ftell to get the
// offset to the file begin, yet the offset is the size of the file.
// Parameters
// filePath: the path of the file.
// content: This is the point to the memory which you want to store the content in. The size of this
//          memory is indicated by contentSize.
// contentSize: The size of the memory, this is a reference. This means that this parameters may be
//              changed by this function. When the file size is bigger then contentSize, the memory
//              will be realloc to a bigger size.
// return: The size of the file, it means the valid content in memory, not the parameter contentSize.
LL readFile(char *filePath, char *content, LL &contentSize)
{
    FILE *pf = NULL;
    pf = fopen(filePath, "rb");
    if(pf == NULL) { printf("open file %s failed.\n", filePath); exit(-1); }
    fseek(pf, 0, SEEK_END);
    LL length = ftell(pf);
    if(length+1 >= contentSize) { contentSize = length + 1000; content = (char *)realloc(content, contentSize); }
    rewind(pf);
    length = fread(content, 1, length, pf);
    content[length] = '\0';
    fclose(pf);
    return length;
}

int main()
{
    char *filePath = "./data.txt";
    LL contentSize = MAX_TEXT_LENGTH;
    char *content = (char *)malloc(sizeof(char) * MAX_TEXT_LENGTH);
    if(content == NULL) { printf("allocate memory for content failed.\n"); exit(-1); }
    LL length = readFile(filePath, content, contentSize);
    printf("%s\n", content);
    return 0;
}
