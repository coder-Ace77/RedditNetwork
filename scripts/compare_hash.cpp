// #include <iostream>
// #include <fstream>
// #include <string>
// #include <chrono>
// #include <filesystem>
// #include <algorithm>
// #include <vector>
// #include <omp.h>
// #include <cstdint>
// #include <tuple>
// #include <iomanip>
// #include <unordered_set>

// using namespace std;
// namespace fs = std::filesystem;

// const size_t MAX_N = 10000;

// ofstream output_file;
// ofstream done_file;

// inline void read_hashes_stream(const string& filename, vector<pair<uint64_t, int>>& hashes) {
//     ifstream file(filename);
//     if (!file.is_open()) {
//         cerr << "Error opening file: " << filename << endl;
//         return;
//     }
//     hashes.reserve(MAX_N);
//     string line;
//     getline(file, line); 
//     while (getline(file, line)) {
//         istringstream iss(line);
//         uint64_t hash;
//         int val;
//         if (!(iss >> hash >> val)) {
//             cerr << "Error parsing hash in " << filename << endl;
//             continue;
//         }
//         hashes.emplace_back(hash, val);
//     }
// }

// tuple<long long, long long> compare_hashes(const vector<pair<uint64_t, int>>& hashes1, 
//                                          const vector<pair<uint64_t, int>>& hashes2) {
//     long long i = 0, j = 0, common = 0;
//     long long dot = 0;
//     const long long count1 = hashes1.size();
//     const long long count2 = hashes2.size();

//     while (i < count1 && j < count2) {
//         if (hashes1[i].first == hashes2[j].first) {
//             dot += hashes1[i].second * hashes2[j].second;
//             ++common;
//             ++i;
//             ++j;
//         } 
//         else if (hashes1[i].first < hashes2[j].first) {
//             ++i;
//         } 
//         else {
//             ++j;
//         }
//     }
//     return make_tuple(common, dot);
// }

// void compare_files(const string& file1, const string& file2,int count){
//     vector<pair<uint64_t, int>> hashes1, hashes2;
//     read_hashes_stream(file1, hashes1);
//     read_hashes_stream(file2, hashes2);

//     if (hashes1.empty() || hashes2.empty()) {
//         return;
//     }

//     auto [common, dot] = compare_hashes(hashes1, hashes2);

//     #pragma omp critical
//     {
//         output_file << fs::path(file1).filename().string() << " " 
//                    << fs::path(file2).filename().string() << " " 
//                    << common << " " << dot << "\n";

//         ofstream meta_file("meta.txt", ios::out);
//         if (meta_file.is_open()){
//             meta_file << count;
//             meta_file.close();
//         }else{
//             cerr << "Error updating meta.txt" << endl;
//         }
//     }
// }

// int main() {
//     const string folderPath = "./hash";
    
//     output_file.open("out.txt");
//     if (!output_file.is_open()) {
//         cerr << "Error creating output file out.txt" << endl;
//         return EXIT_FAILURE;
//     }

//     done_file.open("done.txt", ios::app); // Append mode
//     if (!done_file.is_open()) {
//         cerr << "Error creating done.txt" << endl;
//         output_file.close();
//         return EXIT_FAILURE;
//     }
//     int processed = 0;
//     ifstream meta_file("meta.txt");
//     if (meta_file.is_open()) {
//         string line;
//         while (getline(meta_file, line)) {
//             processed = stoi(line);
//         }
//         meta_file.close();
//     }


//     int processed_count = 0;
//     const auto startTime = chrono::high_resolution_clock::now();

