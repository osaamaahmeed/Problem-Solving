// LC-128 — Source: NeetCode 150 (Arrays & Hashing)
/* Notes:
we use a set to store sorted numbers and remove duplicates
then loop over the set 
let's take the first number and keep checking if that number + 1 is in the set
if it exist -> we increase a counter
if it don't exists -> we compare the last loop with the current and put the max in the asnwer
and also keep looping over the set after the last number I was on

Time Complxity O(N * Log N)

need optimization !
*/

#include <bits/stdc++.h>
using namespace std;

int longestConsecutive(vector<int>& nums) {
    int ans = 0;
    set<int>s;
    for (int& i : nums) s.insert(i);

    set<int>::iterator it = s.begin();
    while (it != s.end()) {
        set<int>::iterator temp = it;
        int next = *temp;
        int curr = 0;
        while (s.count(next)) {
            curr++;
            next++;
            ++temp;
        }
        ans = max(ans, curr);
        it = temp;
    }
    return ans;
}

int main () {
    vector<int> a = {100,4,200,1,3,2};
    cout << longestConsecutive(a);

}