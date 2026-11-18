// LC-347 — Source: NeetCode 150 (Arrays & Hashing)
/* Notes:
First Solution (Worst):
1. Create a unordered map to store the frequancy of every number

2. Create a vector of pairs to store the same frequancey data but vise versa
so the first value is the frequancey and the second value is the number itself
why? to use the premade sort function so it sort it based on the frequncy

3. loop over the last vector form the end to get the answer.

Time Complexity: O(N * Log n)
*/

#include<bits/stdc++.h>
using namespace std;

vector<int> topKFrequent(vector<int>& nums, int k) {
    vector<int> ans;
    unordered_map<int,int> freq;
    for (int i : nums) freq[i]++;
    vector<pair<int,int>> v(freq.size());
    int index = 0;
    for (auto i : freq) {
        v[index].first = i.second;
        v[index].second = i.first;
        index++;
    }
    sort(v.begin(), v.end());
    int i = v.size()-1;
    while (k-- && i >= 0) {
        ans.push_back(v[i].second);
        i--;
    }
    return ans;
}

int main () {
    vector<int>nums = {1,2,1,2,1,2,3,1,3,2};
    vector<int>a = topKFrequent(nums, 2);
    for (auto i : a) cout << i << " ";
}