//     ifstream todo_input("todo.csv");
//     if (!todo_input.is_open()) {
//         cerr << "Error opening to_do.txt" << endl;
//         return false;
//     }
//     int count = 0;
//     while(true){
//         string line;
//         while(getline(todo_input, line)){
//             count++;
//             if(count<=processed){
//                 cout<<line<<" Skipped.\n";
//                 continue;
//             }
//             istringstream iss(line);
//             string file1, file2;
//             if (iss >> file1 >> file2){
//                 string file1_path = folderPath + "/" + file1 + ".txt";
//                 string file2_path = folderPath + "/" + file2 + ".txt";
//                 if (!fs::exists(file1_path)){
//                     cerr << "File not found: " << file1_path<< endl;
//                     continue;
//                 }else if(!fs::exists(file2_path)){
//                     cerr << "File not found: " << file2_path<< endl;
//                     continue;
//                 }
//                 compare_files(file1_path, file2_path,count);
//             }
//         }
//     }

//     const auto endTime = chrono::high_resolution_clock::now();
//     const auto totalDuration = chrono::duration_cast<chrono::milliseconds>(endTime - startTime);

//     cout << "\nComparison Results Summary:\n";
//     cout << "==========================\n";
//     cout << "Total pairs processed: " << processed_count << "\n";
//     cout << "Total processing time: " << totalDuration.count() << " ms\n";
    
//     if (processed_count > 0) {
//         cout << "Average time per pair: " 
//              << (totalDuration.count() / static_cast<double>(processed_count)) 
//              << " ms\n";
//     }

//     output_file.close();
//     done_file.close();
//     return EXIT_SUCCESS;
// }

#include <iostream>
#include <fstream>
#include <string>
#include <chrono>
#include <filesystem>
#include <algorithm>
#include <vector>
#include <omp.h>
#include <cstdint>
#include <tuple>
#include <iomanip>
#include <unordered_set>

using namespace std;
namespace fs = std::filesystem;

const size_t MAX_N = 10000;

ofstream output_file;
ofstream done_file;

void print_progress_bar(int current, int total, int width = 50) {
    float progress = static_cast<float>(current) / total;
    int pos = static_cast<int>(width * progress);

    cout << "[";
    for (int i = 0; i < width; ++i) {
        if (i < pos) cout << "=";
        else if (i == pos) cout << ">";
        else cout << " ";
    }
    cout << "] " << setw(3) << static_cast<int>(progress * 100.0) << "% ";
    cout << current << "/" << total << "\r";
    cout.flush();
}

inline void read_hashes_stream(const string& filename, vector<pair<uint64_t, int>>& hashes) {
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "Error opening file: " << filename << endl;
        return;
    }
    hashes.reserve(MAX_N);
    string line;
    getline(file, line); 
    while (getline(file, line)) {
        istringstream iss(line);
        uint64_t hash;
        int val;
        if (!(iss >> hash >> val)) {
            cerr << "Error parsing hash in " << filename << endl;
            continue;
        }
        hashes.emplace_back(hash, val);
    }
}

tuple<long long, long long> compare_hashes(const vector<pair<uint64_t, int>>& hashes1, 
                                         const vector<pair<uint64_t, int>>& hashes2) {
    long long i = 0, j = 0, common = 0;
    long long dot = 0;
    const long long count1 = hashes1.size();
    const long long count2 = hashes2.size();

    while (i < count1 && j < count2) {
        if (hashes1[i].first == hashes2[j].first) {
            dot += hashes1[i].second * hashes2[j].second;
            ++common;
            ++i;
            ++j;
        } 
        else if (hashes1[i].first < hashes2[j].first) {
            ++i;
        } 
        else {
            ++j;
        }
    }
    return make_tuple(common, dot);
}

