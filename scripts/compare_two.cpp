#include <iostream>
#include <fstream>
#include <string>
#include <chrono>
#include <filesystem>
#include <algorithm>
#include <vector>
#include <omp.h>

using namespace std;
namespace fs = std::filesystem;

const int  MAX_N = 2000000;

int compareFiles(const string& file1, const string& file2){
    vector<string> usernames1;
    vector<string> usernames2;
    usernames1.reserve(MAX_N);
    usernames2.reserve(MAX_N);
    int count1 = 0, count2 = 0;
    {
        ifstream file(file1);
        if (!file.is_open()) {
            cerr << "Error: Could not open file " << file1 << endl;
            return 0;
        }
        string line;
        getline(file, line); 
        while (getline(file, line)) {
            size_t pos = line.find(',');
            if (pos != string::npos) {
                usernames1.push_back(line.substr(0, pos));
            }
        }
    }

    {
        ifstream file(file2);
        if (!file.is_open()){
            cerr << "Error: Could not open file " << file2 << endl;
            return 0;
        }

        string line;
        getline(file, line); 

        while (getline(file, line)){
            size_t pos = line.find(',');
            if (pos != string::npos) {
                usernames2.push_back(line.substr(0,pos));
            }
        }
    }
    int i = 0, j = 0, commonCount = 0;
    count1 = usernames1.size() , count2 = usernames2.size();
    while (i < count1 && j < count2) {
        if (usernames1[i] == usernames2[j]) {
            i++;
            j++;
            commonCount++;
        } else if (usernames1[i] < usernames2[j]) {
            i++;
        } else {
            j++;
        }
    }
    double val = commonCount / (1.0*min(count1,count2));
    cout<<file1<<" "<<file2<<" "<<count1<<" "<<count2<<" "<<commonCount<<" "<<val<<"\n";
    return commonCount;
}

int main(){
    const string folderPath = "./output/csv";
    vector<string> csvFiles;

    try {
        for (const auto& entry : fs::directory_iterator(folderPath)) {
            if (entry.is_regular_file() && entry.path().extension() == ".csv") {
                csvFiles.push_back(entry.path().string());
            }
        }
    } catch (const fs::filesystem_error& e) {
        cerr << "Error accessing directory '" << folderPath << "': " << e.what() << endl;
        return EXIT_FAILURE;
    }

    if (csvFiles.empty()) {
        cerr << "Error: No CSV files found in directory '" << folderPath << "'" << endl;
        return EXIT_FAILURE;
    }

    const size_t numFiles = csvFiles.size();
    const size_t expectedPairs = numFiles * (numFiles - 1) / 2;
    int actualPairs = 0;

    const auto startTime = chrono::high_resolution_clock::now();

    #pragma omp parallel for schedule(dynamic) reduction(+:actualPairs)
    for (size_t i = 0; i < numFiles; ++i) {
        for (size_t j = i + 1; j < numFiles; ++j) {
            int ans = compareFiles(csvFiles[i],csvFiles[j]);
            actualPairs++;
        }
    }

    const auto endTime = chrono::high_resolution_clock::now();
    const auto totalDuration = chrono::duration_cast<chrono::milliseconds>(endTime - startTime);

    cout << "\nComparison Results Summary:\n";
    cout << "==========================\n";
    cout << "Directory scanned: " << folderPath << "\n";
    cout << "CSV files found: " << numFiles << "\n";
    cout << "Expected file pairs: " << expectedPairs << "\n";
    cout << "Actual pairs processed: " << actualPairs << "\n";
    cout << "Total processing time: " << totalDuration.count() << " ms\n";
    
    if (actualPairs > 0) {
        cout << "Average time per pair: " 
             << (totalDuration.count() / static_cast<double>(actualPairs)) 
             << " ms\n";
    }

    return EXIT_SUCCESS;
}