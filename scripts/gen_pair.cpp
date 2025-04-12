#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>

using namespace std;

vector<string> split(const string& line, char delimiter) {
    vector<string> tokens;
    stringstream ss(line);
    string token;
    while (getline(ss, token, delimiter)) {
        tokens.push_back(token);
    }
    return tokens;
}

int main() {
    string input_file = "redits.csv";
    string output_file = "pairs.csv";

    ifstream infile(input_file);
    ofstream outfile(output_file);

    if (!infile.is_open()) {
        cerr << "Error: Could not open input file " << input_file << endl;
        return 1;
    }

    if (!outfile.is_open()) {
        cerr << "Error: Could not open output file " << output_file << endl;
        return 1;
    }

    vector<string> subreddits;
    string line;

    // Skip the header row
    getline(infile, line);

    // Read the first column of the first 10,000 rows
    int count = 0;
    while (getline(infile, line) && count<2000){
        vector<string> tokens = split(line, ',');
        if(!tokens.empty()){
            subreddits.push_back(tokens[0]);
        }
        count++;
    }

    infile.close();

    // Write the header to the output file
    outfile << "Subreddit1,Subreddit2\n";

    for (size_t i = 0; i < subreddits.size(); ++i) {
        for (size_t j = i + 1; j < subreddits.size(); ++j) {
            outfile << subreddits[i] << "," << subreddits[j] << "\n";
        }
    }

    outfile.close();

    cout << "Generated " << (subreddits.size() * (subreddits.size() - 1)) / 2
         << " pairs and saved them to " << output_file << "." << endl;

    return 0;
}