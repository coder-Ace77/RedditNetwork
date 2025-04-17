#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <vector>
#include <sstream>
#include <iomanip>
#include <cstdint>
#include <algorithm>

namespace fs = std::filesystem;
using namespace std;

const int MIN_POSTS = 3; 

uint64_t mod_pow(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t result = 1;
    base = base % mod;
    while (exp > 0) {
        if (exp % 2 == 1) {
            result = (result * base) % mod;
        }
        exp = exp >> 1;
        base = (base * base) % mod;
    }
    return result;
}

uint64_t polynomial_hash(const std::string& str) {
    const uint64_t p = 31; // prime number
    const uint64_t m = (1ULL << 61) - 1; 
    uint64_t hash_value = 0;
    
    for (size_t i = 0; i < str.size(); ++i) {
        char c = str[i];
        char lower_c = tolower(static_cast<unsigned char>(c));
        uint64_t char_value = (lower_c >= 'a' && lower_c <= 'z') ? (lower_c - 'a' + 1) : static_cast<uint64_t>(c);
        uint64_t power = mod_pow(p, i, m);
        hash_value = (hash_value + char_value * power) % m;
    }
    return hash_value;
}

string convert_to_space_separated(const string& csv_line) {
    string space_separated;
    bool in_quotes = false;
    bool first_field = true;
    
    for (char c : csv_line) {
        if (c == '"') {
            in_quotes = !in_quotes;
        } else if (c == ',' && !in_quotes) {
            space_separated += ' ';
            first_field = false;
        } else {
            space_separated += c;
        }
    }
    
    return space_separated;
}

void process_csv_file(const fs::path& input_path, const fs::path& output_dir) {
    ifstream input_file(input_path);
    if (!input_file.is_open()) {
        cerr << "Error opening file: "<<input_path<<endl;
        return;
    }

    if (!fs::exists(output_dir)) {
        fs::create_directory(output_dir);
    }

    fs::path output_path = output_dir / input_path.filename().replace_extension(".txt");
    ofstream output_file(output_path);
    if (!output_file.is_open()) {
        cerr << "Error creating output file: " << output_path << endl;
        input_file.close();
        return;
    }

    vector<tuple<uint64_t, string, string>> rows_data;
    string header;
    bool is_first_line = true;
    string line;

    while (getline(input_file, line)) {
        if (line.empty()) continue;

        if (is_first_line){
            // Modify header to only include total_post
            header = "total_post";
            is_first_line = false;
            continue;
        }

        size_t pos = line.find(',');
        if (pos == string::npos) {
            cerr << "Invalid line format: " << line << endl;
            continue;
        }

        string username = line.substr(0, pos);
        if(username=="AutoModerator"){
            cout<<"SKIPPED\n";
            continue;
        }
        string rest_of_line = line.substr(pos + 1);
        
        // Parse the line to get total_post
        istringstream iss(rest_of_line);
        string token;
        vector<string> tokens;
        
        bool in_quotes = false;
        string current_token;
        for (char c : rest_of_line) {
            if (c == '"') {
                in_quotes = !in_quotes;
            } else if (c == ',' && !in_quotes) {
                tokens.push_back(current_token);
                current_token.clear();
            } else {
                current_token += c;
            }
        }
        tokens.push_back(current_token);
        
        if (tokens.empty()) {
            cerr << "Invalid data format: " << rest_of_line << endl;
            continue;
        }
        
        // The last token is total_post
        int total_posts = 0;
        try {
            total_posts = stoi(tokens.back());
        } catch (...) {
            cerr << "Invalid total_post value: " << tokens.back() << endl;
            continue;
        }
        
        // Only include users with more than MIN_POSTS
        if (total_posts > MIN_POSTS) {
            uint64_t hash = polynomial_hash(username);
            // Only keep the total_post value in the output
            rows_data.emplace_back(hash, username, to_string(total_posts));
        }
    }

    sort(rows_data.begin(), rows_data.end(),
        [](const auto& a, const auto& b) { return get<0>(a) < get<0>(b); });

    output_file << "hash " << header << "\n";  // Add "hash" as first column in header
    for (const auto& [hash, username, rest] : rows_data) {
        output_file << hash << " " << rest << "\n"; // Space-separated format
    }

    input_file.close();
    output_file.close();
}

int main() {
    const string input_dir = "./Root";
    const string output_dir = "./hash_2";

    try {
        if (!fs::exists(input_dir)) {
            cerr << "Input directory does not exist: " << input_dir << endl;
            return 1;
        }

        for (const auto& entry : fs::directory_iterator(input_dir)) {
            if (entry.is_regular_file() && entry.path().extension() == ".csv") {
                cout << "Processing: " << entry.path() << endl;
                process_csv_file(entry.path(), output_dir);
            }
        }
        cout << "All files processed successfully." << endl;
    } catch (const fs::filesystem_error& e) {
        cerr << "Filesystem error: " << e.what() << endl;
        return 1;
    }

    return 0;
}