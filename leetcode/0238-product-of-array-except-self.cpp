// LC-238 — Source: NeetCode 150 (Arrays & Hashing)
/* Notes:
We will use vector of prefix & suffix product of numers
and use this equation: number[i] = prefix[i-1] * suffix[i+1]
but for the first number it will be suffix[1] 
and for the last number it will be prefix[n-2]

example:

numbers: 1          2     3     4    5
prefix:  1          2     6     24   120
suffix:  120        120   60    20   5
algo:    suff[1]    1*60  2*20  6*5  pref[n-2]

*/

#include <bits/stdc++.h>
using namespace std;

vector<int> productExceptSelf(vector<int>& nums) {
    int n = nums.size();
    vector<int> pref(n), suff(n);
    pref[0] = nums[0];
    for (int i = 1; i < n; i++) pref[i] = pref[i-1]*nums[i];
    suff[n-1] = nums[n-1];
    for (int i = n-2; i >= 0; i--) suff[i] = suff[i+1]*nums[i];
    vector<int>ans(n);
    ans[0] = suff[1];
    ans[n-1] = pref[n-2];
    for (int i = 1; i < n-1; i++) {
        ans[i] = pref[i-1] * suff[i+1];
    }
    return ans;
}

int main () {
    vector<int> nums = {1,2,3,4};
    vector<int> ans = productExceptSelf(nums);
    for (int& i : ans) cout << i << " ";
}