void compare_files(const string& file1, const string& file2, int count, int total_pairs) {
    vector<pair<uint64_t, int>> hashes1, hashes2;
    read_hashes_stream(file1, hashes1);
    read_hashes_stream(file2, hashes2);

    if (hashes1.empty() || hashes2.empty()) {
        return;
    }

    auto [common, dot] = compare_hashes(hashes1, hashes2);

    #pragma omp critical
    {
        output_file << fs::path(file1).filename().string() << " " 
                   << fs::path(file2).filename().string() << " " 
                   << common << " " << dot << "\n";

        done_file << fs::path(file1).filename().string() << " " 
                 << fs::path(file2).filename().string() << "\n";

        ofstream meta_file("meta.txt", ios::out);
        if (meta_file.is_open()){
            meta_file << count;
            meta_file.close();
        } else {
            cerr << "Error updating meta.txt" << endl;
        }
        
        // Update progress every 10 pairs or when complete
        if (count % 10 == 0 || count == total_pairs) {
            print_progress_bar(count, total_pairs);
        }
    }
}

int count_lines_in_file(const string& filename) {
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "Error opening file: " << filename << endl;
        return 0;
    }
    
    int count = 0;
    string line;
    while (getline(file, line)) {
        count++;
    }
    return count;
}

int main() {
    const string folderPath = "./hash";
    const string todo_filename = "todo.csv";
    
    // First count total number of pairs to process
    int total_pairs = count_lines_in_file(todo_filename);
    if (total_pairs == 0) {
        cerr << "No pairs to process in " << todo_filename << endl;
        return EXIT_FAILURE;
    }

    output_file.open("out.txt");
    if (!output_file.is_open()) {
        cerr << "Error creating output file out.txt" << endl;
        return EXIT_FAILURE;
    }

    done_file.open("done.txt", ios::app); // Append mode
    if (!done_file.is_open()) {
        cerr << "Error creating done.txt" << endl;
        output_file.close();
        return EXIT_FAILURE;
    }

    // Get last processed count from meta file
    int processed = 0;
    ifstream meta_file("meta.txt");
    if (meta_file.is_open()) {
        string line;
        if (getline(meta_file, line)) {
            try {
                processed = stoi(line);
            } catch (...) {
                cerr << "Error reading meta.txt" << endl;
            }
        }
        meta_file.close();
    }

    cout << "Resuming from pair " << processed << " of " << total_pairs << endl;
    print_progress_bar(processed, total_pairs);

    const auto startTime = chrono::high_resolution_clock::now();

    ifstream todo_input(todo_filename);
    if (!todo_input.is_open()) {
        cerr << "Error opening " << todo_filename << endl;
        output_file.close();
        done_file.close();
        return EXIT_FAILURE;
    }

    int count = 0;
    string line;
    while (getline(todo_input, line)) {
        count++;
        if (count <= processed) {
            continue; // Skip already processed pairs
        }

        istringstream iss(line);
        string file1, file2;
        if (iss >> file1 >> file2) {
            string file1_path = folderPath + "/" + file1 + ".txt";
            string file2_path = folderPath + "/" + file2 + ".txt";

            if (!fs::exists(file1_path)) {
                cerr << "\nFile not found: " << file1_path << endl;
                continue;
            }
            if (!fs::exists(file2_path)) {
                cerr << "\nFile not found: " << file2_path << endl;
                continue;
            }

            compare_files(file1_path, file2_path, count, total_pairs);
        }
    }

    // Ensure progress bar shows 100% at completion
    print_progress_bar(total_pairs, total_pairs);
    cout << endl; // Move to next line after progress bar

    const auto endTime = chrono::high_resolution_clock::now();
    const auto totalDuration = chrono::duration_cast<chrono::milliseconds>(endTime - startTime);

    cout << "\nComparison Results Summary:\n";
    cout << "==========================\n";
    cout << "Total pairs in file: " << total_pairs << "\n";
    cout << "Pairs processed: " << (count > processed ? count - processed : 0) << "\n";
    cout << "Total processing time: " << totalDuration.count() << " ms\n";
    
    if (count > processed) {
        cout << "Average time per pair: " 
             << (totalDuration.count() / static_cast<double>(count - processed)) 
             << " ms\n";
    }

    output_file.close();
    done_file.close();
    return EXIT_SUCCESS;
}